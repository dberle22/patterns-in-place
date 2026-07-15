from __future__ import annotations

import pandas as pd

from ..matrix_helpers import preserve_runtime_fields
from ..specs import ChartSpec


def _apply_quantile_rule(
    df: pd.DataFrame,
    *,
    column: str,
    limits: tuple[float, float] | list[float] | None,
    winsorize: bool,
) -> pd.DataFrame:
    if not limits or column not in df.columns:
        return df

    finite_values = df.loc[df[column].notna(), column]
    if finite_values.empty:
        return df.iloc[0:0].copy()

    lower, upper = finite_values.quantile([float(limits[0]), float(limits[1])]).tolist()
    if winsorize:
        out = df.copy()
        out[column] = out[column].clip(lower=lower, upper=upper)
        return out
    return df.loc[df[column].between(lower, upper, inclusive="both")].copy()


def prep_hexbin(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
    cfg = spec.runtime_config or {}
    out = df.rename(columns=spec.column_mapping).copy()
    keep = [c for c in spec.required_fields + spec.optional_fields if c in out.columns]
    out = out[keep].copy()
    out = preserve_runtime_fields(df, out, ("question_id", "group", "label_flag"))

    if cfg.get("question_id") and "question_id" in out.columns:
        out = out.loc[out["question_id"].astype(str) == str(cfg["question_id"])].copy()
    if cfg.get("time_window") and "time_window" in out.columns:
        out = out.loc[out["time_window"].astype(str) == str(cfg["time_window"])].copy()
    if cfg.get("geo_ids"):
        out = out.loc[out["geo_id"].astype(str).isin([str(value) for value in cfg["geo_ids"]])].copy()
    if cfg.get("group_values") and "group" in out.columns:
        out = out.loc[out["group"].astype(str).isin([str(value) for value in cfg["group_values"]])].copy()

    out["x_value"] = pd.to_numeric(out["x_value"], errors="coerce")
    out["y_value"] = pd.to_numeric(out["y_value"], errors="coerce")
    if "weight_value" in out.columns:
        out["weight_value"] = pd.to_numeric(out["weight_value"], errors="coerce")
    out["highlight_flag"] = out["highlight_flag"].fillna(False).astype(bool) if "highlight_flag" in out.columns else False
    out["label_flag"] = out["label_flag"].fillna(False).astype(bool) if "label_flag" in out.columns else False

    if cfg.get("drop_na_xy", True):
        out = out.loc[out["x_value"].notna() & out["y_value"].notna()].copy()

    if cfg.get("require_single_time_window", True) and "time_window" in out.columns:
        if out["time_window"].dropna().astype(str).nunique() > 1:
            raise ValueError("hexbin expects a single time_window unless require_single_time_window is disabled.")

    if "weight_value" in out.columns and cfg.get("non_negative_weights", True):
        if out["weight_value"].dropna().lt(0).any():
            raise ValueError("Hexbin weights must be non-negative.")

    out = _apply_quantile_rule(
        out,
        column="x_value",
        limits=cfg.get("x_quantile_limits"),
        winsorize=bool(cfg.get("winsorize", False)),
    )
    out = _apply_quantile_rule(
        out,
        column="y_value",
        limits=cfg.get("y_quantile_limits"),
        winsorize=bool(cfg.get("winsorize", False)),
    )

    if out.empty:
        raise ValueError("hexbin prep removed all rows; adjust the request filters.")

    out.attrs["chart_config"] = cfg
    return out
