from __future__ import annotations

import pandas as pd

from ..request import ChartRequest
from ..specs import ChartSpec
from .mpl_helpers import add_caption, apply_titles, create_figure, create_subplots, require_matplotlib, resolve_font_family


def _method_label(method: str) -> str:
    return "2D bins" if method == "rect" else "Hexbin"


def _uses_weights(df: pd.DataFrame, cfg: dict) -> bool:
    if cfg.get("use_weights") is not None:
        return bool(cfg.get("use_weights"))
    if "weight_value" not in df.columns:
        return False

    weights = pd.to_numeric(df["weight_value"], errors="coerce").dropna()
    if weights.empty:
        return False
    return bool((weights - 1.0).abs().gt(1e-9).any())


def _reference_value(series: pd.Series, method: str) -> float | None:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return None
    return float(numeric.mean()) if str(method).lower() == "mean" else float(numeric.median())


def _build_subtitle(df: pd.DataFrame, cfg: dict, method: str, weighted: bool, facet_by: str) -> str | None:
    windows = df["time_window"].dropna().astype(str).unique().tolist() if "time_window" in df.columns else []
    parts: list[str] = []
    if len(windows) == 1:
        parts.append(f"Time window: {windows[0]}")
    parts.append(
        f"{_method_label(method)} | Fill = "
        f"{cfg.get('weight_label') or 'weighted sum' if weighted else 'count'}"
    )
    if facet_by and facet_by in df.columns and df[facet_by].dropna().astype(str).nunique() > 1:
        parts.append(f"Faceted by {facet_by.replace('_', ' ')}")
    return " | ".join(parts) if parts else None


def _draw_panel(ax, df: pd.DataFrame, request: ChartRequest, *, cfg: dict, method: str, weighted: bool, panel_label: str | None):
    _, _, _, _, _, Line2D = require_matplotlib()
    font_family = resolve_font_family(request.theme.font_family())
    highlight_color = request.theme.color("highlight.selection", "#2C7FB8")

    if method == "rect":
        hist = ax.hist2d(
            df["x_value"],
            df["y_value"],
            bins=int(cfg.get("bins", 28)),
            weights=df["weight_value"] if weighted and "weight_value" in df.columns else None,
            cmap="viridis",
            cmin=1,
        )
        mappable = hist[3]
    else:
        hexbin_kwargs = {
            "x": df["x_value"],
            "y": df["y_value"],
            "gridsize": int(cfg.get("bins", 28)),
            "cmap": "viridis",
            "mincnt": 1,
        }
        if weighted and "weight_value" in df.columns:
            hexbin_kwargs["C"] = df["weight_value"]
            hexbin_kwargs["reduce_C_function"] = sum
        mappable = ax.hexbin(**hexbin_kwargs)

    if cfg.get("add_reference_lines"):
        reference_method = str(cfg.get("reference_method", "median"))
        x_ref = _reference_value(df["x_value"], reference_method)
        y_ref = _reference_value(df["y_value"], reference_method)
        if x_ref is not None:
            ax.axvline(
                x_ref,
                color=request.theme.color("benchmark.line", "#6B7280"),
                linewidth=1.0,
                linestyle="--",
                alpha=0.9,
            )
        if y_ref is not None:
            ax.axhline(
                y_ref,
                color=request.theme.color("benchmark.line", "#6B7280"),
                linewidth=1.0,
                linestyle="--",
                alpha=0.9,
            )

    legend_handles = []
    if cfg.get("overlay_highlights", True) and "highlight_flag" in df.columns and df["highlight_flag"].any():
        highlights = df.loc[df["highlight_flag"]].copy()
        ax.scatter(
            highlights["x_value"],
            highlights["y_value"],
            s=36,
            facecolor=highlight_color,
            edgecolor=request.theme.color("neutral.text", "#1F2933"),
            linewidth=0.8,
            zorder=3,
        )
        legend_handles.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor=highlight_color,
                markeredgecolor=request.theme.color("neutral.text", "#1F2933"),
                markersize=6,
                label="Highlight",
            )
        )

        labels = highlights.loc[highlights.get("label_flag", False)].copy()
        for _, row in labels.iterrows():
            ax.annotate(
                str(row.get("geo_name", "")),
                (row["x_value"], row["y_value"]),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=request.theme.font_size("caption_size", 9),
                fontfamily=font_family,
                color=request.theme.color("neutral.text", "#1F2933"),
            )

    if legend_handles:
        ax.legend(handles=legend_handles, loc="upper left", frameon=False, prop={"family": font_family})

    if panel_label:
        ax.set_title(
            panel_label,
            loc="left",
            fontsize=request.theme.font_size("subtitle_size", 10),
            fontfamily=font_family,
            color=request.theme.color("neutral.text", "#1F2933"),
        )

    ax.set_xlabel(df["x_label"].iloc[0] if len(df) else "", fontfamily=font_family)
    ax.set_ylabel(df["y_label"].iloc[0] if len(df) else "", fontfamily=font_family)
    if cfg.get("x_limits"):
        ax.set_xlim(cfg["x_limits"])
    if cfg.get("y_limits"):
        ax.set_ylim(cfg["y_limits"])
    ax.grid(color=request.theme.color("neutral.grid", "#E5E7EB"), linewidth=0.6, alpha=0.6)
    return mappable


def render_hexbin(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest):
    _, _, _, _, _, _ = require_matplotlib()
    cfg = {**(getattr(df, "attrs", {}).get("chart_config", {}) or {}), **(request.field_values or {})}
    method = "rect" if str(cfg.get("method", "hex")).lower() == "rect" else "hex"
    weighted = _uses_weights(df, cfg)
    facet_by = str(cfg.get("facet_by") or "").strip()

    title = f"Density of {df['y_label'].iloc[0]} vs {df['x_label'].iloc[0]}" if len(df) else "Hexbin"
    subtitle = request.subtitle or _build_subtitle(df, cfg, method, weighted, facet_by)
    colorbar_label = cfg.get("legend_title") or ((cfg.get("weight_label") or "Weighted sum") if weighted else "Count")

    if facet_by and facet_by in df.columns:
        facet_values = df[facet_by].dropna().astype(str).unique().tolist()
        fig, axes = create_subplots(request, "hexbin", len(facet_values), columns=int(cfg.get("facet_ncol") or 2))
        apply_titles(fig, axes[0], request, "hexbin", title, subtitle)
        for index, value in enumerate(facet_values):
            panel_df = df.loc[df[facet_by].astype(str) == value].copy()
            mappable = _draw_panel(axes[index], panel_df, request, cfg=cfg, method=method, weighted=weighted, panel_label=value)
            fig.colorbar(mappable, ax=axes[index], shrink=0.72, label=colorbar_label)
        for ax in axes[len(facet_values):]:
            ax.set_visible(False)
    else:
        fig, ax = create_figure(request, "hexbin")
        apply_titles(fig, ax, request, "hexbin", title, subtitle)
        mappable = _draw_panel(ax, df, request, cfg=cfg, method=method, weighted=weighted, panel_label=None)
        fig.colorbar(mappable, ax=ax, shrink=0.72, label=colorbar_label)

    add_caption(fig, df, request)
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    return fig
