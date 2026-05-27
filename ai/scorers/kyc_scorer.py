"""KYC scorer — 100/50/0 based on KYC status."""


def kyc_scorer(kyc_status: str) -> int:
    """
    Return 0-100 score based on owner KYC status.
    
    - "verified"  → 100 (identity confirmed)
    - "pending"   → 50  (submitted but not yet confirmed)
    - "none"      → 0   (no KYC attempt)
    """
    status_map = {
        "verified": 100,
        "pending": 50,
        "none": 0,
    }
    return status_map.get(kyc_status.lower(), 0)
