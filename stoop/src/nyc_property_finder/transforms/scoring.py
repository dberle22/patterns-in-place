"""Transparent MVP scoring functions."""

from __future__ import annotations

import math

import pandas as pd


DEFAULT_SCORE_WEIGHTS = {"neighborhood": 0.40, "mobility": 0.25, "personal_fit": 0.35}
NEIGHBORHOOD_METRIC_COLUMNS = ["median_income", "median_rent", "pct_bachelors_plus"]


def is_missing(value: object) -> bool:
    """Return true for scalar null values used by pandas and Python."""

    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _as_float(value: object) -> float | None:
    """Coerce a scalar value to float, preserving missing values as None."""

    if is_missing(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number):
        return None
    return number


def clamp_score(value: float, min_value: float = 0, max_value: float = 100) -> float:
    """Constrain a score to a readable 0-100 range."""

    return float(max(min_value, min(max_value, value)))


def normalize_percent(value: object) -> float | None:
    """Normalize a percent-like value to 0-1.

    Sprint 2 sources may use either 0-1 fractions or 0-100 percentages. The MVP
    scoring path accepts both and clamps to a readable range.
    """

    number = _as_float(value)
    if number is None:
        return None
    if number > 1:
        number = number / 100
    return max(0.0, min(1.0, number))


def neighborhood_score(row: pd.Series) -> float | None:
    """Compute an MVP neighborhood score without zero-filling missing metrics."""

    income = _as_float(row.get("median_income"))
    median_rent = _as_float(row.get("median_rent"))
    education = normalize_percent(row.get("pct_bachelors_plus"))
    component_scores: list[tuple[float, float]] = []

    if income is not None:
        component_scores.append((min(income / 150_000, 1.0) * 40, 40))
    if education is not None:
        component_scores.append((education * 35, 35))
    if median_rent is not None:
        rent_score = max(0.0, 1.0 - min(median_rent / 5_000, 1.0)) * 25
        component_scores.append((rent_score, 25))

    if not component_scores:
        return None

    earned = sum(score for score, _ in component_scores)
    possible = sum(weight for _, weight in component_scores)
    return clamp_score(earned / possible * 100)


def neighborhood_score_status(row: pd.Series) -> str:
    """Describe whether neighborhood score inputs were available."""

    available = [not is_missing(row.get(column)) for column in NEIGHBORHOOD_METRIC_COLUMNS]
    if not any(available):
        return "unavailable"
    if not all(available):
        return "partial"
    return "scored"


def mobility_score(nearest_subway_distance_miles: float | None, subway_lines_count: int | None = 0) -> float | None:
    """Score mobility from subway proximity and line access."""

    distance = _as_float(nearest_subway_distance_miles)
    if distance is None:
        return None
    line_count = int(_as_float(subway_lines_count) or 0)
    proximity_component = max(0, 75 - distance * 100)
    line_component = min(line_count * 5, 25)
    return clamp_score(proximity_component + line_component)


def personal_fit_score(
    poi_count: int | None,
    preferred_category_matches: int | None = 0,
    poi_data_available: bool = True,
) -> float | None:
    """Score fit from nearby saved places."""

    if not poi_data_available:
        return None
    poi_component = min(int(_as_float(poi_count) or 0) * 8, 70)
    category_component = min(int(_as_float(preferred_category_matches) or 0) * 10, 30)
    return clamp_score(poi_component + category_component)


def property_fit_score(
    neighborhood: float | None,
    mobility: float | None,
    personal_fit: float | None,
    weights: dict[str, float] | None = None,
) -> float | None:
    """Combine available component scores with explicit reweighting."""

    weights = weights or DEFAULT_SCORE_WEIGHTS
    components = {
        "neighborhood": neighborhood,
        "mobility": mobility,
        "personal_fit": personal_fit,
    }
    available = {
        name: _as_float(score)
        for name, score in components.items()
        if not is_missing(score)
    }
    if not available:
        return None

    available_weight = sum(weights[name] for name in available)
    if available_weight <= 0:
        return None
    weighted_score = sum(score * weights[name] for name, score in available.items()) / available_weight
    return clamp_score(weighted_score)


def property_fit_score_status(
    neighborhood: float | None,
    mobility: float | None,
    personal_fit: float | None,
) -> str:
    """Describe whether total score used all components or reweighted inputs."""

    scores = [neighborhood, mobility, personal_fit]
    available = [not is_missing(score) for score in scores]
    if not any(available):
        return "unavailable"
    if not all(available):
        return "reweighted_missing_components"
    return "scored"
