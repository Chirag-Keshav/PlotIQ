"""Document Service for handling uploads and AI analysis."""
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.listing import Listing, ListingDocument
from ai.chains.document_analyzer import analyze_document, extract_text_from_pdf, extract_text_from_image

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_document_upload(
        self, listing_id: uuid.UUID, doc_type: str, file_bytes: bytes, filename: str, content_type: str
    ) -> uuid.UUID:
        """Process an uploaded document, extract text, and run AI analysis."""
        # 1. Extract text
        if content_type == "application/pdf":
            text = extract_text_from_pdf(file_bytes)
        elif content_type.startswith("image/"):
            text = extract_text_from_image(file_bytes)
        else:
            text = ""
            
        # 2. Run AI Analysis
        analysis_result = await analyze_document(doc_type, text)
        
        # 3. Save to DB
        doc = ListingDocument(
            listing_id=listing_id,
            doc_type=doc_type,
            file_url=f"mock://bucket/{filename}", # In a real app, upload to R2
            analysis_status="complete",
            analysis_data=analysis_result
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        
        return doc.id
