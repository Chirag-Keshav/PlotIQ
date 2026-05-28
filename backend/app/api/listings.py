"""Listings API routes — CRUD, score, price, POIs, growth signals, report."""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.auth import get_current_user, UserClaims
from app.core.database import get_db
from app.schemas.listing import ListingCreate, ListingSummary, ListingDetail, ConfidenceBreakdown
from app.models.listing import Listing, User

router = APIRouter()

SELLER_RATE_LIMIT = 5
RATE_LIMIT_WINDOW_HOURS = 24


async def _check_seller_rate_limit(db: AsyncSession, user_id: str) -> None:
    """Raise HTTP 429 if the seller has created >= 5 listings in the last 24 hours."""
    stmt = select(User).where(User.clerk_user_id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        return

    window_start = datetime.now(timezone.utc) - timedelta(hours=RATE_LIMIT_WINDOW_HOURS)
    count_stmt = (
        select(func.count())
        .select_from(Listing)
        .where(Listing.seller_id == user.id)
        .where(Listing.created_at >= window_start)
    )
    count = await db.scalar(count_stmt)
    if count is not None and count >= SELLER_RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: max {SELLER_RATE_LIMIT} listings per {RATE_LIMIT_WINDOW_HOURS} hours",
            headers={"Retry-After": str(RATE_LIMIT_WINDOW_HOURS * 3600)},
        )


@router.get("/listings", response_model=dict)
async def list_listings(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    locality: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Return paginated listings."""
    from app.services.listing_service import ListingService
    service = ListingService(db)
    items, total = await service.get_listings(page, page_size, locality, status)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/listings/{listing_id}", response_model=ListingDetail)
async def get_listing(
    listing_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return full listing detail."""
    from app.services.listing_service import ListingService
    service = ListingService(db)
    listing = await service.get_listing_detail(listing_id)
    if not listing:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "Listing not found"},
        )
    return listing


@router.post("/listings", status_code=201)
async def create_listing(
    payload: ListingCreate,
    db: AsyncSession = Depends(get_db),
    user: UserClaims = Depends(get_current_user),
):
    """Create a new listing (authenticated sellers only)."""
    # Explicit TOS check — return 400, not 422
    if not payload.tos_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "TOS_NOT_ACCEPTED", "message": "Terms of Service must be accepted"},
        )

    # Rate limiting: 5 listings per seller per 24 hours
    await _check_seller_rate_limit(db, user.user_id)

    from app.services.listing_service import ListingService
    service = ListingService(db)
    listing_id = await service.create_listing(payload, user.user_id)
    return {
        "id": str(listing_id),
        "listing_status": "pending_review",
        "message": "Listing created. AI analysis in progress.",
    }


@router.get("/listings/{listing_id}/score", response_model=ConfidenceBreakdown)
async def get_listing_score(
    listing_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return confidence score breakdown for a listing."""
    from app.services.listing_service import ListingService
    service = ListingService(db)
    score = await service.get_score(listing_id)
    if not score:
        raise HTTPException(status_code=404, detail="Score not available")
    return score


@router.get("/listings/{listing_id}/price-estimate")
async def get_price_estimate(
    listing_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return price estimate with comparables and trend."""
    from app.services.price_service import PriceService
    service = PriceService(db)
    return await service.estimate(listing_id)


@router.get("/listings/{listing_id}/pois")
async def get_pois(
    listing_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return POIs within 5km of listing location."""
    from app.services.listing_service import ListingService
    from app.services.poi_service import POIService
    listing_svc = ListingService(db)
    listing = await listing_svc.get_listing_detail(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    poi_svc = POIService()
    return await poi_svc.get_pois(listing.lat, listing.lng)


@router.get("/listings/{listing_id}/growth-signals")
async def get_growth_signals(
    listing_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return nearby growth signals for a listing."""
    from app.services.growth_service import GrowthService
    service = GrowthService(db)
    return await service.get_signals(listing_id)


@router.post("/listings/{listing_id}/report", status_code=201)
async def report_listing(
    listing_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserClaims = Depends(get_current_user),
):
    """Submit a grievance/takedown report for a listing."""
    report_id = uuid.uuid4()
    return {"report_id": str(report_id), "status": "received"}
