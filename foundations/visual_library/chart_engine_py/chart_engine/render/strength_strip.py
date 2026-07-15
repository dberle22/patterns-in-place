from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_altair_title_params, build_data_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def render_strength_strip(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = theme.chart_defaults_for(request.chart_type)
    title = request.title or "Strength Strip"
    subtitle = request.subtitle or _default_subtitle(df)
    caption = build_data_caption(df)
    title_params = build_altair_title_params(
        title,
        subtitle=subtitle,
        caption=caption,
        title_size=theme.title_size(),
        subtitle_wrap_width=int(cfg.get("subtitle_wrap_width", 120)),
        caption_wrap_width=int(cfg.get("caption_wrap_width", 135)),
    )

    windows = list(dict.fromkeys(df["time_window"].astype(str).tolist())) if "time_window" in df.columns else [None]
    panels = [_build_strength_panel(df if window is None else df[df["time_window"].astype(str) == window].copy(), theme, show_panel_title=len(windows) > 1) for window in windows]
    if len(panels) == 1:
        chart = panels[0].properties(title=alt.TitleParams(**title_params))
    else:
        chart = alt.vconcat(*panels).properties(title=alt.TitleParams(**title_params))

    return chart.configure_axis(
        labelFont=theme.font_family(),
        titleFont=theme.font_family(),
        labelColor=theme.color("neutral.axis", "#5B6770"),
        gridColor=theme.color("neutral.grid_major", "#D9E2EC"),
    ).configure_title(
        font=theme.font_family(),
        color=theme.color("neutral.text", "#1F2933"),
        subtitleColor=theme.color("neutral.text_muted", "#52606D"),
    ).configure_view(stroke=None)


def _build_strength_panel(plot_df: pd.DataFrame, theme, *, show_panel_title: bool) -> alt.Chart:
    row_order = list(dict.fromkeys(plot_df.sort_values(["metric_order", "metric_display_label"])["metric_display_label"].tolist()))
    strip_rows = plot_df[["metric_display_label", "benchmark_normalized_value", "benchmark_label"]].drop_duplicates().copy()
    strip_rows["x_start"] = 0.0
    strip_rows["x_end"] = 100.0
    strips = alt.Chart(strip_rows).mark_rule(
        strokeWidth=6,
        color=theme.color("comparison.neutral", "#A7B4C2"),
        opacity=0.45,
    ).encode(
        x="x_start:Q",
        x2=alt.X2("x_end:Q"),
        y=alt.Y("metric_display_label:N", sort=row_order, title=None),
    )

    point_color_field = "geo_name" if plot_df["geo_name"].nunique() > 1 else "point_group"
    plot_df = plot_df.copy()
    plot_df["point_group"] = plot_df["highlight_flag"].map({True: "highlight", False: "comparison"})
    point_scale = _point_scale(plot_df, theme)
    points = alt.Chart(plot_df).mark_point(filled=True, size=90).encode(
        x=alt.X("normalized_value:Q", title="Percentile within comparison universe", scale=alt.Scale(domain=[0, 100])),
        y=alt.Y("metric_display_label:N", sort=row_order, title=None),
        color=alt.Color(point_color_field + ":N", scale=point_scale, legend=alt.Legend(title=None)),
        tooltip=[
            alt.Tooltip("geo_name:N", title="Geography"),
            alt.Tooltip("metric_label:N", title="Metric"),
            alt.Tooltip("normalized_value:Q", title="Percentile", format=".1f"),
            alt.Tooltip("benchmark_delta:Q", title="Benchmark delta", format=".1f"),
        ],
    )

    layers: list[alt.Chart] = [strips]
    if plot_df["geo_name"].nunique() == 1:
        bar_df = plot_df[plot_df["normalized_value"].notna()].copy()
        bar_df["strip_start"] = 0.0
        bar_df["strip_end"] = bar_df["normalized_value"]
        bars = alt.Chart(bar_df).mark_rule(strokeWidth=5, opacity=0.95).encode(
            x=alt.X("strip_start:Q"),
            x2=alt.X2("strip_end:Q"),
            y=alt.Y("metric_display_label:N", sort=row_order, title=None),
            color=alt.Color(point_color_field + ":N", scale=point_scale, legend=None),
        )
        layers.append(bars)
    layers.append(points)

    benchmark_df = strip_rows[strip_rows["benchmark_normalized_value"].notna()].copy()
    if not benchmark_df.empty:
        benchmark = alt.Chart(benchmark_df).mark_tick(
            color=theme.color("comparison.benchmark", "#52606D"),
            thickness=2,
            size=18,
        ).encode(
            x="benchmark_normalized_value:Q",
            y=alt.Y("metric_display_label:N", sort=row_order, title=None),
            tooltip=[
                alt.Tooltip("benchmark_label:N", title="Benchmark"),
                alt.Tooltip("benchmark_normalized_value:Q", title="Benchmark percentile", format=".1f"),
            ],
        )
        layers.append(benchmark)

    missing_df = plot_df[plot_df["missing_flag"]].copy()
    if not missing_df.empty:
        missing_df["missing_label_text"] = missing_df["geo_name"].astype(str) + " missing" if plot_df["geo_name"].nunique() > 1 else "Missing"
        missing_labels = alt.Chart(missing_df).mark_text(
            align="left",
            dx=6,
            font=theme.font_family(),
            color=theme.color("neutral.text_muted", "#52606D"),
        ).encode(
            x=alt.value(theme.width("strength_strip") - 30),
            y=alt.Y("metric_display_label:N", sort=row_order, title=None),
            text="missing_label_text:N",
        )
        layers.append(missing_labels)

    panel = alt.layer(*layers).properties(width=theme.width("strength_strip"), height=theme.height("strength_strip"))
    if show_panel_title:
        panel = panel.properties(title=str(plot_df["time_window"].iloc[0]))
    return panel


def _default_subtitle(df: pd.DataFrame) -> str | None:
    parts: list[str] = []
    windows = [str(value) for value in df["time_window"].dropna().unique()] if "time_window" in df.columns else []
    if len(windows) == 1:
        parts.append(f"Window: {windows[0]}")
    elif len(windows) > 1:
        parts.append(f"Compared windows: {', '.join(windows)}")
    groups = [str(value).strip() for value in df["metric_group"].dropna().unique()] if "metric_group" in df.columns else []
    groups = [value for value in groups if value]
    if len(groups) > 1:
        parts.append("Category-grouped KPI profile")
    if "benchmark_normalized_value" in df.columns and df["benchmark_normalized_value"].notna().any():
        parts.append("Benchmark markers show normalized comparison reference")
    return " | ".join(parts) if parts else None


def _point_scale(df: pd.DataFrame, theme) -> alt.Scale:
    if df["geo_name"].nunique() == 1:
        return alt.Scale(domain=["comparison", "highlight"], range=[theme.color("comparison.neutral", "#A7B4C2"), theme.color("highlight.selection", "#2C7FB8")])
    geo_names = list(dict.fromkeys(df["geo_name"].astype(str).tolist()))
    highlight_names = set(df.loc[df["highlight_flag"], "geo_name"].astype(str))
    colors = []
    peer_palette = [
        theme.color("comparison.peers.0", "#AEBECD"),
        theme.color("comparison.peers.1", "#6E859E"),
        theme.color("comparison.peers.2", "#8C9472"),
        theme.color("comparison.peers.3", "#9A7F6B"),
    ]
    peer_index = 0
    for name in geo_names:
        if name in highlight_names:
            colors.append(theme.color("highlight.selection", "#2C7FB8"))
        else:
            colors.append(peer_palette[peer_index % len(peer_palette)])
            peer_index += 1
    return alt.Scale(domain=geo_names, range=colors)
