"""Price predictor using Ridge regression on comparable listings."""
from __future__ import annotations
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PricePredictor:
    """
    Predicts listing price based on area and locality comparables using Ridge regression.
    """

    def predict_price_lakhs(
        self,
        area_sqyd: float,
        locality_comparables: list[dict],
    ) -> Optional[float]:
        """
        Predict price in lakhs for a given area in sqyd, using locality comparables.
        Requires at least 3 comparables.
        comparables must be dicts with 'area_sqyd' and 'price_lakhs'.
        """
        if len(locality_comparables) < 3:
            return None

        try:
            from sklearn.linear_model import Ridge
            import numpy as np
            
            X = np.array([[c["area_sqyd"]] for c in locality_comparables])
            y = np.array([c["price_lakhs"] for c in locality_comparables])
            
            # Simple Ridge regression
            model = Ridge(alpha=1.0)
            model.fit(X, y)
            
            prediction = model.predict([[area_sqyd]])
            result = float(prediction[0])
            
            # Basic bounds check: shouldn't be negative
            return max(0.1, result)
        except ImportError:
            logger.warning("scikit-learn not installed; price prediction disabled")
            return None
        except Exception as e:
            logger.warning(f"Price prediction failed: {e}")
            return None


price_predictor = PricePredictor()
