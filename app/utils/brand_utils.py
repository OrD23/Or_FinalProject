# app/utils/brand_utils.py

import socket
import whois
from .string_utils import extract_brand, normalize_company_name

def resolve_ip_brand(ip: str) -> str:
    """
    Given an IPv4 address, returns a lowercase brand identifier,
    or the empty string if none could be discovered.
    """
    # 1) Try reverse-DNS
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        brand = extract_brand(hostname)
        if brand:
            return normalize_company_name(brand)
    except Exception:
        pass

    # 2) Try WHOIS
    try:
        w = whois.whois(ip)
        # python-whois may return .org or .name
        org = (w.org or w.name or "").strip()
        brand = extract_brand(org)
        if brand:
            return normalize_company_name(brand)
    except Exception:
        pass

    # 3) Nothing found
    return ""
