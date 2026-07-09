"""
Demonstrates the full ChartRequest path — benchmark line, annotation,
output persistence with run context — the parts render_chart() (the
convenience wrapper) doesn't expose.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from chart_engine import (
    Annotation,
    BenchmarkConfig,
    ChartRequest,
    OutputConfig,
    RunContext,
    Theme,
    render,
)

theme = Theme.from_yaml(Path(__file__).parent / "theme.yml")

# --- Bar chart with a national-median benchmark rule ------------------
rent_burden = pd.DataFrame({
    "cbsa_name": ["Miami", "Los Angeles", "New York", "Riverside", "San Diego"],
    "rent_to_income_pct": [42.1, 39.8, 37.5, 36.2, 35.9],
})

request = ChartRequest(
    data=rent_burden,
    chart_type="bar_chart",
    theme=theme,
    column_mapping={"cbsa_name": "entity", "rent_to_income_pct": "value"},
    title="Rent-to-Income Ratio, Top 5 Metros",
    benchmark=BenchmarkConfig(kind="national_median", value=31.4, label="US National Median"),
    output=OutputConfig(save=True, path=Path(__file__).parent / "output_bar_with_benchmark.html"),
    run_context=RunContext(question_id="q014", source="publisher"),
)
result = render(request)
print(f"Saved: {result.output_path}  (chart_type={result.chart_type})")

# --- Line chart with an inflection annotation --------------------------
income_trend = pd.DataFrame({
    "year": [2019, 2020, 2021, 2022, 2023] * 2,
    "median_income": [58000, 59500, 62000, 65500, 68200,
                       57000, 58200, 60100, 62800, 65000],
    "geo": ["Jacksonville"] * 5 + ["US National"] * 5,
})

request2 = ChartRequest(
    data=income_trend,
    chart_type="line_chart",
    theme=theme,
    column_mapping={"year": "period", "median_income": "value", "geo": "series"},
    annotations=[
        Annotation(kind="vline", x=2021, label="Post-2020 acceleration"),
    ],
    output=OutputConfig(save=True, path=Path(__file__).parent / "output_line_with_annotation.html"),
    run_context=RunContext(question_id="q014b", source="deep_dive"),
)
result2 = render(request2)
print(f"Saved: {result2.output_path}  (chart_type={result2.chart_type})")

# --- validate_only=True: QA batch runner use case, no render at all ---
request3 = ChartRequest(
    data=rent_burden,
    chart_type="bar_chart",
    theme=theme,
    column_mapping={"cbsa_name": "entity", "rent_to_income_pct": "value"},
    validate_only=True,
    return_prepped_data=True,
)
result3 = render(request3)
print(f"\nvalidate_only result: chart={result3.chart}, "
      f"prepped_data shape={result3.prepped_data.shape if result3.prepped_data is not None else None}")
