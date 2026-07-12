"""
Generate package-local chart spec artifacts from the human-authored chart docs.

The docs under `visual_library/charts/<type>/` remain the source of truth.
This script extracts the runtime contract pieces the Python package needs and
writes deterministic markdown files under `chart_engine/chart_specs/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]
CHARTS_ROOT = ROOT.parent / "charts"
OUTPUT_ROOT = ROOT / "chart_engine" / "chart_specs"


@dataclass(frozen=True)
class ChartDefinition:
    source_dir: str
    chart_type: str
    backend: str
    default_benchmark: str | None = None
    required_fields_override: tuple[str, ...] | None = None
    optional_fields_override: tuple[str, ...] | None = None


CHART_DEFINITIONS = [
    ChartDefinition(
        "bar",
        "bar_chart",
        "altair",
        required_fields_override=("entity", "value"),
        optional_fields_override=("subtitle",),
    ),
    ChartDefinition(
        "line",
        "line_chart",
        "altair",
        default_benchmark="national_median",
        required_fields_override=("period", "value", "series"),
        optional_fields_override=(
            "subtitle",
            "metric_label",
            "geo_name",
            "time_window",
            "group",
            "highlight_flag",
            "benchmark_value",
            "index_base_period",
            "note",
            "source",
            "vintage",
        ),
    ),
    ChartDefinition("scatter", "scatter", "altair"),
    ChartDefinition("slopegraph", "slopegraph", "altair"),
    ChartDefinition("boxplot", "boxplot", "altair"),
    ChartDefinition("heatmap_table", "heatmap_table", "altair"),
    ChartDefinition("bump_chart", "bump_chart", "altair"),
    ChartDefinition("waterfall", "waterfall", "altair"),
    ChartDefinition("strength_strip", "strength_strip", "altair"),
    ChartDefinition("correlation_heatmap", "correlation_heatmap", "altair"),
    ChartDefinition("age_pyramid", "age_pyramid", "altair"),
    ChartDefinition("choropleth", "choropleth", "matplotlib"),
    ChartDefinition("hexbin", "hexbin", "matplotlib"),
    ChartDefinition("highlight_context_map", "highlight_context_map", "matplotlib"),
    ChartDefinition("proportional_symbol_map", "proportional_symbol_map", "matplotlib"),
    ChartDefinition("bivariate_choropleth", "bivariate_choropleth", "matplotlib"),
]


def _extract_field_block(text: str, heading: str) -> list[str]:
    """
    Pull the bullet list that sits under a markdown heading like
    `**Required fields:**`. The source specs use a stable prose structure, so
    a lightweight regex-based extractor is enough here.
    """
    pattern = rf"\*\*{re.escape(heading)}:\*\*\s*\n(?P<body>(?:- .+\n)+)"
    match = re.search(pattern, text)
    if not match:
        return []

    fields: list[str] = []
    for raw_line in match.group("body").strip().splitlines():
        line = raw_line.strip()
        field_match = re.match(r"- `([^`]+)`", line)
        if field_match:
            fields.append(field_match.group(1))
    return fields


def _load_source_spec(defn: ChartDefinition) -> tuple[list[str], list[str], str]:
    spec_path = CHARTS_ROOT / defn.source_dir / f"{defn.source_dir}_spec.md"
    question_coverage_path = CHARTS_ROOT / defn.source_dir / "question_coverage.md"
    raw = spec_path.read_text()
    required_fields = _extract_field_block(raw, "Required fields")
    optional_fields = _extract_field_block(raw, "Optional fields")
    if not optional_fields:
        optional_fields = _extract_field_block(raw, "Optional fields (recommended)")
    if defn.required_fields_override is not None:
        required_fields = list(defn.required_fields_override)
    if defn.optional_fields_override is not None:
        optional_fields = list(defn.optional_fields_override)

    title = raw.splitlines()[0].lstrip("#").strip()
    spec_body = "\n".join(raw.splitlines()[1:]).strip()
    question_coverage = question_coverage_path.read_text().strip() if question_coverage_path.exists() else ""
    docs = (
        f"# {title}\n\n"
        f"Generated from `visual_library/charts/{defn.source_dir}/{defn.source_dir}_spec.md`.\n\n"
        f"Backend: `{defn.backend}`. Required fields: `{', '.join(required_fields)}`.\n\n"
        f"## Source Spec\n\n"
        f"{spec_body}\n"
    )
    if question_coverage:
        docs += (
            f"\n## Question Coverage\n\n"
            f"Generated from `visual_library/charts/{defn.source_dir}/question_coverage.md`.\n\n"
            f"{question_coverage}\n"
        )
    return required_fields, optional_fields, docs


def _write_generated_spec(defn: ChartDefinition) -> None:
    required_fields, optional_fields, docs = _load_source_spec(defn)
    front_matter = {
        "chart_type": defn.chart_type,
        "backend": defn.backend,
        "required_fields": required_fields,
        "optional_fields": optional_fields,
        "column_mapping": {},
        "default_benchmark": defn.default_benchmark,
    }
    rendered = f"---\n{yaml.safe_dump(front_matter, sort_keys=False).strip()}\n---\n{docs}\n"
    output_path = OUTPUT_ROOT / f"{defn.chart_type}.md"
    output_path.write_text(rendered)


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for definition in CHART_DEFINITIONS:
        _write_generated_spec(definition)


if __name__ == "__main__":
    main()
