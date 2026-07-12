from __future__ import annotations

from typing import Any

import pandas as pd

from ..geo import geometry_to_polygons
from ..request import ChartRequest
from ..specs import ChartSpec
from .mpl_helpers import add_caption, apply_titles, create_figure, create_subplots, finalize_map_axes, get_colormap, require_matplotlib, resolve_font_family


def render_highlight_context_map(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest):
    _, _, colors, patches, PatchCollection, Line2D = require_matplotlib()
    cfg = df.attrs.get("chart_config", {})
    variant = str(cfg.get("variant") or request.field_values.get("variant") or "focus_only").lower()
    facet_by = str(cfg.get("facet_by") or request.field_values.get("facet_by") or "").strip()
    if facet_by and facet_by in df.columns:
        facet_values = df[facet_by].dropna().astype(str).unique().tolist()
        fig, axes = create_subplots(request, "highlight_context_map", len(facet_values), columns=int(cfg.get("facet_ncol") or request.field_values.get("facet_ncol") or 2))
    else:
        facet_values = []
        fig, ax = create_figure(request, "highlight_context_map")
        axes = [ax]
    font_family = resolve_font_family(request.theme.font_family())

    highlight_names = df.loc[df["highlight_flag"], "geo_name"].tolist()
    title = ", ".join(highlight_names[:2]) if highlight_names else "Highlight context map"
    subtitle = request.subtitle or (
        f"{df['time_window'].iloc[0]} | {variant.replace('_', ' ')}" if "time_window" in df.columns and len(df) else variant.replace("_", " ")
    )
    apply_titles(fig, axes[0], request, "highlight_context_map", title, subtitle)

    if "geometry" not in df.columns or df["geometry"].isna().all():
        raise ValueError("highlight_context_map rendering requires a 'geometry' column with polygon-like coordinates")

    def draw_panel(ax_obj: Any, panel_df: pd.DataFrame, label: str | None = None):
        polygons: list[Any] = []
        fill_payload: list[Any] = []
        facecolors: list[Any] = []
        edges: list[str] = []
        for _, row in panel_df.iterrows():
            if variant == "focus_only":
                role = row.get("focus_role")
                if role == "Highlighted geography":
                    facecolor = request.theme.color("highlight.selection", "#2C7FB8")
                elif role == "Neighbor context":
                    facecolor = request.theme.color("comparison.benchmark", "#94A3B8")
                else:
                    facecolor = request.theme.color("neutral.grid", "#E5E7EB")
                fill_value = facecolor
            elif variant == "binned":
                fill_value = row.get("bin")
            else:
                fill_value = row.get("fill_value")

            edge = request.theme.color("highlight.selection", "#2C7FB8") if row["highlight_flag"] else request.theme.color("neutral.grid", "#D9E2EC")
            if bool(row.get("neighbor_flag", False)) and not row["highlight_flag"]:
                edge = request.theme.color("comparison.benchmark", "#52606D")
            for ring in geometry_to_polygons(row["geometry"]):
                polygons.append(patches.Polygon(ring, closed=True))
                fill_payload.append(fill_value)
                edges.append(edge)
                if variant == "focus_only":
                    facecolors.append(fill_value)

        collection = PatchCollection(polygons, linewidths=1.2)
        if variant == "focus_only":
            collection.set_facecolor(facecolors)
        elif variant == "binned":
            categories = sorted({str(value) for value in fill_payload if pd.notna(value)})
            cmap = get_colormap("viridis")
            color_lookup = {category: cmap(index / max(1, len(categories) - 1)) for index, category in enumerate(categories)}
            collection.set_facecolor([color_lookup.get(str(value), request.theme.color("neutral.grid", "#E5E7EB")) for value in fill_payload])
        elif pd.Series(fill_payload).notna().any():
            cmap = get_colormap("RdBu_r" if variant == "diverging" else "Greys")
            numeric = [float(value) for value in fill_payload if pd.notna(value)]
            if variant == "diverging":
                bound = max(abs(min(numeric)), abs(max(numeric)))
                collection.set_norm(colors.TwoSlopeNorm(vmin=-bound, vcenter=0.0, vmax=bound))
            else:
                collection.set_norm(colors.Normalize(vmin=min(numeric), vmax=max(numeric)))
            collection.set_cmap(cmap)
            collection.set_array(pd.Series(fill_payload, dtype="float64"))
        else:
            collection.set_facecolor(request.theme.color("neutral.grid", "#E5E7EB"))
        collection.set_edgecolor(edges)
        collection.set_alpha(0.95)
        ax_obj.add_collection(collection)
        ax_obj.autoscale_view()
        finalize_map_axes(ax_obj)
        if label:
            ax_obj.text(0.02, 0.98, label, transform=ax_obj.transAxes, ha="left", va="top", fontsize=10, family=font_family)
        return collection

    legend_handles = [
        Line2D([0], [0], color=request.theme.color("highlight.selection", "#2C7FB8"), linewidth=2, label="Highlight"),
        Line2D([0], [0], color=request.theme.color("comparison.benchmark", "#52606D"), linewidth=2, label="Neighbor"),
        Line2D([0], [0], color=request.theme.color("neutral.grid", "#D9E2EC"), linewidth=2, label="Context"),
    ]
    if facet_values:
        collections = []
        for index, value in enumerate(facet_values):
            collections.append(draw_panel(axes[index], df.loc[df[facet_by].astype(str) == value].copy(), value))
        for ax in axes[len(facet_values):]:
            ax.set_visible(False)
        axes[0].legend(handles=legend_handles, loc="lower right", frameon=False, prop={"family": font_family, "size": 9})
        if variant in {"continuous", "diverging"} and collections:
            fig.colorbar(collections[0], ax=[ax for ax in axes if ax.get_visible()], shrink=0.72, label=df["metric_label"].iloc[0] if "metric_label" in df.columns else "")
    else:
        collection = draw_panel(axes[0], df)
        axes[0].legend(handles=legend_handles, loc="lower right", frameon=False, prop={"family": font_family, "size": 9})
        if variant in {"continuous", "diverging"} and "metric_value" in df.columns and df["metric_value"].notna().any():
            fig.colorbar(collection, ax=axes[0], shrink=0.72, label=df["metric_label"].iloc[0] if "metric_label" in df.columns else "")
    add_caption(fig, df, request)
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    return fig
