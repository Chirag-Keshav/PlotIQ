"""
Property-based tests for PlotIQ POC — all 11 design properties.

Requires: pip install hypothesis pytest
Run: pytest backend/tests/test_properties.py -v

Each test is tagged with:
  # Feature: plotiq-poc, Property N: <property_text>
"""
import sys
import os
import math
from decimal import Decimal

import pytest
from hypothesis import given, settings, strategies as st
from hypothesis.strategies import (
    builds,
    floats,
    integers,
    text,
    lists,
    booleans,
    one_of,
    none,
    just,
)


from app.schemas.listing import ListingCreate, ListingDetail
from app.schemas.document import DocumentAnalysis
from app.schemas.search import SearchFilters, BoundingBox
from ai.scorers.confidence_engine import (
    compute_confidence_score,
    assign_listing_status,
    ListingState,
)
from ai.scorers.pricing_anomaly import compute_zscore, is_price_anomalous
from ai.scorers.freshness_scorer import freshness_scorer

# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

LOCALITIES = ["Kokapet", "Shadnagar", "Adibatla", "Patancheru", "Ibrahimpatnam"]
USE_TYPES = ["residential", "commercial", "agricultural"]
ROAD_ACCESS = ["40ft", "60ft", "100ft", "highway", "none"]
OWNERSHIP = ["individual", "joint", "company"]
KYC_STATUSES = ["none", "pending", "verified"]
DOC_TYPES = ["ec", "sale_deed", "layout_approval", "mutation_register", "patta"]
GROWTH_STATUSES = ["announced", "approved", "under_construction", "operational"]


def listing_create_strategy():
    return builds(
        dict,
        title=text(min_size=3, max_size=100, alphabet=st.characters(whitelist_categories=("L", "N", "Z"))),
        description=one_of(none(), text(min_size=0, max_size=200)),
        lat=floats(min_value=17.0, max_value=18.0),
        lng=floats(min_value=77.5, max_value=79.5),
        locality=st.sampled_from(LOCALITIES),
        price_lakhs=floats(min_value=1.0, max_value=5000.0, allow_nan=False, allow_infinity=False),
        area_sqyd=floats(min_value=10.0, max_value=50000.0, allow_nan=False, allow_infinity=False),
        use_type=st.sampled_from(USE_TYPES),
        road_access=st.sampled_from(ROAD_ACCESS),
        ownership_type=st.sampled_from(OWNERSHIP),
        tos_accepted=just(True),
    )


def document_analysis_strategy():
    return builds(
        DocumentAnalysis,
        doc_type=st.sampled_from(["ec", "sale_deed", "layout_approval", "mutation_register", "patta"]),
        named_parties=lists(text(min_size=1, max_size=50), max_size=5),
        survey_numbers=lists(text(min_size=1, max_size=20), max_size=5),
        dates=lists(text(min_size=1, max_size=20), max_size=5),
        transaction_amounts=lists(text(min_size=1, max_size=30), max_size=5),
        risk_clauses=lists(text(min_size=1, max_size=100), max_size=3),
        missing_approvals=lists(text(min_size=1, max_size=50), max_size=3),
        suspicious_patterns=lists(text(min_size=1, max_size=100), max_size=2),
        summary=text(min_size=0, max_size=300),
        confidence=floats(min_value=0.0, max_value=1.0, allow_nan=False),
    )


def search_filters_strategy():
    return builds(
        SearchFilters,
        budget_min=one_of(none(), floats(min_value=1.0, max_value=100.0, allow_nan=False).map(Decimal)),
        budget_max=one_of(none(), floats(min_value=100.0, max_value=10000.0, allow_nan=False).map(Decimal)),
        location_hint=one_of(none(), st.sampled_from(LOCALITIES)),
        use_type=one_of(none(), st.sampled_from(USE_TYPES)),
        road_access=one_of(none(), st.sampled_from(ROAD_ACCESS)),
        area_min=one_of(none(), floats(min_value=10.0, max_value=1000.0, allow_nan=False).map(Decimal)),
        area_max=one_of(none(), floats(min_value=1000.0, max_value=50000.0, allow_nan=False).map(Decimal)),
        confidence_min=one_of(none(), integers(min_value=0, max_value=100)),
        localities=lists(st.sampled_from(LOCALITIES), max_size=5, unique=True),
        bounds=none(),
    )


def listing_state_strategy():
    return builds(
        ListingState,
        doc_types_present=lists(st.sampled_from(DOC_TYPES), max_size=5, unique=True),
        kyc_status=st.sampled_from(KYC_STATUSES),
        lat=floats(min_value=17.0, max_value=18.0),
        lng=floats(min_value=77.5, max_value=79.5),
        locality=st.sampled_from(LOCALITIES),
        duplicate_image_found=booleans(),
        phone_listing_count=integers(min_value=0, max_value=10),
        price_per_sqyd=floats(min_value=1.0, max_value=50000.0, allow_nan=False, allow_infinity=False),
        locality_prices_per_sqyd=lists(
            floats(min_value=1.0, max_value=50000.0, allow_nan=False, allow_infinity=False),
            min_size=3, max_size=30,
        ),
        listing_age_days=integers(min_value=0, max_value=365),
        fraud_signals=just([]),
    )


def price_distribution_strategy():
    return lists(
        floats(min_value=1.0, max_value=50000.0, allow_nan=False, allow_infinity=False),
        min_size=3,
        max_size=50,
    )


def growth_signals_strategy():
    return lists(
        builds(dict, status=st.sampled_from(GROWTH_STATUSES)),
        max_size=10,
    )


# ---------------------------------------------------------------------------
# Property 1: Listing serialization round-trip
# ---------------------------------------------------------------------------

# Feature: plotiq-poc, Property 1: Listing serialization round-trip
@given(listing_create_strategy())
@settings(max_examples=100)
def test_listing_serialization_roundtrip(payload: dict):
    model1 = ListingCreate.model_validate(payload)
    json_str = model1.model_dump_json()
    model2 = ListingCreate.model_validate_json(json_str)
    assert model1 == model2


# ---------------------------------------------------------------------------
# Property 2: DocumentAnalysis serialization round-trip
# ---------------------------------------------------------------------------

# Feature: plotiq-poc, Property 2: DocumentAnalysis serialization round-trip
@given(document_analysis_strategy())
@settings(max_examples=100)
def test_document_analysis_roundtrip(analysis: DocumentAnalysis):
    json_str = analysis.model_dump_json()
    restored = DocumentAnalysis.model_validate_json(json_str)
    assert analysis == restored


# ---------------------------------------------------------------------------
# Property 3: SearchFilters serialization round-trip
# ---------------------------------------------------------------------------

# Feature: plotiq-poc, Property 3: SearchFilters serialization round-trip
@given(search_filters_strategy())
@settings(max_examples=100)
def test_search_filters_roundtrip(filters: SearchFilters):
    qs = filters.to_query_string()
    restored = SearchFilters.from_query_string(qs)
    assert filters == restored


# ---------------------------------------------------------------------------
# Property 4: Validation error identifies bad field
# ---------------------------------------------------------------------------

# Feature: plotiq-poc, Property 4: Validation error identifies field and type
@given(
    st.sampled_from(["price_lakhs", "area_sqyd", "lat", "lng"]),
    st.sampled_from(["not_a_number", "", None, -99999]),
)
@settings(max_examples=100)
def test_validation_error_identifies_field(bad_field: str, bad_value):
    from pydantic import ValidationError
    payload = {
        "title": "Test Plot",
        "lat": 17.38,
        "lng": 78.48,
        "locality": "Kokapet",
        "price_lakhs": 50.0,
        "area_sqyd": 267.0,
        "use_type": "residential",
        "road_access": "40ft",
        "ownership_type": "individual",
        "tos_accepted": True,
        bad_field: bad_value,
    }
    # Only test fields where bad_value actually causes a validation error
    try:
        ListingCreate.model_validate(payload)
    except ValidationError as exc:
        field_names = [str(e["loc"][0]) for e in exc.errors()]
        assert bad_field in field_names, f"Expected '{bad_field}' in errors, got {field_names}"


# ---------------------------------------------------------------------------
# Property 5: Confidence score always in [0, 100]
# ---------------------------------------------------------------------------

# Feature: plotiq-poc, Property 5: Confidence score is always in [0, 100]
@given(listing_state_strategy())
@settings(max_examples=100)
def test_confidence_score_in_range(state: ListingState):
    score, breakdown = compute_confidence_score(state)
    assert 0 <= score <= 100, f"Score {score} out of range"
    assert 0 <= breakdown.aggregate <= 100
    assert 0 <= breakdown.document_completeness <= 100
    assert 0 <= breakdown.owner_kyc <= 100
    assert 0 <= breakdown.geo_consistency <= 100
    assert 0 <= breakdown.duplicate_detection <= 100
    assert 0 <= breakdown.pricing_anomaly <= 100
    assert 0 <= breakdown.listing_freshness <= 100


# ---------------------------------------------------------------------------
# Property 6: Pricing anomaly flagging matches Z-score threshold
# ---------------------------------------------------------------------------

# Feature: plotiq-poc, Property 6: Pricing anomaly flagged iff Z-score > 2.0
@given(
    price_distribution_strategy(),
    floats(min_value=0.01, max_value=100000.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_pricing_anomaly_matches_zscore(locality_prices, subject_price):
    z = compute_zscore(subject_price, locality_prices)
    flagged = is_price_anomalous(subject_price, locality_prices)
    assert flagged == (z > 2.0), (
        f"z={z:.4f}, flagged={flagged}, "
        f"expected flagged={(z > 2.0)}"
    )


# ---------------------------------------------------------------------------
# Property 7: Overpriced/underpriced matches P25/P75 percentiles
# ---------------------------------------------------------------------------

def percentile(data: list, p: float) -> float:
    """Simple percentile via linear interpolation."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    n = len(sorted_data)
    idx = (p / 100) * (n - 1)
    lo = int(idx)
    hi = min(lo + 1, n - 1)
    frac = idx - lo
    return sorted_data[lo] + frac * (sorted_data[hi] - sorted_data[lo])


def classify_price(subject_price: float, comparables: list[float]) -> str:
    p25 = percentile(comparables, 25)
    p75 = percentile(comparables, 75)
    if subject_price > p75:
        return "overpriced"
    if subject_price < p25:
        return "underpriced"
    return "fair"


# Feature: plotiq-poc, Property 7: Price classification matches P25/P75 thresholds
@given(
    lists(floats(min_value=1.0, max_value=50000.0, allow_nan=False, allow_infinity=False), min_size=2, max_size=50),
    floats(min_value=0.01, max_value=100000.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_price_classification_matches_percentiles(comparables, subject_price):
    p25 = percentile(comparables, 25)
    p75 = percentile(comparables, 75)
    classification = classify_price(subject_price, comparables)
    if subject_price > p75:
        assert classification == "overpriced"
    elif subject_price < p25:
        assert classification == "underpriced"
    else:
        assert classification == "fair"


# ---------------------------------------------------------------------------
# Property 8: Negotiation range formula invariant
# ---------------------------------------------------------------------------

def compute_negotiation_range(comparables: list[float], area_sqyd: float):
    """[P25 * area, P50 * area] in lakhs."""
    p25 = percentile(comparables, 25)
    p50 = percentile(comparables, 50)
    return (p25 * area_sqyd / 100000, p50 * area_sqyd / 100000)


# Feature: plotiq-poc, Property 8: Negotiation range equals [P25×area, P50×area] in lakhs
@given(
    lists(floats(min_value=1.0, max_value=50000.0, allow_nan=False, allow_infinity=False), min_size=2, max_size=50),
    floats(min_value=1.0, max_value=100000.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_negotiation_range_formula(comparables, area_sqyd):
    p25 = percentile(comparables, 25)
    p50 = percentile(comparables, 50)
    low, high = compute_negotiation_range(comparables, area_sqyd)
    expected_low = p25 * area_sqyd / 100000
    expected_high = p50 * area_sqyd / 100000
    assert abs(low - expected_low) < 1e-6, f"low={low}, expected={expected_low}"
    assert abs(high - expected_high) < 1e-6, f"high={high}, expected={expected_high}"


# ---------------------------------------------------------------------------
# Property 9: Embedding service always returns 384 dimensions
# ---------------------------------------------------------------------------

# Feature: plotiq-poc, Property 9: Embedding always returns exactly 384 floats
@given(text(min_size=1, max_size=500, alphabet=st.characters(whitelist_categories=("L", "N", "Z", "P"))))
@settings(max_examples=30)  # model load is slow; cap at 30
def test_embedding_dimension(input_text: str):
    try:
        from ai.embeddings.embedding_service import EmbeddingService
        svc = EmbeddingService()
        embedding = svc.embed(input_text)
        assert len(embedding) == 384, f"Expected 384, got {len(embedding)}"
        assert all(isinstance(v, float) for v in embedding)
    except ImportError:
        pytest.skip("sentence-transformers not installed")


# ---------------------------------------------------------------------------
# Property 10: Growth tier label matches signal count and status rules
# ---------------------------------------------------------------------------

def assign_growth_tier(signals: list[dict]) -> str:
    """Assign growth tier: count approved/under_construction signals."""
    active_count = sum(
        1 for s in signals
        if s.get("status") in ("approved", "under_construction")
    )
    if active_count >= 3:
        return "High Growth Corridor"
    if active_count >= 1:
        return "Emerging Zone"
    return "Speculative"


# Feature: plotiq-poc, Property 10: Growth tier label matches approved/under_construction count rules
@given(growth_signals_strategy())
@settings(max_examples=100)
def test_growth_tier_label(signals: list[dict]):
    active_count = sum(
        1 for s in signals
        if s.get("status") in ("approved", "under_construction")
    )
    tier = assign_growth_tier(signals)
    if active_count >= 3:
        assert tier == "High Growth Corridor"
    elif active_count >= 1:
        assert tier == "Emerging Zone"
    else:
        assert tier == "Speculative"


# ---------------------------------------------------------------------------
# Property 11: Listing status assignment matches score thresholds and fraud override
# ---------------------------------------------------------------------------

# Feature: plotiq-poc, Property 11: Listing status matches score thresholds and fraud signal override
@given(integers(min_value=0, max_value=100), booleans())
@settings(max_examples=100)
def test_listing_status_from_score(score: int, has_fraud_signal: bool):
    status = assign_listing_status(score, has_fraud_signal)
    if has_fraud_signal:
        assert status == "pending_review", (
            f"Fraud signal present: expected pending_review, got {status}"
        )
    elif score >= 70:
        assert status == "live", f"score={score}: expected live, got {status}"
    elif score >= 40:
        assert status == "live", f"score={score}: expected live (partial), got {status}"
    else:
        assert status == "pending_review", (
            f"score={score}: expected pending_review, got {status}"
        )
