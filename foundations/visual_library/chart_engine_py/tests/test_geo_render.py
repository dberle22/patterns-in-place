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
        request = ChartRequest(
            data=choropleth_fixture(),
            chart_type="choropleth",
            theme=self.theme,
            number_format=NumberFormat(unit="count", decimals=0),
            field_values={"variant": "diverging", "facet_by": "group"},
        )
        figure = render(request).chart
        self.assertEqual(figure.__class__.__name__, "Figure")
        self.assertGreaterEqual(len(figure.axes), 3)

    def test_choropleth_uses_dark_high_sequential_scale(self) -> None:
        request = ChartRequest(
            data=choropleth_fixture(),
            chart_type="choropleth",
            theme=self.theme,
            number_format=NumberFormat(unit="count", decimals=0),
        )
        figure = render(request).chart
        collection = figure.axes[0].collections[0]
        self.assertEqual(collection.cmap.name.lower(), "blues")

    def test_hexbin_renders_matplotlib_figure(self) -> None:
        request = ChartRequest(
            data=hexbin_fixture(),
            chart_type="hexbin",
            theme=self.theme,
            number_format=NumberFormat(unit="count", decimals=0),
            field_values={"facet_by": "group", "use_weights": True, "add_reference_lines": True},
        )
        figure = render(request).chart
        self.assertEqual(figure.__class__.__name__, "Figure")
        self.assertGreaterEqual(len(figure.axes), 4)
        self.assertGreaterEqual(len(figure.axes[0].lines), 2)

    def test_highlight_context_map_renders_matplotlib_figure(self) -> None:
        request = ChartRequest(
            data=highlight_context_map_fixture(),
            chart_type="highlight_context_map",
            theme=self.theme,
            number_format=NumberFormat(unit="count", decimals=0),
            field_values={"variant": "focus_only", "facet_by": "group"},
        )
        figure = render(request).chart
        self.assertEqual(figure.__class__.__name__, "Figure")
        self.assertGreaterEqual(len(figure.legends), 1)
        self.assertIn("Map role", [legend.get_title().get_text() for legend in figure.legends if legend.get_title()])

    def test_highlight_context_map_binned_variant_uses_separate_legends(self) -> None:
        request = ChartRequest(
            data=highlight_context_map_fixture(),
            chart_type="highlight_context_map",
            theme=self.theme,
            number_format=NumberFormat(unit="count", decimals=0),
            field_values={"variant": "binned"},
        )
        figure = render(request).chart
        legend_titles = [legend.get_title().get_text() for legend in figure.legends if legend.get_title()]
        self.assertIn("Jobs", legend_titles)
        self.assertIn("Map role", legend_titles)

    def test_proportional_symbol_map_renders_matplotlib_figure(self) -> None:
        request = ChartRequest(
            data=proportional_symbol_map_fixture(),
            chart_type="proportional_symbol_map",
            theme=self.theme,
            number_format=NumberFormat(unit="count", decimals=0),
            field_values={"color_mode": "color_group"},
        )
        figure = render(request).chart
        self.assertEqual(figure.__class__.__name__, "Figure")
        self.assertGreaterEqual(len(figure.axes[0].get_legend().get_texts()), 1)

    def test_bivariate_choropleth_renders_matplotlib_figure(self) -> None:
        request = ChartRequest(
            data=bivariate_choropleth_fixture(),
            chart_type="bivariate_choropleth",
            theme=self.theme,
            number_format=NumberFormat(unit="count", decimals=0),
            field_values={"facet_by": "group"},
        )
        figure = render(request).chart
        self.assertEqual(figure.__class__.__name__, "Figure")
        self.assertGreaterEqual(len(figure.axes), 3)


if __name__ == "__main__":
    unittest.main()
