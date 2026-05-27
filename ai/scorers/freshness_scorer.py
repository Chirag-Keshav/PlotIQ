"""Freshness scorer — linear decay from 100 at 0 days to 0 at 90 days."""


def freshness_scorer(listing_age_days: int) -> int:
    """
    Return 0-100 score for listing freshness.
    
    - 0 days: 100
    - 30 days: ~67
    - 60 days: ~33
    - 90+ days: 0 (stale)
    
    Linear decay: score = max(0, 100 - (age_days / 90) * 100)
    """
    if listing_age_days < 0:
        listing_age_days = 0
    score = max(0, 100 - int((listing_age_days / 90) * 100))
    return min(100, score)
