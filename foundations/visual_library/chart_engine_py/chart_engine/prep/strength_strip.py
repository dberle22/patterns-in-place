from __future__ import annotations

import pandas as pd

from ..comparison_helpers import coerce_optional_bool, preferred_geo_sequence
from ..prep_helpers import coerce_numeric_column, ensure_single_geo_level, select_known_fields
from ..specs import ChartSpec


def prep_strength_strip(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    # Keep normalization and benchmark shaping centralized here so single-geo,
    # peers, and delta-vs-benchmark strip stories share the same prep output.
    cfg = spec.runtime_config or {}
    out = df.rename(columns=spec.column_mapping).copy()
    keep = list(dict.fromkeys(spec.required_fields + spec.optional_fields + ["benchmark_value", "benchmark_normalized_value", "metric_order"]))
    out = out[[column for column in keep if column in out.columns]].copy()
    ensure_single_geo_level(out, "strength_strip")
    out = coerce_numeric_column(out, "metric_value")
    out = coerce_numeric_column(out, "normalized_value")
    out = coerce_numeric_column(out, "benchmark_value")
    out = coerce_numeric_column(out, "benchmark_normalized_value")
    out = coerce_numeric_column(out, "metric_order")
    if "normalized_value" not in out.columns:
        out["normalized_value"] = float("nan")
    if "benchmark_value" not in out.columns:
        out["benchmark_value"] = float("nan")
    if "benchmark_normalized_value" not in out.columns:
        out["benchmark_normalized_value"] = float("nan")

    if cfg.get("time_window") is not None and "time_window" in out.columns:
        keep_windows = {str(value) for value in _as_list(cfg.get("time_window"))}
        out = out[out["time_window"].astype(str).isin(keep_windows)].copy()
    if cfg.get("metric_ids") is not None and "metric_id" in out.columns:
        keep_metrics = {str(value) for value in _as_list(cfg.get("metric_ids"))}
        out = out[out["metric_id"].astype(str).isin(keep_metrics)].copy()
    if out.empty:
        raise ValueError("No rows left after strength strip prep filtering; adjust request field_values.")

    out = coerce_optional_bool(out, "highlight_flag")
    if "benchmark_label" in out.columns:
        benchmark_label = out["benchmark_label"].astype("string")
        out["benchmark_flag"] = benchmark_label.notna() & benchmark_label.str.len().gt(0)
    else:
        out["benchmark_flag"] = False

    out["direction"] = out["direction"].fillna("higher_is_better").astype(str) if "direction" in out.columns else "higher_is_better"
    out["metric_group"] = out["metric_group"].fillna("Profile").astype(str) if "metric_group" in out.columns else "Profile"
    out["time_window"] = out["time_window"].astype(str)

    metric_sequence = _metric_sequence(out, cfg)
    geo_sequence = preferred_geo_sequence(
        out,
        requested_order=cfg.get("geo_order"),
        highlight_column="highlight_flag",
        benchmark_column="benchmark_flag",
    )

    out["geo_name"] = pd.Categorical(out["geo_name"].astype(str), categories=geo_sequence, ordered=True)
    out = _normalize_groups(out, normalize=bool(cfg.get("normalize", True)))
    out["metric_order"] = out["metric_id"].astype(str).map({metric_id: idx + 1 for idx, metric_id in enumerate(metric_sequence)})
    out["metric_display_label"] = out["metric_group"].astype(str) + ": " + out["metric_label"].astype(str)
    out["missing_flag"] = ~out["normalized_value"].notna()
    out["benchmark_delta"] = out["normalized_value"] - out["benchmark_normalized_value"]
    if not bool(cfg.get("keep_missing_metrics", True)):
        out = out[~out["missing_flag"]].copy()
    return out.sort_values(["time_window", "metric_order", "geo_name"]).copy()


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set, pd.Series, pd.Index)):
        return [item for item in value]
    return [value]


def _metric_sequence(df: pd.DataFrame, cfg: dict) -> list[str]:
    metric_ids = df["metric_id"].astype(str)
    if cfg.get("metric_order"):
        ordered = [str(value) for value in _as_list(cfg.get("metric_order"))]
        for metric_id in metric_ids:
            if metric_id not in ordered:
                ordered.append(metric_id)
        return ordered
    if "metric_order" in df.columns and df["metric_order"].notna().any():
        ranked = (
            df[["metric_id", "metric_order"]]
            .dropna()
            .drop_duplicates(subset=["metric_id"])
            .sort_values(["metric_order", "metric_id"])
        )
        ordered = ranked["metric_id"].astype(str).tolist()
        for metric_id in metric_ids:
            if metric_id not in ordered:
                ordered.append(metric_id)
        return ordered
    return list(dict.fromkeys(metric_ids.tolist()))


def _normalize_groups(df: pd.DataFrame, *, normalize: bool) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for _, group_df in df.groupby(["metric_id", "time_window"], sort=False):
        group = group_df.copy()
        higher_is_better = not group["direction"].astype(str).str.lower().isin({"lower_is_better", "lower-better", "lower"}).iloc[0]
        if normalize or group["normalized_value"].isna().all():
            group["normalized_value"] = _percentile_rank(group["metric_value"], higher_is_better=higher_is_better)
        elif not higher_is_better:
            group["normalized_value"] = 100 - group["normalized_value"]

        benchmark_values = group["benchmark_value"].dropna().unique().tolist() if "benchmark_value" in group.columns else []
        if benchmark_values:
            group["benchmark_normalized_value"] = _benchmark_percentile(
                group["metric_value"],
                float(benchmark_values[0]),
                higher_is_better=higher_is_better,
            )
        parts.append(group)
    return pd.concat(parts, ignore_index=True)


def _percentile_rank(values: pd.Series, *, higher_is_better: bool) -> pd.Series:
    valid = values.dropna()
    result = pd.Series([float("nan")] * len(values), index=values.index, dtype="float64")
    if valid.empty:
        return result
    ranks = valid.rank(method="average", pct=True) * 100.0
    if not higher_is_better:
        ranks = 100.0 - ranks
    result.loc[valid.index] = ranks
    return result


def _benchmark_percentile(values: pd.Series, benchmark_value: float, *, higher_is_better: bool):
    combined = pd.concat([values.dropna(), pd.Series([benchmark_value])], ignore_index=True)
    ranks = combined.rank(method="average", pct=True) * 100.0
    benchmark_rank = float(ranks.iloc[-1])
    return benchmark_rank if higher_is_better else 100.0 - benchmark_rank
