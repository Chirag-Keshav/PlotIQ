"""Price Service — estimation, comparables, trend, classification."""
import uuid
import math
import statistics
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.listing import Listing, Comparable


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _percentile(data: list[float], p: float) -> float:
    if not data:
        return 0.0
    s = sorted(data)
    n = len(s)
    idx = (p / 100) * (n - 1)
    lo, hi = int(idx), min(int(idx) + 1, n - 1)
    return s[lo] + (idx - lo) * (s[hi] - s[lo])


def _bootstrap_percentiles(
    price_per_sqyd: float,
    area_sqyd: float,
    comp_prices: list[float],
    n_samples: int = 100,
) -> dict:
    """Return P10/P50/P90 in lakhs via bootstrap resampling of comparables."""
    import random
    if not comp_prices:
        est = price_per_sqyd * area_sqyd / 100_000
        return {"p10_lakhs": round(est * 0.8, 2), "p50_lakhs": round(est, 2), "p90_lakhs": round(est * 1.2, 2)}

    estimates = []
    for _ in range(n_samples):
        sample = random.choices(comp_prices, k=len(comp_prices))
        median_ppsqyd = statistics.median(sample)
        estimates.append(median_ppsqyd * area_sqyd / 100_000)

    estimates.sort()
    return {
        "p10_lakhs": round(_percentile(estimates, 10), 2),
        "p50_lakhs": round(_percentile(estimates, 50), 2),
        "p90_lakhs": round(_percentile(estimates, 90), 2),
    }


def _classify_price(subject_ppsqyd: float, comp_prices: list[float]) -> str:
    if len(comp_prices) < 2:
        return "fair"
    p25 = _percentile(comp_prices, 25)
    p75 = _percentile(comp_prices, 75)
    if subject_ppsqyd > p75:
        return "overpriced"
    if subject_ppsqyd < p25:
        return "underpriced"
    return "fair"


def _negotiation_range(area_sqyd: float, comp_prices: list[float]) -> dict:
    p25 = _percentile(comp_prices, 25)
    p50 = _percentile(comp_prices, 50)
    return {
        "low_lakhs": round(p25 * area_sqyd / 100_000, 2),
        "high_lakhs": round(p50 * area_sqyd / 100_000, 2),
    }


class PriceService:
    COMP_RADIUS_KM = 20.0
    AREA_TOLERANCE = 0.20  # 20%
    MAX_COMPS = 10

    def __init__(self, db: AsyncSession):
        self.db = db

    async def estimate(self, listing_id: uuid.UUID) -> dict:
        stmt = select(Listing).where(Listing.id == listing_id)
        listing = (await self.db.execute(stmt)).scalars().first()
        if not listing:
            return {"error": "Listing not found"}

        area = float(listing.area_sqyd)
        price_ppsqyd = float(listing.price_lakhs) * 100_000 / area if area else 0.0

        # Find comparables using haversine distance
        all_comps_stmt = select(Comparable)
        all_comps = (await self.db.execute(all_comps_stmt)).scalars().all()

        nearby_comps = []
        for c in all_comps:
            if c.lat is None or c.lng is None:
                continue
            dist = _haversine_km(float(listing.lat), float(listing.lng), float(c.lat), float(c.lng))
            c_area = float(c.area_sqyd) if c.area_sqyd else 0
            within_area = c_area == 0 or abs(c_area - area) / max(area, 1) <= self.AREA_TOLERANCE
            if dist <= self.COMP_RADIUS_KM and within_area:
                nearby_comps.append((c, dist))

        nearby_comps.sort(key=lambda x: x[1])
        nearby_comps = nearby_comps[: self.MAX_COMPS]

        comp_ppsqyd = [
            float(c.price_lakhs) * 100_000 / float(c.area_sqyd)
            for c, _ in nearby_comps
            if c.price_lakhs and c.area_sqyd and float(c.area_sqyd) > 0
        ]

        # Bootstrap percentiles
        estimate = _bootstrap_percentiles(price_ppsqyd, area, comp_ppsqyd)

        # Classification and negotiation range
        classification = _classify_price(price_ppsqyd, comp_ppsqyd)
        neg_range = _negotiation_range(area, comp_ppsqyd) if comp_ppsqyd else {
            "low_lakhs": round(float(listing.price_lakhs) * 0.85, 2),
            "high_lakhs": round(float(listing.price_lakhs) * 0.95, 2),
        }

        # Price trend: aggregate comparables by month (mock trend when no data)
        price_trend = self._build_price_trend(nearby_comps)

        return {
            "estimate": estimate,
            "classification": classification,
            "negotiation_range": neg_range,
            "comparables": [
                {
                    "locality": c.locality or listing.locality,
                    "area_sqyd": float(c.area_sqyd) if c.area_sqyd else 0,
                    "price_lakhs": float(c.price_lakhs) if c.price_lakhs else 0,
                    "price_per_sqyd": round(float(c.price_lakhs) * 100_000 / float(c.area_sqyd), 0)
                    if c.price_lakhs and c.area_sqyd and float(c.area_sqyd) > 0
                    else 0,
                    "distance_km": round(dist, 2),
                }
                for c, dist in nearby_comps
            ],
            "price_trend": price_trend,
        }

    def _build_price_trend(self, nearby_comps: list) -> list[dict]:
        """Build monthly median price/sqyd from comparables."""
        from collections import defaultdict
        monthly: dict[str, list[float]] = defaultdict(list)
        for c, _ in nearby_comps:
            if c.transaction_date and c.price_lakhs and c.area_sqyd and float(c.area_sqyd) > 0:
                month_key = c.transaction_date.strftime("%Y-%m")
                ppsqyd = float(c.price_lakhs) * 100_000 / float(c.area_sqyd)
                monthly[month_key].append(ppsqyd)

        if not monthly:
            return []

        return [
            {"month": month, "median_price_per_sqyd": round(statistics.median(prices), 0)}
            for month, prices in sorted(monthly.items())
        ]
