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


@celery_app.task(name="app.workers.score_tasks.flag_stale_listings_task")
def flag_stale_listings_task():
    """Daily Celery beat task — flag listings not confirmed for > 60 days."""
    async def _run():
        from datetime import datetime, timedelta, timezone
        from sqlalchemy import select
        from app.models.listing import Listing

        stale_threshold = datetime.now(timezone.utc) - timedelta(days=60)

        async with AsyncSessionLocal() as db:
            stmt = select(Listing).where(
                Listing.last_confirmed_at < stale_threshold,
                Listing.listing_status == "live",
            )
            result = await db.execute(stmt)
            listings = result.scalars().all()

            flagged = 0
            for listing in listings:
                flags = listing.risk_flags or []
                already = any(f.get("type") == "stale" for f in flags)
                if not already:
                    flags = list(flags) + [{"type": "stale", "severity": "low",
                                            "detail": "Listing not confirmed in 60+ days"}]
                    listing.risk_flags = flags
                    flagged += 1

            if flagged:
                await db.commit()
                logger.info(f"Stale listing check: flagged {flagged} listings")

    asyncio.run(_run())
