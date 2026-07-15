from __future__ import annotations

import pandas as pd


def unique_non_empty(series: pd.Series) -> list[str]:
    values = []
    for value in series.dropna().tolist():
        text = str(value).strip()
        if text and text not in values:
            values.append(text)
    return values


def coerce_optional_bool(df: pd.DataFrame, column: str, *, default: bool = False) -> pd.DataFrame:
    if column in df.columns:
        df[column] = df[column].fillna(default).astype(bool)
    else:
        df[column] = default
    return df


def preferred_geo_sequence(
    df: pd.DataFrame,
    *,
    requested_order=None,
    highlight_column: str = "highlight_flag",
    benchmark_column: str | None = None,
) -> list[str]:
    if requested_order:
        ordered = [str(value) for value in requested_order]
    else:
        ordered = []
    if highlight_column in df.columns:
        for value in df.loc[df[highlight_column].astype(bool), "geo_name"].dropna():
            text = str(value)
            if text not in ordered:
                ordered.append(text)
    if benchmark_column and benchmark_column in df.columns:
        for value in df.loc[df[benchmark_column].astype(bool), "geo_name"].dropna():
            text = str(value)
            if text not in ordered:
                ordered.append(text)
    for value in sorted(unique_non_empty(df["geo_name"])):
        if value not in ordered:
            ordered.append(value)
    return ordered
