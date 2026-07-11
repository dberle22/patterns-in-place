from __future__ import annotations

import pandas as pd

from ..specs import ChartSpec


def prep_correlation_heatmap(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()
    out["metric_value"] = pd.to_numeric(out["metric_value"], errors="coerce")
    out = out[out["metric_value"].notna()].copy()

    wide = out.pivot_table(index="geo_id", columns="metric_label", values="metric_value", aggfunc="mean")
    corr = wide.corr(method="spearman")
    corr_named = corr.rename_axis(index="metric_y", columns="metric_x")
    try:
        corr_long = corr_named.stack(future_stack=True)
    except TypeError:
        corr_long = corr_named.stack(dropna=False)
    except ValueError:
        corr_long = corr_named.stack(dropna=False)
    corr_df = corr_long.reset_index(name="correlation")
    corr_df["label"] = corr_df["correlation"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    corr_df["source"] = out["source"].iloc[0] if "source" in out.columns and len(out) else None
    corr_df["vintage"] = out["vintage"].iloc[0] if "vintage" in out.columns and len(out) else None
    corr_df["time_window"] = out["time_window"].iloc[0] if "time_window" in out.columns and len(out) else None
    corr_df["geo_level"] = out["geo_level"].iloc[0] if "geo_level" in out.columns and len(out) else None
    # Preserve a minimal version of the generated spec contract so the current
    # orchestrator validation still has the fields it expects after the matrix
    # transform.
    corr_df["geo_id"] = "correlation_matrix"
    corr_df["geo_name"] = "Correlation matrix"
    corr_df["metric_id"] = corr_df["metric_x"]
    corr_df["metric_label"] = corr_df["metric_x"]
    corr_df["metric_value"] = corr_df["correlation"]
    return corr_df
