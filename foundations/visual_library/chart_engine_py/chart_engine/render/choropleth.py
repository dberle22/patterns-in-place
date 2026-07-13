from __future__ import annotations

from typing import Any

import pandas as pd

from ..geo import geometry_to_polygons
from ..request import ChartRequest
from ..specs import ChartSpec
from .mpl_helpers import add_caption, apply_titles, create_figure, create_subplots, finalize_map_axes, get_colormap, require_matplotlib, resolve_font_family, set_map_limits


def _choropleth_panel(ax: Any, df: pd.DataFrame, request: ChartRequest, *, variant: str, label: str | None = None):
    _, _, colors, patches, PatchCollection, _ = require_matplotlib()
    font_family = resolve_font_family(request.theme.font_family())
    polygons: list[Any] = []
    fills: list[Any] = []
    outlines: list[str] = []
    x_values: list[float] = []
    y_values: list[float] = []
    for _, row in df.iterrows():
        for ring in geometry_to_polygons(row["geometry"]):
            polygons.append(patches.Polygon(ring, closed=True))
            fills.append(row["bin"] if variant == "binned" else row["fill_value"])
            outlines.append(
                request.theme.color("highlight.selection", "#2C7FB8")
                if bool(row.get("highlight_flag", False))
                else request.theme.color("neutral.axis", "#D9E2EC")
            )
            x_values.extend(point[0] for point in ring)
            y_values.extend(point[1] for point in ring)

    collection = PatchCollection(polygons, linewidths=1.0)
    if variant == "binned":
        categories = sorted({str(value) for value in fills if pd.notna(value)})
        cmap = get_colormap("Blues")
        color_lookup = {category: cmap(index / max(1, len(categories) - 1)) for index, category in enumerate(categories)}
        collection.set_facecolor([color_lookup.get(str(value), request.theme.color("neutral.grid", "#D9E2EC")) for value in fills])
    elif pd.Series(fills).notna().any():
        if variant == "diverging":
            cmap = get_colormap("RdBu_r")
            bound = max(abs(float(pd.Series(fills).min())), abs(float(pd.Series(fills).max())))
            norm = colors.TwoSlopeNorm(vmin=-bound, vcenter=0.0, vmax=bound)
        else:
            cmap = get_colormap("Blues")
            numeric = [float(value) for value in fills if pd.notna(value)]
            norm = colors.Normalize(vmin=min(numeric), vmax=max(numeric))
        collection.set_cmap(cmap)
        collection.set_norm(norm)
        collection.set_array(pd.Series(fills, dtype="float64"))
    else:
        collection.set_facecolor(request.theme.color("neutral.grid", "#D9E2EC"))
    collection.set_edgecolor(outlines)
    ax.add_collection(collection)
    ax.autoscale_view()
    bounds = None
    if x_values and y_values:
        bounds = (min(x_values), min(y_values), max(x_values), max(y_values))
    set_map_limits(ax, bounds)
    finalize_map_axes(ax)
    if label:
        ax.text(
            0.02,
            0.98,
            label,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=request.theme.font_size("subtitle_size", 10),
            family=font_family,
            color=request.theme.color("neutral.text", "#1F2933"),
        )
    return collection, fills


def render_choropleth(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest):
    plt, _, _, patches, _, _ = require_matplotlib()
    cfg = df.attrs.get("chart_config", {})
    variant = str(cfg.get("variant") or request.field_values.get("variant") or "continuous").lower()
    facet_by = str(cfg.get("facet_by") or request.field_values.get("facet_by") or "").strip()
    if facet_by and facet_by in df.columns:
        facet_values = df[facet_by].dropna().astype(str).unique().tolist()
        fig, axes = create_subplots(request, "choropleth", len(facet_values), columns=int(cfg.get("facet_ncol") or request.field_values.get("facet_ncol") or 2))
    else:
        facet_values = []
        fig, ax = create_figure(request, "choropleth")
        axes = [ax]

    default_title = request.title or (
        f"{df['metric_label'].iloc[0]} map" if "metric_label" in df.columns and len(df) else "Choropleth map"
    )
    default_subtitle = request.subtitle or (
        f"{df['time_window'].iloc[0]} | {variant.title()} map" if "time_window" in df.columns and len(df) else variant.title()
    )
    apply_titles(fig, axes[0], request, "choropleth", default_title, default_subtitle)

    if "geometry" not in df.columns or df["geometry"].isna().all():
        raise ValueError("choropleth rendering requires a 'geometry' column with polygon-like coordinates")

    if facet_values:
        collections = []
        for index, value in enumerate(facet_values):
            subset = df.loc[df[facet_by].astype(str) == value].copy()
            collection, _ = _choropleth_panel(axes[index], subset, request, variant=variant, label=value)
            collections.append(collection)
        for ax in axes[len(facet_values):]:
            ax.set_visible(False)
        colorbar_source = collections[0] if collections else None
    else:
        colorbar_source, fills = _choropleth_panel(axes[0], df, request, variant=variant)

    if variant == "binned":
        legend_labels = sorted(df["bin"].dropna().astype(str).unique().tolist())
        handles = [
            patches.Patch(facecolor=get_colormap("Blues")(index / max(1, len(legend_labels) - 1)), edgecolor="white", label=label)
            for index, label in enumerate(legend_labels)
        ]
        fig.legend(handles=handles, loc="center left", bbox_to_anchor=(0.82, 0.36), frameon=False, title="Bin")
    elif colorbar_source is not None and pd.Series(df["fill_value"] if "fill_value" in df.columns else df["metric_value"]).notna().any():
        fig.colorbar(
            colorbar_source,
            ax=[ax for ax in axes if ax.get_visible()],
            shrink=0.72,
            pad=0.02,
            label=df["metric_label"].iloc[0] if "metric_label" in df.columns else "",
        )

    add_caption(fig, df, request)
    fig.subplots_adjust(left=0.05, right=0.80, top=0.82, bottom=0.12, wspace=0.08, hspace=0.18)
    return fig
