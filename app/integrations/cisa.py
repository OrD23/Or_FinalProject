# app/integrations/cisa.py

import httpx

def fetch_cisa_data() -> list:
    """
    Retrieve the CISA Known Exploited Vulnerabilities feed and map each vulnerability
    to our standardized schema.
    """
    CISA_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    response = httpx.get(CISA_URL)
    response.raise_for_status()

    raw = response.json().get("vulnerabilities", [])
    mapped_list = []
    for vuln in raw:
        # grab vendorProject once
        osvendor = vuln.get("vendorProject", "")

        mapped = {
            "cve_id": vuln.get("cveID", ""),
            "vuln_name": vuln.get("vulnerabilityName", ""),
            "description": vuln.get("shortDescription", ""),
            # label Windows anytime vendorProject mentions Microsoft
            "operating_system": "Windows" if "microsoft" in osvendor.lower() else "Other",
            "osvendor": osvendor,
            "version": vuln.get("version", ""),
            "required_action": vuln.get("requiredAction", ""),
        }
        mapped_list.append(mapped)

    return mapped_list
