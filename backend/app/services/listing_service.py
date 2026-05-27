"""Listing service for CRUD and scoring."""
import uuid
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.listing import Listing, User
from app.schemas.listing import ListingCreate, ListingSummary, ListingDetail, ConfidenceBreakdown
from ai.embeddings.embedding_service import embedding_service
from ai.scorers.confidence_engine import compute_confidence_score, ListingState


class ListingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_listings(
        self, page: int, page_size: int, locality: Optional[str] = None, status: Optional[str] = None
    ) -> Tuple[list[ListingSummary], int]:
        stmt = select(Listing)
        if locality:
            stmt = stmt.where(func.lower(Listing.locality) == locality.lower())
        if status:
            stmt = stmt.where(Listing.listing_status == status)
            
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self.db.scalar(count_stmt)
        
        stmt = stmt.order_by(Listing.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(stmt)
        listings = result.scalars().all()
        
        return [ListingSummary.model_validate(l) for l in listings], total

    async def get_listing_detail(self, listing_id: uuid.UUID) -> Optional[ListingDetail]:
        stmt = select(Listing).options(selectinload(Listing.documents)).where(Listing.id == listing_id)
        result = await self.db.execute(stmt)
        listing = result.scalars().first()
        if not listing:
            return None
        return ListingDetail.model_validate(listing)

    async def create_listing(self, payload: ListingCreate, user_id: str) -> uuid.UUID:
        # Find user
        stmt = select(User).where(User.clerk_user_id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        
        # Embed listing
        embedding = embedding_service.embed_listing(payload.model_dump())
        
        listing = Listing(
            **payload.model_dump(exclude={"tos_accepted"}),
            seller_id=user.id if user else None,
            embedding=embedding
        )
        self.db.add(listing)
        await self.db.commit()
        await self.db.refresh(listing)
        
        return listing.id

    async def get_score(self, listing_id: uuid.UUID) -> Optional[ConfidenceBreakdown]:
        stmt = select(Listing).where(Listing.id == listing_id)
        result = await self.db.execute(stmt)
        listing = result.scalars().first()
        if not listing or not listing.confidence_breakdown:
            return None
        return ConfidenceBreakdown(**listing.confidence_breakdown)

    async def recompute_score(self, listing_id: uuid.UUID) -> None:
        """Triggered when new documents are analyzed or periodically."""
        stmt = select(Listing).options(selectinload(Listing.documents), selectinload(Listing.fraud_signals)).where(Listing.id == listing_id)
        result = await self.db.execute(stmt)
        listing = result.scalars().first()
        if not listing:
            return
            
        state = ListingState(
            doc_types_present=[d.doc_type for d in listing.documents if d.analysis_status == "complete"],
            lat=listing.lat,
            lng=listing.lng,
            locality=listing.locality,
            price_per_sqyd=float(listing.price_per_sqyd) if listing.price_per_sqyd else 0.0,
            fraud_signals=[f.__dict__ for f in listing.fraud_signals]
        )
        # Assuming other fields are populated from other queries...
        score, breakdown = compute_confidence_score(state)
        listing.confidence_score = score
        listing.confidence_breakdown = breakdown.__dict__
        await self.db.commit()
