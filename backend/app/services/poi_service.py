"""POI Service — Overpass API queries with 10s timeout and Redis cache."""
import json
import logging
import math
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
RADIUS_M = 5000  # 5 km
CACHE_TTL = 3600  # 1 hour

# Overpass tags for each POI category
CATEGORY_QUERIES = {
    "schools": '["amenity"~"school|college|university"]',
    "hospitals": '["amenity"~"hospital|clinic|doctors"]',
    "malls": '["shop"~"mall|supermarket"]["name"]',
    "metro_stations": '["railway"~"station|subway_entrance"]["name"]',
    "highways": '["highway"~"motorway|trunk"]["name"]',
    "bus_depots": '["amenity"="bus_station"]',
}


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _build_overpass_query(lat: float, lng: float) -> str:
    parts = [f'[out:json][timeout:10];(']
    for tags in CATEGORY_QUERIES.values():
        parts.append(f'  node{tags}(around:{RADIUS_M},{lat},{lng});')
        parts.append(f'  way{tags}(around:{RADIUS_M},{lat},{lng});')
    parts.append(');out center 50;')
    return "\n".join(parts)


def _parse_overpass_response(data: dict, lat: float, lng: float) -> dict[str, list]:
    result: dict[str, list] = {cat: [] for cat in CATEGORY_QUERIES}
    elements = data.get("elements", [])

    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:en") or tags.get("name:te")
        if not name:
            continue

        # Get coordinates
        if el.get("type") == "node":
            el_lat, el_lng = el.get("lat"), el.get("lon")
        else:
            center = el.get("center", {})
            el_lat, el_lng = center.get("lat"), center.get("lon")

        if el_lat is None or el_lng is None:
            continue

        dist_km = round(_haversine_km(lat, lng, el_lat, el_lng), 2)
        poi = {"name": name, "distance_km": dist_km, "lat": el_lat, "lng": el_lng}

        # Match to category
        amenity = tags.get("amenity", "")
        shop = tags.get("shop", "")
        railway = tags.get("railway", "")
        highway = tags.get("highway", "")

        if amenity in ("school", "college", "university"):
            result["schools"].append(poi)
        elif amenity in ("hospital", "clinic", "doctors"):
            result["hospitals"].append(poi)
        elif shop in ("mall", "supermarket"):
            result["malls"].append(poi)
        elif railway in ("station", "subway_entrance"):
            result["metro_stations"].append(poi)
        elif highway in ("motorway", "trunk"):
            result["highways"].append(poi)
        elif amenity == "bus_station":
            result["bus_depots"].append(poi)

    # Sort by distance and cap at 5 per category
    for cat in result:
        result[cat] = sorted(result[cat], key=lambda p: p["distance_km"])[:5]

    return result


def _get_redis():
    try:
        import redis
        return redis.from_url(settings.redis_url, socket_connect_timeout=2, decode_responses=True)
    except Exception:
        return None


class POIService:
    async def get_pois(self, lat: float, lng: float) -> dict[str, Any]:
        """Fetch POIs within 5km. Results cached in Redis for 1 hour."""
        cache_key = f"pois:{lat:.4f}:{lng:.4f}"

        # Try cache first
        r = _get_redis()
        if r:
            try:
                cached = r.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as exc:
                logger.warning(f"Redis cache read failed: {exc}")

        # Query Overpass API
        query = _build_overpass_query(lat, lng)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(OVERPASS_URL, data={"data": query})
                resp.raise_for_status()
                data = resp.json()
            pois = _parse_overpass_response(data, lat, lng)
            result = {"pois": pois, "error": None}
        except (httpx.TimeoutException, httpx.RequestError, Exception) as exc:
            logger.warning(f"Overpass API failed for ({lat},{lng}): {exc}")
            # Return empty result with error flag — never 5xx
            result = {"pois": {cat: [] for cat in CATEGORY_QUERIES}, "error": "overpass_unavailable"}

        # Write to cache (even on partial error, to avoid hammering Overpass)
        if r:
            try:
                r.setex(cache_key, CACHE_TTL, json.dumps(result))
            except Exception as exc:
                logger.warning(f"Redis cache write failed: {exc}")

        return result
