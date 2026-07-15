from __future__ import annotations

from typing import Any

import pandas as pd

from ..geo import geometry_to_polygons
from ..request import ChartRequest
from ..specs import ChartSpec
from .mpl_helpers import add_caption, apply_titles, create_figure, create_subplots, finalize_map_axes, get_colormap, require_matplotlib, resolve_font_family, set_map_limits


def render_highlight_context_map(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest):
    _, _, colors, patches, PatchCollection, _ = require_matplotlib()
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
        x_values: list[float] = []
        y_values: list[float] = []
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
                x_values.extend(point[0] for point in ring)
                y_values.extend(point[1] for point in ring)

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
        bounds = None
        if x_values and y_values:
            bounds = (min(x_values), min(y_values), max(x_values), max(y_values))
        set_map_limits(ax_obj, bounds)
        finalize_map_axes(ax_obj)
        if label:
            ax_obj.text(0.02, 0.98, label, transform=ax_obj.transAxes, ha="left", va="top", fontsize=10, family=font_family)

        label_mask = panel_df["highlight_flag"].copy()
        if "label_flag" in panel_df.columns:
            label_mask = label_mask | panel_df["label_flag"].fillna(False).astype(bool)
        label_rows = panel_df.loc[label_mask].copy()
        for _, label_row in label_rows.iterrows():
            geometry = label_row.get("geometry")
            if geometry is None:
                continue
            rings = list(geometry_to_polygons(geometry))
            if not rings:
                continue
            ring = rings[0]
            center_x = sum(point[0] for point in ring) / len(ring)
            center_y = sum(point[1] for point in ring) / len(ring)
            ax_obj.text(
                center_x,
                center_y,
                str(label_row.get("geo_name", "")),
                ha="left",
                va="center",
                fontsize=request.theme.font_size("caption_size", 9),
                family=font_family,
                color=request.theme.color("neutral.text", "#1F2933"),
                bbox={
                    "facecolor": request.theme.color("neutral.background_white", "#FFFFFF"),
                    "edgecolor": "none",
                    "alpha": 0.8,
                    "pad": 1.5,
                },
            )
        return collection

    role_handles = []
    if df["highlight_flag"].any():
        role_handles.append(
            patches.Patch(
                facecolor="none",
                edgecolor=request.theme.color("highlight.selection", "#2C7FB8"),
                linewidth=1.8,
                label="Highlighted geography",
            )
        )
    if "neighbor_flag" in df.columns and df["neighbor_flag"].any() and variant == "focus_only":
        role_handles.append(
            patches.Patch(
                facecolor="none",
                edgecolor=request.theme.color("comparison.benchmark", "#52606D"),
                linewidth=1.8,
                label="Neighbor context",
            )
        )
    if facet_values:
        collections = []
        for index, value in enumerate(facet_values):
            collections.append(draw_panel(axes[index], df.loc[df[facet_by].astype(str) == value].copy(), value))
        for ax in axes[len(facet_values):]:
            ax.set_visible(False)
        if variant in {"continuous", "diverging"} and collections:
            fig.colorbar(
                collections[0],
                ax=[ax for ax in axes if ax.get_visible()],
                shrink=0.72,
                pad=0.02,
                label=df["metric_label"].iloc[0] if "metric_label" in df.columns else "",
            )
    else:
        collection = draw_panel(axes[0], df)
        if variant in {"continuous", "diverging"} and "metric_value" in df.columns and df["metric_value"].notna().any():
            fig.colorbar(
                collection,
                ax=axes[0],
                shrink=0.72,
                pad=0.02,
                label=df["metric_label"].iloc[0] if "metric_label" in df.columns else "",
            )

    if variant == "binned":
        tier_labels = sorted(df["bin"].dropna().astype(str).unique().tolist())
        tier_handles = [
            patches.Patch(
                facecolor=get_colormap("viridis")(index / max(1, len(tier_labels) - 1)),
                edgecolor=request.theme.color("neutral.background_white", "#FFFFFF"),
                label=label,
            )
            for index, label in enumerate(tier_labels)
        ]
        if tier_handles:
            tier_legend = fig.legend(
                handles=tier_handles,
                loc="center left",
                bbox_to_anchor=(0.78, 0.30),
                frameon=False,
                title=cfg.get("legend_title") or (df["metric_label"].iloc[0] if "metric_label" in df.columns and len(df) else "Metric tier"),
                prop={"family": font_family, "size": 9},
            )
            if hasattr(tier_legend, "get_title"):
                tier_legend.get_title().set_family(font_family)

    if role_handles:
        role_legend = fig.legend(
            handles=role_handles,
            loc="center left",
            bbox_to_anchor=(0.78, 0.18 if variant == "binned" else 0.28),
            frameon=False,
            title="Map role",
            prop={"family": font_family, "size": 9},
        )
        if hasattr(role_legend, "get_title"):
            role_legend.get_title().set_family(font_family)

    add_caption(fig, df, request)
    fig.tight_layout(rect=(0, 0.05, 0.75, 0.92))
    return fig
