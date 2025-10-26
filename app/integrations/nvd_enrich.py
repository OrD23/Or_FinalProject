# app/integrations/nvd_enrich.py
import logging
import nvdlib
from config import NVD_API_KEY
import asyncio

logger = logging.getLogger(__name__)

# Global semaphore to limit concurrent NVD API requests (set to 5 concurrent calls)
enrichment_semaphore = asyncio.Semaphore(5)


def extract_os_from_configurations(configurations) -> str:
    """
    Attempt to extract an operating system from the configurations.
    Searches for a CPE URI that starts with "cpe:2.3:o:" and returns its fourth field.
    If none found, returns "Other".
    """
    if not configurations:
        return "Other"
    stack = []
    if isinstance(configurations, dict):
        stack.append(configurations)
    elif isinstance(configurations, list):
        stack.extend(configurations)
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            cpe_list = node.get("cpe_match") or node.get("cpeMatch") or []
            for cpe in cpe_list:
                cpe_uri = getattr(cpe, "cpe23Uri", None) or cpe.get("cpe23Uri", "")
                if cpe_uri.startswith("cpe:2.3:o:"):
                    parts = cpe_uri.split(":")
                    if len(parts) > 3:
                        return parts[3].capitalize()
            for key in ("children", "nodes"):
                if key in node and isinstance(node[key], list):
                    stack.extend(node[key])
    return "Other"


from app.utils.date_utils import is_recent


def enrich_vulnerability(cve_id: str) -> dict:
    try:
        results = nvdlib.searchCVE(cveId=cve_id, key=NVD_API_KEY, delay=0.6)
        if not results:
            return {}
        
        cve_obj = results[0]
        
        try:
            print("NVD enrich response keys:", list(cve_obj.__dict__.keys()))
        except Exception as e:
            print("NVD enrich response keys (fallback):", dir(cve_obj))
        
        cve_id_value = getattr(cve_obj, "id", "N/A")
        published = getattr(cve_obj, "published", None) or getattr(cve_obj, "publishedDate", "N/A")
        last_modified = getattr(cve_obj, "lastModified", None) or getattr(cve_obj, "lastModifiedDate", "N/A")
        
        descriptions = getattr(cve_obj, "descriptions", [])
        description = "N/A"
        if descriptions and isinstance(descriptions, list):
            for desc in descriptions:
                lang = getattr(desc, "lang", None) or desc.get("lang")
                if lang == "en":
                    description = getattr(desc, "value", "N/A") or desc.get("value", "N/A")
                    break
        
        score_arr = getattr(cve_obj, "score", [])
        if score_arr and len(score_arr) >= 3:
            numeric_score = score_arr[1]
            severity_str = score_arr[2]
        else:
            numeric_score = 1.0
            severity_str = "UNKNOWN"
        
        vector = (getattr(cve_obj, "v31vector", None) or
                  getattr(cve_obj, "v30vector", None) or
                  getattr(cve_obj, "v2vector", None) or "")
        
        vuln_name = getattr(cve_obj, "title", None) or getattr(cve_obj, "cisaVulnerabilityName", "N/A")
        
        configurations = getattr(cve_obj, "configurations", None)
        operating_system = extract_os_from_configurations(configurations)
        
        is_new = is_recent(published) if published and published != "N/A" else "not new"
        v2auth = getattr(cve_obj, "v2authentication", None)
        auth_value = v2auth if v2auth is not None else "without auth"
        cisa_required_action = getattr(cve_obj, "cisaRequiredAction", "")
        
        # NEW: Extract the URL if available.
        url_value = getattr(cve_obj, "url", "") or ""
        
        return {
            "cve_id": cve_id_value,
            "score": numeric_score,
            "severity": severity_str,
            "vector": vector,
            "vuln_name": vuln_name,
            "description": description,
            "operating_system": operating_system,
            "osvendor": "",
            "is_new": is_new,
            "auth": auth_value,
            "published": published,
            "lastModified": last_modified,
            "required_action": cisa_required_action,
            "url": url_value  # NEW field
        }
    
    except Exception as exc:
        logger.error(f"Error enriching vulnerability {cve_id}: {exc}")
        return {}


async def enrich_vulnerability_async(cve_id: str) -> dict:
    """
    Asynchronously enrich a CVE using the synchronous enrich_vulnerability function.
    """
    async with enrichment_semaphore:
        await asyncio.sleep(0.6)
        return await asyncio.to_thread(enrich_vulnerability, cve_id)
