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
from .prep.line import prep_line_chart
from .render.bar import render_bar_chart
from .render.line import render_line_chart

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
    # Adding a new chart type = one new entry here + a spec .md +
    # a prep fn + a render fn. Nothing else in the package changes,
    # and no consuming repo needs to change anything either.
}
