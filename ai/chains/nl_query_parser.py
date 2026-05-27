"""
NL Query Parser — uses Groq llama-4-scout to parse natural language queries
into structured SearchFilters.
"""
from __future__ import annotations
import json
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

NL_PARSE_SYSTEM_PROMPT = """You are a land plot search filter extractor for Hyderabad, India.

Given a natural language search query, extract structured filters as a JSON object.
Only include fields that are explicitly mentioned or clearly implied. 
Return valid JSON only, no explanation.

Extractable fields:
- budget_max: number in lakhs (extract from phrases like "under 50 lakhs", "below 40L")
- budget_min: number in lakhs (extract from "above 20 lakhs", "minimum 15L")
- location_hint: string (neighborhood name, corridor, e.g., "ORR", "Kokapet", "Gachibowli")
- use_type: one of "residential", "commercial", "agricultural"
- road_access: one of "40ft", "60ft", "100ft", "highway" (extract from "highway access", "main road")
- area_min: number in square yards (convert acres: 1 acre = 4840 sqyd)
- area_max: number in square yards

Example input: "2 acres near ORR under 50 lakhs residential"
Example output: {"budget_max": 50, "location_hint": "ORR", "area_min": 9680, "use_type": "residential"}

Example input: "commercial plots near Hyderabad airport under 1 crore"
Example output: {"budget_max": 100, "location_hint": "Shamshabad", "use_type": "commercial"}

If you cannot extract any filters, return: {}
"""


async def parse_nl_query(query: str) -> dict:
    """
    Parse a natural language search query into structured filter dict.
    
    Returns dict with zero or more filter keys.
    Falls back to {} on any error (pure semantic search fallback).
    """
    if not query.strip():
        return {}

    try:
        import os
        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            logger.warning("GROQ_API_KEY not set; skipping NL parse")
            return {}

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": NL_PARSE_SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            response_format={"type": "json_object"},
            max_tokens=256,
            temperature=0.1,
        )
        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)
        
        # Validate and clean
        return _validate_filters(parsed)

    except Exception as e:
        logger.warning(f"NL query parse failed (falling back to semantic search): {e}")
        return {}


def _validate_filters(raw: dict) -> dict:
    """Validate and coerce extracted filter fields."""
    clean = {}
    
    for key in ("budget_min", "budget_max", "area_min", "area_max"):
        if key in raw:
            try:
                clean[key] = float(raw[key])
            except (ValueError, TypeError):
                pass

    for key in ("location_hint", "use_type", "road_access"):
        if key in raw and isinstance(raw[key], str) and raw[key].strip():
            clean[key] = raw[key].strip()

    return clean
