"""Geography transforms.

This module is intentionally small for now; shared spatial mechanics live in
``utils.geo`` and pipeline-specific geography work lives in pipeline modules.
"""

from __future__ import annotations

import geopandas as gpd

from nyc_property_finder.utils.geo import ensure_crs


def standardize_geography(geo_df: gpd.GeoDataFrame, crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """Return a copy of a geometry layer in the project CRS."""

    return ensure_crs(geo_df.copy(), crs=crs)
