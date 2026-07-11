"""
Shared helpers for matplotlib-backed chart renderers.

These wrappers keep the optional dependency boundary in one place and give the
first geo-chart ports the same title, subtitle, and caption treatment.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from ..captions import build_caption, wrap_text


def require_matplotlib() -> tuple[Any, Any, Any, Any, Any, Any]:
    try:
        from matplotlib import cm, colors, patches
        from matplotlib.collections import PatchCollection
        from matplotlib.lines import Line2D
        from matplotlib import pyplot as plt
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "matplotlib is required for matplotlib-backed charts. "
            "Install the optional plotting dependency before rendering "
            "choropleth, hexbin, or map-based chart types."
        ) from exc
    return plt, cm, colors, patches, PatchCollection, Line2D


def get_colormap(name: str):
    try:
        from matplotlib import colormaps

        return colormaps.get_cmap(name)
    except Exception:
        plt, _, _, _, _, _ = require_matplotlib()
        return plt.get_cmap(name)


@lru_cache(maxsize=None)
def resolve_font_family(preferred_family: str) -> str:
    """Fall back to a bundled Matplotlib font when the theme font is unavailable locally."""
    try:
        from matplotlib import font_manager
    except Exception:
        return preferred_family

    installed = {font.name for font in font_manager.fontManager.ttflist}
    if preferred_family in installed:
        return preferred_family
    if "DejaVu Sans" in installed:
        return "DejaVu Sans"
    return preferred_family


def create_figure(request: Any, chart_type: str) -> tuple[Any, Any]:
    plt, _, _, _, _, _ = require_matplotlib()
    dpi = 96
    width = request.dimensions.width if request.dimensions and request.dimensions.width else request.theme.width(chart_type)
    height = request.dimensions.height if request.dimensions and request.dimensions.height else request.theme.height(chart_type)
    fig, ax = plt.subplots(figsize=(width / dpi, height / dpi), dpi=dpi)
    fig.patch.set_facecolor(request.theme.color("background.canvas", "#F7F9FB"))
    ax.set_facecolor(request.theme.color("background.panel", "#FFFFFF"))
    return fig, ax


def apply_titles(fig: Any, ax: Any, request: Any, chart_type: str, default_title: str, default_subtitle: str | None = None) -> None:
    title = request.title or default_title
    subtitle = request.subtitle or default_subtitle
    font_family = resolve_font_family(request.theme.font_family())
    ax.set_title(
        title,
        loc="left",
        fontsize=request.theme.title_size(),
        fontfamily=font_family,
        color=request.theme.color("neutral.text", "#1F2933"),
        pad=14,
    )
    if subtitle:
        fig.text(
            0.125,
            0.92,
            wrap_text(subtitle, 110),
            ha="left",
            va="top",
            fontsize=request.theme.font_size("subtitle_size", 10),
            family=font_family,
            color=request.theme.color("neutral.text_muted", "#52606D"),
        )


def add_caption(fig: Any, df: Any, request: Any) -> None:
    if len(df) == 0:
        return
    font_family = resolve_font_family(request.theme.font_family())
    caption = build_caption(
        source=df["source"].iloc[0] if "source" in df.columns else None,
        vintage=df["vintage"].iloc[0] if "vintage" in df.columns else None,
    )
    fig.text(
        0.125,
        0.03,
        caption,
        ha="left",
        va="bottom",
        fontsize=request.theme.font_size("caption_size", 9),
        family=font_family,
        color=request.theme.color("neutral.text_muted", "#52606D"),
    )


def finalize_map_axes(ax: Any) -> None:
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def scale_sizes(values: Any, min_size: float = 80.0, max_size: float = 700.0) -> Any:
    numeric = values.astype(float)
    if numeric.max() == numeric.min():
        return numeric * 0 + ((min_size + max_size) / 2)
    scaled = (numeric - numeric.min()) / (numeric.max() - numeric.min())
    return min_size + scaled * (max_size - min_size)
