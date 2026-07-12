from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_altair_title_params, build_data_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def _heatmap_subtitle(df: pd.DataFrame, request: ChartRequest) -> str | None:
    if request.subtitle:
        return request.subtitle

    cfg = df.attrs.get("chart_config", {})
    variant = str(df["heatmap_variant"].dropna().iloc[0]) if "heatmap_variant" in df.columns and df["heatmap_variant"].notna().any() else "geo_metric"
    fill_field = str(cfg.get("fill_value_field", "normalized_value"))
    fill_note = "Fill shows polarity-aligned percentile" if fill_field == "normalized_value" else "Fill shows raw values"
    window = df["time_window"].dropna().iloc[0] if "time_window" in df.columns and df["time_window"].notna().any() else None
    parts = [f"Matrix: {variant.replace('_', ' x ')}", fill_note]
    if window:
        parts.insert(1, f"Time window: {window}")
    return " | ".join(parts)


def render_heatmap_table(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = df.attrs.get("chart_config", {})
    title = request.title or (spec.docs.split("\n")[0].lstrip("#").strip() if spec.docs else spec.chart_type)
    subtitle = _heatmap_subtitle(df, request)
    caption = build_data_caption(df)
    title_params = build_altair_title_params(title, subtitle=subtitle, caption=caption, title_size=theme.title_size())
    base = alt.Chart(df)

    show_labels = bool(cfg.get("show_cell_labels")) if "show_cell_labels" in cfg else len(df) <= int(cfg.get("auto_label_max_cells", 96))
    fill_field = str(cfg.get("fill_value_field", "normalized_value"))
    legend_title = str(cfg.get("legend_title") or ("Better percentile" if fill_field == "normalized_value" else "Value"))
    missing_label = str(cfg.get("missing_label", "No data"))

    color_kwargs = {"scheme": "redyellowgreen"} if fill_field == "normalized_value" else {"scheme": "blues"}
    scale_domain = [0, 100] if fill_field == "normalized_value" else None
    rects = base.mark_rect().encode(
        x=alt.X("column_label:N", title=None),
        y=alt.Y("row_label:N", title=None),
        color=alt.Color(
            "fill_value:Q",
            scale=alt.Scale(domain=scale_domain, **color_kwargs),
            legend=alt.Legend(title=legend_title),
        ),
        tooltip=["row_label:N", "column_label:N", "cell_label:N", alt.Tooltip("fill_value:Q", format=".1f")],
    )

    layers: list[alt.Chart] = [rects]
    if "highlight_flag" in df.columns and df["highlight_flag"].fillna(False).astype(bool).any():
        highlight_df = df[df["highlight_flag"].fillna(False).astype(bool)].copy()
        layers.append(
            alt.Chart(highlight_df).mark_rect(
                fillOpacity=0,
                stroke=theme.color("highlight.selection", "#2C7FB8"),
                strokeWidth=2,
            ).encode(x="column_label:N", y="row_label:N")
        )

    if show_labels:
        label_df = df.copy()
        if not cfg.get("show_missing_labels", True):
            label_df = label_df.loc[~label_df["missing_flag"].fillna(False).astype(bool)].copy()
        label_df["label_color"] = label_df["fill_value"].apply(
            lambda value: "#FFFFFF" if pd.notna(value) and (value >= 78 or value <= 18) else theme.color("neutral.text", "#1F2933")
        )
        label_df.loc[label_df["missing_flag"].fillna(False).astype(bool), "cell_label"] = missing_label
        layers.append(
            alt.Chart(label_df).mark_text(font=theme.font_family()).encode(
                x="column_label:N",
                y="row_label:N",
                text="cell_label:N",
                color=alt.Color("label_color:N", scale=None),
            )
        )

    out = alt.layer(*layers).properties(
        width=theme.width("heatmap_table"),
        height=theme.height("heatmap_table"),
        title=alt.TitleParams(**title_params),
    ).configure_axis(labelFont=theme.font_family(), titleFont=theme.font_family()).configure_title(font=theme.font_family()).configure_view(stroke=None)
    out.usermeta = {"caption": caption} if caption else {}
    return out
