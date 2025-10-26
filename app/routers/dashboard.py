# app/routers/dashboard.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from collections import defaultdict
from datetime import datetime

from app.dependencies import get_db
from app.auth import get_current_active_user
from app.models import Scan, Vulnerability

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}}
)

@router.get("/{scan_id}", response_class=JSONResponse)
def dashboard_api(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    # 1) Fetch the scan record
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # 2) Gather all vulnerabilities for that scan
    vulns = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).all()

    # 3) Compute metrics
    levels = ["critical", "high", "medium", "low", "info"]
    sev_counts = dict.fromkeys(levels, 0)
    os_counts = {}
    auth_counts = {}
    over_time = {lvl: defaultdict(int) for lvl in levels}
    dates_set = set()
    items = []

    for v in vulns:
        sev = (v.severity or "info").lower()
        if sev not in levels:
            sev = "info"
        sev_counts[sev] += 1

        osv = v.operating_system or "Other"
        os_counts[osv] = os_counts.get(osv, 0) + 1

        auth = v.auth or "without auth"
        auth_counts[auth] = auth_counts.get(auth, 0) + 1

        items.append({
            "id": v.id,
            "cve_id": v.cve_id,
            "cve_name": v.name,
            "description": v.description,
            "severity_score": v.severity_score,
            "severity": v.severity,
            "operating_system": v.operating_system,
            "auth": v.auth,
            "is_new": v.is_new,
            "required_action": v.required_action,
            "published": v.published,
            "lastModified": v.lastModified,
        })

        if v.published:
            day = v.published[:10]
            over_time[sev][day] += 1
            dates_set.add(day)

    # Build time-series data
    dates = sorted(dates_set, key=lambda d: datetime.strptime(d, "%Y-%m-%d"))
    vover = {"dates": dates}
    for lvl in levels:
        vover[lvl] = [over_time[lvl].get(d, 0) for d in dates]

    metrics = {
        "vulnerability_counts": sev_counts,
        "operating_system_counts": os_counts,
        "auth_stats": auth_counts,
        "vulnerabilities_over_time": vover
    }

    # Top critical vulnerabilities
    top_vulns = [v for v in items if v["severity"] and v["severity"].lower() == "critical"]

    # 4) Inject brand & ip_address into the scan payload
    #    Fallback to scan.target if no Asset is linked
    ip_address = scan.asset.value if scan.asset else scan.target
    brand = (
        scan.asset.organization.name
        if scan.asset and scan.asset.organization
        else "N/A"
    )

    response = {
        "scan": {
            "id": scan.id,
            "target": scan.target,
            "status": scan.status,
            "aggregated_data": scan.aggregated_data,
            "ip_address": ip_address,
            "brand": brand
        },
        "vulnerabilities": items,
        "metrics": metrics,
        "top_vulnerabilities": top_vulns
    }

    return response
