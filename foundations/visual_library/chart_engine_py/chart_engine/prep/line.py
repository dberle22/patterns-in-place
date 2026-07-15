from __future__ import annotations

import pandas as pd

from ..prep_helpers import coerce_bool_column, coerce_numeric_column, select_known_fields
from ..specs import ChartSpec


def prep_line_chart(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = select_known_fields(df, spec)
    out = coerce_numeric_column(out, "value")
    out = out[out["value"].notna()].copy()

    out = coerce_numeric_column(out, "benchmark_value")
    out = coerce_bool_column(out, "highlight_flag")
    if "note" in out.columns:
        out["note"] = out["note"].astype(str)

    out["_period_numeric"] = pd.to_numeric(out["period"], errors="coerce") if "period" in out.columns else pd.Series(dtype=float)

    if {"series", "period"}.issubset(out.columns) and out.duplicated(["series", "period"]).any():
        raise ValueError("line_chart prep expects one row per series and period after column mapping.")

    out["variant"] = _infer_variant(out)
    out = _complete_series_periods(out)
    out["plot_value"] = out["value"]

    if out["variant"].eq("indexed").any():
        out = _apply_indexed_values(out)
    elif out["variant"].str.startswith("rolling_").any():
        out = _apply_rolling_values(out)

    out = out.sort_values(["series", "_period_numeric", "period"], kind="stable").reset_index(drop=True)
    return out.drop(columns=["_period_numeric"], errors="ignore")


def _infer_variant(df: pd.DataFrame) -> pd.Series:
    if "time_window" not in df.columns:
        return pd.Series(["single"] * len(df.index), index=df.index)
    variant = df["time_window"].fillna("single").astype(str).str.strip().str.lower()
    return variant.replace({"level": "single", "multi": "multi", "": "single"})


def _complete_series_periods(df: pd.DataFrame) -> pd.DataFrame:
    if "_period_numeric" not in df.columns or df["_period_numeric"].dropna().empty or "series" not in df.columns:
        return df

    numeric_periods = df["_period_numeric"].dropna()
    if not (numeric_periods.mod(1) == 0).all():
        return df

    full_periods = list(range(int(numeric_periods.min()), int(numeric_periods.max()) + 1))
    parts: list[pd.DataFrame] = []
    for _, part in df.groupby("series", sort=False):
        template = part.iloc[0].to_dict()
        expanded = pd.DataFrame({"_period_numeric": full_periods})
        expanded = expanded.merge(part, on="_period_numeric", how="left", sort=True)
        expanded["period"] = expanded["period"].fillna(expanded["_period_numeric"].astype(int).astype(str))
        for column, value in template.items():
            if column in {"period", "_period_numeric", "value", "benchmark_value", "plot_value"}:
                continue
            if column not in expanded.columns:
                expanded[column] = value
            else:
                expanded[column] = expanded[column].where(expanded[column].notna(), value)
        parts.append(expanded)
    return pd.concat(parts, ignore_index=True)


def _apply_indexed_values(df: pd.DataFrame) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for _, part in df.groupby("series", sort=False):
        base_period = None
        if "index_base_period" in part.columns and part["index_base_period"].notna().any():
            base_series = pd.to_numeric(part["index_base_period"], errors="coerce").dropna()
            if not base_series.empty:
                base_period = int(base_series.iloc[0])
        if base_period is None:
            base_period = int(part["_period_numeric"].dropna().min()) if part["_period_numeric"].notna().any() else None

        indexed = part.copy()
        base_rows = indexed[indexed["_period_numeric"] == base_period] if base_period is not None else indexed.iloc[0:0]
        base_values = pd.to_numeric(base_rows["value"], errors="coerce").dropna()
        if base_values.empty or base_values.iloc[0] == 0:
            indexed["plot_value"] = pd.NA
        else:
            indexed["plot_value"] = (indexed["value"] / float(base_values.iloc[0])) * 100
            indexed["index_base_period"] = base_period
        parts.append(indexed)
    return pd.concat(parts, ignore_index=True)


def _apply_rolling_values(df: pd.DataFrame) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for _, part in df.groupby("series", sort=False):
        rolling = part.copy()
        variant = str(rolling["variant"].dropna().iloc[0]) if rolling["variant"].dropna().any() else "rolling_3"
        window_token = variant.replace("rolling_", "").replace("yr", "")
        try:
            window = max(int(window_token), 2)
        except ValueError:
            window = 3
        rolling["plot_value"] = rolling["value"].rolling(window=window, min_periods=window).mean()
        parts.append(rolling)
    return pd.concat(parts, ignore_index=True)
