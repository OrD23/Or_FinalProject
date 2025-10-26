# app/services/aggregator.py
import asyncio
import pprint
from typing import List, Dict
from datetime import datetime, timedelta

import nvdlib
from app.integrations.shodan import is_ip_address, get_host_info
from app.integrations.dnsdumpster import fetch_dnsdumpster_data
from app.integrations.onyphe import fetch_onyphe_data
from app.integrations.cisa import fetch_cisa_data
from config import NVD_API_KEY
from app.utils.string_utils import (
    detect_operating_system,
    normalize_company_name,
    extract_brand,
)


async def with_timeout(coro, timeout: int = 10) -> Dict:
    try:
        return await asyncio.wait_for(coro, timeout)
    except asyncio.TimeoutError:
        print(f"Timeout after {timeout}s for {coro}")
        return {"error": "timeout"}


async def fetch_shodan_async(target: str) -> Dict:
    if not is_ip_address(target):
        return {"shodan": {"vulnerabilities": []}}
    data = await with_timeout(
        asyncio.get_running_loop().run_in_executor(None, get_host_info, target)
    )
    return {"shodan": data}


async def fetch_dnsdumpster_async(target: str) -> Dict:
    if is_ip_address(target):
        return {"dnsdumpster": {"vulnerabilities": []}}
    raw = await with_timeout(asyncio.to_thread(fetch_dnsdumpster_data, target))
    return {"dnsdumpster": {"vulnerabilities": raw}}


async def fetch_onyphe_async(target: str) -> Dict:
    data = await with_timeout(asyncio.to_thread(fetch_onyphe_data, target))
    return {"onyphe": data}


async def fetch_cisa_async() -> Dict:
    raw = await with_timeout(asyncio.to_thread(fetch_cisa_data), 20)
    for c in raw:
        c["osvendor"] = c.get("vendorProject", "")
    return {"cisa": {"vulnerabilities": raw}}


async def fetch_nvd_async(cve_id: str) -> Dict:
    try:
        results = nvdlib.searchCVE(cveId=cve_id, key=NVD_API_KEY, delay=0.6)
        if not results:
            return {"nvd": {"vulnerabilities": []}}
        c = results[0]
        data = {
            "cve_id": c.id,
            "vector": getattr(c, "v31vector", None) or getattr(c, "v2vector", ""),
            "descriptions": c.descriptions,
            "score": c.score,
            "published": c.published,
            "lastModified": c.lastModified,
            "operating_system": "Other",
        }
        return {"nvd": {"vulnerabilities": [data]}}
    except Exception:
        return {"nvd": {"vulnerabilities": []}}


async def aggregate_scan_data(target: str) -> Dict:
    import socket  # for reverse‐DNS below

    print(f"Aggregating for target: {target!r}")
    ip_scan = is_ip_address(target)

    # 1) fetch all sources concurrently
    tasks = [
        fetch_shodan_async(target),
        fetch_dnsdumpster_async(target),
        fetch_onyphe_async(target),
        fetch_cisa_async(),
    ]
    if target.upper().startswith("CVE-"):
        tasks.insert(3, fetch_nvd_async(target))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    keys = ["shodan", "dnsdumpster", "onyphe"]
    if target.upper().startswith("CVE-"):
        keys.insert(3, "nvd")
    keys.append("cisa")

    data: Dict[str, Dict] = {}
    errors: Dict[str, str] = {}
    for key, res in zip(keys, results):
        if isinstance(res, Exception):
            errors[key] = str(res)
            data[key] = {"vulnerabilities": []}
        else:
            data[key] = res.get(key, res)
    data.setdefault("nvd", {"vulnerabilities": []})

    # 2) discover “brand”:
    #    • domain base (acme.com → acme)
    #    • Shodan org
    #    • Onyphe osvendor/organization
    #    • reverse‐DNS on the IP
    from app.utils.brand_utils import resolve_ip_brand
    
    def discover_primary_brand() -> str:
        # 1) domain-based
        if "." in target and not target.replace(".", "").isdigit():
            return normalize_company_name(target.split(".", 1)[0])
        
        # 2) Shodan org
        org = data.get("shodan", {}).get("org", "") or ""
        b = extract_brand(org)
        if b:
            return normalize_company_name(b)
        
        # 3) Onyphe osvendor/org
        for v in data.get("onyphe", {}).get("vulnerabilities", []):
            val = v.get("osvendor") or v.get("organization", "") or ""
            b2 = extract_brand(val)
            if b2:
                return normalize_company_name(b2)
        
        # 4) New: WHOIS/reverse-DNS
        if ip_scan:
            brand = resolve_ip_brand(target)
            if brand:
                return brand
        
        return ""
    
    brand = discover_primary_brand().lower().strip()
    print(f"Primary discovered brand: {brand!r}")

    # 3) filter to only CVEs mentioning that brand (if we found one)
    def keep_relevant_vulns(vulns: List[dict]) -> List[dict]:
        out = []
        for v in vulns:
            cid = (v.get("cve_id") or "").upper()
            if not cid.startswith("CVE-"):
                continue
            text = " ".join([
                v.get("osvendor", ""),
                v.get("vuln_name", "") or v.get("name", ""),
                v.get("description", ""),
                v.get("productvendor", ""),
                v.get("cisa_product", ""),
            ]).lower()
            if brand and brand not in text:
                continue
            out.append(v)
        return out

    if brand:
        for src in ("shodan", "onyphe", "cisa", "nvd"):
            data[src]["vulnerabilities"] = keep_relevant_vulns(
                data[src].get("vulnerabilities", [])
            )

    data["dnsdumpster"]["vulnerabilities"] = []

    # 4) normalize OS & auth on remaining
    for src in ("shodan", "onyphe", "cisa", "nvd"):
        for v in data[src].get("vulnerabilities", []):
            combined = " ".join([
                v.get("vuln_name", "") or v.get("name", ""),
                v.get("description", ""),
                v.get("productvendor", ""),
                v.get("cisa_product", ""),
            ])
            v["operating_system"] = detect_operating_system(combined)
            vec = (v.get("vector") or "").lower()
            v["auth"] = "with auth" if ("pr:l" in vec or "pr:h" in vec) else "without auth"

    return {"target": target, "data": data, "errors": errors}
