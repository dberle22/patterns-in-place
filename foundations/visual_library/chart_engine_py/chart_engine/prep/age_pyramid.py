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
    # Preserve facet labels when callers want an overlaid benchmark instead of
    # the default one-panel-per-geo fallback.
    keep += [c for c in ("facet_label",) if c in out.columns and c not in keep]
    out = out[keep].copy()

    out["pop_value"] = pd.to_numeric(out["pop_value"], errors="coerce").fillna(0)
    if "pop_share" in out.columns:
        out["pop_share"] = pd.to_numeric(out["pop_share"], errors="coerce")

    if "pop_share" not in out.columns or out["pop_share"].isna().all():
        totals = out.groupby(["geo_id", "period"])["pop_value"].transform("sum")
        out["pop_share"] = out["pop_value"] / totals.where(totals != 0)

    out["sex"] = out["sex"].replace({"M": "Male", "F": "Female"})
    if "benchmark_label" not in out.columns:
        out["benchmark_label"] = pd.NA
    if "facet_label" not in out.columns:
        out["facet_label"] = out["geo_name"].astype(str)
    out["plot_value"] = out.apply(lambda row: -row["pop_share"] if str(row["sex"]).lower() == "male" else row["pop_share"], axis=1)
    out["plot_abs_value"] = out["pop_share"].abs()
    if "highlight_flag" in out.columns:
        out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool)
    else:
        out["highlight_flag"] = out["benchmark_label"].isna()
    out["comparison_role"] = out["highlight_flag"].map({True: "Selected geography", False: "Benchmark"})
    ordered_bins = sorted(out["age_bin"].astype(str).unique(), key=_age_sort_key)
    out["age_bin"] = pd.Categorical(out["age_bin"].astype(str), categories=ordered_bins, ordered=True)
    return out.sort_values(["facet_label", "period", "age_bin", "sex"]).copy()
