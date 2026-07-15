from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_bar_chart(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    # Keep the full row context after canonical renaming so the renderer can use
    # benchmark values, notes, time windows, and labels that already exist in
    # the manual CE result sets.
    out = df.rename(columns=spec.column_mapping).copy()

    if "value" in out.columns:
        out["value"] = pd.to_numeric(out["value"], errors="coerce")
        out = out.loc[out["value"].notna()].copy()
        out = out.sort_values("value", ascending=False, kind="mergesort")

    if "rank" in out.columns:
        numeric_rank = pd.to_numeric(out["rank"], errors="coerce")
        fallback_order = pd.Series(range(1, len(out) + 1), index=out.index, dtype="float64")
        out["display_order"] = numeric_rank.where(numeric_rank.notna(), fallback_order)
    else:
        out["display_order"] = range(1, len(out) + 1)

    if "entity" in out.columns and "entity_label" not in out.columns:
        out["entity_label"] = out["entity"].astype(str)

    if "subtitle" not in out.columns:
        subtitle_parts: list[str] = []
        if "time_window" in out.columns:
            time_values = [str(v).strip() for v in out["time_window"].dropna().unique() if str(v).strip()]
            if time_values:
                subtitle_parts.append(time_values[0])
        if "group" in out.columns:
            group_values = [str(v).strip() for v in out["group"].dropna().unique() if str(v).strip()]
            if len(group_values) == 1:
                subtitle_parts.append(group_values[0])
        if subtitle_parts:
            out["subtitle"] = " | ".join(subtitle_parts)

    preferred = []
    for column in spec.required_fields + spec.optional_fields:
        if column in out.columns and column not in preferred:
            preferred.append(column)
    for column in ["display_order", "entity_label", "subtitle"]:
        if column in out.columns and column not in preferred:
            preferred.append(column)
    remaining = [column for column in out.columns if column not in preferred]
    return out[preferred + remaining]
