from __future__ import annotations

import pandas as pd

from ..request import ChartRequest
from ..specs import ChartSpec
from .mpl_helpers import add_caption, apply_titles, create_figure, require_matplotlib, resolve_font_family


def render_hexbin(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest):
    _, _, _, _, _, _ = require_matplotlib()
    fig, ax = create_figure(request, "hexbin")
    font_family = resolve_font_family(request.theme.font_family())

    title = f"{df['x_label'].iloc[0]} vs {df['y_label'].iloc[0]}" if len(df) else "Hexbin"
    subtitle = request.subtitle or (df["time_window"].iloc[0] if "time_window" in df.columns and len(df) else None)
    apply_titles(fig, ax, request, "hexbin", title, subtitle)

    hexbin_kwargs = {
        "x": df["x_value"],
        "y": df["y_value"],
        "gridsize": 20,
        "cmap": "Blues",
        "mincnt": 1,
    }
    if "weight_value" in df.columns and df["weight_value"].notna().any():
        hexbin_kwargs["C"] = df["weight_value"]
        hexbin_kwargs["reduce_C_function"] = sum

    hexes = ax.hexbin(**hexbin_kwargs)
    colorbar_label = "Weighted mass" if "C" in hexbin_kwargs else "Observation count"
    fig.colorbar(hexes, ax=ax, shrink=0.72, label=colorbar_label)

    if "highlight_flag" in df.columns and df["highlight_flag"].any():
        highlights = df[df["highlight_flag"]]
        ax.scatter(
            highlights["x_value"],
            highlights["y_value"],
            s=36,
            facecolor=request.theme.color("highlight.selection", "#2C7FB8"),
            edgecolor=request.theme.color("neutral.text", "#1F2933"),
            linewidth=0.8,
            zorder=3,
        )

    ax.set_xlabel(df["x_label"].iloc[0] if len(df) else "", fontfamily=font_family)
    ax.set_ylabel(df["y_label"].iloc[0] if len(df) else "", fontfamily=font_family)
    ax.grid(color=request.theme.color("neutral.grid", "#E5E7EB"), linewidth=0.6, alpha=0.6)
    add_caption(fig, df, request)
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    return fig
