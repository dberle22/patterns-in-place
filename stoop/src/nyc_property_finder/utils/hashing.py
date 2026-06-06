"""Stable hashing helpers."""

from __future__ import annotations

import hashlib
from typing import Any


def normalize_hash_part(value: Any) -> str:
    """Normalize one value before hashing."""

    if value is None:
        return ""
    return str(value).strip().lower()


def generate_property_id(
    source: str,
    source_listing_id: str | None = None,
    address: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
) -> str:
    """Generate a stable property id from source data."""

    parts = [
        normalize_hash_part(source),
        normalize_hash_part(source_listing_id),
        normalize_hash_part(address),
        normalize_hash_part(round(lat, 6) if lat is not None else None),
        normalize_hash_part(round(lon, 6) if lon is not None else None),
    ]
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return f"prop_{digest[:16]}"
