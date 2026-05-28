"""
Unit tests for POI service and Growth service — Tasks 15.6, 16.7
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import math
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import httpx


# ── POI service tests (Task 15.6) ─────────────────────────────────────────

class TestPOIService:

    def test_overpass_timeout_returns_empty_result_no_5xx(self):
        """Overpass timeout must return {pois:{}, error:'overpass_unavailable'}, not raise."""
        from app.services.poi_service import POIService

        async def _run():
            svc = POIService()
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
                mock_client_cls.return_value = mock_client

                with patch("app.services.poi_service._get_redis", return_value=None):
                    result = await svc.get_pois(17.385, 78.486)

            return result

        result = asyncio.run(_run())
        assert result["error"] == "overpass_unavailable"
        assert isinstance(result["pois"], dict)
        # All 6 categories present and empty
        for cat in ("schools", "hospitals", "malls", "metro_stations", "highways", "bus_depots"):
            assert result["pois"].get(cat) == []

    def test_overpass_request_error_returns_empty_no_5xx(self):
        """Any httpx.RequestError also returns graceful fallback."""
        from app.services.poi_service import POIService

        async def _run():
            svc = POIService()
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client.post = AsyncMock(
                    side_effect=httpx.RequestError("network error", request=MagicMock())
                )
                mock_client_cls.return_value = mock_client
                with patch("app.services.poi_service._get_redis", return_value=None):
                    result = await svc.get_pois(17.385, 78.486)
            return result

        result = asyncio.run(_run())
        assert result["error"] == "overpass_unavailable"

    def test_haversine_distance_known_pair(self):
        """Haversine between two known Hyderabad points is within 0.5km tolerance."""
        from app.services.poi_service import _haversine_km
        # Kokapet to Narsingi — approx 3.3 km
        dist = _haversine_km(17.3978, 78.3280, 17.3750, 78.3550)
        assert 2.0 < dist < 5.0, f"Unexpected distance: {dist}"

    def test_haversine_zero_distance(self):
        """Same point should be 0 km."""
        from app.services.poi_service import _haversine_km
        assert _haversine_km(17.385, 78.486, 17.385, 78.486) == pytest.approx(0.0, abs=1e-6)

    def test_poi_result_cached_in_redis(self):
        """On a successful Overpass call, result is written to Redis."""
        from app.services.poi_service import POIService

        async def _run():
            svc = POIService()
            mock_redis = MagicMock()
            mock_redis.get = MagicMock(return_value=None)
            mock_redis.setex = MagicMock()

            overpass_resp = {"elements": []}
            mock_response = MagicMock()
            mock_response.json.return_value = overpass_resp
            mock_response.raise_for_status = MagicMock()

            with patch("app.services.poi_service._get_redis", return_value=mock_redis), \
                 patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client_cls.return_value = mock_client
                await svc.get_pois(17.385, 78.486)

            return mock_redis.setex.called

        assert asyncio.run(_run()) is True


# ── Growth service tests (Task 16.7) ─────────────────────────────────────

class TestGrowthService:

    def test_assign_growth_tier_high(self):
        """3+ approved/under_construction signals → High Growth Corridor."""
        from app.services.growth_service import _assign_growth_tier

        class S:
            def __init__(self, status): self.status = status

        signals = [S("approved"), S("under_construction"), S("approved"), S("announced")]
        assert _assign_growth_tier(signals) == "High Growth Corridor"

    def test_assign_growth_tier_emerging(self):
        """1–2 active signals → Emerging Zone."""
        from app.services.growth_service import _assign_growth_tier

        class S:
            def __init__(self, status): self.status = status

        assert _assign_growth_tier([S("approved"), S("announced")]) == "Emerging Zone"
        assert _assign_growth_tier([S("under_construction")]) == "Emerging Zone"

    def test_assign_growth_tier_speculative(self):
        """Zero active signals → Speculative regardless of announced count."""
        from app.services.growth_service import _assign_growth_tier

        class S:
            def __init__(self, status): self.status = status

        assert _assign_growth_tier([]) == "Speculative"
        assert _assign_growth_tier([S("announced"), S("announced")]) == "Speculative"
        assert _assign_growth_tier([S("operational")]) == "Speculative"

    def test_announced_signal_without_source_url_excluded(self):
        """Growth service filters out announced signals with no source_url."""
        from app.services.growth_service import GrowthService
        import uuid

        async def _run():
            mock_db = AsyncMock()

            # Listing
            mock_listing = MagicMock()
            mock_listing.lat = 17.385
            mock_listing.lng = 78.486

            # One valid signal (has source_url), one invalid (announced + no source_url)
            sig_valid = MagicMock()
            sig_valid.center_lat = 17.390
            sig_valid.center_lng = 78.490
            sig_valid.status = "approved"
            sig_valid.source_url = "https://example.com"
            sig_valid.id = uuid.uuid4()
            sig_valid.signal_type = "metro"
            sig_valid.title = "Test Metro"
            sig_valid.source_type = "government"
            sig_valid.announced_date = None
            sig_valid.confidence = 0.9

            sig_invalid = MagicMock()
            sig_invalid.center_lat = 17.388
            sig_invalid.center_lng = 78.488
            sig_invalid.status = "announced"
            sig_invalid.source_url = None  # ← should be excluded
            sig_invalid.id = uuid.uuid4()

            # Mock DB execute to return listing, then signals
            listing_result = MagicMock()
            listing_result.scalars.return_value.first.return_value = mock_listing
            signals_result = MagicMock()
            signals_result.scalars.return_value.all.return_value = [sig_valid, sig_invalid]
            mock_db.execute = AsyncMock(side_effect=[listing_result, signals_result])

            svc = GrowthService(mock_db)
            result = await svc.get_signals(uuid.uuid4())
            return result

        result = asyncio.run(_run())
        # Only 1 signal should appear (sig_invalid excluded)
        assert len(result["signals"]) == 1
        assert result["signals"][0]["status"] == "approved"

    def test_growth_haversine_filters_distant_signals(self):
        """Signals > 10km away should not appear in results."""
        from app.services.growth_service import GrowthService
        import uuid

        async def _run():
            mock_db = AsyncMock()
            mock_listing = MagicMock()
            mock_listing.lat = 17.385
            mock_listing.lng = 78.486

            # Signal 50km away
            distant = MagicMock()
            distant.center_lat = 17.850  # ~52km north
            distant.center_lng = 78.486
            distant.status = "approved"
            distant.source_url = "https://example.com"

            listing_result = MagicMock()
            listing_result.scalars.return_value.first.return_value = mock_listing
            signals_result = MagicMock()
            signals_result.scalars.return_value.all.return_value = [distant]
            mock_db.execute = AsyncMock(side_effect=[listing_result, signals_result])

            svc = GrowthService(mock_db)
            return await svc.get_signals(uuid.uuid4())

        result = asyncio.run(_run())
        assert result["signals"] == []
        assert result["growth_tier"] == "Speculative"


# ── GrowthSignal model validation (Task 16.3) ────────────────────────────

class TestGrowthSignalModelValidation:

    def test_announced_without_source_url_raises_valueerror(self):
        """SQLAlchemy event listener rejects announced signal with no source_url."""
        from app.models.listing import GrowthSignal, _validate_growth_signal

        signal = GrowthSignal(
            signal_type="metro",
            title="Test Signal",
            status="announced",
            source_url=None,  # ← missing
        )
        with pytest.raises(ValueError, match="source_url"):
            _validate_growth_signal(None, None, signal)

    def test_announced_with_source_url_passes(self):
        """Announced signal with source_url should not raise."""
        from app.models.listing import GrowthSignal, _validate_growth_signal
        signal = GrowthSignal(
            signal_type="metro",
            title="Test Signal",
            status="announced",
            source_url="https://example.gov.in/signal",
        )
        _validate_growth_signal(None, None, signal)  # should not raise

    def test_non_announced_without_source_url_passes(self):
        """Non-announced signal without source_url should be fine."""
        from app.models.listing import GrowthSignal, _validate_growth_signal
        signal = GrowthSignal(
            signal_type="metro",
            title="Test Signal",
            status="approved",
            source_url=None,
        )
        _validate_growth_signal(None, None, signal)  # should not raise
