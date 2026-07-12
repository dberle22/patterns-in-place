from __future__ import annotations

import pandas as pd

from ..geo import quantile_class
from ..matrix_helpers import preserve_runtime_fields
from ..specs import ChartSpec


def prep_highlight_context_map(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    cfg = spec.runtime_config or {}
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()
    out = preserve_runtime_fields(df, out, ("question_id", "label_flag", "benchmark_value", "group"))

    if cfg.get("question_id") and "question_id" in out.columns:
        out = out.loc[out["question_id"] == cfg["question_id"]].copy()
    if cfg.get("time_window") and "time_window" in out.columns:
        out = out.loc[out["time_window"].astype(str) == str(cfg["time_window"])].copy()
    if cfg.get("geo_ids"):
        out = out.loc[out["geo_id"].astype(str).isin([str(value) for value in cfg["geo_ids"]])].copy()
    if cfg.get("group_values") and "group" in out.columns:
        out = out.loc[out["group"].astype(str).isin([str(value) for value in cfg["group_values"]])].copy()

    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool)
    if "neighbor_flag" in out.columns:
        out["neighbor_flag"] = out["neighbor_flag"].fillna(False).astype(bool)
    else:
        out["neighbor_flag"] = False
    if "label_flag" in out.columns:
        out["label_flag"] = out["label_flag"].fillna(False).astype(bool)
    else:
        out["label_flag"] = False
    if "metric_value" in out.columns:
        out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    if "benchmark_value" in out.columns:
        out["benchmark_value"] = pd.to_numeric(out["benchmark_value"], errors="coerce")
    out["time_window"] = out["time_window"].astype(str)
    variant = str(cfg.get("variant", "focus_only")).lower()
    value_field = str(cfg.get("value_field") or "metric_value")
    if value_field in out.columns:
        out["metric_value"] = pd.to_numeric(out[value_field], errors="coerce")
    out["map_variant"] = variant
    out["fill_value"] = out["metric_value"] if "metric_value" in out.columns else float("nan")
    if variant == "diverging" and "benchmark_value" in out.columns:
        out["fill_value"] = out["metric_value"] - out["benchmark_value"]
    if variant == "binned":
        out["bin"] = out["bin"].astype(str) if "bin" in out.columns and out["bin"].notna().any() else quantile_class(out["fill_value"], classes=int(cfg.get("bin_count", 5))).astype("string")
    else:
        out["bin"] = out["bin"].astype(str) if "bin" in out.columns and out["bin"].notna().any() else pd.Series([None] * len(out), index=out.index, dtype="object")
    if variant == "focus_only":
        out["focus_role"] = out.apply(
            lambda row: "Highlighted geography" if bool(row["highlight_flag"]) else ("Neighbor context" if bool(row["neighbor_flag"]) else "Background context"),
            axis=1,
        )
    else:
        out["outline_role"] = out.apply(
            lambda row: "Highlighted geography" if bool(row["highlight_flag"]) else ("Neighbor context" if bool(row["neighbor_flag"]) else None),
            axis=1,
        )
    if cfg.get("require_highlight", True) and not out["highlight_flag"].any():
        raise ValueError("highlight_context_map requires at least one highlighted geography.")
    if cfg.get("drop_missing_metric") and "metric_value" in out.columns:
        out = out.loc[out["metric_value"].notna()].copy()
    if out.empty:
        raise ValueError("highlight_context_map prep removed all rows; adjust the request filters.")
    out.attrs["chart_config"] = cfg
    return out
