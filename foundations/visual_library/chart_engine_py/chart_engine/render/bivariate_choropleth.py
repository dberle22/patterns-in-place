from __future__ import annotations

from typing import Any

import pandas as pd

from ..geo import geometry_to_polygons
from ..request import ChartRequest
from ..specs import ChartSpec
from .mpl_helpers import add_caption, apply_titles, create_figure, create_subplots, finalize_map_axes, require_matplotlib, resolve_font_family


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
    cfg = df.attrs.get("chart_config", {})
    facet_by = str(cfg.get("facet_by") or request.field_values.get("facet_by") or "").strip()
    if facet_by and facet_by in df.columns:
        facet_values = df[facet_by].dropna().astype(str).unique().tolist()
        fig, axes = create_subplots(request, "bivariate_choropleth", len(facet_values), columns=int(cfg.get("facet_ncol") or request.field_values.get("facet_ncol") or 2))
    else:
        facet_values = []
        fig, ax = create_figure(request, "bivariate_choropleth")
        axes = [ax]
    font_family = resolve_font_family(request.theme.font_family())

    title = request.title or (
        f"{df['x_label'].iloc[0]} and {df['y_label'].iloc[0]}" if len(df) else "Bivariate choropleth"
    )
    bin_method = df["bin_method"].iloc[0] if "bin_method" in df.columns and len(df) else "quantile"
    subtitle = request.subtitle or (
        f"{df['time_window'].iloc[0]} | {bin_method.title()} binning" if "time_window" in df.columns and len(df) else f"{bin_method.title()} binning"
    )
    apply_titles(fig, axes[0], request, "bivariate_choropleth", title, subtitle)

    if "geometry" not in df.columns or df["geometry"].isna().all():
        raise ValueError("bivariate_choropleth rendering requires a 'geometry' column with polygon-like coordinates")

    def draw_panel(ax_obj: Any, panel_df: pd.DataFrame, label: str | None = None):
        polygon_patches: list[Any] = []
        facecolors: list[str] = []
        edgecolors: list[str] = []
        for _, row in panel_df.iterrows():
            facecolor = _BIVARIATE_PALETTE.get(str(row["bivar_class"]), "#F0F4F8")
            edgecolor = request.theme.color("highlight.selection", "#2C7FB8") if bool(row.get("highlight_flag", False)) else "#FFFFFF"
            for ring in geometry_to_polygons(row["geometry"]):
                polygon_patches.append(patches.Polygon(ring, closed=True))
                facecolors.append(facecolor)
                edgecolors.append(edgecolor)
        collection = PatchCollection(polygon_patches, linewidths=1.0, facecolor=facecolors, edgecolor=edgecolors)
        ax_obj.add_collection(collection)
        ax_obj.autoscale_view()
        finalize_map_axes(ax_obj)
        if label:
            ax_obj.text(0.02, 0.98, label, transform=ax_obj.transAxes, ha="left", va="top", fontsize=10, family=font_family)

    if facet_values:
        for index, value in enumerate(facet_values):
            draw_panel(axes[index], df.loc[df[facet_by].astype(str) == value].copy(), value)
        for ax in axes[len(facet_values):]:
            ax.set_visible(False)
    else:
        draw_panel(axes[0], df)

    legend_ax = fig.add_axes([0.77, 0.12, 0.12, 0.12])
    bin_count = int(df["bin_count"].iloc[0]) if "bin_count" in df.columns and len(df) else 3
    for x_bin in range(1, bin_count + 1):
        for y_bin in range(1, bin_count + 1):
            legend_ax.add_patch(
                patches.Rectangle(
                    (x_bin - 1, y_bin - 1),
                    1,
                    1,
                    facecolor=_BIVARIATE_PALETTE.get(f"{x_bin}-{y_bin}", "#F0F4F8"),
                    edgecolor="#FFFFFF",
                )
            )
    legend_ax.set_xlim(0, bin_count)
    legend_ax.set_ylim(0, bin_count)
    tick_positions = [index + 0.5 for index in range(bin_count)]
    tick_labels = ["Low", "Mid", "High"][:bin_count] if bin_count <= 3 else [str(index + 1) for index in range(bin_count)]
    legend_ax.set_xticks(tick_positions, tick_labels)
    legend_ax.set_yticks(tick_positions, tick_labels)
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
