"""Search API routes."""
import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.search import SearchRequest, SearchResponse, SearchFilters

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_listings(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Natural language + filter hybrid search over Hyderabad listings."""
    from app.services.search_service import SearchService
    start = time.time()
    service = SearchService(db)
    results, parsed_filters = await service.search(request.query, request.filters)
    return SearchResponse(
        results=results,
        parsed_filters=parsed_filters,
        total=len(results),
        query_time_ms=round((time.time() - start) * 1000, 2),
    )
