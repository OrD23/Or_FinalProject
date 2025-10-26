# app/integrations/onyphe.py

import logging
import ipaddress
from pyonyphe.onyphe import Onyphe
from config import ONYPHE_API_KEY

logger = logging.getLogger(__name__)


def fetch_onyphe_data(target: str) -> dict:
    """
    Query Onyphe and return only real CVE vulnerabilities.
    """
    if not ONYPHE_API_KEY or ONYPHE_API_KEY == "your_onyphe_api_key_here":
        logger.warning("Skipping Onyphe: invalid API key")
        return {"vulnerabilities": [], "count": 0, "results": []}

    client = Onyphe(ONYPHE_API_KEY)
    try:
        # determine query: ip:xxx if IP, else raw domain
        try:
            ipaddress.ip_address(target)
            query = f"ip:{target}"
        except ValueError:
            query = target

        response = client.search(query)
        if response.get("error") != 0:
            err = response.get("text", "Unknown error")
            logger.error(f"Onyphe API error: {err}")
            raise RuntimeError(err)

        raw = response.get("results", []) or []
        filtered = []
        for item in raw:
            cve = item.get("cve")
            if cve and cve.startswith("CVE-"):
                os_val = item.get("os", "").strip()
                osvendor_val = item.get("osvendor", "").strip()
                extkey = item.get("extkeyusage", [])
                auth = "with auth" if ("serverAuth" in extkey) else "without auth"
                filtered.append({
                    "cve_id": cve,
                    "vuln_name": item.get("title") or item.get("service") or cve,
                    "description": item.get("description", ""),
                    "operating_system": os_val,
                    "osvendor": osvendor_val,
                    "auth": auth,
                })

        return {
            "vulnerabilities": filtered,
            "count": response.get("count", 0),
            "results": raw
        }

    except Exception as exc:
        logger.error(f"Error in fetch_onyphe_data: {exc}")
        return {"vulnerabilities": [], "count": 0, "results": []}
