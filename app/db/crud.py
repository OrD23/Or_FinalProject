# app/db/crud.py
from typing import Optional, List, Dict
import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import Scan, Vulnerability, Fix, Asset, Organization


def create_organization(db: Session, name: str) -> Dict:
    """Create a new organization or return existing one by name."""
    try:
        org = Organization(name=name)
        db.add(org)
        db.commit()
        db.refresh(org)
        return {"id": org.id, "name": org.name}
    except IntegrityError:
        db.rollback()
        existing = db.query(Organization).filter_by(name=name).first()
        return {"id": existing.id, "name": existing.name}


def get_organizations(db: Session) -> List[Dict]:
    """List all organizations."""
    orgs = db.query(Organization).all()
    return [{"id": o.id, "name": o.name} for o in orgs]


def create_asset(
    db: Session,
    org_id: int,
    value: str,
    asset_type: str = "ip",
    is_internal: bool = False
) -> Dict:
    """Add an asset (IP or domain) to an organization."""
    asset = Asset(
        org_id=org_id,
        value=value,
        asset_type=asset_type,
        is_internal=is_internal
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return {
        "id": asset.id,
        "org_id": asset.org_id,
        "value": asset.value,
        "asset_type": asset.asset_type,
        "is_internal": asset.is_internal,
    }


def get_assets_by_org(db: Session, org_id: int) -> List[Dict]:
    """Return all assets for a given organization."""
    assets = db.query(Asset).filter_by(org_id=org_id).all()
    return [
        {
            "id": a.id,
            "org_id": a.org_id,
            "value": a.value,
            "asset_type": a.asset_type,
            "is_internal": a.is_internal,
        }
        for a in assets
    ]


def get_scans_by_org(db: Session, org_id: int) -> List[Dict]:
    """Return all scans for a given organization."""
    scans = (
        db.query(Scan)
        .join(Asset, Scan.asset_id == Asset.id)
        .filter(Asset.org_id == org_id)
        .order_by(Scan.scan_time.desc())
        .all()
    )
    return [
        {
            "scan_id": s.id,
            "scan_time": s.scan_time.isoformat(),
            "target": s.target,
        }
        for s in scans
    ]


def get_latest_scan_by_org(db: Session, org_id: int) -> Optional[Dict]:
    """Return the most recent scan for an organization, or None."""
    s = (
        db.query(Scan)
        .join(Asset, Scan.asset_id == Asset.id)
        .filter(Asset.org_id == org_id)
        .order_by(Scan.scan_time.desc())
        .first()
    )
    if not s:
        return None
    return {
        "scan_id": s.id,
        "scan_time": s.scan_time.isoformat(),
        "target": s.target,
    }


def create_scan(
    db: Session,
    target: str,
    user_id: int,
    status: str,
    aggregated_data: dict,
    asset_id: Optional[int] = None
) -> Dict:
    scan = Scan(
        user_id=user_id,
        target=target,
        status=status,
        scan_time=datetime.datetime.utcnow(),
        aggregated_data=aggregated_data,
        asset_id=asset_id
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return {
        "id": scan.id,
        "target": scan.target,
        "scan_time": scan.scan_time.isoformat(),
        "asset_id": scan.asset_id
    }


def add_vulnerability(db: Session, scan_id: int, vuln_data: dict) -> Vulnerability:
    v = Vulnerability(
        scan_id=scan_id,
        cve_id=vuln_data.get("cve_id", "N/A"),
        name=vuln_data.get("name") or vuln_data.get("vuln_name", "N/A"),
        description=vuln_data.get("description", ""),
        severity_score=str(vuln_data.get("severity_score", 0.0)),
        severity=vuln_data.get("severity", "UNKNOWN"),
        operating_system=vuln_data.get("operating_system", "Other"),
        auth=vuln_data.get("auth", "without auth"),
        is_new=vuln_data.get("is_new", False),
        required_action=vuln_data.get("required_action", ""),
        hardware_score=vuln_data.get("hardware_score"),
        region_code=vuln_data.get("region_code"),
        tags=vuln_data.get("tags"),
        ip=vuln_data.get("ip"),
        domains=vuln_data.get("domains"),
        hostnames=vuln_data.get("hostnames"),
        cisa_product=vuln_data.get("cisa_product", ""),
        osvendor=vuln_data.get("osvendor", ""),
        version=vuln_data.get("version", ""),
        published=vuln_data.get("published"),
        lastModified=vuln_data.get("lastModified")
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def upsert_vulnerability(db: Session, scan_id: int, vuln_data: dict) -> dict:
    existing = (
        db.query(Vulnerability)
        .filter_by(scan_id=scan_id, cve_id=vuln_data.get("cve_id"))
        .first()
    )
    if existing:
        for field in [
            "name", "description", "severity_score", "severity", "operating_system",
            "auth", "is_new", "required_action", "hardware_score", "region_code",
            "tags", "ip", "domains", "hostnames", "cisa_product",
            "osvendor", "version", "published", "lastModified"
        ]:
            setattr(existing, field, vuln_data.get(field, getattr(existing, field)))
        db.commit()
        db.refresh(existing)
        vuln = existing
    else:
        vuln = add_vulnerability(db, scan_id, vuln_data)
    return {
        "id": vuln.id,
        "cve_id": vuln.cve_id,
        "name": vuln.name,
        "description": vuln.description,
        "severity_score": float(vuln.severity_score),
        "severity": vuln.severity,
        "operating_system": vuln.operating_system,
        "auth": vuln.auth,
        "is_new": vuln.is_new,
        "required_action": vuln.required_action,
        "published": vuln.published,
        "lastModified": vuln.lastModified,
    }


def add_fix(db: Session, vulnerability_id: int, fix_data: dict) -> Fix:
    f = Fix(
        vulnerability_id=vulnerability_id,
        recommended_fix=fix_data.get("recommended_fix"),
        status=fix_data.get("status", "open")
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    return f