"""Seed dataset for PlotIQ POC."""

LOCALITIES = [
    {"name": "Kokapet", "lat": 17.3978, "lng": 78.3280, "base_price": 40000},
    {"name": "Shadnagar", "lat": 17.0694, "lng": 78.1867, "base_price": 10000},
    {"name": "Adibatla", "lat": 17.3103, "lng": 78.5906, "base_price": 20000},
    {"name": "Patancheru", "lat": 17.5372, "lng": 78.2656, "base_price": 18000},
    {"name": "Ibrahimpatnam", "lat": 17.2228, "lng": 78.6714, "base_price": 12000},
    {"name": "Shamshabad", "lat": 17.2403, "lng": 78.4294, "base_price": 25000},
    {"name": "Ghatkesar", "lat": 17.4435, "lng": 78.6970, "base_price": 15000},
    {"name": "Sangareddy", "lat": 17.6238, "lng": 78.0880, "base_price": 8000},
]

GROWTH_SIGNALS = [
    {
        "title": "HMDA Layout Expansion",
        "signal_type": "hmda_layout",
        "status": "approved",
        "confidence": 0.95,
        "locality": "Kokapet",
    },
    {
        "title": "New Metro Route Alignment",
        "signal_type": "metro",
        "status": "announced",
        "confidence": 0.70,
        "locality": "Shamshabad",
    },
    {
        "title": "Industrial Park Development",
        "signal_type": "industrial_park",
        "status": "under_construction",
        "confidence": 0.85,
        "locality": "Adibatla",
    },
    {
        "title": "Regional Ring Road (RRR) Interchange",
        "signal_type": "nhai_highway",
        "status": "announced",
        "confidence": 0.60,
        "locality": "Shadnagar",
    },
]

# Generate synthetic listings during seeding based on localities
