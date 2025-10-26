# app/integrations/shodan.py

import re
import httpx
import logging
import socket
from typing import Optional
from config import SHODAN_API_KEY

API_BASE_URL = "https://api.shodan.io"
logger = logging.getLogger(__name__)


def is_ip_address(target: str) -> bool:
    return bool(re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", target))


def resolve_to_ip(target: str) -> Optional[str]:
    """
    Resolve a domain name to an IPv4 address, or return None on failure.
    """
    try:
        return socket.gethostbyname(target)
    except Exception as e:
        logger.error(f"Error resolving {target}: {e}")
        return None


def get_host_info(target: str) -> dict:
    """
    Query Shodan for host data and return only true CVE vulnerabilities.
    """
    # 1) resolve domain → IP
    if not is_ip_address(target):
        ip = resolve_to_ip(target)
        if not ip:
            return {"error": "Could not resolve target to IP address."}
        target = ip

    # 2) require API key
    if SHODAN_API_KEY == "your_shodan_api_key_here":
        raise ValueError("Please set a valid SHODAN_API_KEY in your .env")

    # 3) fetch from Shodan
    url = f"{API_BASE_URL}/shodan/host/{target}?key={SHODAN_API_KEY}"
    resp = httpx.get(url, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()

    # 4) extract only CVE entries
    raw_vulns = data.get("vulns", {}) or {}
    filtered = []
    for cve, details in raw_vulns.items():
        if isinstance(cve, str) and cve.startswith("CVE-"):
            filtered.append({
                "cve_id": cve,
                "vuln_name": cve,
                "description": details.get("summary", ""),
                "score": details.get("cvss"),
                "vector": details.get("vector"),
                "dateAdded": "",  # Shodan doesn’t provide publish date
                "operating_system": data.get("os") or "Other",
                "osvendor": data.get("org", ""),
                "ip_str": data.get("ip_str", ""),
            })

    # 5) overwrite `vulnerabilities` key
    data["vulnerabilities"] = filtered
    return {"shodan": data}
