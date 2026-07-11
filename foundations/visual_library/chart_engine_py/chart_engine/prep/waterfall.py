from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_waterfall(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()

    out["component_value"] = pd.to_numeric(out["component_value"], errors="coerce")
    out = out[out["component_value"].notna()].copy()
    if "sort_order" in out.columns:
        out["sort_order"] = pd.to_numeric(out["sort_order"], errors="coerce")
        out = out.sort_values(["sort_order", "component_label"]).copy()
    else:
        out = out.reset_index(drop=True)
        out["sort_order"] = range(1, len(out) + 1)

    out["cumulative_end"] = out["component_value"].cumsum()
    out["cumulative_start"] = out["cumulative_end"].shift(fill_value=0) - out["component_value"]
    out["waterfall_position"] = range(1, len(out) + 1)
    out["direction"] = out["component_value"].apply(lambda x: "positive" if x >= 0 else "negative")
    return out
