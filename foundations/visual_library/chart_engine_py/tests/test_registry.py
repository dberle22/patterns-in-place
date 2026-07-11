"""
Registry-level tests for generated specs and renderer wiring.

The registry is the package seam that must stay boring: each entry needs a
loadable spec and the expected prep/render function shape.
"""

from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chart_engine.registry import CHART_REGISTRY
from chart_engine.specs import load_spec


class RegistryTests(unittest.TestCase):
    def test_registered_specs_exist_and_load(self) -> None:
        for chart_type, registration in CHART_REGISTRY.items():
            with self.subTest(chart_type=chart_type):
                self.assertTrue(registration.spec_path.exists())
                spec = load_spec(registration.spec_path)
                self.assertEqual(spec.chart_type, chart_type)

    def test_prep_functions_take_df_and_spec(self) -> None:
        for chart_type, registration in CHART_REGISTRY.items():
            with self.subTest(chart_type=chart_type):
                params = list(inspect.signature(registration.prep_fn).parameters)
                self.assertEqual(params, ["df", "spec"])

    def test_render_functions_take_df_spec_and_request(self) -> None:
        for chart_type, registration in CHART_REGISTRY.items():
            with self.subTest(chart_type=chart_type):
                params = list(inspect.signature(registration.render_fn).parameters)
                self.assertEqual(params, ["df", "spec", "request"])


if __name__ == "__main__":
    unittest.main()
