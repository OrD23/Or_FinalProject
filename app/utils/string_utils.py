# app/utils/string_utils.py
import re

# Known brands for extract_brand (unchanged)
KNOWN_BRANDS = {
    "google", "microsoft", "amazon", "aws", "meta", "facebook", "mitel", "vmware",
    "apple", "oracle", "ibm", "cisco", "juniper", "huawei", "fortinet", "linux"
}

OS_KEYWORDS = {
    "windows": "Windows",
    "microsoft": "Windows",
    "linux": "Linux",
    "ubuntu": "Linux",
    "debian": "Linux",
    "red hat": "Linux",
    "centos": "Linux",
    "android": "Android",
    "apple": "macOS",
    "mac": "macOS",
    "os x": "macOS",
    "ios": "iOS",
    "unix": "Unix",
}

def extract_brand(org_or_domain: str) -> str:
    """
    Extract a known brand name from an org or domain string.
    """
    s = org_or_domain.lower().strip()
    if not s:
        return ""
    s = s.replace("www.", "")
    s = re.sub(r"^as\d+\s+", "", s)  # drop AS# prefix
    for brand in KNOWN_BRANDS:
        if brand in s:
            return brand
    parts = s.split(".")
    if parts and len(parts[0]) >= 3:
        return parts[0]
    return ""

def normalize_company_name(name: str) -> str:
    """
    Lowercase, strip legal suffixes & punctuation.
    """
    s = name.lower().strip().replace("www.", "")
    s = re.sub(r'\b(llc|inc|corp(oration)?|company|gmbh|limited|co\.ltd)\b',
               "", s, flags=re.IGNORECASE)
    return re.sub(r"[^\w\s]", "", s).strip()



def detect_operating_system(text: str) -> str:
    s = (text or "").lower()
    for key, label in OS_KEYWORDS.items():
        if key in s:
            return label
    return "Other"

