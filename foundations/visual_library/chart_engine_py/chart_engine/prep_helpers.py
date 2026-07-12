from __future__ import annotations

import pandas as pd

from .specs import ChartSpec


def select_known_fields(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    """
    Apply chart column mapping and keep only the documented contract fields.

    This keeps prep functions focused on chart semantics instead of repeatedly
    reimplementing the same rename-and-prune boilerplate.
    """
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [column for column in spec.required_fields + spec.optional_fields if column in out.columns]
    return out[keep].copy()


def coerce_numeric_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def coerce_bool_column(df: pd.DataFrame, column: str, *, default: bool = False) -> pd.DataFrame:
    if column in df.columns:
        df[column] = df[column].fillna(default).astype(bool)
    else:
        df[column] = default
    return df


def ensure_single_geo_level(df: pd.DataFrame, chart_type: str) -> None:
    if "geo_level" not in df.columns:
        return
    geo_levels = [str(value).strip() for value in df["geo_level"].dropna().unique() if str(value).strip()]
    if len(geo_levels) > 1:
        raise ValueError(f"{chart_type} input contains multiple geo_levels; filter to one level per chart.")
