"""
Theme: the per-consumer visual identity (colors, fonts, sizing).

One theme.yml per repo/org. Nothing chart-specific lives here — that's
the ChartSpec's job (see specs.py). Theme only answers "what does it
look like," never "what fields does this chart need."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Theme:
    palette: dict = field(default_factory=dict)
    fonts: dict = field(default_factory=dict)
    chart_defaults: dict = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Theme":
        raw = yaml.safe_load(Path(path).read_text())
        return cls(
            palette=raw.get("palette", {}),
            fonts=raw.get("fonts", {}),
            chart_defaults=raw.get("chart_defaults", {}),
        )

    # convenience accessors so render functions don't sprinkle .get() everywhere
    def color(self, key: str, fallback: str = "#333333") -> str:
        return self.palette.get(key, fallback)

    def font_family(self, fallback: str = "sans-serif") -> str:
        return self.fonts.get("family", fallback)

    def title_size(self, fallback: int = 16) -> int:
        return self.fonts.get("title_size", fallback)

    def width(self, fallback: int = 640) -> int:
        return self.chart_defaults.get("width", fallback)

    def height(self, fallback: int = 400) -> int:
        return self.chart_defaults.get("height", fallback)
