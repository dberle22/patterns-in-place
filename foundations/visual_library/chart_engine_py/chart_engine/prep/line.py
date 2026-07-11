from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_line_chart(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping)
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()
    if "period" in out.columns:
        out = out.sort_values("period")
    return out
