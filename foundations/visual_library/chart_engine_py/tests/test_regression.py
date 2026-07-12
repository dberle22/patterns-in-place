"""
Golden regression tests for rendered chart output.

These tests compare a deterministic chart spec snapshot against a committed
golden JSON file. The goal is to catch accidental visual-contract changes in
the Altair output structure as we keep porting chart types.
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chart_engine.orchestrator import render
from chart_engine.request import ChartRequest, NumberFormat
from chart_engine.theme import Theme
from tests.fixtures import (
    age_pyramid_fixture,
    bar_fixture,
    boxplot_fixture,
    bump_chart_fixture,
    correlation_heatmap_fixture,
    heatmap_table_fixture,
    line_fixture,
    scatter_fixture,
    slopegraph_fixture,
    strength_strip_fixture,
    waterfall_fixture,
)

GOLDEN_DIR = PROJECT_ROOT / "tests" / "golden"


def _normalize_chart_payload(data: dict) -> dict:
    """
    Keep the regression surface focused on chart structure, not serializer version.

    Altair writes a Vega-Lite schema URL that changes across library versions
    even when the chart spec is otherwise identical. Normalizing that field
    keeps these goldens stable across environments.
    """
    normalized = json.loads(json.dumps(data))
    if "$schema" in normalized and isinstance(normalized["$schema"], str):
        normalized["$schema"] = "https://vega.github.io/schema/vega-lite/normalized.json"
    view_config = normalized.get("config", {}).get("view")
    if isinstance(view_config, dict):
        view_config.pop("continuousWidth", None)
        view_config.pop("continuousHeight", None)
    datasets = normalized.get("datasets")
    if isinstance(datasets, dict):
        dataset_name_map = {
            old_name: f"dataset_{index}"
            for index, old_name in enumerate(sorted(datasets), start=1)
        }
        normalized["datasets"] = {
            dataset_name_map[old_name]: datasets[old_name]
            for old_name in sorted(datasets)
        }
        _replace_dataset_names(normalized, dataset_name_map)
    return normalized


def _replace_dataset_names(value, dataset_name_map: dict[str, str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "name" and isinstance(child, str) and child in dataset_name_map:
                value[key] = dataset_name_map[child]
            else:
                _replace_dataset_names(child, dataset_name_map)
    elif isinstance(value, list):
        for child in value:
            _replace_dataset_names(child, dataset_name_map)


def _canonical_json(data: dict) -> str:
    return json.dumps(_normalize_chart_payload(data), indent=2, sort_keys=True) + "\n"


class RegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.theme = Theme.default()

    def _assert_matches_golden(self, name: str, payload: dict) -> None:
        golden_path = GOLDEN_DIR / f"{name}.json"
        rendered = _canonical_json(payload)

        if os.getenv("UPDATE_GOLDEN") == "1":
            golden_path.parent.mkdir(parents=True, exist_ok=True)
            golden_path.write_text(rendered)

        expected = _canonical_json(json.loads(golden_path.read_text()))
        self.assertEqual(rendered, expected)

    def _render_chart(self, chart_type: str, data: pd.DataFrame) -> dict:
        request = ChartRequest(
            data=data,
            chart_type=chart_type,
            theme=self.theme,
            number_format=NumberFormat(unit="count", decimals=0),
        )
        return render(request).chart.to_dict()

    def test_scatter_chart_matches_golden(self) -> None:
        chart_dict = self._render_chart("scatter", scatter_fixture())
        self._assert_matches_golden("scatter", chart_dict)

    def test_bar_chart_matches_golden(self) -> None:
        request = ChartRequest(
            data=bar_fixture(),
            chart_type="bar_chart",
            theme=self.theme,
            column_mapping={
                "geo_name": "entity",
                "metric_value": "value",
            },
            number_format=NumberFormat(unit="percent", decimals=1),
        )
        chart_dict = render(request).chart.to_dict()
        self._assert_matches_golden("bar_chart", chart_dict)

    def test_line_chart_matches_golden(self) -> None:
        chart_dict = self._render_chart("line_chart", line_fixture())
        self._assert_matches_golden("line_chart", chart_dict)

    def test_slopegraph_matches_golden(self) -> None:
        chart_dict = self._render_chart("slopegraph", slopegraph_fixture())
        self._assert_matches_golden("slopegraph", chart_dict)

    def test_boxplot_matches_golden(self) -> None:
        chart_dict = self._render_chart("boxplot", boxplot_fixture())
        self._assert_matches_golden("boxplot", chart_dict)

    def test_heatmap_table_matches_golden(self) -> None:
        chart_dict = self._render_chart("heatmap_table", heatmap_table_fixture())
        self._assert_matches_golden("heatmap_table", chart_dict)

    def test_bump_chart_matches_golden(self) -> None:
        chart_dict = self._render_chart("bump_chart", bump_chart_fixture())
        self._assert_matches_golden("bump_chart", chart_dict)

    def test_waterfall_matches_golden(self) -> None:
        chart_dict = self._render_chart("waterfall", waterfall_fixture())
        self._assert_matches_golden("waterfall", chart_dict)

    def test_strength_strip_matches_golden(self) -> None:
        chart_dict = self._render_chart("strength_strip", strength_strip_fixture())
        self._assert_matches_golden("strength_strip", chart_dict)

    def test_correlation_heatmap_matches_golden(self) -> None:
        chart_dict = self._render_chart("correlation_heatmap", correlation_heatmap_fixture())
        self._assert_matches_golden("correlation_heatmap", chart_dict)

    def test_age_pyramid_matches_golden(self) -> None:
        chart_dict = self._render_chart("age_pyramid", age_pyramid_fixture())
        self._assert_matches_golden("age_pyramid", chart_dict)


if __name__ == "__main__":
    unittest.main()
