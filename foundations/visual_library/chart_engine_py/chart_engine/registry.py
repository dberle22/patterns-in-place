"""
CHART_REGISTRY is the single source of truth for "which spec belongs to
which prep/render functions." A caller never touches this file — it's
only edited when a new chart type is added to the engine itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .prep.bar import prep_bar_chart
from .prep.bivariate_choropleth import prep_bivariate_choropleth
from .prep.boxplot import prep_boxplot
from .prep.bump_chart import prep_bump_chart
from .prep.choropleth import prep_choropleth
from .prep.correlation_heatmap import prep_correlation_heatmap
from .prep.hexbin import prep_hexbin
from .prep.highlight_context_map import prep_highlight_context_map
from .prep.heatmap_table import prep_heatmap_table
from .prep.line import prep_line_chart
from .prep.proportional_symbol_map import prep_proportional_symbol_map
from .prep.slopegraph import prep_slopegraph
from .prep.scatter import prep_scatter
from .prep.strength_strip import prep_strength_strip
from .prep.waterfall import prep_waterfall
from .prep.age_pyramid import prep_age_pyramid
from .render.bar import render_bar_chart
from .render.bivariate_choropleth import render_bivariate_choropleth
from .render.boxplot import render_boxplot
from .render.bump_chart import render_bump_chart
from .render.choropleth import render_choropleth
from .render.correlation_heatmap import render_correlation_heatmap
from .render.hexbin import render_hexbin
from .render.highlight_context_map import render_highlight_context_map
from .render.heatmap_table import render_heatmap_table
from .render.line import render_line_chart
from .render.proportional_symbol_map import render_proportional_symbol_map
from .render.slopegraph import render_slopegraph
from .render.scatter import render_scatter
from .render.strength_strip import render_strength_strip
from .render.waterfall import render_waterfall
from .render.age_pyramid import render_age_pyramid

SPECS_DIR = Path(__file__).parent / "chart_specs"


@dataclass(frozen=True)
class ChartRegistration:
    spec_path: Path
    prep_fn: Callable
    render_fn: Callable


CHART_REGISTRY: dict[str, ChartRegistration] = {
    "bar_chart": ChartRegistration(
        spec_path=SPECS_DIR / "bar_chart.md",
        prep_fn=prep_bar_chart,
        render_fn=render_bar_chart,
    ),
    "line_chart": ChartRegistration(
        spec_path=SPECS_DIR / "line_chart.md",
        prep_fn=prep_line_chart,
        render_fn=render_line_chart,
    ),
    "scatter": ChartRegistration(
        spec_path=SPECS_DIR / "scatter.md",
        prep_fn=prep_scatter,
        render_fn=render_scatter,
    ),
    "slopegraph": ChartRegistration(
        spec_path=SPECS_DIR / "slopegraph.md",
        prep_fn=prep_slopegraph,
        render_fn=render_slopegraph,
    ),
    "boxplot": ChartRegistration(
        spec_path=SPECS_DIR / "boxplot.md",
        prep_fn=prep_boxplot,
        render_fn=render_boxplot,
    ),
    "heatmap_table": ChartRegistration(
        spec_path=SPECS_DIR / "heatmap_table.md",
        prep_fn=prep_heatmap_table,
        render_fn=render_heatmap_table,
    ),
    "bump_chart": ChartRegistration(
        spec_path=SPECS_DIR / "bump_chart.md",
        prep_fn=prep_bump_chart,
        render_fn=render_bump_chart,
    ),
    "waterfall": ChartRegistration(
        spec_path=SPECS_DIR / "waterfall.md",
        prep_fn=prep_waterfall,
        render_fn=render_waterfall,
    ),
    "strength_strip": ChartRegistration(
        spec_path=SPECS_DIR / "strength_strip.md",
        prep_fn=prep_strength_strip,
        render_fn=render_strength_strip,
    ),
    "correlation_heatmap": ChartRegistration(
        spec_path=SPECS_DIR / "correlation_heatmap.md",
        prep_fn=prep_correlation_heatmap,
        render_fn=render_correlation_heatmap,
    ),
    "age_pyramid": ChartRegistration(
        spec_path=SPECS_DIR / "age_pyramid.md",
        prep_fn=prep_age_pyramid,
        render_fn=render_age_pyramid,
    ),
    "choropleth": ChartRegistration(
        spec_path=SPECS_DIR / "choropleth.md",
        prep_fn=prep_choropleth,
        render_fn=render_choropleth,
    ),
    "hexbin": ChartRegistration(
        spec_path=SPECS_DIR / "hexbin.md",
        prep_fn=prep_hexbin,
        render_fn=render_hexbin,
    ),
    "highlight_context_map": ChartRegistration(
        spec_path=SPECS_DIR / "highlight_context_map.md",
        prep_fn=prep_highlight_context_map,
        render_fn=render_highlight_context_map,
    ),
    "proportional_symbol_map": ChartRegistration(
        spec_path=SPECS_DIR / "proportional_symbol_map.md",
        prep_fn=prep_proportional_symbol_map,
        render_fn=render_proportional_symbol_map,
    ),
    "bivariate_choropleth": ChartRegistration(
        spec_path=SPECS_DIR / "bivariate_choropleth.md",
        prep_fn=prep_bivariate_choropleth,
        render_fn=render_bivariate_choropleth,
    ),
    # Adding a new chart type = one new entry here + a spec .md +
    # a prep fn + a render fn. Nothing else in the package changes,
    # and no consuming repo needs to change anything either.
}
