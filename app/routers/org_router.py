# app/routers/org_router.py

import re
import socket
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.dependencies import get_db
from app.db import crud
from app.routers.scan_router import trigger_scan, ScanRequest
from app.models import Organization, User

router = APIRouter(prefix="/organizations", tags=["organizations"])


class OrgCreate(BaseModel):
    name: str = Field(..., example="Acme Corp")


class AssetCreate(BaseModel):
    value: str = Field(..., example="8.8.8.8")
    asset_type: str = Field(..., example="ip")
    is_internal: bool = Field(False)


class SuggestRequest(BaseModel):
    name: str = Field(..., example="Acme Corp")


@router.post(
    "/create_org",
    response_model=Dict,
    summary="Create a new organization"
)
def create_organization(
    org: OrgCreate,
    db: Session = Depends(get_db)
) -> Dict:
    return crud.create_organization(db, name=org.name)


@router.post(
    "/suggest",
    response_model=Dict[str, List[str]],
    summary="Suggest domains & IPs for an organization name"
)
def suggest_assets(
    req: SuggestRequest
) -> Dict[str, List[str]]:
    base = re.sub(r"\s+", "", req.name).lower()
    domains = [f"{base}.{tld}" for tld in ("com", "net", "org")]
    ips: List[str] = []
    for d in domains:
        try:
            infos = socket.getaddrinfo(d, None, family=socket.AF_INET)
        except socket.gaierror:
            continue
        for info in infos:
            ip = info[4][0]
            if ip not in ips:
                ips.append(ip)
    return {"domains": domains, "ips": ips}


@router.get(
    "/{org_id}/assets",
    response_model=List[Dict],
    summary="List assets for an organization"
)
def list_org_assets(
    org_id: int,
    db: Session = Depends(get_db)
) -> List[Dict]:
    org = db.query(Organization).filter_by(id=org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return crud.get_assets_by_org(db, org_id)


@router.post(
    "/{org_id}/assets",
    response_model=Dict,
    summary="Add an asset (IP/domain) to an organization"
)
def add_asset(
    org_id: int,
    asset: AssetCreate,
    db: Session = Depends(get_db)
) -> Dict:
    org = db.query(Organization).filter_by(id=org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return crud.create_asset(
        db,
        org_id=org_id,
        value=asset.value,
        asset_type=asset.asset_type,
        is_internal=asset.is_internal
    )


@router.get(
    "/",
    response_model=List[Dict],
    summary="List all organizations"
)
def list_organizations(
    db: Session = Depends(get_db)
) -> List[Dict]:
    return crud.get_organizations(db)


@router.get(
    "/{org_id}/scans",
    response_model=List[Dict],
    summary="List scans for this organization"
)
def list_org_scans(
    org_id: int,
    db: Session = Depends(get_db)
) -> List[Dict]:
    return crud.get_scans_by_org(db, org_id)


@router.post(
    "/{org_id}/scan",
    response_model=Dict,
    summary="Trigger a scan for this organization"
)
async def scan_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
) -> Dict:
    # ensure org exists
    org = db.query(Organization).filter_by(id=org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    # fetch or discover assets
    assets = crud.get_assets_by_org(db, org_id)
    if not assets:
        base = re.sub(r"\s+", "", org.name).lower()
        domains = [f"{base}.{tld}" for tld in ("com", "net", "org")]
        ips: List[str] = []
        # save domains
        for d in domains:
            crud.create_asset(db, org_id, d, "domain", False)
        # save IPs
        for d in domains:
            try:
                infos = socket.getaddrinfo(d, None, family=socket.AF_INET)
            except socket.gaierror:
                continue
            for info in infos:
                ip = info[4][0]
                if ip not in ips:
                    ips.append(ip)
                    crud.create_asset(db, org_id, ip, "ip", False)
        assets = crud.get_assets_by_org(db, org_id)
        if not assets:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "No assets found",
                    "message": "Couldn't discover any assets automatically; please enter one manually.",
                    "suggestions": domains
                }
            )
    # pick scan target: prefer domain
    domain_asset = next((a for a in assets if a["asset_type"] == "domain"), None)
    if domain_asset:
        target = domain_asset["value"]
        asset_id = domain_asset["id"]
    else:
        target = assets[0]["value"]
        asset_id = assets[0]["id"]
    scan_req = ScanRequest(target=target, asset_id=asset_id)
    result = await trigger_scan(scan_req, db, current_user)
    return result
