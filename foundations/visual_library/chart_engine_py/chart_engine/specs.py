"""
ChartSpec: the contract for one chart type.

Loaded from YAML front-matter inside generated chart_specs/<chart_type>.md
files. The human-authored source lives under visual_library/charts/<type>/;
these package-local files are runtime artifacts the engine reads directly.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field, replace
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ChartSpec:
    chart_type: str
    backend: str                      # "altair" | "matplotlib"
    required_fields: list = field(default_factory=list)
    optional_fields: list = field(default_factory=list)
    column_mapping: dict = field(default_factory=dict)   # source_col -> canonical name
    default_benchmark: str | None = None
    docs: str = ""                    # the markdown body below the front-matter


def _split_front_matter(text: str) -> tuple[dict, str]:
    """
    Parse a small markdown file with YAML front matter without depending on an
    extra package at runtime. Generated specs use a predictable shape, so we
    keep the parser narrow and easy to reason about.
    """
    if not text.startswith("---\n"):
        raise ValueError("Spec file is missing YAML front matter opening delimiter")

    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        raise ValueError("Spec file is missing YAML front matter closing delimiter")

    raw_meta = parts[0][4:]
    raw_body = parts[1]
    metadata = yaml.safe_load(raw_meta) or {}
    return metadata, raw_body.strip()


def load_spec(path: str | Path) -> ChartSpec:
    meta, docs = _split_front_matter(Path(path).read_text())
    return ChartSpec(
        chart_type=meta["chart_type"],
        backend=meta["backend"],
        required_fields=meta.get("required_fields", []),
        optional_fields=meta.get("optional_fields", []),
        column_mapping=meta.get("column_mapping", {}) or {},
        default_benchmark=meta.get("default_benchmark"),
        docs=docs,
    )


def apply_overrides(spec: ChartSpec, overrides: dict) -> ChartSpec:
    """
    Let a caller override spec fields per-call without touching the .md file.
    Example: overrides={"column_mapping": {"cbsa_name": "entity"}}
    Only known ChartSpec fields are accepted — unknown keys are left for
    the render function to pick up as chart-specific kwargs instead.
    """
    known = {f.name for f in dataclasses.fields(ChartSpec)}
    spec_overrides = {k: v for k, v in overrides.items() if k in known}
    return replace(spec, **spec_overrides) if spec_overrides else spec
