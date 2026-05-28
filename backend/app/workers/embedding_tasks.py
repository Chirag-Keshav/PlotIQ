"""Celery task — asynchronous embedding generation."""
import uuid
import asyncio
import logging

from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


@celery_app.task(
    name="generate_embedding",
    bind=True,
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=30,
)
def generate_embedding_task(self, listing_id_str: str):
    """Generate and store pgvector embedding for a listing asynchronously."""
    async def _run():
        from sqlalchemy import select
        from app.models.listing import Listing
        from ai.embeddings.embedding_service import embedding_service

        async with AsyncSessionLocal() as db:
            stmt = select(Listing).where(Listing.id == uuid.UUID(listing_id_str))
            result = await db.execute(stmt)
            listing = result.scalars().first()
            if not listing:
                logger.warning(f"Listing {listing_id_str} not found for embedding")
                return

            embedding = embedding_service.embed_listing({
                "title": listing.title,
                "description": listing.description or "",
                "locality": listing.locality,
                "use_type": listing.use_type or "",
                "road_access": listing.road_access or "",
            })
            listing.embedding = embedding
            await db.commit()

    try:
        asyncio.run(_run())
    except Exception as exc:
        logger.error(f"Embedding generation failed for {listing_id_str}: {exc}")
        raise
