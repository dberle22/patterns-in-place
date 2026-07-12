from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_altair_title_params, build_data_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def render_age_pyramid(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    title = request.title or _default_title(df)
    subtitle = request.subtitle or _default_subtitle(df)
    caption = build_data_caption(df, side_note=_benchmark_note(df))
    title_params = build_altair_title_params(title, subtitle=subtitle, caption=caption, title_size=theme.title_size())

    color_scale = alt.Scale(
        domain=["Male", "Female"],
        range=[theme.color("comparison.peers.1", "#4C78A8"), theme.color("highlight.opportunity", "#2A9D8F")],
    )
    selected_data = df[df["highlight_flag"]].copy() if "highlight_flag" in df.columns else df.copy()
    benchmark_data = df[~df["highlight_flag"]].copy() if "highlight_flag" in df.columns else df.iloc[0:0].copy()

    bars = alt.Chart(selected_data).mark_bar().encode(
        x=alt.X("plot_value:Q", title="Share of total population", axis=alt.Axis(format=".1%")),
        y=alt.Y("age_bin:N", sort=list(df["age_bin"].cat.categories) if hasattr(df["age_bin"], "cat") else None, title=None),
        color=alt.Color("sex:N", scale=color_scale, legend=alt.Legend(title=None)),
        tooltip=["age_bin:N", "sex:N", alt.Tooltip("plot_abs_value:Q", format=".1%")],
    )
    rule = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color=theme.color("neutral.axis", "#5B6770")).encode(x="x:Q")
    layers: list[alt.Chart] = [rule]

    if not benchmark_data.empty:
        benchmark_lines = alt.Chart(benchmark_data).mark_line(
            color=theme.color("comparison.benchmark", "#52606D"),
            strokeWidth=1.5,
            opacity=0.9,
        ).encode(
            x="plot_value:Q",
            y=alt.Y("age_bin:N", sort=list(df["age_bin"].cat.categories) if hasattr(df["age_bin"], "cat") else None, title=None),
            detail="sex:N",
            strokeDash=alt.value([4, 2]),
        )
        layers.append(benchmark_lines)

    layers.append(bars)

    layered = alt.layer(*layers, data=df).properties(
        width=theme.width("age_pyramid"),
        height=theme.height("age_pyramid"),
    )

    facet_field = None
    if request.facet and request.facet.facet_field in df.columns:
        facet_field = request.facet.facet_field
        columns = request.facet.columns
    elif "facet_label" in df.columns and df["facet_label"].nunique() > 1:
        facet_field = "facet_label"
        columns = 3
    elif "period" in df.columns and df["period"].nunique() > 1:
        facet_field = "period"
        columns = 2

    if facet_field:
        out = layered.facet(facet=alt.Facet(f"{facet_field}:N"), columns=columns).properties(title=alt.TitleParams(**title_params))
    else:
        out = layered.properties(title=alt.TitleParams(**title_params))

    out = out.configure_axis(labelFont=theme.font_family(), titleFont=theme.font_family()).configure_title(font=theme.font_family()).configure_view(stroke=None)
    out.usermeta = {"caption": caption} if caption else {}
    return out


def _default_title(df: pd.DataFrame) -> str:
    highlighted = [str(value).strip() for value in df.loc[df["highlight_flag"], "geo_name"].dropna().unique()] if {"highlight_flag", "geo_name"}.issubset(df.columns) else []
    benchmark_labels = [str(value).strip() for value in df.loc[~df["highlight_flag"], "benchmark_label"].dropna().unique()] if {"highlight_flag", "benchmark_label"}.issubset(df.columns) else []
    if len(highlighted) == 1 and benchmark_labels:
        return f"Age structure: {highlighted[0]} vs {benchmark_labels[0]}"
    if len(highlighted) == 1:
        return f"Age structure: {highlighted[0]}"
    return "Age structure comparison"


def _default_subtitle(df: pd.DataFrame) -> str | None:
    periods = pd.to_numeric(df["period"], errors="coerce").dropna() if "period" in df.columns else pd.Series(dtype=float)
    parts: list[str] = []
    if not periods.empty:
        parts.append(f"Period: {int(periods.min())}-{int(periods.max())}")
    parts.append("Measure: percent of total population")
    parts.append("Male plotted left; female plotted right")
    return " | ".join(parts)


def _benchmark_note(df: pd.DataFrame) -> str | None:
    if "highlight_flag" not in df.columns or df["highlight_flag"].all():
        return None
    benchmark_labels = [str(value).strip() for value in df.loc[~df["highlight_flag"], "benchmark_label"].dropna().unique() if str(value).strip()]
    label = benchmark_labels[0] if benchmark_labels else "benchmark"
    return f"Gray dashed outlines show {label} using the same age bins and period when available."
