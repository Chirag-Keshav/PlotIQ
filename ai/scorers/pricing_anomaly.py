"""Pricing anomaly scorer — Z-score vs locality median price/sqyd.

Property 6: flagged if and only if Z-score > 2.0 relative to locality median.
"""
from __future__ import annotations
import math
import statistics
from typing import Optional


def compute_zscore(subject_price: float, locality_prices: list[float]) -> float:
    """
    Compute Z-score of subject_price vs the locality price distribution.
    
    Z = (subject - median) / stdev
    
    Returns 0.0 if fewer than 3 comparable prices (insufficient data).
    """
    if len(locality_prices) < 3:
        return 0.0

    try:
        median = statistics.median(locality_prices)
        stdev = statistics.stdev(locality_prices)
        if stdev == 0:
            return 0.0
        return (subject_price - median) / stdev
    except Exception:
        return 0.0


def is_price_anomalous(subject_price: float, locality_prices: list[float]) -> bool:
    """
    Return True if the listing price is anomalously high (Z-score > 2.0).
    
    Property 6: flagged iff Z-score > 2.0
    """
    return compute_zscore(subject_price, locality_prices) > 2.0


def pricing_anomaly_scorer(
    subject_price_per_sqyd: float,
    locality_prices_per_sqyd: list[float],
) -> int:
    """
    Return 0-100 score for price reasonableness.
    
    - Anomalous (Z-score > 2): 20
    - Slightly elevated (1.5 < Z <= 2): 60
    - Normal (Z <= 1.5): 100
    - Insufficient data: 80 (benefit of the doubt)
    """
    if len(locality_prices_per_sqyd) < 3:
        return 80  # benefit of the doubt

    z = compute_zscore(subject_price_per_sqyd, locality_prices_per_sqyd)
    if z > 2.0:
        return 20
    if z > 1.5:
        return 60
    return 100
