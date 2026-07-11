"""
Prep scatter chart data for rendering.

This stays intentionally narrow: column mapping, numeric coercion, and the
small amount of filtering needed so the renderer receives a usable frame.
More opinionated analytical shaping belongs upstream of the chart engine.
"""

from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_scatter(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()

    # Keep only the fields the chart contract knows about so renderers don't
    # accidentally start depending on ad hoc upstream columns.
    keep = [column for column in spec.required_fields + spec.optional_fields if column in out.columns]
    out = out[keep].copy()

    for column in ("x_value", "y_value", "size_value"):
        if column in out.columns:
            out[column] = pd.to_numeric(out[column], errors="coerce")

    # Scatter charts are unusable without valid coordinates, so rows missing
    # x or y are dropped during prep rather than rendered as silent gaps.
    if {"x_value", "y_value"}.issubset(out.columns):
        out = out[out["x_value"].notna() & out["y_value"].notna()].copy()

    if "label_flag" in out.columns:
        out["label_flag"] = out["label_flag"].fillna(False).astype(bool)

    return out
