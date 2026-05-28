"""Celery task — asynchronous confidence score computation."""
import uuid
import asyncio
import logging

from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


@celery_app.task(
    name="compute_confidence_score",
    bind=True,
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=30,
)
def compute_confidence_score_task(self, listing_id_str: str):
    """Compute and store confidence score for a listing asynchronously."""
    async def _run():
        async with AsyncSessionLocal() as db:
            from app.services.listing_service import ListingService
            service = ListingService(db)
            await service.recompute_score(uuid.UUID(listing_id_str))

    try:
        asyncio.run(_run())
    except Exception as exc:
        logger.error(f"Score computation failed for {listing_id_str}: {exc}")
        raise
