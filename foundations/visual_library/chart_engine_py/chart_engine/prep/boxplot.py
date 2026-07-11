from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_boxplot(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()

    out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    out = out[out["metric_value"].notna()].copy()
    out["box_group"] = out["group"].fillna("All observations") if "group" in out.columns else "All observations"
    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool) if "highlight_flag" in out.columns else False
    out["label_flag"] = out["label_flag"].fillna(False).astype(bool) if "label_flag" in out.columns else False
    return out
