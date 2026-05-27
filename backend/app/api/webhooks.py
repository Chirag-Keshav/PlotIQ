"""Clerk webhook handler — user sync."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhooks/clerk", status_code=200)
async def clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Receive Clerk webhook events and sync user records."""
    # Verify SVIX signature
    body = await request.body()
    svix_id = request.headers.get("svix-id")
    svix_ts = request.headers.get("svix-timestamp")
    svix_sig = request.headers.get("svix-signature")

    if settings.clerk_webhook_secret:
        try:
            from svix.webhooks import Webhook, WebhookVerificationError
            wh = Webhook(settings.clerk_webhook_secret)
            wh.verify(body, {
                "svix-id": svix_id or "",
                "svix-timestamp": svix_ts or "",
                "svix-signature": svix_sig or "",
            })
        except Exception as e:
            logger.warning(f"Clerk webhook signature verification failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

    import json
    payload = json.loads(body)
    event_type = payload.get("type")

    if event_type in ("user.created", "user.updated"):
        data = payload.get("data", {})
        clerk_user_id = data.get("id")
        email = (data.get("email_addresses") or [{}])[0].get("email_address", "")
        phone = (data.get("phone_numbers") or [{}])[0].get("phone_number", "")
        name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()

        from app.services.user_service import UserService
        user_svc = UserService(db)
        await user_svc.upsert_user(
            clerk_user_id=clerk_user_id,
            email=email,
            phone=phone,
            display_name=name,
        )
        logger.info(f"Clerk webhook: synced user {clerk_user_id} ({event_type})")

    return {"status": "ok"}
