"""
Integration tests for seller listing creation — Tasks 13.7
Tests: TOS → 400, rate-limit → 429, missing auth → 401
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.auth import get_current_user, UserClaims


# ── helpers ────────────────────────────────────────────────────────────────

def _valid_payload(**overrides) -> dict:
    base = {
        "title": "Test Plot Kokapet",
        "lat": 17.39,
        "lng": 78.33,
        "locality": "Kokapet",
        "price_lakhs": 45.0,
        "area_sqyd": 267.0,
        "use_type": "residential",
        "road_access": "40ft",
        "ownership_type": "individual",
        "tos_accepted": True,
    }
    base.update(overrides)
    return base


def _mock_user(user_id: str = "user_test_123") -> UserClaims:
    return UserClaims({"sub": user_id, "email": "test@example.com",
                       "public_metadata": {"role": "seller"}})


# ── tests ──────────────────────────────────────────────────────────────────

class TestListingCreation:

    def test_unauthenticated_returns_401(self):
        """POST /listings without auth token returns 401."""
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/api/v1/listings", json=_valid_payload())
        assert resp.status_code == 401

    def test_tos_not_accepted_returns_400(self):
        """POST /listings with tos_accepted=False returns HTTP 400."""
        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user

        with patch("app.services.listing_service.ListingService.create_listing",
                   new_callable=AsyncMock) as mock_create, \
             patch("app.api.listings._check_seller_rate_limit",
                   new_callable=AsyncMock):
            mock_create.return_value = "uuid-placeholder"
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/api/v1/listings", json=_valid_payload(tos_accepted=False))

        app.dependency_overrides.clear()
        assert resp.status_code == 400
        body = resp.json()
        assert body["detail"]["code"] == "TOS_NOT_ACCEPTED"

    def test_rate_limit_returns_429(self):
        """POST /listings returns 429 when seller exceeds 5/24h limit."""
        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user

        from fastapi import HTTPException, status

        async def _rate_limit_exceeded(db, user_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded: max 5 listings per 24 hours",
                headers={"Retry-After": "86400"},
            )

        with patch("app.api.listings._check_seller_rate_limit", side_effect=_rate_limit_exceeded):
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/api/v1/listings", json=_valid_payload())

        app.dependency_overrides.clear()
        assert resp.status_code == 429
        assert "Retry-After" in resp.headers

    def test_valid_submission_returns_201(self):
        """POST /listings with valid payload and auth returns 201."""
        import uuid as _uuid
        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user

        listing_id = _uuid.uuid4()
        with patch("app.services.listing_service.ListingService.create_listing",
                   new_callable=AsyncMock, return_value=listing_id), \
             patch("app.api.listings._check_seller_rate_limit", new_callable=AsyncMock):
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/api/v1/listings", json=_valid_payload())

        app.dependency_overrides.clear()
        assert resp.status_code == 201
        body = resp.json()
        assert "id" in body
        assert body["listing_status"] == "pending_review"
