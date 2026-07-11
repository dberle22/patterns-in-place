"""
Prep-level tests for the matplotlib-backed geo chart ports.

These tests stay valuable even without matplotlib installed because they lock
down the data-shaping rules that the renderers rely on.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chart_engine.registry import CHART_REGISTRY
from chart_engine.specs import load_spec
from tests.fixtures import (
    bivariate_choropleth_fixture,
    choropleth_fixture,
    hexbin_fixture,
    highlight_context_map_fixture,
    proportional_symbol_map_fixture,
)


class GeoPrepTests(unittest.TestCase):
    def test_choropleth_prep_preserves_highlight_and_metric(self) -> None:
        reg = CHART_REGISTRY["choropleth"]
        spec = load_spec(reg.spec_path)
        prepped = reg.prep_fn(choropleth_fixture(), spec)

        self.assertIn("metric_value", prepped.columns)
        self.assertIn("highlight_flag", prepped.columns)
        self.assertTrue(prepped["highlight_flag"].any())

    def test_hexbin_prep_drops_missing_xy_and_keeps_highlight(self) -> None:
        reg = CHART_REGISTRY["hexbin"]
        spec = load_spec(reg.spec_path)
        prepped = reg.prep_fn(hexbin_fixture(), spec)

        self.assertEqual(len(prepped), 6)
        self.assertTrue(prepped["highlight_flag"].any())

    def test_highlight_context_map_prep_keeps_context_flags(self) -> None:
        reg = CHART_REGISTRY["highlight_context_map"]
        spec = load_spec(reg.spec_path)
        prepped = reg.prep_fn(highlight_context_map_fixture(), spec)

        self.assertEqual(prepped["highlight_flag"].sum(), 1)
        self.assertEqual(prepped["neighbor_flag"].sum(), 1)

    def test_proportional_symbol_map_prep_keeps_coordinates(self) -> None:
        reg = CHART_REGISTRY["proportional_symbol_map"]
        spec = load_spec(reg.spec_path)
        prepped = reg.prep_fn(proportional_symbol_map_fixture(), spec)

        self.assertTrue(prepped["lon"].notna().all())
        self.assertTrue(prepped["lat"].notna().all())

    def test_bivariate_prep_computes_classes(self) -> None:
        reg = CHART_REGISTRY["bivariate_choropleth"]
        spec = load_spec(reg.spec_path)
        prepped = reg.prep_fn(bivariate_choropleth_fixture(), spec)

        self.assertIn("bivar_class", prepped.columns)
        self.assertTrue(prepped["bivar_class"].notna().all())


if __name__ == "__main__":
    unittest.main()
