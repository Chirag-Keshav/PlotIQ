"""Admin API routes — verification queue, actions, and metrics."""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_admin, UserClaims
from app.core.database import get_db
from app.schemas.admin import AdminAction, AdminMetrics

router = APIRouter()


@router.get("/admin/queue")
async def get_verification_queue(
    db: AsyncSession = Depends(get_db),
    admin: UserClaims = Depends(require_admin),
):
    """Return pending_review listings sorted by fraud signal severity."""
    from app.services.admin_service import AdminService
    service = AdminService(db)
    return await service.get_queue()


@router.post("/admin/listings/{listing_id}/action", status_code=200)
async def admin_action(
    listing_id: uuid.UUID,
    action: AdminAction,
    db: AsyncSession = Depends(get_db),
    admin: UserClaims = Depends(require_admin),
):
    """Perform admin action: approve/request_docs/reject/mark_scam."""
    from app.services.admin_service import AdminService
    service = AdminService(db)
    return await service.perform_action(listing_id, action, admin.user_id)


@router.get("/admin/metrics", response_model=AdminMetrics)
async def get_admin_metrics(
    db: AsyncSession = Depends(get_db),
    admin: UserClaims = Depends(require_admin),
):
    """Return trust dashboard metrics."""
    from app.services.admin_service import AdminService
    service = AdminService(db)
    return await service.get_metrics()
