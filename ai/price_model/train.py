"""
Train the PlotIQ price model on seed data and serialize to model.joblib.

Usage (from repo root):
    python ai/price_model/train.py

The script:
  1. Loads listings from the database (or falls back to seed_data locality params)
  2. Builds feature matrix: locality (one-hot), area_sqyd, road_access (ordinal),
     listing_age_days, use_type (one-hot)
  3. Trains scikit-learn Ridge regression on price_per_sqyd target
  4. Serializes the fitted Pipeline to ai/price_model/model.joblib
"""
from __future__ import annotations

import os
import sys
import logging

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")

ROAD_ACCESS_ORDINAL = {"none": 0, "40ft": 1, "60ft": 2, "100ft": 3, "highway": 4}
USE_TYPE_MAP = {"agricultural": 0, "residential": 1, "commercial": 2}


def _fallback_training_data() -> list[dict]:
    """Generate synthetic training data from seed locality params when DB is unavailable."""
    import random
    random.seed(0)

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    from seed.seed_data import LOCALITIES

    records = []
    for loc in LOCALITIES:
        for _ in range(20):
            area = random.choice([100, 150, 200, 267, 300, 500, 968, 2000])
            ppsqyd = loc["base_price"] * random.uniform(0.6, 1.5)
            use_type = random.choice(["residential", "commercial", "agricultural"])
            road_access = random.choice(["40ft", "60ft", "100ft", "highway", "none"])
            age_days = random.randint(0, 180)
            records.append({
                "locality": loc["name"],
                "area_sqyd": float(area),
                "use_type": use_type,
                "road_access": road_access,
                "listing_age_days": age_days,
                "price_per_sqyd": ppsqyd,
            })
    return records


def _load_from_db() -> list[dict]:
    """Load listings from the database for training."""
    try:
        import asyncio
        from sqlalchemy import select

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        from app.core.database import AsyncSessionLocal
        from app.models.listing import Listing
        from datetime import datetime

        async def _fetch():
            async with AsyncSessionLocal() as db:
                stmt = select(Listing).where(
                    Listing.price_lakhs.isnot(None),
                    Listing.area_sqyd.isnot(None),
                )
                result = await db.execute(stmt)
                rows = result.scalars().all()
                records = []
                for r in rows:
                    area = float(r.area_sqyd)
                    if area <= 0:
                        continue
                    ppsqyd = float(r.price_lakhs) * 100_000 / area
                    age_days = 0
                    if r.created_at:
                        age_days = max(0, (datetime.utcnow() - r.created_at.replace(tzinfo=None)).days)
                    records.append({
                        "locality": r.locality or "Unknown",
                        "area_sqyd": area,
                        "use_type": r.use_type or "residential",
                        "road_access": r.road_access or "none",
                        "listing_age_days": age_days,
                        "price_per_sqyd": ppsqyd,
                    })
                return records

        return asyncio.run(_fetch())
    except Exception as exc:
        logger.warning(f"DB load failed ({exc}); using synthetic fallback data")
        return []


def train(records: list[dict] | None = None) -> object:
    """
    Train Ridge regression pipeline. Returns the fitted sklearn Pipeline.

    Feature columns:
      - locality (OneHotEncoder, handle_unknown='ignore')
      - use_type (OneHotEncoder, handle_unknown='ignore')
      - area_sqyd, road_access_ordinal, listing_age_days (StandardScaler)

    Target: price_per_sqyd
    """
    try:
        import numpy as np
        import pandas as pd
        import joblib
        from sklearn.pipeline import Pipeline
        from sklearn.compose import ColumnTransformer
        from sklearn.preprocessing import OneHotEncoder, StandardScaler, OrdinalEncoder
        from sklearn.linear_model import Ridge
        from sklearn.model_selection import cross_val_score
    except ImportError as exc:
        raise ImportError(f"scikit-learn / joblib / pandas required: {exc}")

    if records is None:
        records = _load_from_db()
    if len(records) < 10:
        logger.info("DB has < 10 records — using synthetic fallback data")
        records = _fallback_training_data()

    df = pd.DataFrame(records)
    df = df[df["price_per_sqyd"] > 0].copy()

    # Encode road_access as ordinal
    df["road_access_ordinal"] = df["road_access"].map(ROAD_ACCESS_ORDINAL).fillna(0)

    CATEGORICAL = ["locality", "use_type"]
    NUMERIC = ["area_sqyd", "road_access_ordinal", "listing_age_days"]

    X = df[CATEGORICAL + NUMERIC]
    y = df["price_per_sqyd"]

    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
        ("num", StandardScaler(), NUMERIC),
    ])

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", Ridge(alpha=1.0)),
    ])

    pipeline.fit(X, y)

    # Quick CV score for logging
    try:
        scores = cross_val_score(pipeline, X, y, cv=min(5, len(df) // 5), scoring="r2")
        logger.info(f"Price model CV R² = {scores.mean():.3f} ± {scores.std():.3f} (n={len(df)})")
        print(f"Price model trained: CV R² = {scores.mean():.3f} ± {scores.std():.3f} on {len(df)} samples")
    except Exception:
        print(f"Price model trained on {len(df)} samples")

    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    return pipeline


def load_or_train() -> object | None:
    """Load model from disk; train if not found. Returns None if sklearn unavailable."""
    try:
        import joblib
    except ImportError:
        return None

    if os.path.exists(MODEL_PATH):
        try:
            pipeline = joblib.load(MODEL_PATH)
            logger.info(f"Loaded price model from {MODEL_PATH}")
            return pipeline
        except Exception as exc:
            logger.warning(f"Failed to load model ({exc}); retraining")

    logger.info("No saved model found — training now")
    try:
        return train()
    except Exception as exc:
        logger.warning(f"Model training failed: {exc}")
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train()
