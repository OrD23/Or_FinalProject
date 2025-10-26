# app/integrations/nvd_guess.py
import logging
import nvdlib
from config import NVD_API_KEY

logger = logging.getLogger(__name__)


def guess_cve_by_product_vendor(vendor: str, product: str, version: str = "", cpe_type: str = "o") -> dict:
    if not vendor or not product:
        print("no vendor or product!")
        return {}
    
    vendor_norm = vendor.lower().strip()
    product_norm = product.lower().strip().replace(" ", "_")  # Replace spaces with underscores
    
    if version:
        cpe = f"cpe:2.3:{cpe_type}:{vendor_norm}:{product_norm}:{version}:*:*:*:*:*:*:*"
    else:
        cpe = f"cpe:2.3:{cpe_type}:{vendor_norm}:{product_norm}:-:*:*:*:*:*:*:*"
    
    try:
        results = nvdlib.searchCVE(cpeName=cpe, key=NVD_API_KEY, delay=0.6)
        print("nvd_guess results: ", results)
    except Exception as e:
        logger.error(f"Error searching NVD for CPE {cpe}: {e}")
        return {}
    
    if results:
        best = None
        best_score = 0.0
        for cve in results:
            # Debug: print the attributes/keys of each CVE object
            try:
                cve_keys = cve.__dict__
            except AttributeError:
                cve_keys = dir(cve)
            print("DEBUG: CVE object keys:", cve_keys)
            
            score_arr = getattr(cve, "score", [])
            if score_arr and len(score_arr) >= 2:
                if score_arr[1] > best_score:
                    best_score = score_arr[1]
                    best = cve
        
        if best:
            try:
                best_keys = best.__dict__
            except AttributeError:
                best_keys = dir(best)
            print("DEBUG: Best CVE object keys:", best_keys)
            
            # Try both 'id' and 'cve_id'
            cve_id_value = getattr(best, "id", None) or getattr(best, "cve_id", "N/A")
            
            return {
                "cve_id": cve_id_value,
                "score": score_arr[1],
                "severity": score_arr[2] if len(score_arr) >= 3 else "UNKNOWN",
                "vector": getattr(best, "v31vector", "") or getattr(best, "v30vector", "") or getattr(best, "v2vector",
                                                                                                      ""),
            }
    return {}
