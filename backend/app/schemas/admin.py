"""Pydantic v2 schemas for Admin dashboard endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

from app.schemas.listing import ListingSummary, RiskFlag


class AdminQueueItem(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    locality: str
    price_lakhs: float
    confidence_score: Optional[int] = None
    listing_status: str
    fraud_signal_count: int = 0
    max_fraud_severity: Optional[str] = None
    created_at: datetime


class AdminAction(BaseModel):
    action: Literal["approve", "request_docs", "reject", "mark_scam"]
    note: Optional[str] = None


class AdminMetrics(BaseModel):
    total_listings: int
    live_listings: int
    pending_review_listings: int
    verification_rate_pct: float
    fraud_catch_rate_pct: float
    stale_listing_count: int
