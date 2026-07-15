from __future__ import annotations

import pandas as pd

from ..geo import quantile_class
from ..matrix_helpers import preserve_runtime_fields
from ..specs import ChartSpec


def prep_choropleth(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    cfg = spec.runtime_config or {}
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()
    out = preserve_runtime_fields(df, out, ("question_id", "label_flag"))

    if cfg.get("question_id") and "question_id" in out.columns:
        out = out.loc[out["question_id"] == cfg["question_id"]].copy()
    if cfg.get("time_window") and "time_window" in out.columns:
        out = out.loc[out["time_window"].astype(str) == str(cfg["time_window"])].copy()
    if cfg.get("geo_ids"):
        out = out.loc[out["geo_id"].astype(str).isin([str(value) for value in cfg["geo_ids"]])].copy()
    if cfg.get("group_values") and "group" in out.columns:
        out = out.loc[out["group"].astype(str).isin([str(value) for value in cfg["group_values"]])].copy()
    if cfg.get("metric_id") and "metric_id" in out.columns:
        out = out.loc[out["metric_id"].astype(str) == str(cfg["metric_id"])].copy()

    value_field = str(cfg.get("value_field") or "metric_value")
    if value_field in out.columns:
        out["metric_value"] = pd.to_numeric(out[value_field], errors="coerce")
    else:
        out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    if "benchmark_value" in out.columns:
        out["benchmark_value"] = pd.to_numeric(out["benchmark_value"], errors="coerce")
    out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    out["time_window"] = out["time_window"].astype(str)
    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool) if "highlight_flag" in out.columns else False
    out["label_flag"] = out["label_flag"].fillna(False).astype(bool) if "label_flag" in out.columns else False
    out["missing_geometry"] = ~out.get("geometry", pd.Series(index=out.index, dtype=object)).notna() if "geometry" in out.columns else True
    variant = str(cfg.get("variant", "continuous")).lower()
    out["map_variant"] = variant
    out["fill_value"] = out["metric_value"]
    if variant == "diverging" and "benchmark_value" in out.columns:
        out["fill_value"] = out["metric_value"] - out["benchmark_value"]
    if cfg.get("drop_missing_metric"):
        out = out.loc[out["metric_value"].notna()].copy()
    if out.empty:
        raise ValueError("choropleth prep removed all rows; adjust the request filters.")

    if "bin" in out.columns and out["bin"].notna().any():
        out["bin"] = out["bin"].astype(str)
    elif variant == "binned":
        classes = int(cfg.get("bin_count", 5))
        ranked = quantile_class(out["fill_value"], classes=classes)
        out["bin"] = ranked.astype("string")
    else:
        out["bin"] = out["bin"].astype(str) if "bin" in out.columns else pd.Series([None] * len(out), index=out.index, dtype="object")
    out.attrs["chart_config"] = cfg
    return out
