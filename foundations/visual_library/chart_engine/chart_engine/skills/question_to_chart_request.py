"""
Implementation of skills/question_to_chart_request.md.

Pure function: (question metadata + result df) -> ChartRequest.
Never calls render() itself — see the skill spec for why.

The chart_rules / metric_catalog dicts are passed in rather than loaded
from disk here, so this stays testable without touching real YAML files
or your actual semantic layer. In production, load them once at process
start and pass the same dicts into every call.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..request import BenchmarkConfig, ChartRequest, NumberFormat, RunContext
from ..specs import load_spec
from ..theme import Theme


class ChartMappingError(ValueError):
    """Raised when this skill can't confidently resolve a chart_type or field mapping."""


@dataclass
class ResultProfile:
    """Mirrors app/charts/profiler.py's output shape — subset needed here."""
    row_count: int
    has_time_series: bool
    dimension_count: int
    inferred_shape: str   # e.g. "ranking_single_metric", "trend_multi_series"


TITLE_TEMPLATES = {
    "ranking": "{metric}, Top Metros",
    "trend": "{metric} Over Time",
    "compare_selected": "{metric} by Metro",
    "distribution": "Distribution of {metric}",
    "benchmark": "{metric} vs. Benchmark",
    "growth": "{metric} Growth",
}


def infer_column_roles(
    result_df: pd.DataFrame,
    result_profile: ResultProfile,
    required_fields: list[str],
) -> dict:
    """
    Minimal starting heuristic — dtype + position based. Expand as real
    QA cases surface (see 'Optimization Levers' in the skill spec).
    """
    numeric_cols = [c for c in result_df.columns if pd.api.types.is_numeric_dtype(result_df[c])]
    non_numeric_cols = [c for c in result_df.columns if c not in numeric_cols]
    time_cols = [c for c in result_df.columns if c.lower() in ("year", "period", "date")]

    mapping = {}

    if "value" in required_fields and numeric_cols:
        candidates = [c for c in numeric_cols if c not in time_cols]
        if len(candidates) != 1:
            raise ChartMappingError(
                f"Can't confidently resolve 'value' field: candidates are {candidates}. "
                f"Result columns: {list(result_df.columns)}"
            )
        mapping[candidates[0]] = "value"

    if "period" in required_fields:
        if len(time_cols) != 1:
            raise ChartMappingError(
                f"Can't confidently resolve 'period' field: candidates are {time_cols}."
            )
        mapping[time_cols[0]] = "period"

    dimension_candidates = [c for c in non_numeric_cols if c not in time_cols]
    if "entity" in required_fields:
        if len(dimension_candidates) != 1:
            raise ChartMappingError(
                f"Can't confidently resolve 'entity' field: candidates are {dimension_candidates}."
            )
        mapping[dimension_candidates[0]] = "entity"
    if "series" in required_fields:
        if len(dimension_candidates) != 1:
            raise ChartMappingError(
                f"Can't confidently resolve 'series' field: candidates are {dimension_candidates}."
            )
        mapping[dimension_candidates[0]] = "series"

    return mapping


def question_to_chart_request(
    *,
    question_type: str,
    result_df: pd.DataFrame,
    result_profile: ResultProfile,
    question_text: str,
    metric_id: str,
    geo_level: str,
    chart_rules: dict,
    metric_catalog: dict,
    theme: Theme,
    run_context: RunContext | None = None,
) -> ChartRequest:
    # 1. chart type selection — fail loud, don't guess
    try:
        chart_type = chart_rules[question_type][result_profile.inferred_shape]
    except KeyError:
        raise ChartMappingError(
            f"No chart_rules entry for question_type='{question_type}', "
            f"shape='{result_profile.inferred_shape}'. This is a chart_rules.yml "
            f"gap, not something to default around."
        )

    # 2. field resolution
    spec = load_spec_for_chart_type(chart_type)
    column_mapping = infer_column_roles(result_df, result_profile, spec.required_fields)

    # 3. benchmark
    benchmark = None
    if question_type == "benchmark" or spec.default_benchmark is not None:
        benchmark = BenchmarkConfig(
            kind="national_median",
            value=metric_catalog.get(metric_id, {}).get("national_median"),
            label="US National Median",
        )

    # 4. number format
    unit_format = metric_catalog.get(metric_id, {}).get("unit_format", {})
    number_format = NumberFormat(**unit_format) if unit_format else None

    # 5. text
    display_name = metric_catalog.get(metric_id, {}).get("display_name", metric_id)
    title = TITLE_TEMPLATES.get(question_type, "{metric}").format(metric=display_name)
    subtitle = f"{geo_level.title()} grain" if geo_level != "cbsa" else None

    return ChartRequest(
        data=result_df,
        chart_type=chart_type,
        theme=theme,
        column_mapping=column_mapping,
        benchmark=benchmark,
        number_format=number_format,
        title=title,
        subtitle=subtitle,
        run_context=run_context,
    )


def load_spec_for_chart_type(chart_type: str):
    from ..registry import CHART_REGISTRY
    reg = CHART_REGISTRY[chart_type]
    return load_spec(reg.spec_path)
