"""SQLAlchemy ORM models for all PlotIQ database tables."""
import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    UUID, BigInteger, Boolean, Column, Date, DateTime, Float,
    ForeignKey, Integer, Numeric, SmallInteger, String, Text,
    func, Computed,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

try:
    from geoalchemy2 import Geography
    from pgvector.sqlalchemy import Vector
    HAS_GEO = True
except ImportError:
    HAS_GEO = False


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    role = Column(String(20), default="buyer")  # buyer / seller / admin
    kyc_status = Column(String(20), default="none")  # none / pending / verified
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    listings = relationship("Listing", back_populates="seller")
    audit_logs = relationship("AuditLog", back_populates="user")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    # PostGIS geography column — created by migration
    locality = Column(String(100), nullable=False)
    price_lakhs = Column(Numeric(10, 2), nullable=False)
    area_sqyd = Column(Numeric(10, 2), nullable=False)
    # price_per_sqyd is a generated column — handled in migration
    use_type = Column(String(50), nullable=True)  # residential/commercial/agricultural
    road_access = Column(String(50), nullable=True)  # 40ft/60ft/100ft/highway/none
    ownership_type = Column(String(50), nullable=True)  # individual/joint/company
    listing_status = Column(String(30), default="pending_review")  # live/pending_review/removed
    verification_tier = Column(String(30), default="unverified")  # full/partial/unverified
    confidence_score = Column(SmallInteger, nullable=True)
    confidence_breakdown = Column(JSONB, nullable=True)
    risk_flags = Column(JSONB, default=list)
    growth_signals = Column(JSONB, default=list)
    last_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # embedding column added by migration (VECTOR 384-dim)

    seller = relationship("User", back_populates="listings")
    documents = relationship("ListingDocument", back_populates="listing", cascade="all, delete-orphan")
    fraud_signals = relationship("FraudSignal", back_populates="listing", cascade="all, delete-orphan")


class ListingDocument(Base):
    __tablename__ = "listing_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    doc_type = Column(String(50), nullable=False)  # ec/sale_deed/layout_approval/mutation_register/patta/photo
    storage_url = Column(Text, nullable=False)
    ocr_text = Column(Text, nullable=True)
    ai_analysis = Column(JSONB, nullable=True)
    analysis_status = Column(String(30), default="pending")  # pending/processing/complete/failed
    failure_reason = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    listing = relationship("Listing", back_populates="documents")


class GrowthSignal(Base):
    __tablename__ = "growth_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    signal_type = Column(String(50), nullable=False)  # hmda_layout/nhai_highway/metro/industrial_park
    title = Column(Text, nullable=False)
    source_url = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=True)  # government/news/official
    status = Column(String(30), nullable=False)  # announced/approved/under_construction/operational
    announced_date = Column(Date, nullable=True)
    # location GEOGRAPHY(POLYGON) added by migration
    confidence = Column(Numeric(3, 2), nullable=True)  # 0.00-1.00
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Lat/lng center for simpler proximity checks
    center_lat = Column(Float, nullable=True)
    center_lng = Column(Float, nullable=True)
    radius_km = Column(Float, default=5.0)  # approximate coverage radius


class FraudSignal(Base):
    __tablename__ = "fraud_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False)
    signal_type = Column(String(50), nullable=False)  # duplicate_image/phone_reuse/price_anomaly/stale
    severity = Column(String(20), nullable=False)  # high/medium/low
    detail = Column(Text, nullable=True)
    status = Column(String(20), default="active")  # active/resolved/dismissed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    listing = relationship("Listing", back_populates="fraud_signals")


class Comparable(Base):
    __tablename__ = "comparables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    locality = Column(String(100), nullable=True)
    area_sqyd = Column(Numeric(10, 2), nullable=True)
    price_lakhs = Column(Numeric(10, 2), nullable=True)
    transaction_date = Column(Date, nullable=True)
    source = Column(String(50), nullable=True)  # seed/igrs/manual


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action_type = Column(String(50), nullable=False)  # document_access/listing_create/admin_approve/etc.
    target_type = Column(String(50), nullable=True)  # listing/document/user
    target_id = Column(UUID(as_uuid=True), nullable=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")
