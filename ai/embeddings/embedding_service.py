"""EmbeddingService wrapping sentence-transformers/all-MiniLM-L6-v2."""
from __future__ import annotations
import logging
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Loaded sentence-transformers/all-MiniLM-L6-v2")
        except ImportError:
            logger.warning("sentence-transformers not installed; embeddings disabled")
            _model = None
    return _model


class EmbeddingService:
    """Wraps sentence-transformers for 384-dimensional text embeddings."""

    EXPECTED_DIM = 384

    def embed(self, text: str) -> list[float]:
        """
        Embed a single text string.
        Returns exactly 384 floats (all-MiniLM-L6-v2 output dimension).
        Raises ValueError if the model produces wrong dimension.
        """
        model = _get_model()
        if model is None:
            # Return zero vector as fallback (development without GPU/model)
            return [0.0] * self.EXPECTED_DIM

        embedding = model.encode(text, normalize_embeddings=True)
        result = embedding.tolist()

        if len(result) != self.EXPECTED_DIM:
            raise ValueError(
                f"Expected {self.EXPECTED_DIM} dimensions, got {len(result)}"
            )
        return result

    def embed_listing(self, listing: dict) -> list[float]:
        """
        Build a representative text from listing fields and embed it.
        Combines title, description, locality, use_type for semantic representation.
        """
        parts = [
            listing.get("title", ""),
            listing.get("description", ""),
            listing.get("locality", ""),
            listing.get("use_type", ""),
            listing.get("road_access", ""),
            f"{listing.get('area_sqyd', '')} sqyd",
            f"{listing.get('price_lakhs', '')} lakhs",
        ]
        text = " ".join(p for p in parts if p)
        return self.embed(text)


# Module-level singleton
embedding_service = EmbeddingService()
