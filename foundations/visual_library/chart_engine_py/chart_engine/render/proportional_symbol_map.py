from __future__ import annotations

import pandas as pd

from ..request import ChartRequest
from ..specs import ChartSpec
from .mpl_helpers import add_caption, apply_titles, create_figure, create_subplots, finalize_map_axes, require_matplotlib, resolve_font_family, scale_sizes


def render_proportional_symbol_map(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest):
    _, _, _, _, _, Line2D = require_matplotlib()
    cfg = df.attrs.get("chart_config", {})
    color_mode = str(cfg.get("color_mode") or request.field_values.get("color_mode") or "highlight").lower()
    facet_by = str(cfg.get("facet_by") or request.field_values.get("facet_by") or "").strip()
    if facet_by and facet_by in df.columns:
        facet_values = df[facet_by].dropna().astype(str).unique().tolist()
        fig, axes = create_subplots(request, "proportional_symbol_map", len(facet_values), columns=int(cfg.get("facet_ncol") or request.field_values.get("facet_ncol") or 2))
    else:
        facet_values = []
        fig, ax = create_figure(request, "proportional_symbol_map")
        axes = [ax]
    font_family = resolve_font_family(request.theme.font_family())

    title = request.title or (df["size_label"].iloc[0] if len(df) else "Proportional symbol map")
    subtitle = request.subtitle or (
        f"{df['time_window'].iloc[0]} | bubbles show totals" if "time_window" in df.columns and len(df) else "Bubbles show totals"
    )
    apply_titles(fig, axes[0], request, "proportional_symbol_map", title, subtitle)

    def draw_panel(ax_obj, panel_df: pd.DataFrame, label: str | None = None):
        sizes = scale_sizes(panel_df["size_value"])
        if color_mode == "color_group" and "color_group" in panel_df.columns:
            groups = panel_df["color_group"].fillna("Unknown").astype(str)
            color_cycle = [
                request.theme.color("highlight.selection", "#2C7FB8"),
                request.theme.color("diverging.better", "#0C7C78"),
                request.theme.color("comparison.benchmark", "#52606D"),
                request.theme.color("diverging.worse", "#D66A4E"),
            ]
            unique_groups = groups.unique().tolist()
            palette = {
                group: color_cycle[index % len(color_cycle)]
                for index, group in enumerate(unique_groups)
            }
            facecolors = [palette[group] for group in groups]
        else:
            facecolors = [
                request.theme.color("highlight.selection", "#2C7FB8") if highlight else request.theme.color("comparison.neutral", "#7B8794")
                for highlight in panel_df.get("highlight_flag", pd.Series(False, index=panel_df.index))
            ]
        ax_obj.scatter(
            panel_df["lon"],
            panel_df["lat"],
            s=sizes,
            c=facecolors,
            alpha=float(cfg.get("point_alpha", 0.72)),
            edgecolors=request.theme.color("neutral.text", "#1F2933"),
            linewidths=0.8,
        )
        if "label_flag" in panel_df.columns and panel_df["label_flag"].any():
            for _, row in panel_df[panel_df["label_flag"]].iterrows():
                label_text = str(row["geo_name"])
                if cfg.get("label_include_value", True):
                    label_text = f"{label_text}\n{request.theme.format(row['size_value'], request.number_format) or row['size_value']}"
                ax_obj.text(
                    row["lon"],
                    row["lat"],
                    label_text,
                    fontsize=9,
                    family=font_family,
                    color=request.theme.color("neutral.text", "#1F2933"),
                    ha="left",
                    va="bottom",
                )
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

    size_breaks = sorted(df["size_value"].dropna().unique().tolist())
    if len(size_breaks) > 4:
        step = max(1, len(size_breaks) // 4)
        size_breaks = size_breaks[::step][:4]
    size_handles = [
        axes[0].scatter([], [], s=scale_sizes(pd.Series([value])).iloc[0], c=request.theme.color("comparison.neutral", "#7B8794"), alpha=0.72, edgecolors=request.theme.color("neutral.text", "#1F2933"))
        for value in size_breaks
    ]
    size_labels = [request.theme.format(value, request.number_format) or str(value) for value in size_breaks]
    legend_one = axes[0].legend(size_handles, size_labels, loc="upper left", frameon=False, title=df["size_label"].iloc[0] if "size_label" in df.columns and len(df) else "Size")
    axes[0].add_artist(legend_one)

    if color_mode == "color_group" and "color_group" in df.columns:
        group_values = df["color_group"].fillna("Unknown").astype(str).unique().tolist()
        color_cycle = [
            request.theme.color("highlight.selection", "#2C7FB8"),
            request.theme.color("diverging.better", "#0C7C78"),
            request.theme.color("comparison.benchmark", "#52606D"),
            request.theme.color("diverging.worse", "#D66A4E"),
        ]
        group_handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=color_cycle[index % len(color_cycle)], markeredgecolor=request.theme.color("neutral.text", "#1F2933"), markersize=8, label=value) for index, value in enumerate(group_values)]
        axes[0].legend(handles=group_handles, loc="lower right", frameon=False, title="Group")
    else:
        role_handles = [
            Line2D([0], [0], marker="o", color="w", markerfacecolor=request.theme.color("highlight.selection", "#2C7FB8"), markeredgecolor=request.theme.color("neutral.text", "#1F2933"), markersize=8, label="Highlight"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=request.theme.color("comparison.neutral", "#7B8794"), markeredgecolor=request.theme.color("neutral.text", "#1F2933"), markersize=8, label="Context"),
        ]
        axes[0].legend(handles=role_handles, loc="lower right", frameon=False)

    add_caption(fig, df, request)
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    return fig
