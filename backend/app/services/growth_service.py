"""Growth Service for infrastructure signals."""
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.models.listing import Listing, GrowthSignal
from app.schemas.listing import GrowthSignalSummary


class GrowthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_signals(self, listing_id: uuid.UUID) -> list[GrowthSignalSummary]:
        """Fetch nearby growth signals using PostGIS radius based on signal's radius_km."""
        stmt = select(Listing).where(Listing.id == listing_id)
        result = await self.db.execute(stmt)
        listing = result.scalars().first()
        
        if not listing:
            return []
            
        # Match signals where distance between listing and signal center is less than signal.radius_km
        # radius_km * 1000 = radius_meters
        # ST_DWithin uses meters for Geography type
        signals_stmt = select(GrowthSignal).where(
            GrowthSignal.location.ST_DWithin(listing.location, GrowthSignal.radius_km * 1000)
        )
        
        sig_result = await self.db.execute(signals_stmt)
        signals = sig_result.scalars().all()
        
        return [
            GrowthSignalSummary(
                id=str(s.id),
                title=s.title,
                signal_type=s.signal_type,
                status=s.status,
                confidence=s.confidence
            ) for s in signals
        ]
