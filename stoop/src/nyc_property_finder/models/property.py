"""Property domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PropertyListing:
    """Small typed representation of a property listing."""

    property_id: str
    source: str
    address: str
    lat: float
    lon: float
    price: float | None = None
    beds: float | None = None
    baths: float | None = None
    url: str | None = None
