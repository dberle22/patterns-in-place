from __future__ import annotations

import pandas as pd

from ..geo import quantile_class
from ..specs import ChartSpec


def prep_bivariate_choropleth(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()

    out["x_value"] = pd.to_numeric(out["x_value"], errors="coerce")
    out["y_value"] = pd.to_numeric(out["y_value"], errors="coerce")
    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool) if "highlight_flag" in out.columns else False
    out = out[out["x_value"].notna() & out["y_value"].notna()].copy()

    if "x_bin" in out.columns:
        out["x_bin"] = pd.to_numeric(out["x_bin"], errors="coerce").astype("Int64")
    else:
        out["x_bin"] = quantile_class(out["x_value"], classes=3)

    if "y_bin" in out.columns:
        out["y_bin"] = pd.to_numeric(out["y_bin"], errors="coerce").astype("Int64")
    else:
        out["y_bin"] = quantile_class(out["y_value"], classes=3)

    if "bivar_class" not in out.columns or out["bivar_class"].isna().all():
        out["bivar_class"] = out.apply(
            lambda row: None
            if pd.isna(row["x_bin"]) or pd.isna(row["y_bin"])
            else f"{int(row['x_bin'])}-{int(row['y_bin'])}",
            axis=1,
        )
    return out
