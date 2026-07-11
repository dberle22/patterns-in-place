"""
Theme utilities for the Python chart engine.

This module ports the shared visual defaults from `visual_library/shared/standards.R`
into a package-native Python object. Render functions should ask the Theme for
colors, mode defaults, and chart defaults instead of hardcoding display choices
chart by chart.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import resources
from typing import Any

import yaml

from .formatters import format_value_for_request, to_d3_format


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge nested dicts so chart- and mode-level overrides stay small."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _lookup_path(mapping: dict[str, Any], dotted_key: str) -> Any:
    current: Any = mapping
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


@dataclass
class Theme:
    palette: dict[str, Any] = field(default_factory=dict)
    fonts: dict[str, Any] = field(default_factory=dict)
    modes: dict[str, Any] = field(default_factory=dict)
    chart_defaults: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def default(cls) -> "Theme":
        raw = yaml.safe_load(resources.files("chart_engine").joinpath("pip_theme.yml").read_text()) or {}
        return cls(
            palette=raw.get("palette", {}) or {},
            fonts=raw.get("fonts", {}) or {},
            modes=raw.get("modes", {}) or {},
            chart_defaults=raw.get("chart_defaults", {}) or {},
        )

    @classmethod
    def from_yaml(cls, path: str | "Path") -> "Theme":
        from pathlib import Path

        raw = yaml.safe_load(Path(path).read_text()) or {}
        return cls(
            palette=raw.get("palette", {}) or {},
            fonts=raw.get("fonts", {}) or {},
            modes=raw.get("modes", {}) or {},
            chart_defaults=raw.get("chart_defaults", {}) or {},
        )

    # These helpers are intentionally small wrappers around nested dict access.
    # The goal is to keep renderers readable and make the semantic theme keys
    # obvious at the call site.
    def color(self, key: str, fallback: str = "#333333") -> str:
        return _lookup_path(self.palette, key) or fallback

    def font_family(self, fallback: str = "sans-serif") -> str:
        return self.fonts.get("family", fallback)

    def font_size(self, key: str, fallback: float | int) -> float | int:
        return self.fonts.get(key, fallback)

    def title_size(self, fallback: float | int = 16) -> float | int:
        return self.font_size("title_size", fallback)

    def mode_defaults(self, mode: str = "notebook") -> dict[str, Any]:
        resolved_mode = (mode or "notebook").lower()
        if resolved_mode not in self.modes:
            raise ValueError("mode must be one of 'notebook' or 'presentation'")
        return self.modes[resolved_mode]

    def chart_defaults_for(self, chart_type: str | None = None, mode: str = "notebook") -> dict[str, Any]:
        defaults = self.chart_defaults.get("base", {})
        if chart_type:
            chart_key = chart_type
            aliases = {
                "bar_chart": "bar",
                "line_chart": "line",
            }
            defaults = _deep_merge(defaults, self.chart_defaults.get(aliases.get(chart_key, chart_key), {}))
        return _deep_merge(defaults, self.mode_defaults(mode))

    def width(self, chart_type: str | None = None, mode: str = "notebook", fallback: int = 640) -> int:
        return int(self.chart_defaults_for(chart_type, mode).get("width", fallback))

    def height(self, chart_type: str | None = None, mode: str = "notebook", fallback: int = 400) -> int:
        return int(self.chart_defaults_for(chart_type, mode).get("height", fallback))

    def format(self, value: Any, number_format: Any = None) -> str | None:
        return format_value_for_request(value, number_format)

    def d3_format(self, number_format: Any = None) -> str:
        return to_d3_format(number_format)
