from __future__ import annotations

import pandas as pd

from ..matrix_helpers import preserve_runtime_fields
from ..prep_helpers import coerce_bool_column, coerce_numeric_column, select_known_fields
from ..specs import ChartSpec


def prep_boxplot(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    cfg = spec.runtime_config or {}
    out = select_known_fields(df, spec)
    out = preserve_runtime_fields(df, out, ("question_id",))

    # Normalize the numeric fields the R prep uses for filtering, display, and
    # optional benchmark/reference logic.
    out = coerce_numeric_column(out, "metric_value")
    out = coerce_numeric_column(out, "benchmark_value")
    out = coerce_numeric_column(out, "weight_value")

    if cfg.get("question_id") and "question_id" in out.columns:
        out = out.loc[out["question_id"] == cfg["question_id"]].copy()
    if cfg.get("time_window") and "time_window" in out.columns:
        out = out.loc[out["time_window"] == cfg["time_window"]].copy()
    if cfg.get("metric_id") and "metric_id" in out.columns:
        out = out.loc[out["metric_id"] == cfg["metric_id"]].copy()
    if cfg.get("geo_ids"):
        out = out.loc[out["geo_id"].astype(str).isin([str(value) for value in cfg["geo_ids"]])].copy()

    group_field = str(cfg.get("group_field", "group"))
    if cfg.get("group_values") and group_field in out.columns:
        out = out.loc[out[group_field].astype(str).isin([str(value) for value in cfg["group_values"]])].copy()

    out["missing_metric_count"] = int(out["metric_value"].isna().sum())
    if cfg.get("drop_missing_metric", True):
        out = out.loc[out["metric_value"].notna()].copy()
    if out.empty:
        raise ValueError("boxplot prep removed all rows; adjust the request filters.")

    if group_field in out.columns:
        out["box_group"] = out[group_field].fillna("Ungrouped").astype(str)
        out.loc[out["box_group"].str.strip() == "", "box_group"] = "Ungrouped"
    else:
        out["box_group"] = "All observations"

    out = coerce_bool_column(out, "highlight_flag")
    out = coerce_bool_column(out, "label_flag")
    out["plot_value"] = out["metric_value"]

    trim_quantiles = cfg.get("trim_quantiles")
    if trim_quantiles and len(trim_quantiles) == 2:
        lower, upper = sorted([float(trim_quantiles[0]), float(trim_quantiles[1])])
        bounds = out["plot_value"].quantile([lower, upper]).tolist()
        if cfg.get("winsorize_display"):
            out["plot_value"] = out["plot_value"].clip(lower=bounds[0], upper=bounds[1])
        else:
            out = out.loc[out["plot_value"].between(bounds[0], bounds[1], inclusive="both")].copy()

    group_stats = (
        out.groupby("box_group", dropna=False)["plot_value"]
        .agg(group_median="median", group_n="count")
        .reset_index()
    )
    out = out.merge(group_stats, on="box_group", how="left")

    order_mode = str(cfg.get("order_groups", "median_desc")).lower()
    if cfg.get("row_order"):
        group_levels = [str(value) for value in cfg["row_order"]]
    elif order_mode == "median_asc":
        group_levels = group_stats.sort_values(["group_median", "box_group"], ascending=[True, True])["box_group"].tolist()
    elif order_mode == "alphabetical":
        group_levels = sorted(group_stats["box_group"].astype(str).tolist())
    else:
        group_levels = group_stats.sort_values(["group_median", "box_group"], ascending=[False, True])["box_group"].tolist()

    out["box_group"] = pd.Categorical(out["box_group"], categories=group_levels, ordered=True)
    out.attrs["chart_config"] = cfg
    return out
