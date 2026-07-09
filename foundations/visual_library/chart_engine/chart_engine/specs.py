"""
ChartSpec: the contract for one chart type.

Loaded from YAML front-matter inside chart_specs/<chart_type>.md, so the
machine-readable spec and the human-readable doc are physically the same
file — can't drift out of sync because there's only one file to edit.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field, replace
from pathlib import Path

import frontmatter


@dataclass(frozen=True)
class ChartSpec:
    chart_type: str
    backend: str                      # "altair" | "matplotlib"
    required_fields: list = field(default_factory=list)
    optional_fields: list = field(default_factory=list)
    column_mapping: dict = field(default_factory=dict)   # source_col -> canonical name
    default_benchmark: str | None = None
    docs: str = ""                    # the markdown body below the front-matter


def load_spec(path: str | Path) -> ChartSpec:
    post = frontmatter.load(str(path))
    meta = post.metadata
    return ChartSpec(
        chart_type=meta["chart_type"],
        backend=meta["backend"],
        required_fields=meta.get("required_fields", []),
        optional_fields=meta.get("optional_fields", []),
        column_mapping=meta.get("column_mapping", {}) or {},
        default_benchmark=meta.get("default_benchmark"),
        docs=post.content.strip(),
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
