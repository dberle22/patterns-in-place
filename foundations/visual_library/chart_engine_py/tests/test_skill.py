"""
Tests for question_to_chart_request().

This skill is the bridge between analytics output and the chart engine, so we
want loud failures when mapping rules or column-role inference are ambiguous.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chart_engine import RunContext, Theme, render
from chart_engine.skills.question_to_chart_request import (
    ChartMappingError,
    ResultProfile,
    question_to_chart_request,
)


class QuestionToChartRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.theme = Theme.default()
        cls.chart_rules = {
            "ranking": {"ranking_single_metric": "bar_chart"},
            "trend": {"trend_multi_series": "line_chart"},
        }
        cls.metric_catalog = {
            "rent_to_income": {
                "display_name": "Rent-to-Income Ratio",
                "national_median": 31.4,
                "unit_format": {"unit": "percent", "decimals": 1},
            }
        }

    def test_unmapped_question_type_and_shape_raises(self) -> None:
        with self.assertRaises(ChartMappingError) as exc:
            question_to_chart_request(
                question_type="distribution",
                result_df=pd.DataFrame({"metric_value": [1.0]}),
                result_profile=ResultProfile(
                    row_count=1,
                    has_time_series=False,
                    dimension_count=0,
                    inferred_shape="single_value",
                ),
                question_text="Example question",
                metric_id="rent_to_income",
                geo_level="cbsa",
                chart_rules=self.chart_rules,
                metric_catalog=self.metric_catalog,
                theme=self.theme,
            )

        self.assertIn("No chart_rules entry", str(exc.exception))

    def test_ambiguous_dimension_inference_raises(self) -> None:
        result_df = pd.DataFrame(
            {
                "cbsa_name": ["A", "B"],
                "state_name": ["VA", "NC"],
                "metric_value": [1.0, 2.0],
            }
        )

        with self.assertRaises(ChartMappingError) as exc:
            question_to_chart_request(
                question_type="ranking",
                result_df=result_df,
                result_profile=ResultProfile(
                    row_count=2,
                    has_time_series=False,
                    dimension_count=2,
                    inferred_shape="ranking_single_metric",
                ),
                question_text="Which metros lead?",
                metric_id="rent_to_income",
                geo_level="cbsa",
                chart_rules=self.chart_rules,
                metric_catalog=self.metric_catalog,
                theme=self.theme,
            )

        self.assertIn("entity", str(exc.exception))
        self.assertIn("cbsa_name", str(exc.exception))
        self.assertIn("state_name", str(exc.exception))

    def test_happy_path_produces_request_render_accepts(self) -> None:
        result_df = pd.DataFrame(
            {
                "cbsa_name": ["Miami", "Los Angeles", "New York"],
                "rent_to_income_pct": [0.421, 0.398, 0.375],
            }
        )

        request = question_to_chart_request(
            question_type="ranking",
            result_df=result_df,
            result_profile=ResultProfile(
                row_count=3,
                has_time_series=False,
                dimension_count=1,
                inferred_shape="ranking_single_metric",
            ),
            question_text="Which metros have the highest rent burden?",
            metric_id="rent_to_income",
            geo_level="cbsa",
            chart_rules=self.chart_rules,
            metric_catalog=self.metric_catalog,
            theme=self.theme,
            run_context=RunContext(question_id="q1", source="publisher"),
        )

        self.assertEqual(request.chart_type, "bar_chart")
        self.assertEqual(request.column_mapping, {"cbsa_name": "entity", "rent_to_income_pct": "value"})

        result = render(request)
        self.assertIsNotNone(result.chart)


if __name__ == "__main__":
    unittest.main()
