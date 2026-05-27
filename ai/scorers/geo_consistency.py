"""Geo-consistency scorer — validates lat/lng within Hyderabad bounding box and locality."""

# Hyderabad metropolitan area bounding box
HYDERABAD_BOUNDS = {
    "lat_min": 17.0,
    "lat_max": 18.0,
    "lng_min": 77.8,
    "lng_max": 79.0,
}

# Expected locality-to-approximate-center mapping for cross-check
LOCALITY_CENTERS: dict[str, tuple[float, float]] = {
    "kokapet": (17.3978, 78.3280),
    "shadnagar": (17.0694, 78.1867),
    "adibatla": (17.3103, 78.5906),
    "patancheru": (17.5372, 78.2656),
    "ibrahimpatnam": (17.2228, 78.6714),
    "shamshabad": (17.2403, 78.4294),
    "ghatkesar": (17.4435, 78.6970),
    "sangareddy": (17.6238, 78.0880),
    "kompally": (17.5410, 78.4775),
    "bachupally": (17.5311, 78.3986),
    "miyapur": (17.4962, 78.3567),
    "gachibowli": (17.4401, 78.3489),
    "hitech city": (17.4504, 78.3808),
    "financial district": (17.4182, 78.3430),
}

# Maximum allowed distance (km) between listing coords and locality center
MAX_LOCALITY_DISTANCE_KM = 25.0


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in km between two points."""
    import math
    R = 6371.0
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lng2 - lng1)
    a = math.sin(Δφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def geo_consistency_scorer(lat: float, lng: float, locality: str) -> int:
    """
    Return 0-100 score for geographic consistency.
    
    Checks:
    1. lat/lng within Hyderabad metropolitan bounding box (required for any score)
    2. If locality is known, distance from listing to locality center
    """
    # Check bounding box
    in_bounds = (
        HYDERABAD_BOUNDS["lat_min"] <= lat <= HYDERABAD_BOUNDS["lat_max"]
        and HYDERABAD_BOUNDS["lng_min"] <= lng <= HYDERABAD_BOUNDS["lng_max"]
    )
    if not in_bounds:
        return 0

    # Check locality proximity if we know the locality
    locality_key = locality.lower().strip()
    if locality_key in LOCALITY_CENTERS:
        center_lat, center_lng = LOCALITY_CENTERS[locality_key]
        dist_km = _haversine_km(lat, lng, center_lat, center_lng)
        if dist_km > MAX_LOCALITY_DISTANCE_KM:
            return 40  # In Hyderabad but wrong locality
        # Linear score: 100 at center, 60 at max distance
        score = max(60, 100 - int(dist_km / MAX_LOCALITY_DISTANCE_KM * 40))
        return min(100, score)

    # In Hyderabad but unknown locality: partial credit
    return 70
