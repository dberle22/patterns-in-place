"""
End-to-end orchestration tests for the currently ported chart types.

These tests focus on the package contract rather than chart appearance:
validation-only flows, persistence dispatch, and helpful failure messages.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chart_engine.orchestrator import render
from chart_engine.request import ChartRequest, NumberFormat, OutputConfig
from chart_engine.theme import Theme


class OrchestratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.theme = Theme.default()

    def test_validate_only_skips_render_and_returns_prepped_data(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame({"entity": ["A", "B"], "value": [2.0, 1.0]}),
            chart_type="bar_chart",
            theme=self.theme,
            validate_only=True,
            return_prepped_data=True,
        )

        result = render(request)

        self.assertIsNone(result.chart)
        self.assertIsNotNone(result.prepped_data)
        self.assertEqual(list(result.prepped_data.columns), ["entity", "value"])

    def test_output_save_routes_through_persist(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame({"entity": ["A", "B"], "value": [2.0, 1.0]}),
            chart_type="bar_chart",
            theme=self.theme,
            output=OutputConfig(save=True, path=Path("ignored.html")),
        )

        with patch("chart_engine.orchestrator._persist", return_value=Path("saved.html")) as mocked_persist:
            result = render(request)

        mocked_persist.assert_called_once()
        self.assertEqual(result.output_path, Path("saved.html"))

    def test_unknown_chart_type_lists_available_types(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame({"entity": ["A"], "value": [1.0]}),
            chart_type="not_a_chart",
            theme=self.theme,
        )

        with self.assertRaises(KeyError) as exc:
            render(request)

        message = str(exc.exception)
        self.assertIn("Unknown chart_type", message)
        self.assertIn("bar_chart", message)
        self.assertIn("line_chart", message)

    def test_rendered_chart_can_persist_to_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "bar_chart.html"
            request = ChartRequest(
                data=pd.DataFrame({"entity": ["A", "B"], "value": [0.12, 0.34]}),
                chart_type="bar_chart",
                theme=self.theme,
                number_format=NumberFormat(unit="percent", decimals=1),
                output=OutputConfig(save=True, path=output_path),
            )

            result = render(request)

            self.assertEqual(result.output_path, output_path)
            self.assertTrue(output_path.exists())

    def test_scatter_chart_renders_with_labels_and_grouping(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_level": ["cbsa", "cbsa", "cbsa"],
                    "geo_id": ["1", "2", "3"],
                    "geo_name": ["A", "B", "C"],
                    "time_window": ["2023", "2023", "2023"],
                    "x_value": [10.0, 12.0, 15.0],
                    "y_value": [20.0, 22.0, 28.0],
                    "x_label": ["X metric", "X metric", "X metric"],
                    "y_label": ["Y metric", "Y metric", "Y metric"],
                    "group": ["South", "South", "West"],
                    "size_value": [100, 200, 150],
                    "label_flag": [False, True, False],
                    "source": ["ACS", "ACS", "ACS"],
                    "vintage": ["2023", "2023", "2023"],
                }
            ),
            chart_type="scatter",
            theme=self.theme,
            number_format=NumberFormat(unit="count", decimals=0),
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertEqual(result.chart_type, "scatter")
        self.assertEqual(chart_dict["layer"][0]["mark"]["type"], "circle")
        self.assertEqual(chart_dict["layer"][0]["encoding"]["x"]["title"], "X metric")
        self.assertEqual(chart_dict["layer"][0]["encoding"]["y"]["title"], "Y metric")


if __name__ == "__main__":
    unittest.main()
