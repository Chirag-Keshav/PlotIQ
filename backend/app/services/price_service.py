"""Price Service for estimation and comparables."""
import uuid
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.models.listing import Listing, Comparable
from ai.price_model.price_predictor import price_predictor


class PriceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def estimate(self, listing_id: uuid.UUID) -> Dict[str, Any]:
        """Generate a price estimate and fetch comparables using PostGIS radius."""
        stmt = select(Listing).where(Listing.id == listing_id)
        result = await self.db.execute(stmt)
        listing = result.scalars().first()
        
        if not listing:
            return {"error": "Listing not found"}
            
        # Get comparables within 5km
        # ST_DWithin uses meters for geography types
        comp_stmt = select(Comparable).where(
            Comparable.location.ST_DWithin(listing.location, 5000)
        ).limit(10)
        
        comp_result = await self.db.execute(comp_stmt)
        comparables = comp_result.scalars().all()
        
        comp_list = [
            {
                "area_sqyd": c.area_sqyd,
                "price_lakhs": c.price_lakhs,
                "distance_km": 2.5 # approximation for POC, or we could calculate ST_Distance
            } for c in comparables
        ]
        
        # Estimate price
        estimate = price_predictor.predict_price_lakhs(listing.area_sqyd, comp_list)
        
        return {
            "estimated_price_lakhs": round(estimate, 2) if estimate else None,
            "confidence_band": "High" if estimate and len(comp_list) >= 3 else "Low",
            "comparables_used": len(comp_list),
            "trend": "+5% YoY",
            "comparables": comp_list
        }
