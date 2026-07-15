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
from unittest.mock import MagicMock, patch

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chart_engine.orchestrator import render
from chart_engine.request import BenchmarkConfig, ChartRequest, NumberFormat, OutputConfig
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
        self.assertIn("entity", result.prepped_data.columns)
        self.assertIn("value", result.prepped_data.columns)

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

    def test_altair_png_persistence_routes_through_vl_convert(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame({"entity": ["A", "B"], "value": [0.12, 0.34]}),
            chart_type="bar_chart",
            theme=self.theme,
            output=OutputConfig(save=True, path=Path("ignored.png"), scale_factor=2),
        )

        fake_vlc = MagicMock()
        fake_vlc.vegalite_to_png.return_value = b"png-bytes"
        fake_vlc.get_vegalite_versions.return_value = ["5.8", "5.14"]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "bar_chart.png"
            request.output.path = output_path
            with patch.dict(sys.modules, {"vl_convert": fake_vlc}):
                result = render(request)
            self.assertEqual(result.output_path, output_path)
            self.assertTrue(output_path.exists())

        fake_vlc.vegalite_to_png.assert_called_once()
        _, kwargs = fake_vlc.vegalite_to_png.call_args
        self.assertEqual(kwargs["vl_version"], "5.8")
        self.assertEqual(kwargs["scale"], 2)

    def test_bar_chart_uses_axis_labels_and_benchmark_annotation(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_name": ["Miami-Fort Lauderdale-West Palm Beach, FL", "New York-Newark-Jersey City, NY-NJ-PA"],
                    "metric_value": [63.1, 57.4],
                    "metric_label": ["Share of renter households spending 30%+ of income on rent"] * 2,
                    "time_window": ["2023 level", "2023 level"],
                    "group": ["Top CBSAs by renter cost burden"] * 2,
                    "benchmark_value": [50.4, 50.4],
                    "source": ["ACS", "ACS"],
                    "vintage": ["2023", "2023"],
                }
            ),
            chart_type="bar_chart",
            theme=self.theme,
            column_mapping={"geo_name": "entity", "metric_value": "value"},
            benchmark=BenchmarkConfig(kind="custom", value=50.4, label="US benchmark"),
            number_format=NumberFormat(unit="percent", decimals=1),
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertEqual(result.chart_type, "bar_chart")
        self.assertEqual(chart_dict["title"]["text"], "Share of renter households spending 30%+ of income on rent")
        self.assertEqual(chart_dict["layer"][0]["mark"], "bar")
        self.assertEqual(chart_dict["layer"][1]["mark"]["type"], "rule")
        self.assertEqual(chart_dict["layer"][2]["mark"]["type"], "text")
        self.assertEqual(chart_dict["layer"][0]["encoding"]["y"]["field"], "entity_axis_label")

    def test_bar_chart_supports_diverging_benchmark_delta_variant(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_name": ["Alabama", "California", "New York"],
                    "metric_value": [54.0, 47.0, 51.0],
                    "benchmark_value": [50.0, 50.0, 50.0],
                    "metric_label": ["Real per-capita income"] * 3,
                    "time_window": ["2024", "2024", "2024"],
                    "source": ["BEA", "BEA", "BEA"],
                    "vintage": ["2024", "2024", "2024"],
                }
            ),
            chart_type="bar_chart",
            theme=self.theme,
            column_mapping={"geo_name": "entity", "metric_value": "value"},
            field_values={"bar_variant": "diverging"},
            number_format=NumberFormat(unit="percent", decimals=1),
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertEqual(chart_dict["layer"][0]["encoding"]["x"]["field"], "benchmark_delta")
        self.assertEqual(chart_dict["layer"][1]["mark"]["type"], "rule")
        self.assertEqual(chart_dict["layer"][0]["encoding"]["color"]["field"], "delta_direction")

    def test_bar_chart_supports_stacked_composition_variant(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_name": ["A", "A", "B", "B"],
                    "metric_value": [0.62, 0.38, 0.55, 0.45],
                    "share_value": [0.62, 0.38, 0.55, 0.45],
                    "series": ["Owner", "Renter", "Owner", "Renter"],
                    "metric_label": ["Housing tenure mix"] * 4,
                    "time_window": ["2024", "2024", "2024", "2024"],
                    "source": ["ACS", "ACS", "ACS", "ACS"],
                    "vintage": ["2024", "2024", "2024", "2024"],
                }
            ),
            chart_type="bar_chart",
            theme=self.theme,
            column_mapping={"geo_name": "entity", "metric_value": "value"},
            field_values={"bar_variant": "stacked_100"},
            number_format=NumberFormat(unit="percent", decimals=1),
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertEqual(chart_dict["mark"], "bar")
        self.assertEqual(chart_dict["encoding"]["x"]["field"], "share_value")
        self.assertEqual(chart_dict["encoding"]["x"]["stack"], "zero")
        self.assertEqual(chart_dict["encoding"]["color"]["field"], "series")

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

    def test_scatter_chart_supports_reference_line_quadrants_and_color_highlight_mode(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_level": ["cbsa", "cbsa", "cbsa"],
                    "geo_id": ["1", "2", "3"],
                    "geo_name": ["A", "B", "C"],
                    "time_window": ["2024", "2024", "2024"],
                    "x_value": [10.0, 12.0, 15.0],
                    "y_value": [11.0, 14.0, 13.0],
                    "x_label": ["Opportunity", "Opportunity", "Opportunity"],
                    "y_label": ["Risk", "Risk", "Risk"],
                    "highlight_flag": [False, True, False],
                    "source": ["ACS", "ACS", "ACS"],
                    "vintage": ["2024", "2024", "2024"],
                }
            ),
            chart_type="scatter",
            theme=self.theme,
            number_format=NumberFormat(unit="count", decimals=0),
            field_values={"highlight_mode": "color", "add_reference_line": True, "add_quadrants": True},
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertEqual(chart_dict["layer"][0]["encoding"]["color"]["field"], "color_flag")
        self.assertEqual(chart_dict["layer"][2]["mark"]["type"], "line")
        self.assertEqual(chart_dict["layer"][3]["mark"]["type"], "rule")
        self.assertEqual(chart_dict["layer"][4]["mark"]["type"], "rule")

    def test_scatter_chart_rejects_mixed_geo_levels(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_level": ["cbsa", "county"],
                    "geo_id": ["1", "2"],
                    "geo_name": ["A", "B"],
                    "time_window": ["2024", "2024"],
                    "x_value": [10.0, 12.0],
                    "y_value": [11.0, 14.0],
                    "x_label": ["Opportunity", "Opportunity"],
                    "y_label": ["Risk", "Risk"],
                    "source": ["ACS", "ACS"],
                    "vintage": ["2024", "2024"],
                }
            ),
            chart_type="scatter",
            theme=self.theme,
            number_format=NumberFormat(unit="count", decimals=0),
        )

        with self.assertRaises(ValueError):
            render(request)

    def test_slopegraph_supports_rank_variant_and_top_n_selection(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_level": ["cbsa"] * 8,
                    "geo_id": ["1", "1", "2", "2", "3", "3", "4", "4"],
                    "geo_name": ["A", "A", "B", "B", "C", "C", "D", "D"],
                    "period": ["2019", "2023"] * 4,
                    "metric_id": ["m1"] * 8,
                    "metric_label": ["Jobs"] * 8,
                    "metric_value": [10.0, 15.0, 12.0, 13.0, 18.0, 11.0, 9.0, 8.0],
                    "highlight_flag": [False, False, False, False, True, True, False, False],
                    "source": ["ACS"] * 8,
                    "vintage": ["2023"] * 8,
                }
            ),
            chart_type="slopegraph",
            theme=self.theme,
            field_values={"variant": "rank", "top_n": 2, "order_by": "delta_value", "include_highlighted": True},
            return_prepped_data=True,
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertIsNotNone(result.prepped_data)
        self.assertEqual(set(result.prepped_data["geo_name"]), {"A", "B", "C"})
        self.assertEqual(chart_dict["layer"][0]["encoding"]["y"]["title"], "Rank")
        self.assertIn("Rank view; lower rank is better", chart_dict["title"]["subtitle"][0])

    def test_slopegraph_supports_explicit_periods_and_indexed_variant(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_level": ["cbsa"] * 6,
                    "geo_id": ["1", "1", "1", "2", "2", "2"],
                    "geo_name": ["A", "A", "A", "B", "B", "B"],
                    "period": ["2018", "2019", "2023", "2018", "2019", "2023"],
                    "metric_id": ["m1"] * 6,
                    "metric_label": ["Income"] * 6,
                    "metric_value": [90.0, 100.0, 120.0, 80.0, 100.0, 110.0],
                    "source": ["BEA"] * 6,
                    "vintage": ["2024"] * 6,
                }
            ),
            chart_type="slopegraph",
            theme=self.theme,
            field_values={"variant": "indexed", "start_period": "2019", "end_period": "2023"},
            number_format=NumberFormat(unit="index", decimals=1),
            return_prepped_data=True,
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertEqual(sorted(result.prepped_data["period"].unique().tolist()), ["2019", "2023"])
        self.assertEqual(chart_dict["layer"][0]["encoding"]["y"]["title"], "Income (2019 = 100)")
        self.assertIn("Indexed to 2019 = 100", chart_dict["title"]["subtitle"][0])

    def test_bump_chart_supports_peer_set_and_endpoint_metadata(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_level": ["cbsa"] * 12,
                    "geo_id": ["1", "1", "1", "2", "2", "2", "3", "3", "3", "4", "4", "4"],
                    "geo_name": ["Target", "Target", "Target", "Peer A", "Peer A", "Peer A", "Peer B", "Peer B", "Peer B", "Context", "Context", "Context"],
                    "period": ["2019", "2021", "2023"] * 4,
                    "metric_id": ["m1"] * 12,
                    "metric_label": ["Jobs"] * 12,
                    "metric_value": [10.0, 12.0, 15.0, 20.0, 19.0, 18.0, 14.0, 13.0, 16.0, 30.0, 28.0, 25.0],
                    "highlight_flag": [True, True, True, False, False, False, False, False, False, False, False, False],
                    "peer_flag": [True, True, True, True, True, True, True, True, True, False, False, False],
                    "source": ["ACS"] * 12,
                    "vintage": ["2023"] * 12,
                }
            ),
            chart_type="bump_chart",
            theme=self.theme,
            field_values={"entity_strategy": "peer_set"},
            return_prepped_data=True,
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertEqual(set(result.prepped_data["geo_name"]), {"Target", "Peer A", "Peer B"})
        self.assertIn("Fixed peer set", chart_dict["title"]["subtitle"][0])
        self.assertIn("rank_change", result.prepped_data.columns)

    def test_strength_strip_supports_benchmark_and_window_facet_prep(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_level": ["cbsa"] * 8,
                    "geo_id": ["1", "2", "1", "2", "1", "2", "1", "2"],
                    "geo_name": ["Target", "Peer", "Target", "Peer", "Target", "Peer", "Target", "Peer"],
                    "time_window": ["level", "level", "level", "level", "growth", "growth", "growth", "growth"],
                    "metric_id": ["m1", "m1", "m2", "m2", "m1", "m1", "m2", "m2"],
                    "metric_label": ["Jobs", "Jobs", "Income", "Income", "Jobs", "Jobs", "Income", "Income"],
                    "metric_value": [10.0, 20.0, 30.0, 40.0, 2.0, 5.0, -1.0, 3.0],
                    "benchmark_value": [15.0, 15.0, 35.0, 35.0, 4.0, 4.0, 0.0, 0.0],
                    "metric_group": ["Economy", "Economy", "Prosperity", "Prosperity", "Economy", "Economy", "Prosperity", "Prosperity"],
                    "highlight_flag": [True, False, True, False, True, False, True, False],
                    "benchmark_label": ["Benchmark"] * 8,
                    "source": ["ACS"] * 8,
                    "vintage": ["2023"] * 8,
                }
            ),
            chart_type="strength_strip",
            theme=self.theme,
            return_prepped_data=True,
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertIn("benchmark_delta", result.prepped_data.columns)
        self.assertTrue(result.prepped_data["benchmark_normalized_value"].notna().any())
        self.assertTrue("facet" in chart_dict or "vconcat" in chart_dict)

    def test_boxplot_supports_group_ordering_and_benchmark_overlay(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_level": ["cbsa"] * 6,
                    "geo_id": ["1", "2", "3", "4", "5", "6"],
                    "geo_name": ["A", "B", "C", "D", "E", "F"],
                    "time_window": ["2024"] * 6,
                    "metric_id": ["m1"] * 6,
                    "metric_label": ["Jobs"] * 6,
                    "metric_value": [10.0, 12.0, 16.0, 20.0, 14.0, 18.0],
                    "group": ["East", "East", "West", "West", "South", "South"],
                    "highlight_flag": [False, True, False, False, False, False],
                    "label_flag": [False, True, False, False, False, False],
                    "benchmark_value": [15.0] * 6,
                    "source": ["ACS"] * 6,
                    "vintage": ["2024"] * 6,
                }
            ),
            chart_type="boxplot",
            theme=self.theme,
            field_values={"show_benchmark": True},
            return_prepped_data=True,
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertEqual(result.prepped_data["box_group"].cat.categories.tolist(), ["West", "South", "East"])
        self.assertIn("group_median", result.prepped_data.columns)
        self.assertEqual(chart_dict["layer"][1]["mark"]["type"], "point")
        self.assertEqual(chart_dict["layer"][3]["mark"]["type"], "rule")

    def test_heatmap_table_supports_runtime_row_order_and_highlight_overlay(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_level": ["cbsa"] * 4,
                    "geo_id": ["1", "1", "2", "2"],
                    "geo_name": ["Target", "Target", "Peer", "Peer"],
                    "metric_id": ["m1", "m2", "m1", "m2"],
                    "metric_label": ["Jobs", "Income", "Jobs", "Income"],
                    "metric_value": [10.0, 20.0, 30.0, 40.0],
                    "normalized_value": [0.2, 0.4, 0.8, 0.9],
                    "highlight_flag": [True, True, False, False],
                    "time_window": ["2024"] * 4,
                    "source": ["ACS"] * 4,
                    "vintage": ["2024"] * 4,
                }
            ),
            chart_type="heatmap_table",
            theme=self.theme,
            field_values={"row_order": ["Target", "Peer"]},
            return_prepped_data=True,
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertEqual(result.prepped_data["row_label"].cat.categories.tolist(), ["Target", "Peer"])
        self.assertTrue(result.prepped_data["fill_value"].max() > 1)
        self.assertEqual(chart_dict["layer"][1]["mark"]["strokeWidth"], 2)

    def test_waterfall_supports_benchmark_panel_comparison_and_total_rows(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_level": ["cbsa"] * 6,
                    "geo_id": ["1"] * 6,
                    "geo_name": ["A"] * 6,
                    "time_window": ["2024"] * 6,
                    "total_label": ["Total"] * 6,
                    "component_id": ["c1", "c2", "c3", "c1", "c2", "c3"],
                    "component_label": ["Base", "Growth", "Adjustment", "Base", "Growth", "Adjustment"],
                    "component_value": [100.0, 20.0, -10.0, 90.0, 15.0, -5.0],
                    "sort_order": [1, 2, 3, 1, 2, 3],
                    "benchmark_label": ["Target", "Target", "Target", "Benchmark", "Benchmark", "Benchmark"],
                    "source": ["ACS"] * 6,
                    "vintage": ["2024"] * 6,
                }
            ),
            chart_type="waterfall",
            theme=self.theme,
            return_prepped_data=True,
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertEqual(set(result.prepped_data["row_type"]), {"component", "total"})
        self.assertEqual(result.prepped_data["waterfall_group"].nunique(), 2)
        self.assertIn("vconcat", chart_dict)

    def test_correlation_heatmap_supports_group_facets_and_method_metadata(self) -> None:
        request = ChartRequest(
            data=pd.DataFrame(
                {
                    "geo_level": ["cbsa"] * 18,
                    "geo_id": ["1", "1", "1", "2", "2", "2", "3", "3", "3", "4", "4", "4", "5", "5", "5", "6", "6", "6"],
                    "geo_name": ["A", "A", "A", "B", "B", "B", "C", "C", "C", "D", "D", "D", "E", "E", "E", "F", "F", "F"],
                    "time_window": ["2024"] * 18,
                    "metric_id": ["m1", "m2", "m3"] * 6,
                    "metric_label": ["Jobs", "Income", "Rent"] * 6,
                    "metric_value": [10.0, 20.0, 30.0, 30.0, 10.0, 28.0, 50.0, 40.0, 18.0, 20.0, 12.0, 22.0, 45.0, 32.0, 26.0, 15.0, 18.0, 29.0],
                    "group": ["Target", "Target", "Target", "Target", "Target", "Target", "Target", "Target", "Target", "Benchmark", "Benchmark", "Benchmark", "Benchmark", "Benchmark", "Benchmark", "Benchmark", "Benchmark", "Benchmark"],
                    "include_flag": [True] * 18,
                    "source": ["ACS"] * 18,
                    "vintage": ["2024"] * 18,
                }
            ),
            chart_type="correlation_heatmap",
            theme=self.theme,
            field_values={"facet_by": "group", "weak_threshold": 0.15},
            return_prepped_data=True,
        )

        result = render(request)
        chart_dict = result.chart.to_dict()

        self.assertEqual(result.prepped_data["group"].nunique(), 2)
        self.assertIn("missingness_policy", result.prepped_data.columns)
        self.assertIn("vconcat", chart_dict)
        self.assertIn("Missingness:", chart_dict["title"]["subtitle"][0])


if __name__ == "__main__":
    unittest.main()
