# app/integrations/nvd.py
import nvdlib
import logging
from config import NVD_API_KEY

logger = logging.getLogger(__name__)


def fetch_nvd_data(target: str) -> dict:
    """
    Fetch vulnerability data using nvdlib.
    Only supports CVE ID searches.
    """
    if not target.upper().startswith("CVE-"):
        return {"nvd": {"error": "Only CVE ID searches are supported by nvdlib."}}
    try:
        results = nvdlib.searchCVE(cveId=target, key=NVD_API_KEY)
        
        # Print keys of the first NVD response result if available.
        if results and len(results) > 0:
            try:
                print("NVD response keys:", list(results[0].__dict__.keys()))
            except Exception as e:
                print("NVD response keys (fallback):", dir(results[0]))
        
        logger.info("Full CVE object: %s", results[0].__dict__)
        
        if not results:
            return {"nvd": {"error": "No data found for CVE."}}
        
        vulnerabilities = []
        for r in results:
            print("nvd result:", r)
            try:
                print("nvd response keys for result:", list(r.__dict__.keys()))
            except Exception as e:
                print("nvd response keys (fallback):", dir(r))
            descriptions = getattr(r, "descriptions", None)
            desc = "N/A"
            if descriptions and isinstance(descriptions, list) and len(descriptions) > 0:
                desc = descriptions[0].value if hasattr(descriptions[0], "value") else str(descriptions[0])
            # Try to get CVSS v3 data first
            cvss_v3 = getattr(r, "cvssV3", None)
            if cvss_v3 and isinstance(cvss_v3, dict):
                base_score = cvss_v3.get("baseScore")
                severity = cvss_v3.get("baseSeverity")
                vector = cvss_v3.get("vectorString")
            else:
                base_score = getattr(r, "v31score", None)
                severity = getattr(r, "v31severity", None)
                vector = getattr(r, "v31vector", None)
            
            vuln = {
                "cve_id": getattr(r, "cveId", getattr(r, "cve_id", "N/A")),
                "description": desc,
                "score": base_score,
                "severity": severity,
                "vector": vector,
                "dateAdded": getattr(r, "publishedDate", ""),
            }
            vulnerabilities.append(vuln)
        return {"nvd": {"vulnerabilities": vulnerabilities}}
    except Exception as e:
        logger.error(f"NVD error: {e}")
        return {"nvd": {"error": str(e)}}
