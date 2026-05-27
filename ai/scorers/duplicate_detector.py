"""Duplicate detector — perceptual hash comparison + phone reuse check."""
from __future__ import annotations


def duplicate_detection_scorer(
    duplicate_image_found: bool,
    phone_listing_count: int,
    phone_reuse_threshold: int = 3,
) -> int:
    """
    Return 0-100 score for duplicate/fraud signals.
    
    - Duplicate image found: 0 (definitive fraud signal)
    - Phone used in > threshold other listings: 20
    - Phone used in 1-threshold other listings: 60
    - No duplicate signals: 100
    """
    if duplicate_image_found:
        return 0

    if phone_listing_count > phone_reuse_threshold:
        return 20

    if phone_listing_count > 0:
        return 60

    return 100


def compute_perceptual_hash(image_bytes: bytes) -> str:
    """
    Compute a perceptual hash of an image for duplicate detection.
    Returns a hex string suitable for database storage and comparison.
    
    Requires: imagehash, pillow
    """
    try:
        import imagehash
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_bytes))
        phash = imagehash.phash(img)
        return str(phash)
    except ImportError:
        return ""
    except Exception:
        return ""


def hashes_are_similar(hash1: str, hash2: str, threshold: int = 10) -> bool:
    """
    Return True if two perceptual hashes differ by at most `threshold` bits.
    Threshold of 10 is industry-standard for "likely duplicate".
    """
    if not hash1 or not hash2:
        return False
    try:
        import imagehash
        h1 = imagehash.hex_to_hash(hash1)
        h2 = imagehash.hex_to_hash(hash2)
        return (h1 - h2) <= threshold
    except Exception:
        return False
