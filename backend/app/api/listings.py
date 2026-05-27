"""Listings API routes — CRUD, score, price, POIs, growth signals, report."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, get_optional_user, UserClaims
from app.core.database import get_db
from app.schemas.listing import ListingCreate, ListingSummary, ListingDetail, ConfidenceBreakdown

router = APIRouter()


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
    import uuid as uuid_lib
    report_id = uuid_lib.uuid4()
    # In production: insert grievance record, notify ops team
    return {"report_id": str(report_id), "status": "received"}
