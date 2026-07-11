from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_choropleth(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()

    out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    out["time_window"] = out["time_window"].astype(str)
    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool) if "highlight_flag" in out.columns else False
    out["missing_geometry"] = ~out.get("geometry", pd.Series(index=out.index, dtype=object)).notna() if "geometry" in out.columns else True
    if "bin" in out.columns:
        out["bin"] = out["bin"].astype(str)
    return out
