"""Admin Service — verification queue, actions, metrics, audit logging."""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.models.listing import Listing, FraudSignal, AuditLog, User
from app.schemas.admin import AdminAction, AdminMetrics


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_queue(self) -> dict:
        """Return pending_review listings sorted by fraud signal severity."""
        stmt = (
            select(Listing)
            .where(Listing.listing_status == "pending_review")
            .order_by(Listing.created_at.desc())
        )
        result = await self.db.execute(stmt)
        listings = result.scalars().all()

        # Fetch fraud signals per listing
        queue = []
        for listing in listings:
            fraud_stmt = select(FraudSignal).where(
                FraudSignal.listing_id == listing.id,
                FraudSignal.status == "active",
            )
            fraud_result = await self.db.execute(fraud_stmt)
            fraud_signals = fraud_result.scalars().all()

            severity_order = {"high": 0, "medium": 1, "low": 2}
            sorted_signals = sorted(
                fraud_signals, key=lambda s: severity_order.get(s.severity, 3)
            )

            queue.append({
                "listing_id": str(listing.id),
                "title": listing.title,
                "locality": listing.locality,
                "confidence_score": listing.confidence_score,
                "fraud_signals": [
                    {"type": s.signal_type, "severity": s.severity}
                    for s in sorted_signals
                ],
                "created_at": listing.created_at.isoformat() if listing.created_at else None,
            })

        # Sort by highest fraud severity first
        severity_rank = {"high": 0, "medium": 1, "low": 2}
        queue.sort(
            key=lambda item: min(
                (severity_rank.get(s["severity"], 3) for s in item["fraud_signals"]),
                default=3,
            )
        )

        return {"queue": queue, "total": len(queue)}

    async def perform_action(
        self,
        listing_id: uuid.UUID,
        action: AdminAction,
        admin_clerk_id: str,
    ) -> dict:
        """Execute an admin action and write to the audit log."""
        stmt = select(Listing).where(Listing.id == listing_id)
        result = await self.db.execute(stmt)
        listing = result.scalars().first()

        if not listing:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Listing not found")

        # Map action → new status
        status_map = {
            "approve": "live",
            "request_docs": listing.listing_status,  # status unchanged
            "reject": "removed",
            "mark_scam": "removed",
        }
        new_status = status_map[action.action]
        listing.listing_status = new_status

        if action.action == "approve" and listing.confidence_score:
            listing.verification_tier = (
                "full" if listing.confidence_score >= 70 else "partial"
            )

        # If mark_scam, create a fraud signal record
        if action.action == "mark_scam":
            fraud = FraudSignal(
                listing_id=listing_id,
                signal_type="admin_flagged_scam",
                severity="high",
                detail=action.note or "Flagged as scam by admin",
                status="active",
            )
            self.db.add(fraud)

        # Resolve admin user FK
        admin_user = await self._get_user_by_clerk_id(admin_clerk_id)

        # Audit log entry
        log = AuditLog(
            user_id=admin_user.id if admin_user else None,
            action_type=f"admin_{action.action}",
            target_type="listing",
            target_id=listing_id,
            metadata={"note": action.note, "new_status": new_status},
        )
        self.db.add(log)
        await self.db.commit()

        return {
            "listing_id": str(listing_id),
            "new_status": new_status,
            "action": action.action,
        }

    async def get_metrics(self) -> AdminMetrics:
        """Return aggregated trust dashboard metrics."""
        total = await self.db.scalar(select(func.count()).select_from(Listing)) or 0
        live = (
            await self.db.scalar(
                select(func.count())
                .select_from(Listing)
                .where(Listing.listing_status == "live")
            )
            or 0
        )
        pending = (
            await self.db.scalar(
                select(func.count())
                .select_from(Listing)
                .where(Listing.listing_status == "pending_review")
            )
            or 0
        )

        # Stale = last_confirmed_at > 60 days ago or NULL and created > 60 days ago
        stale_threshold = datetime.now(timezone.utc) - timedelta(days=60)
        stale = (
            await self.db.scalar(
                select(func.count())
                .select_from(Listing)
                .where(Listing.last_confirmed_at < stale_threshold)
            )
            or 0
        )

        # Fraud catch rate = listings with at least one active fraud signal / total reviewed
        fraud_flagged = (
            await self.db.scalar(
                select(func.count(FraudSignal.listing_id.distinct()))
                .where(FraudSignal.status == "active")
            )
            or 0
        )

        verification_rate = round((live / total * 100) if total else 0, 1)
        fraud_catch_rate = round((fraud_flagged / total * 100) if total else 0, 1)

        return AdminMetrics(
            total_listings=total,
            live_listings=live,
            pending_review_listings=pending,
            verification_rate_pct=verification_rate,
            fraud_catch_rate_pct=fraud_catch_rate,
            stale_listing_count=stale,
        )

    async def _get_user_by_clerk_id(self, clerk_id: str) -> Optional[User]:
        stmt = select(User).where(User.clerk_user_id == clerk_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
