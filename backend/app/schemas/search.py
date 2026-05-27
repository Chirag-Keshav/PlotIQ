"""Pydantic v2 schemas for Search endpoints."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional
from urllib.parse import urlencode, parse_qs

from pydantic import BaseModel, Field

from app.schemas.listing import ListingSummary


class BoundingBox(BaseModel):
    north: float
    south: float
    east: float
    west: float


class SearchFilters(BaseModel):
    budget_min: Optional[Decimal] = None
    budget_max: Optional[Decimal] = None
    location_hint: Optional[str] = None
    use_type: Optional[str] = None
    road_access: Optional[str] = None
    area_min: Optional[Decimal] = None
    area_max: Optional[Decimal] = None
    confidence_min: Optional[int] = Field(None, ge=0, le=100)
    localities: list[str] = []
    bounds: Optional[BoundingBox] = None

    def to_query_string(self) -> str:
        """Serialize to URL-safe query string for round-trip testing."""
        params = {}
        for field_name, value in self.model_dump(exclude_none=True).items():
            if field_name == "bounds" and value:
                params["bounds_north"] = str(value["north"])
                params["bounds_south"] = str(value["south"])
                params["bounds_east"] = str(value["east"])
                params["bounds_west"] = str(value["west"])
            elif field_name == "localities":
                if value:
                    params["localities"] = ",".join(value)
            elif value is not None:
                params[field_name] = str(value)
        return urlencode(params)

    @classmethod
    def from_query_string(cls, qs: str) -> "SearchFilters":
        """Deserialize from URL-safe query string."""
        parsed = parse_qs(qs, keep_blank_values=False)
        kwargs: dict = {}
        for key, values in parsed.items():
            val = values[0] if values else None
            if val is None:
                continue
            if key.startswith("bounds_"):
                pass  # handled separately
            elif key == "localities":
                kwargs["localities"] = [v.strip() for v in val.split(",") if v.strip()]
            elif key in ("budget_min", "budget_max", "area_min", "area_max"):
                kwargs[key] = Decimal(val)
            elif key == "confidence_min":
                kwargs[key] = int(val)
            else:
                kwargs[key] = val

        # Reconstruct bounds
        if all(f"bounds_{d}" in parsed for d in ("north", "south", "east", "west")):
            kwargs["bounds"] = BoundingBox(
                north=float(parsed["bounds_north"][0]),
                south=float(parsed["bounds_south"][0]),
                east=float(parsed["bounds_east"][0]),
                west=float(parsed["bounds_west"][0]),
            )

        return cls(**kwargs)


class SearchRequest(BaseModel):
    query: str = ""
    filters: SearchFilters = SearchFilters()


class SearchResponse(BaseModel):
    results: list[ListingSummary]
    parsed_filters: SearchFilters
    total: int
    query_time_ms: float
