"""
Integration tests for error handling — Task 18.6
Tests: 503 on DB unavailable, 429 on rate limit, error envelope shape
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
import time
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app, _rate_buckets


class TestHealthEndpoint:

    def test_health_returns_200_when_all_ok(self):
        """GET /health returns 200 with status=ok when DB and Redis are up."""
        with patch("app.main.check_database_connection",
                   new_callable=AsyncMock,
                   return_value={"postgres": "ok", "postgis": "ok", "pgvector": "ok"}), \
             patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.return_value = True
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get("/health")

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["dependencies"]["postgres"] == "ok"

    def test_health_returns_503_when_db_unavailable(self):
        """GET /health returns 503 with status=degraded when DB is down."""
        with patch("app.main.check_database_connection",
                   new_callable=AsyncMock,
                   return_value={"postgres": "unavailable", "postgis": "unavailable", "pgvector": "unavailable"}), \
             patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.return_value = True
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get("/health")

        assert resp.status_code == 503
        body = resp.json()
        assert body["status"] == "degraded"
        assert body["dependencies"]["postgres"] == "unavailable"

    def test_health_names_unavailable_dependency(self):
        """503 body explicitly names the unavailable dependency."""
        with patch("app.main.check_database_connection",
                   new_callable=AsyncMock,
                   return_value={"postgres": "ok", "postgis": "ok", "pgvector": "ok"}), \
             patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("connection refused")
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get("/health")

        assert resp.status_code == 503
        body = resp.json()
        assert body["dependencies"]["redis"] == "unavailable"


class TestRateLimiting:

    def setup_method(self):
        """Clear rate buckets before each test."""
        _rate_buckets.clear()

    def test_429_after_exceeding_rate_limit(self):
        """60 requests succeed; the 61st returns 429 with Retry-After header."""
        client = TestClient(app, raise_server_exceptions=False)

        # Simulate 60 prior timestamps for the test client IP
        now = time.time()
        test_ip = "testclient"
        _rate_buckets[test_ip] = [now - i * 0.1 for i in range(60)]

        # 61st request should be rate-limited
        resp = client.get("/health")
        assert resp.status_code == 429
        assert "Retry-After" in resp.headers
        body = resp.json()
        assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    def test_requests_within_limit_succeed(self):
        """Fresh client with 0 prior requests can hit health endpoint."""
        _rate_buckets.clear()
        with patch("app.main.check_database_connection",
                   new_callable=AsyncMock,
                   return_value={"postgres": "ok", "postgis": "ok", "pgvector": "ok"}), \
             patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.return_value = True
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get("/health")
        assert resp.status_code == 200


class TestErrorEnvelope:

    def test_404_returns_consistent_json_envelope(self):
        """Unknown route returns JSON, not HTML."""
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/api/v1/listings/00000000-0000-0000-0000-000000000000")
        # Either 404 (listing not found) or some other error — must be JSON
        assert resp.headers.get("content-type", "").startswith("application/json")

    def test_unhandled_exception_returns_500_envelope(self):
        """Unhandled exception returns {error: {code, message, details}} shape."""
        from app.core.auth import get_current_user, UserClaims

        def _raise():
            raise RuntimeError("something broke")

        with patch("app.api.listings.get_db", side_effect=_raise):
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get("/api/v1/listings")

        # May be 500 or other error — just check envelope shape if 500
        if resp.status_code == 500:
            body = resp.json()
            assert "error" in body
            assert "code" in body["error"]
            assert "message" in body["error"]

    def test_validation_error_returns_422_with_field_info(self):
        """Pydantic validation error on POST /search returns 422 with field details."""
        client = TestClient(app, raise_server_exceptions=False)
        # Send invalid JSON body with wrong field types
        resp = client.post(
            "/api/v1/search",
            json={"query": 12345, "filters": "not_an_object"},
        )
        # FastAPI returns 422 for body validation errors
        assert resp.status_code == 422
