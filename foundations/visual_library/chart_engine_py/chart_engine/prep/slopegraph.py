from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_slopegraph(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()

    out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    if "rank" in out.columns:
        out["rank"] = pd.to_numeric(out["rank"], errors="coerce")
    if "highlight_flag" in out.columns:
        out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool)
    else:
        out["highlight_flag"] = False
    if "benchmark_label" in out.columns:
        out["benchmark_flag"] = out["benchmark_label"].notna() & out["benchmark_label"].astype(str).str.len().gt(0)
    else:
        out["benchmark_flag"] = False

    out = out[out["metric_value"].notna()].copy()
    periods = sorted(out["period"].dropna().unique())
    if len(periods) >= 2:
        selected = [periods[0], periods[-1]]
        out = out[out["period"].isin(selected)].copy()
    out["period_label"] = out["period"].astype(str)
    out["plot_value"] = out["metric_value"]
    return out
