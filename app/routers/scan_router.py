# app/routers/scan_router.py

import asyncio
import json
import logging
import random
import traceback
from typing import Optional, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.sql import expression
from sqlalchemy.orm import Session

from app.integrations.shodan import is_ip_address
from app.db import crud
from app.services.aggregator import aggregate_scan_data
from app.integrations.nvd_guess import guess_cve_by_product_vendor
from app.integrations.nvd_enrich import enrich_vulnerability_async
from app.dependencies import get_db
from app.auth import get_current_active_user
from app.models import User

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/scan",
    tags=["scan"],
    responses={404: {"description": "Not found"}}
)


class ScanRequest(BaseModel):
    target: str = Field(..., example="8.8.8.8")
    asset_id: Optional[int] = Field(
        None, description="(Optional) existing Asset ID to link this scan to"
    )

    @field_validator("target", mode="before")
    @classmethod
    def validate_target(cls, v):
        v_str = str(v).strip() if v else ""
        if not v_str:
            raise ValueError("Target must be provided.")
        return v_str


async def ensure_test_user(db: Session):
    from app.auth import get_password_hash

    user = (
        db.query(User)
        .filter(expression.true() & (User.email == "manager@example.com"))
        .first()
    )
    if not user:
        user = User(
            name="Test Manager",
            email="manager@example.com",
            role="manager",
            password_hash=get_password_hash("password123"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.password_hash.startswith("$2b$"):
        user.password_hash = get_password_hash("password123")
        db.commit()
        db.refresh(user)
    return user

async def normalize_vulnerability_async(
    vuln: dict,
    default_onyphe: dict = None,
    discovered_brands: List[str] = None,
    apply_filter: bool = True,
) -> Optional[dict]:
    """
    Normalize one raw vulnerability record into our DB shape,
    enriching via NVD if CVE, extracting OS by keyword,
    and deriving auth strictly from CVSS vector.
    """
    try:
        logger.info("→ normalize input: %s", json.dumps(vuln))
        # 1) extract or guess CVE
        cve = (vuln.get("cve_id") or vuln.get("cve") or "").strip()
        if not cve or cve.upper() == "N/A":
            vendor = (vuln.get("osvendor") or (default_onyphe or {}).get("osvendor", "")).strip()
            guessed = guess_cve_by_product_vendor(
                vendor, vuln.get("product", ""), vuln.get("version", ""), cpe_type="o"
            )
            if guessed:
                cve = guessed.get("cve_id", cve)
        if apply_filter and (not cve or not cve.upper().startswith("CVE-")):
            return None

        final = {}
        # 2) NVD enrichment
        if cve.upper().startswith("CVE-"):
            enriched = await enrich_vulnerability_async(cve)
            logger.info("   enrichment for %s: %s", cve, enriched)
            if enriched:
                final = {
                    "cve_id": enriched["cve_id"],
                    "name": enriched.get("vuln_name", cve),
                    "description": enriched.get("description", ""),
                    "severity_score": float(enriched.get("score", 0)),
                    "severity": enriched.get("severity", ""),
                    "vector": enriched.get("vector", ""),
                    "operating_system": enriched.get("operating_system", "Other"),
                    "published": enriched.get("published", ""),
                    "lastModified": enriched.get("lastModified", ""),
                    "required_action": enriched.get("cisaRequiredAction", ""),
                }

        # 3) fallback to raw fields
        if not final:
            final = {
                "cve_id": cve,
                "name": vuln.get("vuln_name", "") or vuln.get("vulnerabilityName", ""),
                "description": vuln.get("description", "") or vuln.get("shortDescription", ""),
                "severity_score": float(vuln.get("score", 0)),
                "severity": vuln.get("severity", "")
                or vuln.get("v31severity", "")
                or vuln.get("v2severity", ""),
                "vector": vuln.get("vector", ""),
                "operating_system": vuln.get("operating_system", "Other"),
                "published": vuln.get("published", ""),
                "lastModified": vuln.get("lastModified", ""),
                "required_action": vuln.get("required_action", "")
                or vuln.get("requiredAction", ""),
            }

        # ─── override OS by keyword ───
        from app.utils.string_utils import detect_operating_system

        combined = f"{final['name']} {final.get('description','')}"
        final["operating_system"] = detect_operating_system(combined)

        # ─── derive auth strictly from CVSS PR flag ───
        vec = (final.get("vector") or "").lower()
        final["auth"] = "with auth" if "/pr:l" in vec or "/pr:h" in vec else "without auth"

        # ─── is-new? ───
        dt_str = final.get("published") or final.get("lastModified")
        try:
            dt = datetime.fromisoformat(dt_str)
        except:
            dt = None
        final["is_new"] = bool(dt and dt >= datetime.utcnow() - timedelta(days=365))

        logger.info("   normalize output: %s", final)
        return final

    except Exception:
        logger.error("Normalization error:\n%s", traceback.format_exc())
        return None

@router.post("/", summary="Trigger a new scan")
async def trigger_scan(
    request: ScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        # ensure we have a valid user in DB
        await ensure_test_user(db)

        # run the external aggregations
        aggregated = await aggregate_scan_data(request.target)

        # ─── NEW: auto-link or create an Asset/Org if none provided ───
        if not request.asset_id:
            # use the scan target as the organization name
            org = crud.create_organization(db, aggregated["target"])
            # create an asset record for this org
            asset = crud.create_asset(db, org["id"], request.target)
            # assign it back onto the request
            request.asset_id = asset["id"]

        # 1) record the scan, now with a guaranteed asset_id
        scan_rec = crud.create_scan(
            db,
            request.target,
            current_user.id,
            "completed",
            aggregated,
            request.asset_id
        )

        # 2) flatten & dedupe *all* sources (same as before)
        sources = ("cisa", "shodan", "dnsdumpster", "onyphe", "nvd")
        items = []
        for src in sources:
            blk = aggregated["data"].get(src, {})
            items += blk.get("vulnerabilities", [])
        seen, unique = set(), []
        for v in items:
            cid = (v.get("cve_id") or "").upper()
            if cid and cid not in seen:
                seen.add(cid)
                unique.append(v)
        if len(unique) > 50:
            unique = random.sample(unique, 50)

        # 3) normalize them all
        normalized = await asyncio.gather(*[
            normalize_vulnerability_async(
                v,
                aggregated["data"].get("onyphe", {}),
                aggregated["data"].get("discovered_brands", []),
                False,
            )
            for v in unique
        ])

        # 4) final domain-vs-IP filtering (same)
        if is_ip_address(request.target):
            final_vulns = [v for v in normalized if v]
        else:
            base = request.target.lower().split(".", 1)[0]
            final_vulns = [
                v for v in normalized if v and (
                    base in v["name"].lower() or base in v.get("description", "").lower()
                )
            ]

        # 5) upsert & add fixes
        created = []
        for nv in final_vulns:
            rec = crud.upsert_vulnerability(db, scan_rec["id"], nv)
            created.append(rec)
            if nv.get("required_action"):
                crud.add_fix(db, rec["id"], {
                    "recommended_fix": nv["required_action"],
                    "status": "open"
                })

        # return the usual payload
        return {
            "message": "Scan completed and data saved.",
            "scan_id": scan_rec["id"],
            "aggregated_data": aggregated,
            "vulnerabilities_added": created,
        }

    except Exception:
        logger.error("Scan error:\n%s", traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
