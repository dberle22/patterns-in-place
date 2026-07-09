"""
ChartRequest is the full input surface for render(). It's deliberately a
rich object, not a flat function signature — render() taking 25 kwargs
would be worse to maintain, worse to test, and impossible to serialize
for the QA harness (question_queue pipeline needs to dump the exact
request that produced a chart, alongside query_plan.json / result.sql).

A ChartRequest is JSON-serializable in spirit (every field is a plain
type, dataclass, or DataFrame) so a caller — the publisher, the deep
dive builder, an ad hoc notebook — can construct it, log it, and hand
it to render() without render() needing to know who built it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from .theme import Theme


# ---------------------------------------------------------------------------
# Sub-configs — each optional, each independently meaningful
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkConfig:
    """A reference line/shape drawn against the primary series."""
    kind: Literal["national_median", "regional", "peer_cluster", "custom"] = "national_median"
    value: float | None = None          # required if kind == "custom"
    label: str | None = None            # e.g. "US National", "Southeast Division"
    style: Literal["line", "band", "polygon_overlay"] = "line"  # polygon_overlay = radar chart national shape


@dataclass
class Annotation:
    """A single callout on a chart: an inflection point, a threshold, a note."""
    kind: Literal["point", "vline", "hline", "range", "text"]
    x: Any = None
    y: Any = None
    x_end: Any = None                   # for "range"
    label: str | None = None
    style: Literal["default", "warning", "highlight"] = "default"


@dataclass
class FacetConfig:
    """Small multiples — e.g. Section 6's 4-6 panel trend grid."""
    facet_field: str = "series"
    columns: int = 3
    shared_y_axis: bool = True
    max_panels: int = 8


@dataclass
class DimensionOverride:
    width: int | None = None
    height: int | None = None


@dataclass
class NumberFormat:
    """Pulled from metric_catalog.yml's unit_format in production use."""
    unit: Literal["percent", "currency", "count", "ratio", "index"] = "count"
    decimals: int = 1
    compact: bool = False               # e.g. "1.2M" instead of "1,200,000"


@dataclass
class OutputConfig:
    """Where and how the chart gets persisted, if at all."""
    save: bool = False
    path: Path | None = None
    format: Literal["html", "png", "svg", "json"] = "html"
    social_crop: Literal[None, "x_post", "x_thread_card"] = None
    scale_factor: float = 1.0           # for high-DPI PNG export


@dataclass
class RunContext:
    """Provenance for QA / publisher tracking — never affects rendering."""
    question_id: str | None = None
    source: Literal["publisher", "deep_dive", "adhoc", "chatbot"] = "adhoc"
    run_id: str | None = None


# ---------------------------------------------------------------------------
# The request itself
# ---------------------------------------------------------------------------

@dataclass
class ChartRequest:
    # --- required ---
    data: pd.DataFrame
    chart_type: str
    theme: Theme

    # --- content mapping ---
    column_mapping: dict = field(default_factory=dict)
    field_values: dict = field(default_factory=dict)
    # ^ chart-specific optional-field VALUES, e.g. {"highlight_entity": "Jacksonville"}
    #   distinct from column_mapping (which renames columns) — this sets content.

    # --- text ---
    title: str | None = None            # overrides the spec-derived default title
    subtitle: str | None = None
    alt_text: str | None = None

    # --- optional composed configs ---
    benchmark: BenchmarkConfig | None = None
    annotations: list = field(default_factory=list)      # list[Annotation]
    facet: FacetConfig | None = None
    dimensions: DimensionOverride | None = None
    number_format: NumberFormat | None = None
    output: OutputConfig = field(default_factory=OutputConfig)
    run_context: RunContext | None = None

    # --- behavior flags ---
    interactive: bool = True
    validate_only: bool = False         # run contract validation, skip render (QA batch use)
    return_prepped_data: bool = False   # attach prepped df to the result for debugging


@dataclass
class ChartResult:
    """What render() hands back — not just a chart object."""
    chart: Any                          # None if validate_only=True
    chart_type: str
    output_path: Path | None
    prepped_data: pd.DataFrame | None   # only populated if requested
    alt_text: str | None
    warnings: list = field(default_factory=list)   # non-fatal issues (e.g. facet truncated to max_panels)
