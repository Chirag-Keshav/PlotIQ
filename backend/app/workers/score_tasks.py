import uuid
import asyncio
from typing import Optional
from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.listing_service import ListingService

@celery_app.task(name="compute_confidence_score")
def compute_confidence_score_task(listing_id_str: str):
    """Celery task to compute the confidence score asynchronously."""
    async def _run():
        async with AsyncSessionLocal() as db:
            service = ListingService(db)
            await service.recompute_score(uuid.UUID(listing_id_str))
            
    asyncio.run(_run())
