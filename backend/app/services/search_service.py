"""Search service — hybrid NL and vector search."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text, func

from app.models.listing import Listing
from app.schemas.search import SearchFilters, SearchResponse
from app.schemas.listing import ListingSummary
from ai.chains.nl_query_parser import parse_nl_query
from ai.embeddings.embedding_service import embedding_service


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self, query: str, base_filters: SearchFilters
    ) -> tuple[list[ListingSummary], SearchFilters]:
        """
        Execute search combining NL parsing, exact filters, and vector search.
        """
        # Parse NL query if present
        nl_filters_dict = await parse_nl_query(query) if query else {}
        
        # Merge parsed filters with explicit filters
        # Explicit filters take precedence
        merged_dict = nl_filters_dict.copy()
        for k, v in base_filters.model_dump(exclude_none=True).items():
            if v and (isinstance(v, list) and not v):
                continue
            merged_dict[k] = v
            
        parsed_filters = SearchFilters(**merged_dict)
        
        # Build base SQL query
        stmt = select(Listing).where(Listing.listing_status == "live")
        
        # Apply strict filters
        if parsed_filters.budget_min is not None:
            stmt = stmt.where(Listing.price_lakhs >= parsed_filters.budget_min)
        if parsed_filters.budget_max is not None:
            stmt = stmt.where(Listing.price_lakhs <= parsed_filters.budget_max)
        if parsed_filters.area_min is not None:
            stmt = stmt.where(Listing.area_sqyd >= parsed_filters.area_min)
        if parsed_filters.area_max is not None:
            stmt = stmt.where(Listing.area_sqyd <= parsed_filters.area_max)
        if parsed_filters.use_type:
            stmt = stmt.where(Listing.use_type == parsed_filters.use_type)
        if parsed_filters.road_access:
            stmt = stmt.where(Listing.road_access == parsed_filters.road_access)
        if parsed_filters.confidence_min is not None:
            stmt = stmt.where(Listing.confidence_score >= parsed_filters.confidence_min)
        if parsed_filters.localities:
            # handle case-insensitive locality match
            localities_lower = [loc.lower() for loc in parsed_filters.localities]
            stmt = stmt.where(func.lower(Listing.locality).in_(localities_lower))
            
        # Bounds filter (PostGIS)
        if parsed_filters.bounds:
            b = parsed_filters.bounds
            # ST_MakeEnvelope(xmin, ymin, xmax, ymax, 4326)
            # x = lng, y = lat
            envelope = text(f"ST_MakeEnvelope({b.west}, {b.south}, {b.east}, {b.north}, 4326)")
            stmt = stmt.where(Listing.location.ST_Intersects(envelope))
            
        # Vector Similarity Search
        if query:
            query_embedding = embedding_service.embed(query)
            # Add cosine distance ordering
            # <-> operator in pgvector computes cosine distance
            stmt = stmt.order_by(Listing.embedding.cosine_distance(query_embedding))
        else:
            # Default ordering (newest first, high confidence)
            stmt = stmt.order_by(Listing.confidence_score.desc().nullslast(), Listing.created_at.desc())
            
        # Limit to 50 results for POC
        stmt = stmt.limit(50)
        
        result = await self.db.execute(stmt)
        listings = result.scalars().all()
        
        # Map to Pydantic schemas
        items = [ListingSummary.model_validate(l) for l in listings]
        
        return items, parsed_filters
