"""POI Service using Google Maps Places API."""
import os
import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class POIService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")

    async def get_pois(self, lat: float, lng: float) -> Dict[str, list]:
        """Fetch POIs (schools, hospitals, transit) near the location."""
        # For POC, if no API key is provided, return mock data
        if not self.api_key:
            return self._mock_pois()
            
        try:
            # We would use HTTPX to call Places API
            # For this POC, we'll just return mock data to save API costs
            return self._mock_pois()
        except Exception as e:
            logger.warning(f"Google Maps API failed: {e}")
            return self._mock_pois()
            
    def _mock_pois(self) -> Dict[str, list]:
        """Mock POI data for the POC."""
        return {
            "schools": [
                {"name": "Delhi Public School", "distance_km": 1.2, "rating": 4.5},
                {"name": "Oakridge International", "distance_km": 3.4, "rating": 4.8}
            ],
            "hospitals": [
                {"name": "Apollo Hospitals", "distance_km": 2.1, "rating": 4.6},
                {"name": "Care Hospital", "distance_km": 4.0, "rating": 4.2}
            ],
            "transit": [
                {"name": "ORR Exit 1", "distance_km": 0.5, "rating": None},
                {"name": "Proposed Metro Station", "distance_km": 1.5, "rating": None}
            ]
        }
