"""Pure calculation functions for the versioned trajectory mart.

The command-line builder handles source reads and DuckDB writes. Keeping the
method here lets the unit tests exercise scoring rules without a live database.
"""

from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd


def empirical_percentile(values: pd.Series) -> pd.Series:
    """Return average-rank empirical percentiles on the 0–100 scale.

    Missing values stay missing. Tied observations receive the same midpoint
    rank, which avoids inventing distinctions between equal estimates.
    """

    return values.rank(method="average", pct=True) * 100


def theil_sen_slope(years: pd.Series, values: pd.Series) -> float:
    """Estimate a robust annual slope from all valid pairs in a time window."""

    valid = pd.DataFrame({"year": years, "value": values}).dropna().sort_values("year")
    if len(valid) < 2:
        return np.nan

    slopes = [
        (right.value - left.value) / (right.year - left.year)
        for left, right in combinations(valid.itertuples(index=False), 2)
        if right.year != left.year
    ]
    return float(np.median(slopes)) if slopes else np.nan


def transform_values(values: pd.Series, transform: str) -> pd.Series:
    """Apply the metric's declared analytical transform without changing raw values."""

    numeric = pd.to_numeric(values, errors="coerce")
    if transform == "identity":
        return numeric
    if transform == "log":
        # Non-positive observations cannot be represented on the log scale and
        # are recorded as unavailable rather than silently shifted.
        return numeric.where(numeric > 0).map(np.log)
    raise ValueError(f"Unsupported metric transform: {transform}")


def polarity_multiplier(polarity: str) -> float:
    """Map a normative metric polarity to an aligned movement direction."""

    if polarity == "positive":
        return 1.0
    if polarity == "negative":
        return -1.0
    if polarity == "neutral":
        return 1.0
    raise ValueError(f"Unsupported metric polarity: {polarity}")


def signal_tier(salience_percentile: float | None) -> str:
    """Assign the nested 80/90/95 sensitivity tier for a valid score."""

    if pd.isna(salience_percentile):
        return "insufficient_evidence"
    if salience_percentile >= 95:
        return "exceptional"
    if salience_percentile >= 90:
        return "strong"
    if salience_percentile >= 80:
        return "notable"
    return "common"


def position_band(position_percentile: float | None, scoring: dict[str, Any]) -> str:
    """Map a frame's current percentile into a reader-facing position band."""

    if pd.isna(position_percentile):
        return "insufficient_evidence"
    if position_percentile >= scoring["position_high_min"]:
        return "high"
    if position_percentile <= scoring["position_low_max"]:
        return "low"
    return "middle"


def frame_label(
    frame_id: str,
    band: str,
    movement: str,
    tier: str,
    coverage_status: str,
) -> str:
    """Create display wording while preserving the component measures separately."""

    if coverage_status != "eligible":
        return "insufficient_evidence"
    if frame_id == "character":
        character_tier = {"common": "typical", "notable": "notable", "strong": "strong", "exceptional": "exceptional"}[tier]
        return f"{character_tier}_character_change"
    if tier == "common":
        return "no_standout_trend"
    if movement == "gaining_ground":
        return {"high": "pulling_ahead", "low": "catching_up", "middle": "moving_up_quickly"}[band]
    if movement == "losing_ground":
        return {
            "high": "losing_ground",
            "low": "falling_further_behind",
            "middle": "moving_down_quickly",
        }[band]
    return "no_standout_trend"


def turn_status(
    short_momentum: float | None,
    medium_momentum: float | None,
    short_salience: float | None,
    medium_salience: float | None,
    shared_metric_count: int,
    minimum_shared_metrics: int,
    gate: float,
) -> str:
    """Classify a compatible short/medium comparison without treating noise as a turn."""

    required = [short_momentum, medium_momentum, short_salience, medium_salience]
    if any(pd.isna(value) for value in required) or shared_metric_count < minimum_shared_metrics:
        return "insufficient_evidence"

    directions_conflict = np.sign(short_momentum) != np.sign(medium_momentum)
    short_passes = short_salience >= gate
    medium_passes = medium_salience >= gate
    if directions_conflict and short_passes and medium_passes:
        return "confirmed_turn"
    if directions_conflict and short_passes:
        return "emerging_turn_watch"
    return "no_turn_signal"


def _metric_window_rows(
    series: pd.DataFrame,
    metric: dict[str, Any],
    window_name: str,
    window: dict[str, Any],
) -> list[dict[str, Any]]:
    """Compute endpoint and robust-trend evidence for one metric/window panel."""

    scoped = series[
        (series["metric_id"] == metric["metric_id"])
        & series["year"].between(window["start_year"], window["end_year"])
    ]
    rows: list[dict[str, Any]] = []
    multiplier = polarity_multiplier(metric["polarity"])

    for (cbsa_code, cbsa_name), group in scoped.groupby(["cbsa_code", "cbsa_name"], dropna=False):
        group = group.sort_values("year")
        start = group.loc[group["year"] == window["start_year"]].iloc[0]
        end = group.loc[group["year"] == window["end_year"]].iloc[0]
        available = group.dropna(subset=["transformed_value"])
        has_endpoints = pd.notna(start["transformed_value"]) and pd.notna(end["transformed_value"])
        observation_count = len(available)
        is_eligible = has_endpoints and observation_count >= window["minimum_observations"]

        slope = theil_sen_slope(available["year"], available["transformed_value"]) if is_eligible else np.nan
        if window["years"] == 1 and is_eligible:
            # A two-point window is a named short-run change, not a fitted trend.
            slope = float(end["transformed_value"] - start["transformed_value"])

        if metric["polarity"] == "neutral":
            absolute_direction = "non_normative"
        elif not is_eligible:
            absolute_direction = "insufficient_evidence"
        elif slope > 0:
            absolute_direction = "improving"
        elif slope < 0:
            absolute_direction = "declining"
        else:
            absolute_direction = "unchanged"

        rows.append(
            {
                "cbsa_code": cbsa_code,
                "cbsa_name": cbsa_name,
                "frame_id": metric["frame_id"],
                "topic_id": metric["topic_id"],
                "metric_id": metric["metric_id"],
                "metric_label": metric["metric_label"],
                "source_table": metric["source_table"],
                "source_column": metric["source_column"],
                "transform": metric["transform"],
                "polarity": metric["polarity"],
                "window_name": window_name,
                "window_years": window["years"],
                "start_year": window["start_year"],
                "end_year": window["end_year"],
                "observation_count": observation_count,
                "trend_estimator": "two_point_change" if window["years"] == 1 else "theil_sen",
                "start_raw_value": start["raw_value"],
                "end_raw_value": end["raw_value"],
                "endpoint_change_raw": end["raw_value"] - start["raw_value"] if has_endpoints else np.nan,
                "start_percentile": start["national_percentile"],
                "end_percentile": end["national_percentile"],
                "percentile_point_change": (
                    end["national_percentile"] - start["national_percentile"] if has_endpoints else np.nan
                ),
                "trend_slope_transformed": slope,
                "polarity_aligned_slope": slope * multiplier if is_eligible else np.nan,
                "absolute_direction": absolute_direction,
                "coverage_status": "eligible" if is_eligible else "insufficient_history",
            }
        )
    return rows


def build_metric_mart(series: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Build the metric-grain mart from prepared annual series observations."""

    rows: list[dict[str, Any]] = []
    for metric in config["metrics"]:
        for window_name in metric["windows"]:
            rows.extend(_metric_window_rows(series, metric, window_name, config["engine"]["windows"][window_name]))

    result = pd.DataFrame(rows)
    eligible = result["coverage_status"] == "eligible"
    ranking_keys = ["metric_id", "window_name", "end_year"]
    result.loc[eligible, "momentum_percentile"] = (
        result.loc[eligible].groupby(ranking_keys)["polarity_aligned_slope"].transform(empirical_percentile)
    )
    result["relative_momentum_score"] = 2 * (result["momentum_percentile"] / 100) - 1
    result.loc[eligible, "metric_salience_percentile"] = (
        result.loc[eligible]
        .groupby(ranking_keys)["relative_momentum_score"]
        .transform(lambda values: empirical_percentile(values.abs()))
    )
    result["signal_tier"] = result["metric_salience_percentile"].map(signal_tier)
    return result


def _frame_spine(universe: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Create frame/window rows even when a metro lacks enough eligible topics."""

    pairs = {
        (metric["frame_id"], window_name)
        for metric in config["metrics"]
        for window_name in metric["windows"]
    }
    rows = []
    for frame_id, window_name in sorted(pairs):
        window = config["engine"]["windows"][window_name]
        for metro in universe[["cbsa_code", "cbsa_name"]].itertuples(index=False):
            rows.append(
                {
                    "cbsa_code": metro.cbsa_code,
                    "cbsa_name": metro.cbsa_name,
                    "frame_id": frame_id,
                    "window_name": window_name,
                    "window_years": window["years"],
                    "start_year": window["start_year"],
                    "end_year": window["end_year"],
                }
            )
    return pd.DataFrame(rows)


def build_frame_mart(metric: pd.DataFrame, universe: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Balance metrics within topics, then topics within frames, before ranking results."""

    eligible = metric.loc[metric["coverage_status"] == "eligible"].copy()
    eligible["start_position_score"] = 2 * (eligible["start_percentile"] / 100) - 1
    eligible["end_position_score"] = 2 * (eligible["end_percentile"] / 100) - 1

    # Normative frames orient both level and movement using polarity. Character
    # preserves neutral positions and uses magnitude only for frame momentum.
    normative = eligible["polarity"] != "neutral"
    eligible.loc[normative, "start_position_score"] *= eligible.loc[normative, "polarity"].map(polarity_multiplier)
    eligible.loc[normative, "end_position_score"] *= eligible.loc[normative, "polarity"].map(polarity_multiplier)
    eligible["metric_magnitude_score"] = eligible["relative_momentum_score"].abs()
    eligible["is_improving"] = (eligible["absolute_direction"] == "improving").astype(float)

    topic_keys = ["cbsa_code", "cbsa_name", "frame_id", "window_name", "window_years", "start_year", "end_year", "topic_id"]
    topic = (
        eligible.groupby(topic_keys, as_index=False)
        .agg(
            topic_metric_count=("metric_id", "nunique"),
            topic_start_position_score=("start_position_score", "mean"),
            topic_end_position_score=("end_position_score", "mean"),
            topic_signed_momentum=("relative_momentum_score", "mean"),
            topic_magnitude_momentum=("metric_magnitude_score", "mean"),
            topic_improving_share=("is_improving", "mean"),
        )
    )

    frame_keys = ["cbsa_code", "cbsa_name", "frame_id", "window_name", "window_years", "start_year", "end_year"]
    frame = (
        topic.groupby(frame_keys, as_index=False)
        .agg(
            topic_count=("topic_id", "nunique"),
            metric_count=("topic_metric_count", "sum"),
            start_position_score=("topic_start_position_score", "mean"),
            end_position_score=("topic_end_position_score", "mean"),
            signed_momentum_score=("topic_signed_momentum", "mean"),
            magnitude_momentum_score=("topic_magnitude_momentum", "mean"),
            improving_metric_share=("topic_improving_share", "mean"),
        )
    )
    result = _frame_spine(universe, config).merge(frame, how="left", on=frame_keys)
    minimum_topics = config["engine"]["scoring"]["minimum_topics_per_frame"]
    result["coverage_status"] = np.where(result["topic_count"].fillna(0) >= minimum_topics, "eligible", "insufficient_evidence")
    result["topic_count"] = result["topic_count"].fillna(0).astype(int)
    result["metric_count"] = result["metric_count"].fillna(0).astype(int)

    character = result["frame_id"] == "character"
    result["frame_momentum_score"] = result["signed_momentum_score"]
    result.loc[character, "frame_momentum_score"] = result.loc[character, "magnitude_momentum_score"]
    eligible_frames = result["coverage_status"] == "eligible"
    rank_keys = ["frame_id", "window_name", "end_year"]
    result.loc[eligible_frames, "start_position_percentile"] = (
        result.loc[eligible_frames].groupby(rank_keys)["start_position_score"].transform(empirical_percentile)
    )
    result.loc[eligible_frames, "end_position_percentile"] = (
        result.loc[eligible_frames].groupby(rank_keys)["end_position_score"].transform(empirical_percentile)
    )
    result.loc[eligible_frames, "trajectory_salience_percentile"] = (
        result.loc[eligible_frames]
        .groupby(rank_keys)["frame_momentum_score"]
        .transform(lambda values: empirical_percentile(values.abs()))
    )
    result["percentile_point_change"] = result["end_position_percentile"] - result["start_position_percentile"]
    result["position_band"] = result["end_position_percentile"].map(
        lambda value: position_band(value, config["engine"]["scoring"])
    )
    result["signal_tier"] = result["trajectory_salience_percentile"].map(signal_tier)
    thresholds = config["engine"]["scoring"]["signal_thresholds"]
    for threshold in thresholds:
        result[f"signal_p{threshold}"] = result["trajectory_salience_percentile"] >= threshold

    result["movement_direction"] = np.where(
        result["frame_momentum_score"] > 0,
        "gaining_ground",
        np.where(result["frame_momentum_score"] < 0, "losing_ground", "no_relative_movement"),
    )
    result.loc[character, "movement_direction"] = "non_normative"
    result["absolute_direction"] = np.where(
        result["improving_metric_share"] >= 0.60,
        "improving",
        np.where(result["improving_metric_share"] <= 0.40, "declining", "mixed"),
    )
    result.loc[character, "absolute_direction"] = "non_normative"
    result.loc[result["coverage_status"] != "eligible", "absolute_direction"] = "insufficient_evidence"
    result["trajectory_label"] = result.apply(
        lambda row: frame_label(
            row["frame_id"],
            row["position_band"],
            row["movement_direction"],
            row["signal_tier"],
            row["coverage_status"],
        ),
        axis=1,
    )
    return result


def build_turn_signals(metric: pd.DataFrame, frame: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Compare the fixed Opportunity KPI panel across its compatible windows."""

    opportunity = frame.loc[frame["frame_id"] == "opportunity"].copy()
    index_columns = ["cbsa_code", "cbsa_name", "frame_id", "end_year"]
    short = opportunity.loc[opportunity["window_name"] == "one_year"].set_index(index_columns)
    medium = opportunity.loc[opportunity["window_name"] == "five_year"].set_index(index_columns)
    paired = short.join(medium, lsuffix="_short", rsuffix="_medium", how="outer").reset_index()

    eligible_metric = metric.loc[
        (metric["frame_id"] == "opportunity") & (metric["coverage_status"] == "eligible"),
        ["cbsa_code", "metric_id", "window_name", "relative_momentum_score"],
    ]
    metric_pairs = (
        eligible_metric.pivot_table(
            index=["cbsa_code", "metric_id"], columns="window_name", values="relative_momentum_score", aggfunc="first"
        )
        .dropna(subset=["one_year", "five_year"], how="any")
        .reset_index()
    )
    shared = metric_pairs.groupby("cbsa_code", as_index=False).agg(
        shared_metric_count=("metric_id", "nunique"),
        supporting_metric_ids=("metric_id", lambda values: ", ".join(sorted(values))),
    )
    result = paired.merge(shared, on="cbsa_code", how="left")
    result["shared_metric_count"] = result["shared_metric_count"].fillna(0).astype(int)
    result["supporting_metric_ids"] = result["supporting_metric_ids"].fillna("")
    gate = config["engine"]["scoring"]["production_signal_threshold"]
    result["turn_status"] = result.apply(
        lambda row: turn_status(
            row.get("frame_momentum_score_short"),
            row.get("frame_momentum_score_medium"),
            row.get("trajectory_salience_percentile_short"),
            row.get("trajectory_salience_percentile_medium"),
            row["shared_metric_count"],
            2,
            gate,
        ),
        axis=1,
    )
    result["method_window_pair"] = "five_year_vs_one_year"
    result["signal_gate_percentile"] = gate
    return result[
        [
            "cbsa_code",
            "cbsa_name",
            "frame_id",
            "method_window_pair",
            "end_year",
            "frame_momentum_score_short",
            "frame_momentum_score_medium",
            "trajectory_salience_percentile_short",
            "trajectory_salience_percentile_medium",
            "shared_metric_count",
            "supporting_metric_ids",
            "signal_gate_percentile",
            "turn_status",
        ]
    ]


def build_sensitivity_summary(frame: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Summarize nested sensitivity cuts without selecting a new scoring model."""

    rows: list[dict[str, Any]] = []
    eligible = frame.loc[frame["coverage_status"] == "eligible"]
    for (frame_id, window_name, end_year), group in eligible.groupby(["frame_id", "window_name", "end_year"]):
        for threshold in config["engine"]["scoring"]["signal_thresholds"]:
            selected = group.loc[group["trajectory_salience_percentile"] >= threshold]
            rows.append(
                {
                    "frame_id": frame_id,
                    "window_name": window_name,
                    "end_year": end_year,
                    "threshold_percentile": threshold,
                    "eligible_cbsa_count": len(group),
                    "selected_cbsa_count": len(selected),
                    "gaining_ground_count": int((selected["movement_direction"] == "gaining_ground").sum()),
                    "losing_ground_count": int((selected["movement_direction"] == "losing_ground").sum()),
                }
            )
    return pd.DataFrame(rows)
