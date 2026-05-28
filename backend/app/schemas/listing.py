"""Pydantic v2 schemas for Listing endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class RiskFlag(BaseModel):
    flag_type: str
    severity: Literal["high", "medium", "low"]
    detail: str = ""


class GrowthSignalSummary(BaseModel):
    id: uuid.UUID
    title: str
    signal_type: str
    status: str
    source_type: Optional[str] = None
    announced_date: Optional[str] = None
    confidence: Optional[float] = None


class ListingCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: Optional[str] = None
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    locality: str = Field(min_length=2, max_length=100)
    price_lakhs: Decimal = Field(gt=0)
    area_sqyd: Decimal = Field(gt=0)
    use_type: Literal["residential", "commercial", "agricultural"]
    road_access: Literal["40ft", "60ft", "100ft", "highway", "none"]
    ownership_type: Literal["individual", "joint", "company"]
    tos_accepted: bool  # must be True, else HTTP 400

    @field_validator("tos_accepted")
    @classmethod
    def tos_must_be_accepted(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Terms of Service must be accepted")
        return v


class ListingSummary(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    locality: str
    price_lakhs: Decimal
    area_sqyd: Decimal
    price_per_sqyd: Optional[Decimal] = None
    confidence_score: Optional[int] = None
    risk_flags: list[RiskFlag] = []
    listing_status: str
    lat: float
    lng: float


class DocumentSummary(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    doc_type: str
    analysis_status: str
    ai_analysis: Optional[dict] = None
    failure_reason: Optional[str] = None
    uploaded_at: Optional[datetime] = None


class ListingDetail(ListingSummary):
    description: Optional[str] = None
    use_type: Optional[str] = None
    road_access: Optional[str] = None
    ownership_type: Optional[str] = None
    verification_tier: str = "unverified"
    confidence_breakdown: Optional[dict] = None
    growth_signals: list[GrowthSignalSummary] = []
    documents: list[DocumentSummary] = []
    created_at: Optional[datetime] = None
    last_confirmed_at: Optional[datetime] = None


class ConfidenceBreakdown(BaseModel):
    document_completeness: int = Field(ge=0, le=100)
    owner_kyc: int = Field(ge=0, le=100)
    geo_consistency: int = Field(ge=0, le=100)
    duplicate_detection: int = Field(ge=0, le=100)
    pricing_anomaly: int = Field(ge=0, le=100)
    listing_freshness: int = Field(ge=0, le=100)
    aggregate: int = Field(ge=0, le=100)
