"""PlotIQ seed script — populates listings, comparables, and growth signals."""
import asyncio
import os
import sys
import random
from datetime import datetime, timedelta, date

# Add repo root to path for app/ai imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.models.listing import Listing, GrowthSignal, Comparable
from ai.embeddings.embedding_service import embedding_service
from seed.seed_data import LOCALITIES
from seed.growth_signals_data import GROWTH_SIGNALS

random.seed(42)

# ────────────────────────────────────────────────────────────────────────────
# Listings
# ────────────────────────────────────────────────────────────────────────────

def _confidence_tier(i: int, total_per_locality: int) -> int:
    """Distribute scores across high (80-100), medium (50-79), low (0-49)."""
    segment = i % 3
    if segment == 0:
        return random.randint(80, 98)
    if segment == 1:
        return random.randint(50, 79)
    return random.randint(10, 49)


async def seed_listings(session: AsyncSession) -> int:
    count = 0
    for loc in LOCALITIES:
        num = 8  # 8 × 8 localities = 64 listings (> 50 minimum)
        for i in range(num):
            lat = loc["lat"] + random.uniform(-0.025, 0.025)
            lng = loc["lng"] + random.uniform(-0.025, 0.025)

            area_sqyd = random.choice([100, 150, 200, 267, 300, 500, 968, 2000])
            price_per_sqyd = loc["base_price"] * random.uniform(0.65, 1.40)
            price_lakhs = round((area_sqyd * price_per_sqyd) / 100_000, 2)

            use_types = loc.get("use_types", ["residential", "commercial", "agricultural"])
            use_type = random.choice(use_types)
            road_access = random.choice(["40ft", "60ft", "100ft", "highway", "none"])
            ownership = random.choice(["individual", "joint", "company"])

            confidence = _confidence_tier(i, num)
            status = "live" if confidence >= 40 else "pending_review"
            vtier = "full" if confidence >= 70 else ("partial" if confidence >= 40 else "unverified")

            title = f"{area_sqyd} sqyd {use_type.title()} Plot in {loc['name']}"
            description = (
                f"{use_type.title()} land in {loc['name']} with {road_access} road access. "
                f"Good connectivity to ORR. Suitable for {use_type} development."
            )

            listing_dict = {
                "title": title,
                "description": description,
                "locality": loc["name"],
                "use_type": use_type,
                "road_access": road_access,
            }
            embedding = embedding_service.embed_listing(listing_dict)

            age_days = random.randint(0, 180)
            created_at = datetime.utcnow() - timedelta(days=age_days)

            listing = Listing(
                title=title,
                description=description,
                lat=lat,
                lng=lng,
                locality=loc["name"],
                price_lakhs=price_lakhs,
                area_sqyd=area_sqyd,
                use_type=use_type,
                road_access=road_access,
                ownership_type=ownership,
                listing_status=status,
                verification_tier=vtier,
                confidence_score=confidence,
                confidence_breakdown={
                    "document_completeness": random.randint(20, 100),
                    "owner_kyc": random.randint(0, 100),
                    "geo_consistency": random.randint(60, 100),
                    "duplicate_detection": random.randint(50, 100),
                    "pricing_anomaly": random.randint(30, 100),
                    "listing_freshness": max(0, 100 - int(age_days / 90 * 100)),
                    "aggregate": confidence,
                },
                risk_flags=_random_risk_flags(confidence),
                last_confirmed_at=datetime.utcnow() - timedelta(days=random.randint(0, 90)),
                embedding=embedding,
            )
            # Set created_at via backdating after flush
            session.add(listing)
            count += 1

            # Add comparable
            comp = Comparable(
                lat=lat + random.uniform(-0.005, 0.005),
                lng=lng + random.uniform(-0.005, 0.005),
                locality=loc["name"],
                area_sqyd=area_sqyd * random.uniform(0.85, 1.15),
                price_lakhs=round(price_lakhs * random.uniform(0.85, 1.15), 2),
                transaction_date=date.today() - timedelta(days=random.randint(30, 365)),
                source="seed",
            )
            session.add(comp)

    await session.commit()
    return count


def _random_risk_flags(confidence: int) -> list:
    flags = []
    if confidence < 40:
        flags.append({"type": "low_confidence", "severity": "high", "detail": "Score below verification threshold"})
    if confidence < 60 and random.random() < 0.3:
        flags.append({"type": "incomplete_docs", "severity": "medium", "detail": "Missing key documents"})
    if random.random() < 0.1:
        flags.append({"type": "stale", "severity": "low", "detail": "Listing not confirmed recently"})
    return flags


# ────────────────────────────────────────────────────────────────────────────
# Growth Signals
# ────────────────────────────────────────────────────────────────────────────

async def seed_growth_signals(session: AsyncSession) -> int:
    count = 0
    for sig in GROWTH_SIGNALS:
        gs = GrowthSignal(
            signal_type=sig["signal_type"],
            title=sig["title"],
            source_url=sig.get("source_url"),
            source_type=sig.get("source_type"),
            status=sig["status"],
            announced_date=date.fromisoformat(sig["announced_date"]) if sig.get("announced_date") else None,
            center_lat=sig["center_lat"],
            center_lng=sig["center_lng"],
            radius_km=sig.get("radius_km", 5.0),
            confidence=sig.get("confidence"),
        )
        session.add(gs)
        count += 1

    await session.commit()
    return count


# ────────────────────────────────────────────────────────────────────────────
# Validation queries
# ────────────────────────────────────────────────────────────────────────────

async def validate(session: AsyncSession):
    """Run spot checks to verify the seed data is queryable."""
    import math

    # 1. Total count
    total = (await session.execute(text("SELECT COUNT(*) FROM listings"))).scalar()
    assert total >= 50, f"Expected ≥50 listings, got {total}"
    print(f"  ✓ {total} listings inserted")

    # 2. Confidence tier distribution
    high = (await session.execute(text("SELECT COUNT(*) FROM listings WHERE confidence_score >= 80"))).scalar()
    mid = (await session.execute(text("SELECT COUNT(*) FROM listings WHERE confidence_score BETWEEN 50 AND 79"))).scalar()
    low = (await session.execute(text("SELECT COUNT(*) FROM listings WHERE confidence_score < 50"))).scalar()
    assert high >= 10 and mid >= 10 and low >= 10, f"Tier distribution: high={high} mid={mid} low={low}"
    print(f"  ✓ Confidence tiers: high={high} medium={mid} low={low}")

    # 3. Embeddings present
    no_emb = (await session.execute(text("SELECT COUNT(*) FROM listings WHERE embedding IS NULL"))).scalar()
    assert no_emb == 0, f"{no_emb} listings missing embeddings"
    print(f"  ✓ All listings have embeddings")

    # 4. Growth signals
    gs_count = (await session.execute(text("SELECT COUNT(*) FROM growth_signals"))).scalar()
    assert gs_count >= 15, f"Expected ≥15 growth signals, got {gs_count}"
    print(f"  ✓ {gs_count} growth signals inserted")

    # 5. Simple bounding-box query (Hyderabad metro extent)
    bb = (await session.execute(text(
        "SELECT COUNT(*) FROM listings WHERE lat BETWEEN 16.9 AND 18.0 AND lng BETWEEN 77.9 AND 79.0"
    ))).scalar()
    print(f"  ✓ {bb} listings within Hyderabad metro bounding box")

    print("  All validation checks passed.")


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────

async def main():
    print("=== PlotIQ Database Seed ===\n")

    async with AsyncSessionLocal() as session:
        print("Clearing existing data...")
        await session.execute(text("DELETE FROM listing_documents"))
        await session.execute(text("DELETE FROM fraud_signals"))
        await session.execute(text("DELETE FROM comparables"))
        await session.execute(text("DELETE FROM listings"))
        await session.execute(text("DELETE FROM growth_signals"))
        await session.commit()
        print("  ✓ Tables cleared\n")

        print("Seeding listings and comparables...")
        n_listings = await seed_listings(session)
        print(f"  ✓ {n_listings} listings + {n_listings} comparables inserted\n")

        print("Seeding growth signals...")
        n_signals = await seed_growth_signals(session)
        print(f"  ✓ {n_signals} growth signals inserted\n")

        print("Running validation queries...")
        await validate(session)

    print("\n=== Seed complete ===")


if __name__ == "__main__":
    asyncio.run(main())
