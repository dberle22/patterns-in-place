from __future__ import annotations

import pandas as pd

from ..comparison_helpers import coerce_optional_bool
from ..prep_helpers import coerce_numeric_column, ensure_single_geo_level, select_known_fields
from ..specs import ChartSpec


def prep_bump_chart(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    # Keep entity selection request-driven so fixed top-N, peer-set, and
    # rolling-top-N bump stories can share the same prep path.
    cfg = spec.runtime_config or {}
    out = select_known_fields(df, spec)
    ensure_single_geo_level(out, "bump_chart")
    out = coerce_numeric_column(out, "metric_value")
    out = out[out["metric_value"].notna()].copy()

    if cfg.get("metric_id") is not None and "metric_id" in out.columns:
        out = out[out["metric_id"] == cfg["metric_id"]].copy()
    if cfg.get("geo_ids") and "geo_id" in out.columns:
        keep_geo_ids = {str(value) for value in _as_list(cfg.get("geo_ids"))}
        out = out[out["geo_id"].astype(str).isin(keep_geo_ids)].copy()
    if cfg.get("periods"):
        keep_periods = {str(value) for value in _as_list(cfg.get("periods"))}
        out = out[out["period"].astype(str).isin(keep_periods)].copy()
    if cfg.get("period_min") is not None:
        out = out[pd.to_numeric(out["period"], errors="coerce") >= float(cfg["period_min"])].copy()
    if cfg.get("period_max") is not None:
        out = out[pd.to_numeric(out["period"], errors="coerce") <= float(cfg["period_max"])].copy()
    if out.empty:
        raise ValueError("No rows left after bump chart prep filtering; adjust request field_values.")

    out = coerce_optional_bool(out, "highlight_flag")
    out = coerce_optional_bool(out, "peer_flag")
    if "rank" in out.columns:
        out = coerce_numeric_column(out, "rank")

    out["period"] = out["period"].astype(str)
    key = out["geo_id"].astype(str) + "::" + out["metric_id"].astype(str) + "::" + out["period"]
    if key.duplicated().any():
        raise ValueError("Bump chart prep expects one row per geo_id, metric_id, and period after filtering.")

    if "rank" not in out.columns or out["rank"].isna().all() or not bool(cfg.get("use_precomputed_rank", True)):
        out = _compute_period_ranks(
            out,
            higher_is_better=_resolve_higher_is_better(cfg),
        )
        out["rank_source"] = "derived"
    else:
        out["rank_source"] = "precomputed"

    if bool(cfg.get("drop_missing_rank", True)):
        out = out[out["rank"].notna()].copy()
    if out.empty:
        raise ValueError("No finite ranks remain for bump chart rendering.")

    out["rank_method"] = "precomputed" if out["rank_source"].eq("precomputed").all() else str(cfg.get("rank_method", "row_number"))
    out["rank_higher_is_better"] = _resolve_higher_is_better(cfg)
    out = _select_entities(out, cfg)
    out = _add_endpoint_fields(out)
    out = out.sort_values(["rank", "geo_name", "period"]).copy()
    return out


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set, pd.Series, pd.Index)):
        return [item for item in value]
    return [value]


def _resolve_higher_is_better(cfg: dict) -> bool:
    direction = str(cfg.get("direction", "") or "").strip().lower()
    if direction in {"lower_is_better", "lower-better", "lower"}:
        return False
    return bool(cfg.get("metric_higher_is_better", True))


def _compute_period_ranks(df: pd.DataFrame, *, higher_is_better: bool) -> pd.DataFrame:
    ranked_parts: list[pd.DataFrame] = []
    for _, period_df in df.groupby("period", sort=False):
        ranked = period_df.copy()
        ranked["rank"] = ranked["metric_value"].rank(
            method="first",
            ascending=not higher_is_better,
        )
        ranked_parts.append(ranked)
    return pd.concat(ranked_parts, ignore_index=True)


def _select_entities(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    strategy = str(cfg.get("entity_strategy", "fixed_top_n"))
    periods = sorted(df["period"].dropna().unique().tolist())
    if not periods:
        raise ValueError("Bump chart prep requires at least one period.")
    selection_role = str(cfg.get("selection_period_role", "end"))
    selection_period = str(cfg.get("selection_period") or (periods[0] if selection_role == "start" else periods[-1]))

    if strategy == "peer_set":
        keep_geo = set(df.loc[df["peer_flag"], "geo_id"].astype(str))
        keep_geo.update(str(value) for value in _as_list(cfg.get("geo_ids")))
    elif strategy == "rolling_top_n":
        top_n = int(cfg.get("top_n", 10))
        keep_geo = set(df.loc[df["rank"].le(top_n), "geo_id"].astype(str))
    elif strategy == "all":
        keep_geo = set(df["geo_id"].astype(str))
    else:
        top_n = int(cfg.get("top_n", 10))
        selection_rows = df[df["period"] == selection_period].sort_values(["rank", "geo_name", "geo_id"])
        keep_geo = set(selection_rows.head(top_n)["geo_id"].astype(str))

    keep_geo.update(str(value) for value in _as_list(cfg.get("include_geo_ids")))
    if bool(cfg.get("include_highlighted", True)):
        keep_geo.update(df.loc[df["highlight_flag"], "geo_id"].astype(str))
    if not keep_geo:
        raise ValueError("No entities selected for bump chart display; adjust request field_values.")

    out = df[df["geo_id"].astype(str).isin(keep_geo)].copy()
    out["selection_period"] = selection_period
    out["entity_strategy"] = strategy
    out["display_entity_n"] = out["geo_id"].nunique()
    return out


def _add_endpoint_fields(df: pd.DataFrame) -> pd.DataFrame:
    periods = sorted(df["period"].dropna().unique().tolist())
    start_period = periods[0]
    end_period = periods[-1]
    start_rows = df[df["period"] == start_period][["geo_id", "rank"]].rename(columns={"rank": "start_rank"})
    end_rows = df[df["period"] == end_period][["geo_id", "rank", "metric_value"]].rename(
        columns={"rank": "end_rank", "metric_value": "end_metric_value"}
    )
    out = df.merge(start_rows, on="geo_id", how="left").merge(end_rows, on="geo_id", how="left")
    out["rank_change"] = out["start_rank"] - out["end_rank"]
    out["complete_endpoint_flag"] = out["start_rank"].notna() & out["end_rank"].notna()
    out["is_start_period"] = out["period"].eq(start_period)
    out["is_end_period"] = out["period"].eq(end_period)
    return out
