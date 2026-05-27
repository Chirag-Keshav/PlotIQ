"""Pydantic v2 schemas for Document endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class DocumentAnalysis(BaseModel):
    """Structured output from the LLM document analysis chain."""
    doc_type: Literal["ec", "sale_deed", "layout_approval", "mutation_register", "patta"]
    named_parties: list[str] = []
    survey_numbers: list[str] = []
    dates: list[str] = []
    transaction_amounts: list[str] = []
    risk_clauses: list[str] = []
    missing_approvals: list[str] = []
    suspicious_patterns: list[str] = []
    summary: str = ""
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class DocumentUploadResponse(BaseModel):
    doc_id: uuid.UUID
    status: str = "pending"
    message: str = "Document uploaded. Analysis queued."


class DocumentRecord(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    doc_type: str
    analysis_status: str
    ai_analysis: Optional[DocumentAnalysis] = None
    failure_reason: Optional[str] = None
    uploaded_at: datetime
