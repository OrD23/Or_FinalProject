# app/utils/cpe_utils.py

def normalize_cpe(vendor: str, product: str, version: str = "") -> str:
    vendor_norm = vendor.lower().strip()
    product_norm = product.lower().strip().replace(" ", "_")  # Replace spaces with underscores
    if version:
        return f"cpe:2.3:o:{vendor_norm}:{product_norm}:{version}:*:*:*:*:*:*:*"
    else:
        return f"cpe:2.3:o:{vendor_norm}:{product_norm}:-:*:*:*:*:*:*:*"
