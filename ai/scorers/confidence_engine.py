"""
Confidence Score Engine — orchestrates all sub-scorers.

Weights:
  document_completeness  25%
  owner_kyc              20%
  geo_consistency        15%
  duplicate_detection    20%
  pricing_anomaly        10%
  listing_freshness      10%
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from ai.scorers.document_completeness import document_completeness_scorer
from ai.scorers.kyc_scorer import kyc_scorer
from ai.scorers.geo_consistency import geo_consistency_scorer
from ai.scorers.duplicate_detector import duplicate_detection_scorer
from ai.scorers.pricing_anomaly import pricing_anomaly_scorer
from ai.scorers.freshness_scorer import freshness_scorer


WEIGHTS = {
    "document_completeness": 0.25,
    "owner_kyc": 0.20,
    "geo_consistency": 0.15,
    "duplicate_detection": 0.20,
    "pricing_anomaly": 0.10,
    "listing_freshness": 0.10,
}


@dataclass
class ListingState:
    """Input state for the confidence score engine."""
    # Documents
    doc_types_present: list[str] = field(default_factory=list)
    # KYC
    kyc_status: str = "none"  # none / pending / verified
    # Geo
    lat: float = 0.0
    lng: float = 0.0
    locality: str = ""
    # Duplicate detection
    image_hashes: list[str] = field(default_factory=list)
    seller_phone: Optional[str] = None
    phone_listing_count: int = 0
    duplicate_image_found: bool = False
    # Pricing
    price_per_sqyd: float = 0.0
    locality_prices_per_sqyd: list[float] = field(default_factory=list)
    # Freshness
    listing_age_days: int = 0
    # Fraud override
    fraud_signals: list[dict] = field(default_factory=list)


@dataclass
class ConfidenceBreakdown:
    document_completeness: int
    owner_kyc: int
    geo_consistency: int
    duplicate_detection: int
    pricing_anomaly: int
    listing_freshness: int
    aggregate: int


def compute_confidence_score(state: ListingState) -> tuple[int, ConfidenceBreakdown]:
    """
    Compute weighted aggregate confidence score [0, 100] and breakdown.
    
    Returns (aggregate_score, ConfidenceBreakdown).
    The aggregate score is guaranteed to be in [0, 100].
    """
    scores = {
        "document_completeness": document_completeness_scorer(state.doc_types_present),
        "owner_kyc": kyc_scorer(state.kyc_status),
        "geo_consistency": geo_consistency_scorer(state.lat, state.lng, state.locality),
        "duplicate_detection": duplicate_detection_scorer(
            state.duplicate_image_found, state.phone_listing_count
        ),
        "pricing_anomaly": pricing_anomaly_scorer(
            state.price_per_sqyd, state.locality_prices_per_sqyd
        ),
        "listing_freshness": freshness_scorer(state.listing_age_days),
    }

    weighted = sum(scores[dim] * weight for dim, weight in WEIGHTS.items())
    aggregate = max(0, min(100, round(weighted)))

    breakdown = ConfidenceBreakdown(
        document_completeness=scores["document_completeness"],
        owner_kyc=scores["owner_kyc"],
        geo_consistency=scores["geo_consistency"],
        duplicate_detection=scores["duplicate_detection"],
        pricing_anomaly=scores["pricing_anomaly"],
        listing_freshness=scores["listing_freshness"],
        aggregate=aggregate,
    )

    return aggregate, breakdown


def assign_listing_status(score: int, has_fraud_signal: bool) -> str:
    """
    Property 11: Assign listing status from score threshold and fraud signal override.
    
    - fraud signal present → pending_review (always)
    - score >= 70 → live
    - 40 <= score < 70 → live (partial badge)  
    - score < 40 → pending_review
    """
    if has_fraud_signal:
        return "pending_review"
    if score >= 70:
        return "live"
    if score >= 40:
        return "live"  # partial verification badge applied separately
    return "pending_review"


def assign_verification_tier(score: int, has_fraud_signal: bool) -> str:
    """Return verification tier label based on score."""
    if has_fraud_signal or score < 40:
        return "unverified"
    if score >= 70:
        return "full"
    return "partial"
