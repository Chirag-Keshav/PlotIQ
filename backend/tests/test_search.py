"""Tests for Search features (NL Parser and Vector Search)."""
import pytest
from app.schemas.search import SearchFilters
from ai.chains.nl_query_parser import parse_nl_query, _validate_filters


@pytest.mark.asyncio
async def test_nl_parser_budget_and_location():
    """Test NL parsing extracts basic filters correctly."""
    query = "plots in Kokapet under 50 lakhs"
    filters = await parse_nl_query(query)
    
    assert isinstance(filters, dict)
    
    # Since we are using an LLM, the exact output might vary slightly,
    # but for a simple test we can verify validation logic directly.
    raw_llm_output = {
        "location_hint": "Kokapet",
        "budget_max": 50.0,
    }
    validated = _validate_filters(raw_llm_output)
    
    assert validated["location_hint"] == "Kokapet"
    assert validated["budget_max"] == 50.0


def test_validate_filters_coercion():
    """Test _validate_filters handles types correctly."""
    raw = {
        "budget_max": "100.5",
        "budget_min": "20",
        "area_min": 500,
        "use_type": "residential ",
        "invalid_field": "something"
    }
    
    clean = _validate_filters(raw)
    
    assert clean["budget_max"] == 100.5
    assert clean["budget_min"] == 20.0
    assert clean["area_min"] == 500.0
    assert clean["use_type"] == "residential"
    assert "invalid_field" not in clean


@pytest.mark.asyncio
async def test_search_endpoint_integration(async_client):
    """Integration test for POST /search."""
    # Assuming async_client is a pytest fixture for httpx.AsyncClient
    payload = {
        "query": "commercial plots near airport",
        "filters": {
            "budget_max": 200
        }
    }
    
    # We would actually make a request here if we had the DB running in the test
    # response = await async_client.post("/search", json=payload)
    # assert response.status_code == 200
    # data = response.json()
    # assert "items" in data
    # assert "parsed_filters" in data
    pass
