from __future__ import annotations

import pandas as pd

from ..matrix_helpers import complete_matrix, format_numeric_labels, ordered_unique, percentile_rank, preserve_runtime_fields
from ..specs import ChartSpec


def prep_heatmap_table(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    cfg = spec.runtime_config or {}
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()
    out = preserve_runtime_fields(df, out, ("question_id", "row_order", "metric_order", "cell_label", "value_label"))

    # Prep resolves the matrix slice and order first so render can stay focused
    # on fill/label treatment rather than chart-specific filtering rules.
    out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    if "normalized_value" in out.columns:
        out["normalized_value"] = pd.to_numeric(out["normalized_value"], errors="coerce")
    else:
        out["normalized_value"] = float("nan")
    if "row_order" in out.columns:
        out["row_order"] = pd.to_numeric(out["row_order"], errors="coerce")
    else:
        out["row_order"] = float("nan")
    if "metric_order" in out.columns:
        out["metric_order"] = pd.to_numeric(out["metric_order"], errors="coerce")
    else:
        out["metric_order"] = float("nan")

    if cfg.get("question_id") and "question_id" in out.columns:
        out = out.loc[out["question_id"] == cfg["question_id"]].copy()
    if cfg.get("time_window") and "time_window" in out.columns:
        allowed_windows = {str(value) for value in (cfg["time_window"] if isinstance(cfg["time_window"], (list, tuple, set)) else [cfg["time_window"]])}
        out = out.loc[out["time_window"].astype(str).isin(allowed_windows)].copy()
    if cfg.get("metric_ids"):
        out = out.loc[out["metric_id"].astype(str).isin([str(value) for value in cfg["metric_ids"]])].copy()
    if cfg.get("periods") and "period" in out.columns:
        out = out.loc[out["period"].astype(str).isin([str(value) for value in cfg["periods"]])].copy()
    if cfg.get("geo_ids"):
        out = out.loc[out["geo_id"].astype(str).isin([str(value) for value in cfg["geo_ids"]])].copy()
    if out.empty:
        raise ValueError("heatmap_table prep removed all rows; adjust the request filters.")

    out["direction"] = out["direction"].fillna("higher_is_better").astype(str) if "direction" in out.columns else "higher_is_better"
    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool) if "highlight_flag" in out.columns else False
    out["period"] = out["period"].astype(str) if "period" in out.columns else ""
    out["time_window"] = out["time_window"].astype(str) if "time_window" in out.columns else ""
    out["metric_group"] = out["metric_group"].astype(str) if "metric_group" in out.columns else ""

    variant = str(cfg.get("variant") or "").strip().lower()
    if not variant:
        metric_n = out["metric_id"].nunique(dropna=True)
        period_n = out["period"].nunique(dropna=True) if "period" in out.columns else 0
        geo_n = out["geo_id"].nunique(dropna=True)
        if metric_n == 1 and period_n > 1:
            variant = "geo_period"
        elif geo_n == 1 and period_n > 1 and metric_n > 1:
            variant = "metric_period"
        else:
            variant = "geo_metric"
    out["heatmap_variant"] = variant

    if variant == "metric_period":
        out["row_id"] = out["metric_id"].astype(str)
        out["row_label"] = out["metric_label"].astype(str)
        out["column_id"] = out["period"].astype(str)
        out["column_label"] = out["period"].astype(str)
    elif variant == "geo_period":
        out["row_id"] = out["geo_id"].astype(str)
        out["row_label"] = out["geo_name"].astype(str)
        out["column_id"] = out["period"].astype(str)
        out["column_label"] = out["period"].astype(str)
    else:
        out["row_id"] = out["geo_id"].astype(str)
        out["row_label"] = out["geo_name"].astype(str)
        out["column_id"] = out["metric_id"].astype(str)
        out["column_label"] = out["metric_label"].astype(str)

    if cfg.get("normalize", True) or not out["normalized_value"].notna().any():
        if variant == "geo_metric":
            norm_group = out["metric_id"].astype(str) + "|" + out["time_window"].astype(str)
        elif variant == "geo_period":
            norm_group = out["metric_id"].astype(str) + "|" + out["period"].astype(str)
        else:
            norm_group = out["metric_id"].astype(str)
        for _, index in pd.Series(norm_group, index=out.index).groupby(norm_group).groups.items():
            group_index = pd.Index(index)
            direction_values = out.loc[group_index, "direction"].astype(str).str.lower()
            higher_is_better = not direction_values.isin(["lower_is_better", "lower-better", "lower"]).all()
            out.loc[group_index, "normalized_value"] = percentile_rank(
                out.loc[group_index, "metric_value"],
                higher_is_better=higher_is_better,
            )
    elif out["normalized_value"].dropna().max() <= 1:
        out["normalized_value"] = out["normalized_value"] * 100.0

    if cfg.get("complete_matrix", True):
        out = complete_matrix(
            out,
            row_fields=("row_id", "row_label", "geo_level", "geo_id", "geo_name", "row_order"),
            column_fields=("column_id", "column_label", "metric_id", "metric_label", "metric_group", "metric_order", "period"),
        )
        if "heatmap_variant" not in out.columns:
            out["heatmap_variant"] = variant

    fill_value_field = str(cfg.get("fill_value_field", "normalized_value"))
    if fill_value_field not in out.columns:
        fill_value_field = "metric_value"
    out["fill_value"] = pd.to_numeric(out[fill_value_field], errors="coerce")
    out["missing_flag"] = out["fill_value"].isna()

    if "cell_label" in out.columns:
        out["cell_label"] = out["cell_label"].fillna("").astype(str)
        out.loc[out["cell_label"].str.strip() == "", "cell_label"] = format_numeric_labels(
            out["metric_value"],
            decimals=int(cfg.get("label_decimals", 1)),
            missing_label=str(cfg.get("missing_label", "No data")),
        )
    else:
        label_field = str(cfg.get("label_value_field", "metric_value"))
        if label_field not in out.columns:
            label_field = "metric_value"
        out["cell_label"] = format_numeric_labels(
            out[label_field],
            decimals=int(cfg.get("label_decimals", 1)),
            missing_label=str(cfg.get("missing_label", "No data")),
        )

    row_priority = [str(value) for value in cfg.get("row_order", [])] if cfg.get("row_order") else []
    if row_priority:
        row_levels = row_priority + [value for value in ordered_unique(out["row_label"]) if value not in row_priority]
    elif out["row_order"].notna().any():
        row_levels = (
            out.loc[:, ["row_label", "row_order"]]
            .drop_duplicates()
            .sort_values(["row_order", "row_label"], ascending=[False, True])["row_label"]
            .astype(str)
            .tolist()
        )
    else:
        row_scores = out.groupby("row_label", dropna=False)["normalized_value"].mean().sort_values(ascending=False)
        row_levels = [str(value) for value in row_scores.index.tolist()]

    column_priority = [str(value) for value in cfg.get("column_order", [])] if cfg.get("column_order") else []
    if column_priority:
        column_levels = column_priority + [value for value in ordered_unique(out["column_label"]) if value not in column_priority]
    elif out["metric_order"].notna().any():
        column_levels = (
            out.loc[:, ["column_label", "metric_order"]]
            .drop_duplicates()
            .sort_values(["metric_order", "column_label"], ascending=[True, True])["column_label"]
            .astype(str)
            .tolist()
        )
    else:
        column_levels = ordered_unique(out["column_label"])

    out["row_label"] = pd.Categorical(out["row_label"].astype(str), categories=row_levels, ordered=True)
    out["column_label"] = pd.Categorical(out["column_label"].astype(str), categories=column_levels, ordered=True)
    out.attrs["chart_config"] = cfg
    return out
