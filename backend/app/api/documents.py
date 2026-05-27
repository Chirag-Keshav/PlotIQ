"""Documents API routes — upload and retrieve listing documents."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, UserClaims
from app.core.database import get_db
from app.schemas.document import DocumentUploadResponse

router = APIRouter()

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png"}
ALLOWED_DOC_TYPES = {"ec", "sale_deed", "layout_approval", "mutation_register", "patta", "photo"}


@router.post("/listings/{listing_id}/documents", response_model=DocumentUploadResponse, status_code=202)
async def upload_document(
    listing_id: uuid.UUID,
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user: UserClaims = Depends(get_current_user),
):
    """Upload a document to a listing. Triggers async analysis pipeline."""
    if doc_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid doc_type. Allowed: {ALLOWED_DOC_TYPES}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum 20MB allowed.")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Only PDF, JPG, PNG files allowed.")

    from app.services.document_service import DocumentService
    service = DocumentService(db)
    doc_id = await service.upload_document(
        listing_id=listing_id,
        file_content=content,
        filename=file.filename or "document",
        content_type=file.content_type,
        doc_type=doc_type,
        user_id=user.user_id,
    )

    return DocumentUploadResponse(doc_id=doc_id)


@router.get("/listings/{listing_id}/documents")
async def get_documents(
    listing_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserClaims = Depends(get_current_user),
):
    """Return all documents for a listing (access logged to audit_log)."""
    from app.services.document_service import DocumentService
    service = DocumentService(db)
    docs = await service.get_documents(listing_id, user.user_id)
    return {"documents": docs}
