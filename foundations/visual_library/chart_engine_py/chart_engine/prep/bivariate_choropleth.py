from __future__ import annotations

import pandas as pd

from ..geo import quantile_class
from ..matrix_helpers import ordered_unique, preserve_runtime_fields
from ..specs import ChartSpec


def prep_bivariate_choropleth(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    cfg = spec.runtime_config or {}
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()
    out = preserve_runtime_fields(df, out, ("question_id",))

    if cfg.get("question_id") and "question_id" in out.columns:
        out = out.loc[out["question_id"] == cfg["question_id"]].copy()
    if cfg.get("time_window") and "time_window" in out.columns:
        out = out.loc[out["time_window"].astype(str) == str(cfg["time_window"])].copy()
    if cfg.get("geo_ids"):
        out = out.loc[out["geo_id"].astype(str).isin([str(value) for value in cfg["geo_ids"]])].copy()
    if cfg.get("group_values") and "group" in out.columns:
        out = out.loc[out["group"].astype(str).isin([str(value) for value in cfg["group_values"]])].copy()

    out["x_value"] = pd.to_numeric(out["x_value"], errors="coerce")
    out["y_value"] = pd.to_numeric(out["y_value"], errors="coerce")
    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool) if "highlight_flag" in out.columns else False
    if cfg.get("drop_missing_values"):
        out = out.loc[out["x_value"].notna() & out["y_value"].notna()].copy()
    if out.empty:
        raise ValueError("bivariate_choropleth prep removed all rows; adjust the request filters.")

    class_count = int(cfg.get("n_bins", 3))
    overwrite_bins = bool(cfg.get("overwrite_bins"))
    bin_by = [str(value) for value in cfg.get("bin_by", [])] if cfg.get("bin_by") else []
    bin_groups = ordered_unique(out[bin_by[0]]) if len(bin_by) == 1 and bin_by[0] in out.columns else [None]

    x_bin_series = pd.Series([pd.NA] * len(out), index=out.index, dtype="object")
    y_bin_series = pd.Series([pd.NA] * len(out), index=out.index, dtype="object")

    for group_value in bin_groups:
        if group_value is None:
            subset_index = out.index
        else:
            subset_index = out.index[out[bin_by[0]].astype(str) == str(group_value)]
        subset = out.loc[subset_index]
        if "x_bin" in subset.columns and subset["x_bin"].notna().any() and not overwrite_bins:
            x_bin_series.loc[subset_index] = pd.to_numeric(subset["x_bin"], errors="coerce").astype("Int64").astype("string")
        else:
            x_bin_series.loc[subset_index] = quantile_class(subset["x_value"], classes=class_count).astype("string")
        if "y_bin" in subset.columns and subset["y_bin"].notna().any() and not overwrite_bins:
            y_bin_series.loc[subset_index] = pd.to_numeric(subset["y_bin"], errors="coerce").astype("Int64").astype("string")
        else:
            y_bin_series.loc[subset_index] = quantile_class(subset["y_value"], classes=class_count).astype("string")

    out["x_bin"] = x_bin_series
    out["y_bin"] = y_bin_series

    if "bivar_class" not in out.columns or out["bivar_class"].isna().all():
        out["bivar_class"] = out.apply(
            lambda row: None
            if pd.isna(row["x_bin"]) or pd.isna(row["y_bin"])
            else f"{int(row['x_bin'])}-{int(row['y_bin'])}",
            axis=1,
        )
    out["bin_method"] = str(cfg.get("bin_method", "quantile")).lower()
    out["bin_count"] = class_count
    out.attrs["chart_config"] = cfg
    return out
