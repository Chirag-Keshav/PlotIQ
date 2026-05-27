import uuid
import asyncio
from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.listing import Listing
from ai.embeddings.embedding_service import embedding_service

@celery_app.task(name="generate_embedding")
def generate_embedding_task(listing_id_str: str):
    """Celery task to generate embeddings asynchronously."""
    async def _run():
        async with AsyncSessionLocal() as db:
            stmt = select(Listing).where(Listing.id == uuid.UUID(listing_id_str))
            result = await db.execute(stmt)
            listing = result.scalars().first()
            if not listing:
                return
                
            embedding = embedding_service.embed_listing({
                "title": listing.title,
                "description": listing.description,
                "locality": listing.locality,
                "use_type": listing.use_type,
                "road_access": listing.road_access,
                "area_sqyd": str(listing.area_sqyd),
                "price_lakhs": str(listing.price_lakhs)
            })
            listing.embedding = embedding
            await db.commit()
            
    asyncio.run(_run())
