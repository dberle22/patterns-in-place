from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_altair_title_params, build_data_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def render_line_chart(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = theme.chart_defaults_for(request.chart_type)
    plot_df = df.copy()
    if "plot_value" not in plot_df.columns:
        plot_df["plot_value"] = plot_df["value"]
    plot_df = plot_df[plot_df["plot_value"].notna()].copy()

    title = request.title or _default_title(plot_df, spec.chart_type)
    subtitle = request.subtitle or _default_subtitle(plot_df)
    caption = build_data_caption(plot_df)

    dims = request.dimensions
    width = dims.width if dims and dims.width else theme.width(request.chart_type)
    height = dims.height if dims and dims.height else theme.height(request.chart_type)

    series_order = list(dict.fromkeys(plot_df["series"]))
    color_scale = alt.Scale(
        domain=series_order,
        range=_resolve_series_colors(plot_df, series_order, theme, cfg),
    )

    title_params = build_altair_title_params(
        title,
        subtitle=subtitle,
        caption=caption,
        title_size=theme.title_size(),
        subtitle_wrap_width=int(cfg.get("subtitle_wrap_width", 120)),
        caption_wrap_width=int(cfg.get("caption_wrap_width", 135)),
    )

    base = (
        alt.Chart(plot_df)
        .mark_line(point=bool(cfg.get("show_points", True)))
        .encode(
            x=alt.X("period:O", title=None),
            y=alt.Y("plot_value:Q", title=_y_axis_title(plot_df), axis=alt.Axis(format=theme.d3_format(request.number_format))),
            color=alt.Color("series:N", scale=color_scale, legend=alt.Legend(title=None)),
            tooltip=[
                alt.Tooltip("series:N", title="Series"),
                alt.Tooltip("period:O", title="Period"),
                alt.Tooltip("plot_value:Q", title="Value", format=theme.d3_format(request.number_format)),
            ],
        )
    )

    layers = [base]

    for ann in request.annotations:
        if ann.kind == "vline":
            ann_df = pd.DataFrame({"period": [ann.x]})
            rule = alt.Chart(ann_df).mark_rule(
                color=theme.color("highlight.risk", "#C44536"), strokeDash=[2, 2]
            ).encode(x="period:O")
            layers.append(rule)
            if ann.label:
                label_df = pd.DataFrame({"period": [ann.x], "plot_value": [plot_df["plot_value"].max()], "label": [ann.label]})
                text = alt.Chart(label_df).mark_text(
                    align="left", dx=5, color=theme.color("highlight.risk", "#C44536")
                ).encode(x="period:O", y="plot_value:Q", text="label:N")
                layers.append(text)

    benchmark = _benchmark_layer(plot_df, request, theme, cfg)
    if benchmark is not None:
        layers.append(benchmark)

    layered = (
        alt.layer(*layers)
        .properties(
            width=width,
            height=height,
        )
    )

    if request.facet and request.facet.facet_field in plot_df.columns:
        chart = layered.facet(
            facet=alt.Facet(f"{request.facet.facet_field}:N", columns=request.facet.columns),
        )
        if not request.facet.shared_y_axis:
            chart = chart.resolve_scale(y="independent")
        chart = chart.properties(title=alt.TitleParams(**title_params))
    else:
        chart = layered.properties(title=alt.TitleParams(**title_params))

    return chart.configure_axis(
        labelFont=theme.font_family(),
        titleFont=theme.font_family(),
        labelColor=theme.color("neutral.axis", "#5B6770"),
        gridColor=theme.color("neutral.grid_major", "#D9E2EC"),
    ).configure_title(
        font=theme.font_family(),
        color=theme.color("neutral.text", "#1F2933"),
        subtitleColor=theme.color("neutral.text_muted", "#52606D"),
        subtitleFont=theme.font_family(),
    ).configure_legend(
        labelFont=theme.font_family(),
        labelColor=theme.color("neutral.text_muted", "#52606D"),
    ).configure_view(stroke=None)


def _default_title(df: pd.DataFrame, fallback: str) -> str:
    metric_label = df["metric_label"].dropna().iloc[0] if "metric_label" in df.columns and df["metric_label"].dropna().any() else fallback
    geo_names = [str(value).strip() for value in df["geo_name"].dropna().unique()] if "geo_name" in df.columns else []
    highlighted = (
        [str(value).strip() for value in df.loc[df["highlight_flag"], "geo_name"].dropna().unique()]
        if {"highlight_flag", "geo_name"}.issubset(df.columns)
        else []
    )

    if len(geo_names) == 1:
        return f"{metric_label}: {geo_names[0]}"
    if len(highlighted) == 1:
        return f"{metric_label}: {highlighted[0]} vs peers"
    return f"{metric_label}: selected geographies"


def _default_subtitle(df: pd.DataFrame) -> str | None:
    parts: list[str] = []
    periods = pd.to_numeric(df["period"], errors="coerce").dropna() if "period" in df.columns else pd.Series(dtype=float)
    if not periods.empty:
        parts.append(f"Period: {int(periods.min())}-{int(periods.max())}")

    variant = str(df["variant"].dropna().iloc[0]) if "variant" in df.columns and df["variant"].dropna().any() else None
    if variant == "indexed":
        base_period = pd.to_numeric(df["index_base_period"], errors="coerce").dropna() if "index_base_period" in df.columns else pd.Series(dtype=float)
        if not base_period.empty:
            parts.append(f"Indexed to {int(base_period.iloc[0])} = 100")
        else:
            parts.append("Indexed series")
    elif variant and variant.startswith("rolling_"):
        parts.append(f"Transform: {variant}")

    if "group" in df.columns:
        groups = [str(value).strip() for value in df["group"].dropna().unique() if str(value).strip()]
        if len(groups) == 1:
            parts.append(f"Scope: {groups[0]}")
    return " | ".join(parts) if parts else None


def _resolve_series_colors(df: pd.DataFrame, series_order: list[str], theme, cfg: dict) -> list[str]:
    peer_palette = cfg.get("peer_palette", []) or [
        theme.color("comparison.peers.0", "#AEBECD"),
        theme.color("comparison.peers.1", "#6E859E"),
        theme.color("comparison.peers.2", "#8C9472"),
        theme.color("comparison.peers.3", "#9A7F6B"),
    ]
    if len(series_order) > len(peer_palette):
        peer_palette = peer_palette + [theme.color("comparison.neutral", "#A7B4C2")] * (len(series_order) - len(peer_palette))

    highlighted = set(df.loc[df["highlight_flag"], "series"].astype(str).unique()) if "highlight_flag" in df.columns else set()
    colors: list[str] = []
    peer_index = 0
    for series in series_order:
        if series in highlighted:
            colors.append(theme.color("highlight.selection", cfg.get("highlight_color", "#2C7FB8")))
        else:
            colors.append(peer_palette[peer_index])
            peer_index += 1
    return colors


def _benchmark_layer(df: pd.DataFrame, request: ChartRequest, theme, cfg: dict):
    benchmark_df = None
    if request.benchmark and request.benchmark.value is not None:
        benchmark_df = pd.DataFrame(
            {
                "period": sorted(df["period"].astype(str).unique()),
                "benchmark_value": [request.benchmark.value] * df["period"].nunique(),
            }
        )
    elif "benchmark_value" in df.columns and df["benchmark_value"].notna().any():
        benchmark_df = df[["period", "benchmark_value"]].dropna().groupby("period", as_index=False)["benchmark_value"].mean()

    if benchmark_df is None or benchmark_df.empty:
        return None

    return (
        alt.Chart(benchmark_df)
        .mark_line(
            color=theme.color("comparison.benchmark", cfg.get("benchmark_color", "#52606D")),
            strokeDash=cfg.get("benchmark_linetype", [4, 4]),
            strokeWidth=cfg.get("benchmark_linewidth", 1),
        )
        .encode(x="period:O", y="benchmark_value:Q")
    )


def _y_axis_title(df: pd.DataFrame) -> str | None:
    metric_label = df["metric_label"].dropna().iloc[0] if "metric_label" in df.columns and df["metric_label"].dropna().any() else None
    variant = str(df["variant"].dropna().iloc[0]) if "variant" in df.columns and df["variant"].dropna().any() else None
    if variant == "indexed":
        base_period = pd.to_numeric(df["index_base_period"], errors="coerce").dropna() if "index_base_period" in df.columns else pd.Series(dtype=float)
        if metric_label and not base_period.empty:
            return f"{metric_label} ({int(base_period.iloc[0])} = 100)"
        return "Index"
    return metric_label
