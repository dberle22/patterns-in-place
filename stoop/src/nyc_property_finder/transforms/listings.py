"""Property listing normalization."""

from __future__ import annotations

import pandas as pd

from nyc_property_finder.utils.hashing import generate_property_id


PROPERTY_COLUMNS = [
    "property_id",
    "source",
    "source_listing_id",
    "address",
    "lat",
    "lon",
    "price",
    "beds",
    "baths",
    "listing_type",
    "active",
    "url",
    "ingest_timestamp",
]


LISTING_TYPE_ALIASES = {
    "rent": "rental",
    "rental": "rental",
    "lease": "rental",
    "sale": "sale",
    "sales": "sale",
    "buy": "sale",
}


def normalize_listing_type(value: object) -> str:
    """Normalize source listing type values into the Property Explorer contract."""

    if pd.isna(value):
        return "rental"
    normalized = str(value).strip().lower()
    return LISTING_TYPE_ALIASES.get(normalized, normalized)


def normalize_property_listings(dataframe: pd.DataFrame, source: str) -> pd.DataFrame:
    """Normalize raw listing rows to the starter property schema."""

    output = dataframe.copy()
    output["source"] = source
    output["source_listing_id"] = output.get("source_listing_id", output.get("id", ""))
    output["address"] = output.get("address", "")
    output["price"] = pd.to_numeric(output.get("price"), errors="coerce")
    output["beds"] = pd.to_numeric(output.get("beds"), errors="coerce")
    output["baths"] = pd.to_numeric(output.get("baths"), errors="coerce")
    output["lat"] = pd.to_numeric(output.get("lat"), errors="coerce")
    output["lon"] = pd.to_numeric(output.get("lon"), errors="coerce")
    output["listing_type"] = output.get("listing_type", "rental")
    output["listing_type"] = output["listing_type"].map(normalize_listing_type)
    output["active"] = output.get("active", True)
    output["url"] = output.get("url", "")
    output["ingest_timestamp"] = pd.Timestamp.now(tz="UTC")
    output["property_id"] = output.apply(
        lambda row: generate_property_id(
            source=row["source"],
            source_listing_id=row.get("source_listing_id"),
            address=row.get("address"),
            lat=row.get("lat"),
            lon=row.get("lon"),
        ),
        axis=1,
    )
    return output[PROPERTY_COLUMNS]
