"""
Render a scatter chart from prepared data.

The first Python scatter port keeps the core narrative tools from the working
R implementation: optional grouping, optional bubble size, trend line, simple
highlight labels, and support for guide annotations.
"""

from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_caption, wrap_text
from ..request import ChartRequest
from ..specs import ChartSpec


def _has_finite_size(df: pd.DataFrame) -> bool:
    return "size_value" in df.columns and df["size_value"].notna().any()


def render_scatter(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = theme.chart_defaults_for(request.chart_type)

    default_title = spec.docs.split("\n")[0].lstrip("#").strip() if spec.docs else spec.chart_type
    title = request.title or default_title
    subtitle = request.subtitle or (df["time_window"].iloc[0] if "time_window" in df.columns and len(df) else None)

    dims = request.dimensions
    width = dims.width if dims and dims.width else theme.width(request.chart_type)
    height = dims.height if dims and dims.height else theme.height(request.chart_type)

    x_title = df["x_label"].iloc[0] if "x_label" in df.columns and len(df) else None
    y_title = df["y_label"].iloc[0] if "y_label" in df.columns and len(df) else None
    d3_format = theme.d3_format(request.number_format)

    title_params = {"text": title, "fontSize": theme.title_size()}
    if subtitle:
        title_params["subtitle"] = wrap_text(subtitle, int(cfg.get("subtitle_wrap_width", 120)))

    has_group = "group" in df.columns and df["group"].notna().any()
    has_size = _has_finite_size(df)
    has_labels = "label_flag" in df.columns and df["label_flag"].any()

    tooltip = [
        alt.Tooltip("geo_name:N", title="Geography"),
        alt.Tooltip("x_value:Q", title=x_title or "X", format=d3_format),
        alt.Tooltip("y_value:Q", title=y_title or "Y", format=d3_format),
    ]

    base = alt.Chart(df).encode(
        x=alt.X("x_value:Q", title=x_title, axis=alt.Axis(format=d3_format)),
        y=alt.Y("y_value:Q", title=y_title, axis=alt.Axis(format=d3_format)),
        tooltip=tooltip,
    )

    point_kwargs = {
        "filled": True,
        "opacity": cfg.get("point_alpha", 0.78),
    }
    points = base.mark_circle(**point_kwargs)

    if has_group:
        groups = [str(value) for value in pd.unique(df["group"].dropna())]
        peer_palette = cfg.get("peer_palette", []) or [
            theme.color("comparison.peers.0", "#AEBECD"),
            theme.color("comparison.peers.1", "#6E859E"),
            theme.color("comparison.peers.2", "#8C9472"),
            theme.color("comparison.peers.3", "#9A7F6B"),
        ]
        if len(groups) > len(peer_palette):
            peer_palette = peer_palette + [theme.color("highlight.selection", "#2C7FB8")] * (len(groups) - len(peer_palette))
        points = points.encode(
            color=alt.Color(
                "group:N",
                scale=alt.Scale(domain=groups, range=peer_palette[: len(groups)]),
                legend=alt.Legend(title=None),
            )
        )
    else:
        points = points.encode(
            color=alt.value(theme.color("highlight.selection", cfg.get("base_color", "#2C7FB8")))
        )

    if has_size:
        points = points.encode(
            size=alt.Size("size_value:Q", legend=alt.Legend(title=None))
        )

    layers: list[alt.Chart] = [points]

    add_trend_line = request.field_values.get("add_trend_line", True)
    if add_trend_line:
        regression = (
            alt.Chart(df)
            .transform_regression("x_value", "y_value")
            .mark_line(
                color=theme.color("neutral.text_muted", "#52606D"),
                opacity=0.7,
                strokeDash=[4, 4],
            )
            .encode(x="x_value:Q", y="y_value:Q")
        )
        layers.append(regression)

    for ann in request.annotations:
        if ann.kind == "vline" and ann.x is not None:
            layers.append(
                alt.Chart(pd.DataFrame({"x_value": [ann.x]}))
                .mark_rule(color=theme.color("highlight.risk", "#C44536"), strokeDash=[2, 2])
                .encode(x="x_value:Q")
            )
        if ann.kind == "hline" and ann.y is not None:
            layers.append(
                alt.Chart(pd.DataFrame({"y_value": [ann.y]}))
                .mark_rule(color=theme.color("highlight.risk", "#C44536"), strokeDash=[2, 2])
                .encode(y="y_value:Q")
            )

    if has_labels:
        labels = (
            alt.Chart(df[df["label_flag"]].copy())
            .mark_text(
                align="left",
                dx=6,
                dy=-6,
                font=theme.font_family(),
                color=theme.color("neutral.text", "#1F2933"),
            )
            .encode(
                x="x_value:Q",
                y="y_value:Q",
                text="geo_name:N",
            )
        )
        layers.append(labels)

    caption = build_caption(
        source=df["source"].iloc[0] if "source" in df.columns and len(df) else None,
        vintage=df["vintage"].iloc[0] if "vintage" in df.columns and len(df) else None,
    )

    chart = (
        alt.layer(*layers)
        .properties(
            width=width,
            height=height,
            title=alt.TitleParams(**title_params),
        )
        .configure_axis(
            labelFont=theme.font_family(),
            titleFont=theme.font_family(),
            labelColor=theme.color("neutral.axis", "#5B6770"),
            gridColor=theme.color("neutral.grid_major", "#D9E2EC"),
        )
        .configure_title(
            font=theme.font_family(),
            color=theme.color("neutral.text", "#1F2933"),
            subtitleColor=theme.color("neutral.text_muted", "#52606D"),
        )
        .configure_legend(
            labelFont=theme.font_family(),
            labelColor=theme.color("neutral.text_muted", "#52606D"),
        )
        .configure_view(stroke=None)
    )

    # Altair does not expose plot captions in the same first-class way as
    # ggplot2, so we keep the caption available on the returned chart object
    # for downstream persistence/review workflows.
    chart.usermeta = {"caption": caption} if caption else {}
    return chart
