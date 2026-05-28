"""Growth Service — infrastructure signals with growth tier labeling."""
import uuid
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.listing import Listing, GrowthSignal


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in kilometres."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _assign_growth_tier(signals: list) -> str:
    """Assign growth tier based on count of approved/under-construction signals."""
    active_count = sum(
        1 for s in signals if s.status in ("approved", "under_construction")
    )
    if active_count >= 3:
        return "High Growth Corridor"
    if active_count >= 1:
        return "Emerging Zone"
    return "Speculative"


class GrowthService:
    SEARCH_RADIUS_KM = 10.0

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_signals(self, listing_id: uuid.UUID) -> dict:
        """Fetch growth signals within 10km and assign growth tier."""
        stmt = select(Listing).where(Listing.id == listing_id)
        result = await self.db.execute(stmt)
        listing = result.scalars().first()

        if not listing:
            return {"growth_tier": "Speculative", "signals": []}

        all_signals_stmt = select(GrowthSignal)
        sig_result = await self.db.execute(all_signals_stmt)
        all_signals = sig_result.scalars().all()

        # Filter by great-circle distance using center_lat/center_lng fallback
        nearby = []
        for s in all_signals:
            s_lat = s.center_lat
            s_lng = s.center_lng
            if s_lat is None or s_lng is None:
                continue
            dist = _haversine_km(listing.lat, listing.lng, s_lat, s_lng)
            if dist <= self.SEARCH_RADIUS_KM:
                nearby.append(s)

        # Validate: announced signal without source_url is excluded
        valid = [s for s in nearby if not (s.status == "announced" and not s.source_url)]

        growth_tier = _assign_growth_tier(valid)

        signals_out = [
            {
                "id": str(s.id),
                "signal_type": s.signal_type,
                "title": s.title,
                "source_url": s.source_url,
                "source_type": s.source_type,
                "status": s.status,
                "announced_date": s.announced_date.isoformat() if s.announced_date else None,
                "confidence": float(s.confidence) if s.confidence is not None else None,
            }
            for s in valid
        ]

        return {"growth_tier": growth_tier, "signals": signals_out}
