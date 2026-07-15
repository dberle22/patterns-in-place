from __future__ import annotations

import pandas as pd

from ..prep_helpers import coerce_bool_column, coerce_numeric_column, ensure_single_geo_level, select_known_fields
from ..specs import ChartSpec


def prep_slopegraph(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    # Keep slopegraph prep request-driven so the same shared function can power
    # value, indexed, rank, and curated-entity variants without caller-side hacks.
    cfg = spec.runtime_config or {}
    out = select_known_fields(df, spec)
    ensure_single_geo_level(out, "slopegraph")
    out = coerce_numeric_column(out, "metric_value")
    if "rank" in out.columns:
        out = coerce_numeric_column(out, "rank")
    out = coerce_bool_column(out, "highlight_flag")

    if cfg.get("metric_id") is not None and "metric_id" in out.columns:
        out = out[out["metric_id"] == cfg["metric_id"]].copy()
    if cfg.get("geo_ids") and "geo_id" in out.columns:
        out = out[out["geo_id"].astype(str).isin({str(value) for value in _as_list(cfg.get("geo_ids"))})].copy()

    if "benchmark_label" in out.columns:
        benchmark_label = out["benchmark_label"].astype("string")
        out["benchmark_flag"] = benchmark_label.notna() & benchmark_label.str.len().gt(0)
    else:
        out["benchmark_flag"] = False

    out = out[out["metric_value"].notna()].copy()
    selected_periods = _resolve_periods(out, cfg)
    out = out[out["period"].astype(str).isin(selected_periods)].copy()
    if out.empty:
        raise ValueError("No rows left after slopegraph prep filtering; adjust request field_values.")

    out["period"] = out["period"].astype(str)
    out["period_role"] = out["period"].map({selected_periods[0]: "start", selected_periods[1]: "end"})
    out["period_label"] = out["period"]
    out["period_sort"] = out["period"].map({selected_periods[0]: 1, selected_periods[1]: 2})
    out["_entity_period_key"] = out["geo_id"].astype(str) + "::" + out["period"]
    if out["_entity_period_key"].duplicated().any():
        raise ValueError("Slopegraph prep expects one row per geo_id and period after filtering.")

    out = out.merge(_build_endpoint_frame(out), on="geo_id", how="left")
    if bool(cfg.get("drop_incomplete", True)):
        out = out[out["complete_endpoint_flag"]].copy()
    if out.empty:
        raise ValueError("No complete two-period entities remain for slopegraph rendering.")

    variant = str(cfg.get("variant", "value")).strip().lower() or "value"
    out["variant"] = variant
    out["plot_value"] = out["metric_value"]
    if variant == "indexed":
        out["plot_value"] = (out["metric_value"] / out["start_value"]) * 100.0
        out.loc[~(out["start_value"].notna() & out["start_value"].ne(0)), "plot_value"] = pd.NA
        out["index_base_period"] = str(cfg.get("base_period", selected_periods[0]))
    elif variant == "rank":
        if "rank" not in out.columns or out["rank"].isna().all():
            out = _compute_rank_variant(out, rank_higher_is_better=bool(cfg.get("rank_higher_is_better", True)))
        out["plot_value"] = out["rank"]

    out = _apply_entity_selection(out, cfg)
    out = out.sort_values(["display_order", "period_sort", "period_label", "geo_name"]).copy()
    return out.drop(columns=["_entity_period_key", "period_sort"])


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set, pd.Series, pd.Index)):
        return [item for item in value]
    return [value]


def _resolve_periods(df: pd.DataFrame, cfg: dict) -> list[str]:
    periods = [str(value) for value in _as_list(cfg.get("periods")) if value is not None]
    if not periods:
        periods = [str(value) for value in [cfg.get("start_period"), cfg.get("end_period")] if value is not None]
    if not periods:
        period_series = df["period"].dropna().astype(str)
        period_numeric = pd.to_numeric(period_series, errors="coerce")
        if not period_series.empty and period_numeric.notna().all():
            period_frame = pd.DataFrame({"period": period_series, "period_numeric": period_numeric}).drop_duplicates("period")
            period_frame = period_frame.sort_values(["period_numeric", "period"])
            periods = period_frame["period"].tolist()
        else:
            periods = sorted(period_series.unique().tolist())
        if len(periods) >= 2:
            periods = [periods[0], periods[-1]]
    if len(periods) != 2:
        raise ValueError("Slopegraph requires exactly two periods.")
    return periods


def _build_endpoint_frame(df: pd.DataFrame) -> pd.DataFrame:
    endpoints = (
        df.pivot_table(index="geo_id", columns="period_role", values="metric_value", aggfunc="first")
        .rename(columns={"start": "start_value", "end": "end_value"})
        .reset_index()
    )
    endpoints["delta_value"] = endpoints["end_value"] - endpoints["start_value"]
    endpoints["pct_change"] = endpoints["delta_value"] / endpoints["start_value"]
    endpoints.loc[~(endpoints["start_value"].notna() & endpoints["start_value"].ne(0)), "pct_change"] = pd.NA
    endpoints["complete_endpoint_flag"] = endpoints["start_value"].notna() & endpoints["end_value"].notna()
    return endpoints


def _compute_rank_variant(df: pd.DataFrame, rank_higher_is_better: bool) -> pd.DataFrame:
    ranked_parts: list[pd.DataFrame] = []
    for _, period_df in df.groupby("period", sort=False):
        ranked = period_df.copy()
        ranked["rank"] = ranked["metric_value"].rank(method="first", ascending=not rank_higher_is_better)
        ranked_parts.append(ranked)
    return pd.concat(ranked_parts, ignore_index=True)


def _apply_entity_selection(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    end_rows = df[df["period_role"] == "end"].copy()
    end_rows["sort_value"] = _sort_values(end_rows, str(cfg.get("order_by", "end_value")))
    sort_desc = bool(cfg.get("sort_desc", True))
    end_rows = end_rows.sort_values(["sort_value", "geo_name"], ascending=[not sort_desc, True], na_position="last")

    top_n = cfg.get("top_n")
    if top_n is not None:
        trimmed = end_rows.head(int(top_n)).copy()
        include_geo_ids = {str(value) for value in _as_list(cfg.get("include_geo_ids"))}
        if include_geo_ids:
            trimmed = pd.concat(
                [trimmed, end_rows[end_rows["geo_id"].astype(str).isin(include_geo_ids)]],
                ignore_index=True,
            )
        if bool(cfg.get("include_highlighted", True)):
            trimmed = pd.concat([trimmed, end_rows[end_rows["highlight_flag"]]], ignore_index=True)
        end_rows = trimmed.drop_duplicates(subset=["geo_id"]).sort_values(
            ["sort_value", "geo_name"],
            ascending=[not sort_desc, True],
            na_position="last",
        )

    display_lookup = end_rows[["geo_id"]].drop_duplicates().reset_index(drop=True)
    display_lookup["display_order"] = display_lookup.index + 1
    return df[df["geo_id"].isin(display_lookup["geo_id"])].merge(display_lookup, on="geo_id", how="left")


def _sort_values(df: pd.DataFrame, order_by: str) -> pd.Series:
    if order_by == "start_value":
        return df["start_value"]
    if order_by == "delta_value":
        return df["delta_value"]
    if order_by == "abs_delta":
        return df["delta_value"].abs()
    if order_by == "pct_change":
        return df["pct_change"]
    if order_by == "abs_pct_change":
        return df["pct_change"].abs()
    if order_by == "rank" and "rank" in df.columns:
        return df["rank"]
    if order_by == "geo_name":
        return df["geo_name"].astype(str)
    return df["end_value"]
