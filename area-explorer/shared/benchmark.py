"""Benchmark formatting helpers for Area Explorer."""

from __future__ import annotations

import pandas as pd


def add_benchmark_ranks(
    df: pd.DataFrame,
    metric_col: str,
    division_col: str,
) -> pd.DataFrame:
    """Add national and division percentile ranks to a metric frame.

    This mirrors the ranking logic the app uses in SQL, but keeping a pandas
    version makes it easier to smoke-test the benchmark contract locally and
    gives us a fallback path for small in-memory data transforms.
    """
    def _percent_rank(series: pd.Series) -> pd.Series:
        valid = series.notna()
        if valid.sum() <= 1:
            return pd.Series([0.0 if is_valid else pd.NA for is_valid in valid], index=series.index, dtype="float64")

        ranks = series.rank(method="min")
        return ((ranks - 1) / (valid.sum() - 1) * 100).where(valid)

    ranked = df.copy()
    ranked["national_pct_rank"] = _percent_rank(ranked[metric_col])
    ranked["division_pct_rank"] = ranked.groupby(division_col, dropna=False)[metric_col].transform(_percent_rank)
    return ranked


def format_metric_value(value: float | int | None, unit_format: str | None) -> str:
    """Format a metric value using the semantic-layer unit contract."""
    if value is None:
        return "NA"

    if unit_format == "currency":
        return f"${value:,.0f}"
    if unit_format == "integer":
        return f"{value:,.0f}"
    if unit_format == "percent":
        return f"{value * 100:.1f}%"
    if unit_format == "ratio":
        return f"{value:.2f}"
    if unit_format == "index":
        return f"{value:.2f}"
    if unit_format == "number_1dp":
        return f"{value:.1f}"
    return f"{value:,.2f}"


def format_percentile(value: float | int | None) -> str:
    """Format a percentile rank for display."""
    if value is None:
        return "NA"
    rounded = int(round(float(value)))
    if 10 <= rounded % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(rounded % 10, "th")
    return f"{rounded}{suffix} percentile"
