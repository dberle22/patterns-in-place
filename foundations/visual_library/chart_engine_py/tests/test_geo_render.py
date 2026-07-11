"""
Structural tests for matplotlib-backed geo charts.

They intentionally skip when matplotlib is unavailable in the local shell so
the rest of the package can still be developed without the plotting extra.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chart_engine.orchestrator import render
from chart_engine.request import ChartRequest, NumberFormat
from chart_engine.theme import Theme
from tests.fixtures import (
    bivariate_choropleth_fixture,
    choropleth_fixture,
    hexbin_fixture,
    highlight_context_map_fixture,
    proportional_symbol_map_fixture,
)


@unittest.skipUnless(importlib.util.find_spec("matplotlib") is not None, "matplotlib not installed in this environment")
class GeoRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.theme = Theme.default()

    def _render(self, chart_type, data):
        request = ChartRequest(
            data=data,
            chart_type=chart_type,
            theme=self.theme,
            number_format=NumberFormat(unit="count", decimals=0),
        )
        return render(request).chart

    def test_choropleth_renders_matplotlib_figure(self) -> None:
        figure = self._render("choropleth", choropleth_fixture())
        self.assertEqual(figure.__class__.__name__, "Figure")

    def test_hexbin_renders_matplotlib_figure(self) -> None:
        figure = self._render("hexbin", hexbin_fixture())
        self.assertEqual(figure.__class__.__name__, "Figure")

    def test_highlight_context_map_renders_matplotlib_figure(self) -> None:
        figure = self._render("highlight_context_map", highlight_context_map_fixture())
        self.assertEqual(figure.__class__.__name__, "Figure")

    def test_proportional_symbol_map_renders_matplotlib_figure(self) -> None:
        figure = self._render("proportional_symbol_map", proportional_symbol_map_fixture())
        self.assertEqual(figure.__class__.__name__, "Figure")

    def test_bivariate_choropleth_renders_matplotlib_figure(self) -> None:
        figure = self._render("bivariate_choropleth", bivariate_choropleth_fixture())
        self.assertEqual(figure.__class__.__name__, "Figure")


if __name__ == "__main__":
    unittest.main()
