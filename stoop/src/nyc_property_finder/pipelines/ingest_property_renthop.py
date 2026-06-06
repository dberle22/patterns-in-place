"""RentHop ingestion placeholder."""

from __future__ import annotations

import pandas as pd


def ingest_property_renthop(search_url: str, limit: int | None = None) -> pd.DataFrame:
    """Return a structured empty dataframe until RentHop access is implemented."""

    # TODO: Add a RentHop scraper if this source becomes part of the MVP.
    columns = [
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
        "url",
        "ingest_timestamp",
    ]
    return pd.DataFrame(columns=columns)
