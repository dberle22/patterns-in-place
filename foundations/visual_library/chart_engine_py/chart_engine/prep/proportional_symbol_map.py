from __future__ import annotations

import pandas as pd

from ..geo import centroid_from_polygons, geometry_to_polygons
from ..matrix_helpers import preserve_runtime_fields
from ..specs import ChartSpec


def prep_proportional_symbol_map(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    cfg = spec.runtime_config or {}
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()
    out = preserve_runtime_fields(df, out, ("question_id", "group"))

    if cfg.get("question_id") and "question_id" in out.columns:
        out = out.loc[out["question_id"] == cfg["question_id"]].copy()
    if cfg.get("time_window") and "time_window" in out.columns:
        out = out.loc[out["time_window"].astype(str) == str(cfg["time_window"])].copy()
    if cfg.get("geo_ids"):
        out = out.loc[out["geo_id"].astype(str).isin([str(value) for value in cfg["geo_ids"]])].copy()
    if cfg.get("color_groups") and "color_group" in out.columns:
        out = out.loc[out["color_group"].astype(str).isin([str(value) for value in cfg["color_groups"]])].copy()

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
    if cfg.get("drop_missing_size", True):
        out = out.loc[out["size_value"].notna() & (out["size_value"] > 0)].copy()
    if cfg.get("drop_missing_coordinates", True):
        out = out.loc[out["lon"].notna() & out["lat"].notna()].copy()
    if out.empty:
        raise ValueError("proportional_symbol_map prep removed all rows; adjust the request filters.")

    group_field = "color_group" if cfg.get("top_n_by_group") and "color_group" in out.columns else None
    if group_field:
        out["size_rank"] = out.groupby(group_field)["size_value"].rank(method="first", ascending=False)
    else:
        out["size_rank"] = out["size_value"].rank(method="first", ascending=False)
    total_size = float(out["size_value"].sum())
    out = out.sort_values(["size_rank", "geo_name", "geo_id"], ascending=[True, True, True]).copy()
    out["size_share"] = out["size_value"] / total_size if total_size > 0 else float("nan")
    out["cumulative_size_share"] = out["size_value"].cumsum() / total_size if total_size > 0 else float("nan")

    if cfg.get("top_n"):
        out = out.loc[out["size_rank"] <= float(cfg["top_n"])].copy()

    label_strategy = str(cfg.get("label_strategy", "provided_or_top_n")).lower()
    label_top_n = cfg.get("label_top_n", 8)
    if label_strategy == "none":
        out["label_flag"] = False
    elif label_strategy == "top_n":
        out["label_flag"] = out["size_rank"] <= float(label_top_n)
    elif label_strategy == "provided_or_top_n" and not out["label_flag"].any():
        out["label_flag"] = out["size_rank"] <= float(label_top_n)

    out.attrs["chart_config"] = cfg
    return out
