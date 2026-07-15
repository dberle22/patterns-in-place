"""
Prep scatter chart data for rendering.

This stays intentionally narrow: column mapping, numeric coercion, and the
small amount of filtering needed so the renderer receives a usable frame.
More opinionated analytical shaping belongs upstream of the chart engine.
"""

from __future__ import annotations

import pandas as pd

from ..prep_helpers import coerce_bool_column, coerce_numeric_column, ensure_single_geo_level, select_known_fields
from ..specs import ChartSpec


def prep_scatter(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = select_known_fields(df, spec)
    ensure_single_geo_level(out, "scatter")

    for column in ("x_value", "y_value", "size_value"):
        out = coerce_numeric_column(out, column)

    # Scatter charts are unusable without valid coordinates, so rows missing
    # x or y are dropped during prep rather than rendered as silent gaps.
    if {"x_value", "y_value"}.issubset(out.columns):
        out = out[out["x_value"].notna() & out["y_value"].notna()].copy()

    out = coerce_bool_column(out, "label_flag")

    return out
