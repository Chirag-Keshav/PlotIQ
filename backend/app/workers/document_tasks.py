"""Celery task — asynchronous document analysis pipeline."""
import uuid
import asyncio
import logging

from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


@celery_app.task(
    name="analyze_document",
    bind=True,
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=30,
)
def analyze_document_task(self, doc_id: str, doc_type: str, storage_url: str):
    """Download document, run OCR + LLM extraction, store result."""
    async def _run():
        from sqlalchemy import select
        from app.models.listing import ListingDocument

        async with AsyncSessionLocal() as db:
            stmt = select(ListingDocument).where(ListingDocument.id == uuid.UUID(doc_id))
            result = await db.execute(stmt)
            doc = result.scalars().first()
            if not doc:
                logger.warning(f"Document {doc_id} not found — skipping analysis")
                return

            doc.analysis_status = "processing"
            await db.commit()

            try:
                # Download file from storage
                import httpx
                file_content = b""
                if not storage_url.startswith("mock://"):
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        resp = await client.get(storage_url)
                        resp.raise_for_status()
                        file_content = resp.content

                # Extract text
                from ai.chains.document_analyzer import (
                    extract_text_from_pdf,
                    extract_text_from_image,
                    analyze_document,
                )
                if storage_url.endswith(".pdf") or "pdf" in storage_url.lower():
                    text = extract_text_from_pdf(file_content) if file_content else ""
                elif any(storage_url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png")):
                    text = extract_text_from_image(file_content) if file_content else ""
                else:
                    text = ""

                # Run LLM analysis
                analysis_result = await analyze_document(doc_type, text or "No text extracted")

                # Store result
                doc.ocr_text = text
                doc.ai_analysis = analysis_result.model_dump() if hasattr(analysis_result, "model_dump") else analysis_result
                doc.analysis_status = "complete"
                doc.failure_reason = None

            except Exception as exc:
                logger.error(f"Document analysis failed for {doc_id}: {exc}")
                doc.analysis_status = "failed"
                doc.failure_reason = str(exc)[:500]
                raise  # triggers Celery retry

            await db.commit()

            # Recompute confidence score after document update
            try:
                from app.workers.score_tasks import compute_confidence_score_task
                compute_confidence_score_task.delay(str(doc.listing_id))
            except Exception as exc:
                logger.warning(f"Could not enqueue score recompute: {exc}")

    asyncio.run(_run())
