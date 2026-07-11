from __future__ import annotations

from typing import Any

import pandas as pd

from ..geo import geometry_to_polygons
from ..request import ChartRequest
from ..specs import ChartSpec
from .mpl_helpers import add_caption, apply_titles, create_figure, finalize_map_axes, get_colormap, require_matplotlib, resolve_font_family


def render_highlight_context_map(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest):
    _, cm, colors, patches, PatchCollection, Line2D = require_matplotlib()
    fig, ax = create_figure(request, "highlight_context_map")
    font_family = resolve_font_family(request.theme.font_family())

    highlight_names = df.loc[df["highlight_flag"], "geo_name"].tolist()
    title = ", ".join(highlight_names[:2]) if highlight_names else "Highlight context map"
    subtitle = request.subtitle or (df["time_window"].iloc[0] if "time_window" in df.columns and len(df) else None)
    apply_titles(fig, ax, request, "highlight_context_map", title, subtitle)

    if "geometry" not in df.columns or df["geometry"].isna().all():
        raise ValueError("highlight_context_map rendering requires a 'geometry' column with polygon-like coordinates")

    polygons: list[Any] = []
    fills: list[float] = []
    edges: list[str] = []
    for _, row in df.iterrows():
        fill_value = row["metric_value"] if "metric_value" in df.columns else None
        edge = request.theme.color("highlight.selection", "#2C7FB8") if row["highlight_flag"] else request.theme.color("neutral.grid", "#D9E2EC")
        if bool(row.get("neighbor_flag", False)) and not row["highlight_flag"]:
            edge = request.theme.color("comparison.benchmark", "#52606D")
        for ring in geometry_to_polygons(row["geometry"]):
            polygons.append(patches.Polygon(ring, closed=True))
            fills.append(fill_value if fill_value is not None and pd.notna(fill_value) else float("nan"))
            edges.append(edge)

    collection = PatchCollection(polygons, linewidths=1.2)
    if pd.Series(fills).notna().any():
        cmap = get_colormap("Greys")
        numeric = [value for value in fills if pd.notna(value)]
        collection.set_cmap(cmap)
        collection.set_norm(colors.Normalize(vmin=min(numeric), vmax=max(numeric)))
        collection.set_array(pd.Series(fills))
    else:
        collection.set_facecolor(request.theme.color("neutral.grid", "#E5E7EB"))
    collection.set_edgecolor(edges)
    collection.set_alpha(0.95)
    ax.add_collection(collection)
    ax.autoscale_view()

    legend_handles = [
        Line2D([0], [0], color=request.theme.color("highlight.selection", "#2C7FB8"), linewidth=2, label="Highlight"),
        Line2D([0], [0], color=request.theme.color("comparison.benchmark", "#52606D"), linewidth=2, label="Neighbor"),
        Line2D([0], [0], color=request.theme.color("neutral.grid", "#D9E2EC"), linewidth=2, label="Context"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", frameon=False, prop={"family": font_family, "size": 9})
    finalize_map_axes(ax)
    add_caption(fig, df, request)
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    return fig
