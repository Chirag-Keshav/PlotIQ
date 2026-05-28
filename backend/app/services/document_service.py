"""Document Service — upload, storage, AI analysis, and retrieval."""
import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.listing import Listing, ListingDocument, AuditLog, User
from app.core.config import settings

logger = logging.getLogger(__name__)


async def _upload_to_storage(content: bytes, filename: str, content_type: str) -> str:
    """Upload file to R2/S3. Falls back to a mock URL when credentials absent."""
    if not settings.r2_bucket or not settings.r2_access_key:
        mock_key = f"documents/{uuid.uuid4()}/{filename}"
        logger.warning(f"R2 not configured — using mock storage URL: {mock_key}")
        return f"mock://plotiq-bucket/{mock_key}"
    try:
        import boto3
        from botocore.config import Config
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint,
            aws_access_key_id=settings.r2_access_key,
            aws_secret_access_key=settings.r2_secret_key,
            config=Config(signature_version="s3v4"),
        )
        key = f"documents/{uuid.uuid4()}/{filename}"
        s3.put_object(
            Bucket=settings.r2_bucket,
            Key=key,
            Body=content,
            ContentType=content_type,
        )
        return f"{settings.r2_endpoint}/{settings.r2_bucket}/{key}"
    except Exception as exc:
        logger.error(f"Storage upload failed: {exc}")
        return f"mock://plotiq-bucket/documents/{uuid.uuid4()}/{filename}"


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_document(
        self,
        listing_id: uuid.UUID,
        file_content: bytes,
        filename: str,
        content_type: str,
        doc_type: str,
        user_id: str,
    ) -> uuid.UUID:
        """Store file, create DB record, enqueue async analysis task."""
        # Verify listing exists
        listing_stmt = select(Listing).where(Listing.id == listing_id)
        listing = (await self.db.execute(listing_stmt)).scalars().first()
        if not listing:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Listing not found")

        # Upload to object storage
        storage_url = await _upload_to_storage(file_content, filename, content_type)

        # Create document record
        doc = ListingDocument(
            listing_id=listing_id,
            doc_type=doc_type,
            storage_url=storage_url,
            analysis_status="pending",
        )
        self.db.add(doc)

        # Audit log — document access/upload
        user_stmt = select(User).where(User.clerk_user_id == user_id)
        user = (await self.db.execute(user_stmt)).scalars().first()
        log = AuditLog(
            user_id=user.id if user else None,
            action_type="document_upload",
            target_type="document",
            target_id=doc.id,
            metadata={"listing_id": str(listing_id), "doc_type": doc_type},
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(doc)

        # Enqueue async analysis (non-blocking; fails gracefully if Celery absent)
        try:
            from app.workers.document_tasks import analyze_document_task
            analyze_document_task.delay(str(doc.id), doc_type, storage_url)
        except Exception as exc:
            logger.warning(f"Could not enqueue document analysis: {exc}")

        return doc.id

    async def get_documents(self, listing_id: uuid.UUID, user_id: str) -> list[dict]:
        """Return all documents for a listing; log access to audit_log."""
        stmt = select(ListingDocument).where(
            ListingDocument.listing_id == listing_id
        ).order_by(ListingDocument.uploaded_at.desc())
        result = await self.db.execute(stmt)
        docs = result.scalars().all()

        # Audit log — document access
        user_stmt = select(User).where(User.clerk_user_id == user_id)
        user = (await self.db.execute(user_stmt)).scalars().first()
        log = AuditLog(
            user_id=user.id if user else None,
            action_type="document_access",
            target_type="listing",
            target_id=listing_id,
            metadata={"doc_count": len(docs)},
        )
        self.db.add(log)
        await self.db.commit()

        return [
            {
                "id": str(d.id),
                "doc_type": d.doc_type,
                "analysis_status": d.analysis_status,
                "ai_analysis": d.ai_analysis,
                "failure_reason": d.failure_reason,
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
            }
            for d in docs
        ]
