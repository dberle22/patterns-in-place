from __future__ import annotations

import pandas as pd

from ..request import ChartRequest
from ..specs import ChartSpec
from .mpl_helpers import add_caption, apply_titles, create_figure, require_matplotlib, resolve_font_family, scale_sizes


def render_proportional_symbol_map(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest):
    _, _, _, _, _, _ = require_matplotlib()
    fig, ax = create_figure(request, "proportional_symbol_map")
    font_family = resolve_font_family(request.theme.font_family())

    title = request.title or (df["size_label"].iloc[0] if len(df) else "Proportional symbol map")
    subtitle = request.subtitle or (df["time_window"].iloc[0] if "time_window" in df.columns and len(df) else None)
    apply_titles(fig, ax, request, "proportional_symbol_map", title, subtitle)

    sizes = scale_sizes(df["size_value"])
    facecolors = [
        request.theme.color("highlight.selection", "#2C7FB8") if highlight else request.theme.color("comparison.neutral", "#7B8794")
        for highlight in df.get("highlight_flag", pd.Series(False, index=df.index))
    ]
    ax.scatter(
        df["lon"],
        df["lat"],
        s=sizes,
        c=facecolors,
        alpha=0.72,
        edgecolors=request.theme.color("neutral.text", "#1F2933"),
        linewidths=0.8,
    )

    if "label_flag" in df.columns and df["label_flag"].any():
        for _, row in df[df["label_flag"]].iterrows():
            ax.text(
                row["lon"],
                row["lat"],
                str(row["geo_name"]),
                fontsize=9,
                family=font_family,
                color=request.theme.color("neutral.text", "#1F2933"),
                ha="left",
                va="bottom",
            )

    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    add_caption(fig, df, request)
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    return fig
