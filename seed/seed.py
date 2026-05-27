"""Seed script for PlotIQ database."""
import asyncio
import os
import sys
import random
import uuid
from datetime import datetime, timedelta

# Ensure we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from alembic import command
from alembic.config import Config

from app.core.database import engine, AsyncSessionLocal
from app.models.listing import Listing, GrowthSignal, Comparable
from ai.embeddings.embedding_service import embedding_service
from seed.seed_data import LOCALITIES, GROWTH_SIGNALS


async def run_migrations():
    print("Running migrations...")
    alembic_cfg = Config("backend/alembic.ini")
    
    # We must run Alembic synchronously
    def upgrade(rev, context):
        return command.upgrade(alembic_cfg, rev)
        
    await asyncio.to_thread(upgrade, "head", None)
    print("Migrations complete.")


async def generate_listings(session: AsyncSession, num_per_locality: int = 8):
    print(f"Generating {len(LOCALITIES) * num_per_locality} listings...")
    
    for loc in LOCALITIES:
        for i in range(num_per_locality):
            # Jitter location slightly
            lat = loc["lat"] + random.uniform(-0.02, 0.02)
            lng = loc["lng"] + random.uniform(-0.02, 0.02)
            
            # Generate properties
            area_sqyd = random.choice([100, 150, 200, 300, 500, 1000, 2000, 4840])
            # Price varies +/- 30% from base
            price_per_sqyd = loc["base_price"] * random.uniform(0.7, 1.3)
            price_lakhs = (area_sqyd * price_per_sqyd) / 100000.0
            
            use_types = ["residential", "commercial", "agricultural"]
            if loc["name"] == "Kokapet":
                use_types = ["residential", "commercial"]
            elif loc["name"] in ["Shadnagar", "Sangareddy"]:
                use_types = ["residential", "agricultural"]
                
            use_type = random.choice(use_types)
            road_access = random.choice(["40ft", "60ft", "100ft", "highway"])
            
            title = f"{area_sqyd} sqyd {use_type.title()} Plot in {loc['name']}"
            description = f"Excellent {use_type} property located near main road. Features {road_access} road access. Good investment opportunity."
            
            # Generate embedding
            listing_dict = {
                "title": title,
                "description": description,
                "locality": loc["name"],
                "use_type": use_type,
                "road_access": road_access,
                "area_sqyd": str(area_sqyd),
                "price_lakhs": str(price_lakhs)
            }
            embedding = embedding_service.embed_listing(listing_dict)
            
            listing = Listing(
                title=title,
                description=description,
                lat=lat,
                lng=lng,
                locality=loc["name"],
                price_lakhs=round(price_lakhs, 2),
                area_sqyd=area_sqyd,
                use_type=use_type,
                road_access=road_access,
                ownership_type="individual",
                listing_status="live" if random.random() > 0.3 else "pending_review",
                confidence_score=random.randint(40, 95),
                embedding=embedding
            )
            session.add(listing)
            
            # Add comparables
            comp = Comparable(
                lat=lat,
                lng=lng,
                locality=loc["name"],
                area_sqyd=area_sqyd,
                price_lakhs=round(price_lakhs * random.uniform(0.9, 1.1), 2),
                transaction_date=datetime.now().date() - timedelta(days=random.randint(1, 365)),
                source="seed"
            )
            session.add(comp)
            
    await session.commit()
    print("Listings and comparables generated.")


async def generate_growth_signals(session: AsyncSession):
    print("Generating growth signals...")
    
    for signal in GROWTH_SIGNALS:
        loc = next((l for l in LOCALITIES if l["name"] == signal["locality"]), None)
        if not loc:
            continue
            
        gs = GrowthSignal(
            title=signal["title"],
            signal_type=signal["signal_type"],
            status=signal["status"],
            confidence=signal["confidence"],
            center_lat=loc["lat"] + random.uniform(-0.01, 0.01),
            center_lng=loc["lng"] + random.uniform(-0.01, 0.01),
            radius_km=random.uniform(2.0, 8.0)
        )
        session.add(gs)
        
    await session.commit()
    print("Growth signals generated.")


async def main():
    print("Starting database seed process...")
    # 1. Run migrations
    try:
        await run_migrations()
    except Exception as e:
        print(f"Migration error: {e}")
        # Proceed anyway if already migrated
        pass
        
    async with AsyncSessionLocal() as session:
        # Clear existing
        print("Clearing existing data...")
        await session.execute(Listing.__table__.delete())
        await session.execute(Comparable.__table__.delete())
        await session.execute(GrowthSignal.__table__.delete())
        await session.commit()
        
        # Insert seed data
        await generate_listings(session)
        await generate_growth_signals(session)
        
    print("Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
