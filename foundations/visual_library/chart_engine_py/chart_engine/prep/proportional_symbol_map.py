from __future__ import annotations

import pandas as pd

from ..geo import centroid_from_polygons, geometry_to_polygons
from ..specs import ChartSpec


def prep_proportional_symbol_map(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()

    out["size_value"] = pd.to_numeric(out["size_value"], errors="coerce")
    if "lon" in out.columns:
        out["lon"] = pd.to_numeric(out["lon"], errors="coerce")
    else:
        out["lon"] = None
    if "lat" in out.columns:
        out["lat"] = pd.to_numeric(out["lat"], errors="coerce")
    else:
        out["lat"] = None

    if "geometry" in out.columns:
        missing_centers = out["lon"].isna() | out["lat"].isna()
        for idx in out[missing_centers].index:
            polygons = geometry_to_polygons(out.at[idx, "geometry"])
            lon, lat = centroid_from_polygons(polygons)
            out.at[idx, "lon"] = lon
            out.at[idx, "lat"] = lat

    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool) if "highlight_flag" in out.columns else False
    out["label_flag"] = out["label_flag"].fillna(False).astype(bool) if "label_flag" in out.columns else False
    out = out[out["size_value"].notna() & out["lon"].notna() & out["lat"].notna()].copy()
    return out
