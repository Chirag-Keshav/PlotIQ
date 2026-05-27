"""Initial schema — all 7 tables with PostGIS, pgvector, indexes.

Revision ID: 001_initial
Revises: 
Create Date: 2026-05-17
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ── users ──────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("clerk_user_id", sa.String(100), unique=True, nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(20), server_default="buyer"),
        sa.Column("kyc_status", sa.String(20), server_default="none"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # ── listings ────────────────────────────────────────────────────────────
    op.create_table(
        "listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("seller_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id"), nullable=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("lat", sa.Float, nullable=False),
        sa.Column("lng", sa.Float, nullable=False),
        sa.Column("locality", sa.String(100), nullable=False),
        sa.Column("price_lakhs", sa.Numeric(10, 2), nullable=False),
        sa.Column("area_sqyd", sa.Numeric(10, 2), nullable=False),
        sa.Column("use_type", sa.String(50), nullable=True),
        sa.Column("road_access", sa.String(50), nullable=True),
        sa.Column("ownership_type", sa.String(50), nullable=True),
        sa.Column("listing_status", sa.String(30), server_default="pending_review"),
        sa.Column("verification_tier", sa.String(30), server_default="unverified"),
        sa.Column("confidence_score", sa.SmallInteger, nullable=True),
        sa.Column("confidence_breakdown", postgresql.JSONB, nullable=True),
        sa.Column("risk_flags", postgresql.JSONB, server_default="[]"),
        sa.Column("growth_signals", postgresql.JSONB, server_default="[]"),
        sa.Column("last_confirmed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    # PostGIS location column
    op.execute(
        "ALTER TABLE listings ADD COLUMN location geography(POINT, 4326) "
        "GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography) STORED"
    )
    # pgvector embedding column (384-dim for all-MiniLM-L6-v2)
    op.execute("ALTER TABLE listings ADD COLUMN embedding vector(384)")

    # price_per_sqyd generated column
    op.execute(
        "ALTER TABLE listings ADD COLUMN price_per_sqyd NUMERIC(10,2) "
        "GENERATED ALWAYS AS (CASE WHEN area_sqyd > 0 THEN price_lakhs * 100000 / area_sqyd ELSE NULL END) STORED"
    )

    # ── listing_documents ────────────────────────────────────────────────────
    op.create_table(
        "listing_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doc_type", sa.String(50), nullable=False),
        sa.Column("storage_url", sa.Text, nullable=False),
        sa.Column("ocr_text", sa.Text, nullable=True),
        sa.Column("ai_analysis", postgresql.JSONB, nullable=True),
        sa.Column("analysis_status", sa.String(30), server_default="pending"),
        sa.Column("failure_reason", sa.Text, nullable=True),
        sa.Column("uploaded_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # ── growth_signals ────────────────────────────────────────────────────────
    op.create_table(
        "growth_signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("signal_type", sa.String(50), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column("source_type", sa.String(50), nullable=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("announced_date", sa.Date, nullable=True),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=True),
        sa.Column("center_lat", sa.Float, nullable=True),
        sa.Column("center_lng", sa.Float, nullable=True),
        sa.Column("radius_km", sa.Float, server_default="5.0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    # PostGIS polygon (optional, fallback to center+radius for POC)
    op.execute(
        "ALTER TABLE growth_signals ADD COLUMN location geography(POLYGON, 4326)"
    )

    # ── fraud_signals ─────────────────────────────────────────────────────────
    op.create_table(
        "fraud_signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("listings.id"), nullable=False),
        sa.Column("signal_type", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("detail", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # ── comparables ────────────────────────────────────────────────────────────
    op.create_table(
        "comparables",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("lat", sa.Float, nullable=True),
        sa.Column("lng", sa.Float, nullable=True),
        sa.Column("locality", sa.String(100), nullable=True),
        sa.Column("area_sqyd", sa.Numeric(10, 2), nullable=True),
        sa.Column("price_lakhs", sa.Numeric(10, 2), nullable=True),
        sa.Column("transaction_date", sa.Date, nullable=True),
        sa.Column("source", sa.String(50), nullable=True),
    )

    # ── audit_log ────────────────────────────────────────────────────────────
    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=True),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # ── Indexes ────────────────────────────────────────────────────────────────
    # B-tree indexes on listings
    op.create_index("ix_listings_locality", "listings", ["locality"])
    op.create_index("ix_listings_confidence_score", "listings", ["confidence_score"])
    op.create_index("ix_listings_price_lakhs", "listings", ["price_lakhs"])
    op.create_index("ix_listings_listing_status", "listings", ["listing_status"])

    # PostGIS spatial index on listings.location
    op.execute("CREATE INDEX ix_listings_location ON listings USING GIST (location)")

    # pgvector IVFFlat index (lists=50 for ~60 listings)
    op.execute(
        "CREATE INDEX ix_listings_embedding ON listings "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50)"
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("fraud_signals")
    op.drop_table("comparables")
    op.drop_table("growth_signals")
    op.drop_table("listing_documents")
    op.drop_table("listings")
    op.drop_table("users")
