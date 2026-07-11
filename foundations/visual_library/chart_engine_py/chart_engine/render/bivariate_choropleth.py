from __future__ import annotations

from typing import Any

import pandas as pd

from ..geo import geometry_to_polygons
from ..request import ChartRequest
from ..specs import ChartSpec
from .mpl_helpers import add_caption, apply_titles, create_figure, finalize_map_axes, require_matplotlib, resolve_font_family


_BIVARIATE_PALETTE = {
    "1-1": "#e8e8e8",
    "2-1": "#b5c0da",
    "3-1": "#6c83b5",
    "1-2": "#b8d6be",
    "2-2": "#90b2b3",
    "3-2": "#567994",
    "1-3": "#73ae80",
    "2-3": "#5a9178",
    "3-3": "#2a5a5b",
}


def render_bivariate_choropleth(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest):
    _, _, _, patches, PatchCollection, _ = require_matplotlib()
    fig, ax = create_figure(request, "bivariate_choropleth")
    font_family = resolve_font_family(request.theme.font_family())

    title = request.title or (
        f"{df['x_label'].iloc[0]} and {df['y_label'].iloc[0]}" if len(df) else "Bivariate choropleth"
    )
    subtitle = request.subtitle or (df["time_window"].iloc[0] if "time_window" in df.columns and len(df) else None)
    apply_titles(fig, ax, request, "bivariate_choropleth", title, subtitle)

    if "geometry" not in df.columns or df["geometry"].isna().all():
        raise ValueError("bivariate_choropleth rendering requires a 'geometry' column with polygon-like coordinates")

    polygon_patches: list[Any] = []
    facecolors: list[str] = []
    edgecolors: list[str] = []
    for _, row in df.iterrows():
        facecolor = _BIVARIATE_PALETTE.get(str(row["bivar_class"]), "#F0F4F8")
        edgecolor = request.theme.color("highlight.selection", "#2C7FB8") if bool(row.get("highlight_flag", False)) else "#FFFFFF"
        for ring in geometry_to_polygons(row["geometry"]):
            polygon_patches.append(patches.Polygon(ring, closed=True))
            facecolors.append(facecolor)
            edgecolors.append(edgecolor)

    collection = PatchCollection(polygon_patches, linewidths=1.0, facecolor=facecolors, edgecolor=edgecolors)
    ax.add_collection(collection)
    ax.autoscale_view()
    finalize_map_axes(ax)

    legend_ax = fig.add_axes([0.77, 0.12, 0.12, 0.12])
    for x_bin in range(1, 4):
        for y_bin in range(1, 4):
            legend_ax.add_patch(
                patches.Rectangle(
                    (x_bin - 1, y_bin - 1),
                    1,
                    1,
                    facecolor=_BIVARIATE_PALETTE[f"{x_bin}-{y_bin}"],
                    edgecolor="#FFFFFF",
                )
            )
    legend_ax.set_xlim(0, 3)
    legend_ax.set_ylim(0, 3)
    legend_ax.set_xticks([0.5, 1.5, 2.5], ["Low", "Mid", "High"])
    legend_ax.set_yticks([0.5, 1.5, 2.5], ["Low", "Mid", "High"])
    legend_ax.set_xlabel(df["x_label"].iloc[0] if len(df) else "", fontsize=8, fontfamily=font_family)
    legend_ax.set_ylabel(df["y_label"].iloc[0] if len(df) else "", fontsize=8, fontfamily=font_family)
    legend_ax.tick_params(length=0, labelsize=7)
    for label in legend_ax.get_xticklabels() + legend_ax.get_yticklabels():
        label.set_fontfamily(font_family)
    for spine in legend_ax.spines.values():
        spine.set_visible(False)

    add_caption(fig, df, request)
    fig.subplots_adjust(left=0.08, right=0.74, bottom=0.12, top=0.84)
    return fig
