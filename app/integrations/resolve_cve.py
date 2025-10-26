# app/integrations/resolve_cve.py
import httpx
import logging

logger = logging.getLogger(__name__)

NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def resolve_cve_id(vuln: dict) -> str:
    # Try to use a direct field first
    cve = vuln.get("cve") or vuln.get("cve_id")
    if cve:
        if isinstance(cve, list) and cve:
            return cve[0]
        return cve
    print("resolve cve vuln: ", vuln)
    # Use vulnerabilityName or shortDescription as query
    query = vuln.get("vulnerabilityName") or vuln.get("shortDescription") or ""
    query = query.strip()
    if not query:
        # Option 1: Return "N/A"
        return "N/A"
        # Option 2: If you prefer to use the target value, you could return it here.
        # return vuln.get("target") or "N/A"
    
    params = {
        "keyword": query,
        "resultsPerPage": 1,
        "startIndex": 0
    }
    
    try:
        response = httpx.get(NVD_BASE_URL, params=params, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            vulnerabilities = data.get("vulnerabilities", [])
            if vulnerabilities:
                cve = vulnerabilities[0].get("cve", {}).get("id", "N/A")
                logger.info(f"Resolved query '{query}' to CVE: {cve}")
                return cve
        return "N/A"
    except Exception as e:
        logger.error(f"Error resolving CVE for query '{query}': {e}")
        return "N/A"

