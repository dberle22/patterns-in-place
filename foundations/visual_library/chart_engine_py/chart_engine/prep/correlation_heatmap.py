from __future__ import annotations

import pandas as pd

from ..matrix_helpers import ordered_unique, preserve_runtime_fields
from ..specs import ChartSpec


def _correlation_metric_order(corr: pd.DataFrame, method: str, input_order: list[str]) -> list[str]:
    labels = [str(label) for label in corr.columns.tolist()]
    resolved = (method or "clustered").strip().lower()
    if len(labels) <= 2 or resolved == "input":
        return [label for label in input_order if label in labels]
    if resolved == "alphabetical":
        return sorted(labels)

    # R uses hierarchical clustering. In Python we use a deterministic
    # correlation-strength ordering that keeps related metrics adjacent without
    # introducing a new heavy dependency for this package.
    abs_corr = corr.abs().fillna(0.0)
    remaining = labels.copy()
    start = abs_corr.sum(axis=1).sort_values(ascending=False).index[0]
    ordered = [str(start)]
    remaining.remove(str(start))
    while remaining:
        anchor = ordered[-1]
        next_label = abs_corr.loc[anchor, remaining].sort_values(ascending=False).index[0]
        ordered.append(str(next_label))
        remaining.remove(str(next_label))
    return ordered


def prep_correlation_heatmap(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    cfg = spec.runtime_config or {}
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()
    out = preserve_runtime_fields(df, out, ("question_id",))
    out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    if cfg.get("question_id") and "question_id" in out.columns:
        out = out.loc[out["question_id"] == cfg["question_id"]].copy()
    if cfg.get("time_window") and "time_window" in out.columns:
        out = out.loc[out["time_window"] == cfg["time_window"]].copy()
    if cfg.get("geo_ids"):
        out = out.loc[out["geo_id"].astype(str).isin([str(value) for value in cfg["geo_ids"]])].copy()
    if cfg.get("metric_ids"):
        out = out.loc[out["metric_id"].astype(str).isin([str(value) for value in cfg["metric_ids"]])].copy()

    include_flag_column = str(cfg.get("include_flag_column", "include_flag"))
    if include_flag_column in out.columns:
        include_mask = out[include_flag_column].fillna(True).astype(bool)
        out = out.loc[include_mask].copy()
    out = out.loc[out["metric_value"].notna()].copy()
    if out.empty:
        raise ValueError("correlation_heatmap prep removed all rows; adjust the request filters.")

    split_var = str(cfg.get("facet_by") or ("group" if "group" in out.columns and out["group"].nunique(dropna=True) > 1 else "")).strip()
    split_values = ordered_unique(out[split_var]) if split_var and split_var in out.columns else []
    if not split_values:
        split_values = ["__all__"]

    method = str(cfg.get("method", "spearman")).lower()
    order_method = str(cfg.get("order_method", "clustered")).lower()
    weak_threshold = cfg.get("weak_threshold")
    pieces: list[pd.DataFrame] = []
    input_order = ordered_unique(out["metric_label"])

    for split_value in split_values:
        if split_value == "__all__":
            subset = out.copy()
        else:
            subset = out.loc[out[split_var].astype(str) == split_value].copy()
        wide = subset.pivot_table(index="geo_id", columns="metric_label", values="metric_value", aggfunc="mean")
        corr = wide.corr(method=method)
        metric_order = _correlation_metric_order(corr, order_method, input_order)

        corr_named = corr.rename_axis(index="metric_y", columns="metric_x")
        try:
            corr_long = corr_named.stack(future_stack=True)
        except TypeError:
            corr_long = corr_named.stack(dropna=False)
        except ValueError:
            corr_long = corr_named.stack(dropna=False)
        corr_df = corr_long.reset_index(name="correlation")
        corr_df["correlation_display"] = corr_df["correlation"]
        if weak_threshold is not None:
            weak_cut = float(weak_threshold)
            off_diagonal = corr_df["metric_x"] != corr_df["metric_y"]
            corr_df.loc[off_diagonal & corr_df["correlation"].abs().lt(weak_cut), "correlation_display"] = float("nan")
        corr_df["label"] = corr_df["correlation"].map(lambda value: f"{value:.2f}" if pd.notna(value) else "")
        corr_df["metric_x"] = pd.Categorical(corr_df["metric_x"], categories=metric_order, ordered=True)
        corr_df["metric_y"] = pd.Categorical(corr_df["metric_y"], categories=list(reversed(metric_order)), ordered=True)
        corr_df["abs_correlation"] = corr_df["correlation"].abs()
        corr_df["source"] = subset["source"].iloc[0] if "source" in subset.columns and len(subset) else None
        corr_df["vintage"] = subset["vintage"].iloc[0] if "vintage" in subset.columns and len(subset) else None
        corr_df["time_window"] = subset["time_window"].iloc[0] if "time_window" in subset.columns and len(subset) else None
        corr_df["geo_level"] = subset["geo_level"].iloc[0] if "geo_level" in subset.columns and len(subset) else None
        corr_df["question_id"] = subset["question_id"].iloc[0] if "question_id" in subset.columns and len(subset) else None
        corr_df["missingness_policy"] = "pairwise.complete.obs"
        corr_df["order_method"] = order_method
        corr_df["method"] = method
        corr_df["geo_id"] = "correlation_matrix"
        corr_df["geo_name"] = "Correlation matrix"
        corr_df["metric_id"] = corr_df["metric_x"].astype(str)
        corr_df["metric_label"] = corr_df["metric_x"].astype(str)
        corr_df["metric_value"] = corr_df["correlation"]
        if split_var and split_var in subset.columns:
            corr_df[split_var] = split_value
        pieces.append(corr_df)

    out_df = pd.concat(pieces, ignore_index=True)
    out_df.attrs["chart_config"] = cfg
    return out_df
