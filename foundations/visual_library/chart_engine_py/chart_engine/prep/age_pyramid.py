from __future__ import annotations

import re

import pandas as pd

from ..specs import ChartSpec


def _age_sort_key(label: str) -> int:
    match = re.search(r"(\d+)", str(label))
    return int(match.group(1)) if match else 0


def prep_age_pyramid(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()

    out["pop_value"] = pd.to_numeric(out["pop_value"], errors="coerce").fillna(0)
    if "pop_share" in out.columns:
        out["pop_share"] = pd.to_numeric(out["pop_share"], errors="coerce")

    if "pop_share" not in out.columns or out["pop_share"].isna().all():
        totals = out.groupby(["geo_id", "period"])["pop_value"].transform("sum")
        out["pop_share"] = out["pop_value"] / totals.where(totals != 0)

    out["sex"] = out["sex"].replace({"M": "Male", "F": "Female"})
    out["plot_value"] = out.apply(lambda row: -row["pop_share"] if str(row["sex"]).lower() == "male" else row["pop_share"], axis=1)
    out["plot_abs_value"] = out["pop_share"].abs()
    out["highlight_flag"] = out["highlight_flag"].fillna(True).astype(bool) if "highlight_flag" in out.columns else True
    ordered_bins = sorted(out["age_bin"].astype(str).unique(), key=_age_sort_key)
    out["age_bin"] = pd.Categorical(out["age_bin"].astype(str), categories=ordered_bins, ordered=True)
    return out.sort_values(["age_bin", "sex"]).copy()
