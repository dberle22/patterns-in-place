from __future__ import annotations

import pandas as pd

from ..matrix_helpers import preserve_runtime_fields
from ..specs import ChartSpec


def prep_waterfall(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    cfg = spec.runtime_config or {}
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()
    out = preserve_runtime_fields(df, out, ("question_id", "group"))

    out["component_value"] = pd.to_numeric(out["component_value"], errors="coerce")
    if "component_delta" in out.columns:
        out["component_delta"] = pd.to_numeric(out["component_delta"], errors="coerce")
    if "sort_order" in out.columns:
        out["sort_order"] = pd.to_numeric(out["sort_order"], errors="coerce")

    if cfg.get("question_id") and "question_id" in out.columns:
        out = out.loc[out["question_id"] == cfg["question_id"]].copy()
    if cfg.get("geo_ids"):
        out = out.loc[out["geo_id"].astype(str).isin([str(value) for value in cfg["geo_ids"]])].copy()
    if cfg.get("time_window") and "time_window" in out.columns:
        out = out.loc[out["time_window"] == cfg["time_window"]].copy()

    value_mode = str(cfg.get("value_mode", "auto")).lower()
    if value_mode == "delta":
        value_field = "component_delta"
    elif value_mode in {"level", "percent"}:
        value_field = "component_value"
    elif "component_delta" in out.columns and out["component_delta"].notna().any():
        value_field = "component_delta"
    else:
        value_field = "component_value"

    if value_field not in out.columns:
        raise ValueError(f"waterfall prep could not find '{value_field}' in the input data.")

    out["plot_value"] = pd.to_numeric(out[value_field], errors="coerce")
    if cfg.get("drop_missing_components", True):
        out = out.loc[out["plot_value"].notna()].copy()
    if out.empty:
        raise ValueError("waterfall prep removed all rows; adjust the request filters.")

    if "sort_order" not in out.columns or out["sort_order"].isna().all():
        out["sort_order"] = out.groupby(
            [column for column in ["geo_id", "time_window", "benchmark_label"] if column in out.columns],
            dropna=False,
        ).cumcount() + 1

    group_fields = cfg.get("group_fields")
    if not group_fields:
        group_fields = [column for column in ("geo_level", "geo_id", "geo_name", "time_window", "benchmark_label") if column in out.columns]
    group_fields = [str(column) for column in group_fields if str(column) in out.columns]

    if group_fields:
        out["waterfall_group"] = out[group_fields].fillna("none").astype(str).agg("|".join, axis=1)
    else:
        out["waterfall_group"] = "all"

    out["row_type"] = "component"
    pieces: list[pd.DataFrame] = []
    for _, piece in out.groupby("waterfall_group", sort=False, dropna=False):
        piece = piece.sort_values(["sort_order", "component_label"], ascending=[True, True]).copy()
        piece["cumulative_end"] = piece["plot_value"].cumsum()
        piece["cumulative_start"] = piece["cumulative_end"].shift(fill_value=0) - piece["plot_value"]
        piece["waterfall_position"] = range(1, len(piece) + 1)
        piece["component_share"] = piece["plot_value"] / piece["plot_value"].sum() if piece["plot_value"].sum() != 0 else float("nan")
        piece["additive_total"] = piece["plot_value"].sum()
        piece["additive_residual"] = piece["additive_total"] - piece["plot_value"].sum()
        piece["additive_pass"] = piece["additive_residual"].abs() <= float(cfg.get("additive_tolerance", 1e-6))
        piece["direction"] = piece["plot_value"].apply(lambda value: "positive" if value >= 0 else "negative")
        pieces.append(piece)

        if cfg.get("include_total", True):
            total_row = piece.iloc[[-1]].copy()
            total_value = float(piece["plot_value"].sum())
            total_row["component_id"] = str(cfg.get("total_component_id", "total"))
            total_row["component_label"] = str(
                cfg.get("total_label")
                or (piece["total_label"].dropna().iloc[0] if "total_label" in piece.columns and piece["total_label"].notna().any() else "Total")
            )
            total_row["component_value"] = total_value
            if "component_delta" in total_row.columns:
                total_row["component_delta"] = total_value
            total_row["plot_value"] = total_value
            total_row["cumulative_start"] = 0.0
            total_row["cumulative_end"] = total_value
            total_row["waterfall_position"] = len(piece) + 1
            total_row["row_type"] = str(cfg.get("total_row_type", "total"))
            total_row["component_group"] = "Total"
            total_row["component_share"] = 1.0
            total_row["additive_total"] = total_value
            total_row["additive_residual"] = 0.0
            total_row["additive_pass"] = True
            total_row["direction"] = "total"
            pieces.append(total_row)

    out = pd.concat(pieces, ignore_index=True)
    out = out.sort_values(["waterfall_group", "waterfall_position"], ascending=[True, True]).reset_index(drop=True)
    out.attrs["chart_config"] = cfg
    return out
