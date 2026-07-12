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
        spec = spec.__class__(**{**spec.__dict__, "runtime_config": {"variant": "diverging", "facet_by": "group"}})
        prepped = reg.prep_fn(choropleth_fixture(), spec)

        self.assertIn("metric_value", prepped.columns)
        self.assertIn("highlight_flag", prepped.columns)
        self.assertTrue(prepped["highlight_flag"].any())
        self.assertIn("fill_value", prepped.columns)
        self.assertIn("map_variant", prepped.columns)
        self.assertTrue(prepped["fill_value"].ne(prepped["metric_value"]).any())

    def test_hexbin_prep_drops_missing_xy_and_keeps_highlight(self) -> None:
        reg = CHART_REGISTRY["hexbin"]
        spec = load_spec(reg.spec_path)
        spec = spec.__class__(
            **{
                **spec.__dict__,
                "runtime_config": {
                    "question_id": "hexbin_regional_density_compare",
                    "group_values": ["Target", "Peer"],
                    "facet_by": "group",
                    "use_weights": True,
                },
            }
        )
        prepped = reg.prep_fn(hexbin_fixture(), spec)

        self.assertEqual(len(prepped), 8)
        self.assertTrue(prepped["highlight_flag"].any())
        self.assertIn("weight_value", prepped.columns)
        self.assertEqual(prepped["group"].nunique(), 2)
        self.assertEqual(prepped.attrs["chart_config"]["facet_by"], "group")

    def test_hexbin_prep_rejects_negative_weights(self) -> None:
        reg = CHART_REGISTRY["hexbin"]
        spec = load_spec(reg.spec_path)
        bad_df = hexbin_fixture().copy()
        bad_df.loc[0, "weight_value"] = -1

        with self.assertRaisesRegex(ValueError, "non-negative"):
            reg.prep_fn(bad_df, spec)

    def test_highlight_context_map_prep_keeps_context_flags(self) -> None:
        reg = CHART_REGISTRY["highlight_context_map"]
        spec = load_spec(reg.spec_path)
        spec = spec.__class__(**{**spec.__dict__, "runtime_config": {"variant": "focus_only", "require_highlight": True}})
        prepped = reg.prep_fn(highlight_context_map_fixture(), spec)

        self.assertEqual(prepped["highlight_flag"].sum(), 2)
        self.assertEqual(prepped["neighbor_flag"].sum(), 2)
        self.assertIn("focus_role", prepped.columns)

    def test_proportional_symbol_map_prep_keeps_coordinates(self) -> None:
        reg = CHART_REGISTRY["proportional_symbol_map"]
        spec = load_spec(reg.spec_path)
        spec = spec.__class__(**{**spec.__dict__, "runtime_config": {"top_n": 3, "label_strategy": "top_n", "label_top_n": 2}})
        prepped = reg.prep_fn(proportional_symbol_map_fixture(), spec)

        self.assertTrue(prepped["lon"].notna().all())
        self.assertTrue(prepped["lat"].notna().all())
        self.assertIn("size_rank", prepped.columns)
        self.assertLessEqual(len(prepped), 3)

    def test_bivariate_prep_computes_classes(self) -> None:
        reg = CHART_REGISTRY["bivariate_choropleth"]
        spec = load_spec(reg.spec_path)
        spec = spec.__class__(**{**spec.__dict__, "runtime_config": {"bin_by": ["group"]}})
        prepped = reg.prep_fn(bivariate_choropleth_fixture(), spec)

        self.assertIn("bivar_class", prepped.columns)
        self.assertTrue(prepped["bivar_class"].notna().all())
        self.assertEqual(prepped["group"].nunique(), 2)


if __name__ == "__main__":
    unittest.main()
