from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_highlight_context_map(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()

    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool)
    if "neighbor_flag" in out.columns:
        out["neighbor_flag"] = out["neighbor_flag"].fillna(False).astype(bool)
    if "metric_value" in out.columns:
        out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    out["time_window"] = out["time_window"].astype(str)
    return out
