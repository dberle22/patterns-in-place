from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_hexbin(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()

    out["x_value"] = pd.to_numeric(out["x_value"], errors="coerce")
    out["y_value"] = pd.to_numeric(out["y_value"], errors="coerce")
    if "weight_value" in out.columns:
        out["weight_value"] = pd.to_numeric(out["weight_value"], errors="coerce")
    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool) if "highlight_flag" in out.columns else False
    out = out[out["x_value"].notna() & out["y_value"].notna()].copy()
    return out
