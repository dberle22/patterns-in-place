from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_strength_strip(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()

    out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    if "normalized_value" in out.columns:
        out["normalized_value"] = pd.to_numeric(out["normalized_value"], errors="coerce")
    else:
        out["normalized_value"] = None

    for _, idx in out.groupby(["time_window", "metric_id"]).groups.items():
        group = out.loc[idx, "normalized_value"]
        if group.notna().any():
            continue
        values = out.loc[idx, "metric_value"]
        ranks = values.rank(method="average", pct=True) * 100
        out.loc[idx, "normalized_value"] = ranks

    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool) if "highlight_flag" in out.columns else False
    out["metric_display_label"] = (
        out["metric_group"].fillna("Profile") + ": " + out["metric_label"]
        if "metric_group" in out.columns
        else out["metric_label"].astype(str)
    )
    return out
