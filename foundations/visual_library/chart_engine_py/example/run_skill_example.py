"""
Simulates what the publisher/chatbot would do: take a question's
metadata + result df, use the skill to build a ChartRequest, then
actually render it. No chart-type or field-mapping knowledge lives
in this script — it's all resolved by the skill.
"""

import sys

import pandas as pd

from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from chart_engine import RunContext, Theme, render
from chart_engine.skills.question_to_chart_request import (
    ResultProfile,
    question_to_chart_request,
)

theme = Theme.default()

# Fake, minimal versions of your real chart_rules.yml / metric_catalog.yml
chart_rules = {
    "ranking": {"ranking_single_metric": "bar_chart"},
    "trend": {"trend_multi_series": "line_chart"},
}
metric_catalog = {
    "rent_to_income": {
        "display_name": "Rent-to-Income Ratio",
        "national_median": 31.4,
        "unit_format": {"unit": "percent", "decimals": 1},
    }
}

result_df = pd.DataFrame({
    "cbsa_name": ["Miami", "Los Angeles", "New York", "Riverside", "San Diego"],
    "rent_to_income_pct": [42.1, 39.8, 37.5, 36.2, 35.9],
})
profile = ResultProfile(row_count=5, has_time_series=False, dimension_count=1,
                         inferred_shape="ranking_single_metric")

request = question_to_chart_request(
    question_type="ranking",
    result_df=result_df,
    result_profile=profile,
    question_text="Which metros have the highest rent-to-income ratios?",
    metric_id="rent_to_income",
    geo_level="cbsa",
    chart_rules=chart_rules,
    metric_catalog=metric_catalog,
    theme=theme,
    run_context=RunContext(question_id="q014", source="publisher"),
)

print(f"Skill resolved chart_type: {request.chart_type}")
print(f"Skill resolved column_mapping: {request.column_mapping}")
print(f"Skill resolved title: {request.title}")
print(f"Skill resolved benchmark: {request.benchmark}")

result = render(request)
result.chart.save(str(Path(__file__).parent / "output_from_skill.html"))
print("Rendered and saved output_from_skill.html")
