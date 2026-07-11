from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_bump_chart(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()

    out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    out = out[out["metric_value"].notna()].copy()
    if "rank" not in out.columns or out["rank"].isna().all():
        out["rank"] = out.groupby("period")["metric_value"].rank(method="first", ascending=False)
    else:
        out["rank"] = pd.to_numeric(out["rank"], errors="coerce")
    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool) if "highlight_flag" in out.columns else False
    out = out.sort_values(["geo_name", "period"]).copy()
    return out
