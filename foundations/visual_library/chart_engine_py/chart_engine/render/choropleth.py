from __future__ import annotations

import pandas as pd

from ..geo import geometry_to_polygons
from ..request import ChartRequest
from ..specs import ChartSpec
from .mpl_helpers import add_caption, apply_titles, create_figure, finalize_map_axes, get_colormap, require_matplotlib


def render_choropleth(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest):
    plt, cm, colors, patches, PatchCollection, _, = require_matplotlib()
    fig, ax = create_figure(request, "choropleth")

    default_title = request.title or (
        f"{df['metric_label'].iloc[0]} map" if "metric_label" in df.columns and len(df) else "Choropleth map"
    )
    default_subtitle = request.subtitle or (df["time_window"].iloc[0] if "time_window" in df.columns and len(df) else None)
    apply_titles(fig, ax, request, "choropleth", default_title, default_subtitle)

    if "geometry" not in df.columns or df["geometry"].isna().all():
        raise ValueError("choropleth rendering requires a 'geometry' column with polygon-like coordinates")

    polygons: list[Any] = []
    fills: list[float] = []
    outlines: list[str] = []
    for _, row in df.iterrows():
        for ring in geometry_to_polygons(row["geometry"]):
            polygons.append(patches.Polygon(ring, closed=True))
            fills.append(row["metric_value"] if pd.notna(row["metric_value"]) else float("nan"))
            outlines.append(
                request.theme.color("highlight.selection", "#2C7FB8")
                if bool(row.get("highlight_flag", False))
                else request.theme.color("neutral.axis", "#D9E2EC")
            )

    collection = PatchCollection(polygons, linewidths=1.0)
    if pd.Series(fills).notna().any():
        cmap = get_colormap("Blues")
        norm = colors.Normalize(vmin=min(value for value in fills if pd.notna(value)), vmax=max(value for value in fills if pd.notna(value)))
        collection.set_cmap(cmap)
        collection.set_norm(norm)
        collection.set_array(pd.Series(fills))
        fig.colorbar(collection, ax=ax, shrink=0.72, label=df["metric_label"].iloc[0] if "metric_label" in df.columns else "")
    else:
        collection.set_facecolor(request.theme.color("neutral.grid", "#D9E2EC"))
    collection.set_edgecolor(outlines)
    ax.add_collection(collection)
    ax.autoscale_view()
    finalize_map_axes(ax)
    add_caption(fig, df, request)
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    return fig
