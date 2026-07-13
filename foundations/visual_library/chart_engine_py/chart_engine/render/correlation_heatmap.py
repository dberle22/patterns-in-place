from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_altair_title_params, build_data_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def _correlation_subtitle(df: pd.DataFrame, request: ChartRequest) -> str | None:
    if request.subtitle:
        return request.subtitle

    method = df["method"].dropna().iloc[0] if "method" in df.columns and df["method"].notna().any() else "spearman"
    missingness = df["missingness_policy"].dropna().iloc[0] if "missingness_policy" in df.columns and df["missingness_policy"].notna().any() else "pairwise.complete.obs"
    order_method = df["order_method"].dropna().iloc[0] if "order_method" in df.columns and df["order_method"].notna().any() else "clustered"
    return f"{str(method).title()} correlation | Missingness: {missingness} | Order: {order_method}"


def _correlation_panel(df: pd.DataFrame, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = df.attrs.get("chart_config", {})
    show_labels = bool(cfg.get("show_cell_labels")) if "show_cell_labels" in cfg else (
        len(df["metric_x"].cat.categories if hasattr(df["metric_x"], "cat") else df["metric_x"].unique()) <= 8
    )
    base = alt.Chart(df)
    rects = base.mark_rect().encode(
        x=alt.X("metric_x:N", title=None, sort=None),
        y=alt.Y("metric_y:N", title=None, sort=None),
        color=alt.Color(
            "correlation_display:Q",
            scale=alt.Scale(domain=[-1, 1], scheme="redblue"),
            legend=alt.Legend(title=str(cfg.get("legend_title") or "Correlation")),
        ),
        tooltip=["metric_x:N", "metric_y:N", alt.Tooltip("correlation:Q", format=".2f")],
    )
    layers: list[alt.Chart] = [rects]
    if show_labels:
        label_df = df.loc[df["correlation_display"].notna()].copy() if "correlation_display" in df.columns else df.copy()
        label_df["label_color"] = label_df["correlation"].abs().apply(lambda value: "#FFFFFF" if value >= 0.55 else theme.color("neutral.text", "#1F2933"))
        label_palette = label_df["label_color"].dropna().astype(str).unique().tolist()
        layers.append(
            alt.Chart(label_df).mark_text(font=theme.font_family()).encode(
                x="metric_x:N",
                y="metric_y:N",
                text="label:N",
                color=alt.Color(
                    "label_color:N",
                    legend=None,
                    scale=alt.Scale(domain=label_palette, range=label_palette),
                ),
            )
        )
    return alt.layer(*layers).properties(
        width=theme.width("correlation_heatmap"),
        height=theme.height("correlation_heatmap"),
    )


def render_correlation_heatmap(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = df.attrs.get("chart_config", {})
    title = request.title or "Correlation Heatmap"
    subtitle = _correlation_subtitle(df, request)
    caption = build_data_caption(df)
    title_params = build_altair_title_params(title, subtitle=subtitle, caption=caption, title_size=theme.title_size())

    facet_by = str(cfg.get("facet_by") or request.field_values.get("facet_by") or "").strip()
    if not facet_by and "group" in df.columns and df["group"].nunique(dropna=True) > 1:
        facet_by = "group"

    if facet_by and facet_by in df.columns:
        panels: list[alt.Chart] = []
        for facet_value in df[facet_by].dropna().astype(str).unique().tolist():
            panels.append(
                _correlation_panel(df.loc[df[facet_by].astype(str) == facet_value].copy(), request).properties(title=facet_value)
            )
        out = alt.vconcat(*panels).properties(title=alt.TitleParams(**title_params))
    else:
        out = _correlation_panel(df, request).properties(title=alt.TitleParams(**title_params))

    out = out.configure_axis(labelFont=theme.font_family(), titleFont=theme.font_family()).configure_title(
        font=theme.font_family()
    ).configure_view(stroke=None)
    out.usermeta = {"caption": caption} if caption else {}
    return out
