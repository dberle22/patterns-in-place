from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_heatmap_table(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()

    out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    if "normalized_value" in out.columns:
        out["normalized_value"] = pd.to_numeric(out["normalized_value"], errors="coerce")

    metric_n = out["metric_id"].nunique(dropna=True)
    period_n = out["period"].nunique(dropna=True) if "period" in out.columns else 0
    if metric_n == 1 and period_n > 1:
        out["column_label"] = out["period"].astype(str)
    else:
        out["column_label"] = out["metric_label"].astype(str)
    out["row_label"] = out["geo_name"].astype(str)
    out["fill_value"] = out["normalized_value"] if "normalized_value" in out.columns and out["normalized_value"].notna().any() else out["metric_value"]
    out["cell_label"] = out["metric_value"].round(1).astype(str)
    out["missing_flag"] = out["fill_value"].isna()
    return out
