from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_altair_title_params, build_data_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def render_bump_chart(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = theme.chart_defaults_for(request.chart_type)
    data = df.copy()
    title = request.title or _default_title(data)
    subtitle = request.subtitle or _default_subtitle(data)
    caption = build_data_caption(df)
    title_params = build_altair_title_params(
        title,
        subtitle=subtitle,
        caption=caption,
        title_size=theme.title_size(),
        subtitle_wrap_width=int(cfg.get("subtitle_wrap_width", 120)),
        caption_wrap_width=int(cfg.get("caption_wrap_width", 135)),
    )

    data["line_type"] = "context"
    data.loc[data.get("peer_flag", False).astype(bool), "line_type"] = "peer"
    data.loc[data.get("highlight_flag", False).astype(bool), "line_type"] = "highlight"
    color_scale = alt.Scale(
        domain=["context", "peer", "highlight"],
        range=[
            theme.color("comparison.neutral", "#A7B4C2"),
            theme.color("comparison.peers.1", "#6E859E"),
            theme.color("highlight.selection", "#2C7FB8"),
        ],
    )
    opacity_scale = alt.Scale(domain=["context", "peer", "highlight"], range=[0.45, 0.72, 1.0])

    base = alt.Chart(data).mark_line(point=bool(request.field_values.get("show_points", True))).encode(
        x=alt.X("period:N", title=None),
        y=alt.Y("rank:Q", sort="descending", title="Rank (1 = top)"),
        detail="geo_id:N",
        color=alt.Color("line_type:N", scale=color_scale, legend=None),
        opacity=alt.Opacity("line_type:N", scale=opacity_scale, legend=None),
        tooltip=[
            alt.Tooltip("geo_name:N", title="Geography"),
            alt.Tooltip("period:N", title="Period"),
            alt.Tooltip("rank:Q", title="Rank", format=",d"),
            alt.Tooltip("rank_change:Q", title="Rank change", format=",d"),
        ],
    )

    labels_df = _label_rows(data, str(request.field_values.get("label_mode", "highlight_end")))
    labels_df["label_text"] = labels_df.apply(_endpoint_label_text, axis=1)
    labels = alt.Chart(labels_df).mark_text(
        align="left",
        dx=6,
        font=theme.font_family(),
        color=theme.color("neutral.text", "#1F2933"),
    ).encode(x="period:N", y="rank:Q", text="label_text:N")

    out = (
        alt.layer(base, labels)
        .properties(
            width=theme.width("bump_chart"),
            height=theme.height("bump_chart"),
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
        .configure_view(stroke=None)
    )
    out.usermeta = {"caption": caption} if caption else {}
    return out


def _default_title(df: pd.DataFrame) -> str:
    metric = df["metric_label"].dropna().iloc[0] if "metric_label" in df.columns and df["metric_label"].dropna().any() else "Metric"
    geo_level = df["geo_level"].dropna().iloc[0] if "geo_level" in df.columns and df["geo_level"].dropna().any() else "geography"
    return f"{metric} {geo_level} rank over time"


def _default_subtitle(df: pd.DataFrame) -> str | None:
    parts: list[str] = []
    periods = [str(value) for value in df["period"].dropna().unique()]
    if periods:
        parts.append(f"Period: {periods[0]}-{periods[-1]}")
    strategy = df["entity_strategy"].dropna().iloc[0] if "entity_strategy" in df.columns and df["entity_strategy"].dropna().any() else "fixed_top_n"
    selection_period = df["selection_period"].dropna().iloc[0] if "selection_period" in df.columns and df["selection_period"].dropna().any() else None
    display_n = int(df["geo_id"].nunique()) if "geo_id" in df.columns else 0
    if strategy == "fixed_top_n" and selection_period is not None:
        parts.append(f"Fixed top {display_n} selected in {selection_period}")
    elif strategy == "rolling_top_n":
        parts.append(f"Entities that entered the rolling top {display_n}")
    elif strategy == "peer_set":
        parts.append(f"Fixed peer set, n = {display_n}")
    elif strategy == "all":
        parts.append(f"All filtered entities, n = {display_n}")
    rank_source = df["rank_source"].dropna().iloc[0] if "rank_source" in df.columns and df["rank_source"].dropna().any() else "derived"
    rank_method = df["rank_method"].dropna().iloc[0] if "rank_method" in df.columns and df["rank_method"].dropna().any() else "row_number"
    parts.append(f"Rank: {rank_source} {rank_method}")
    groups = [str(value).strip() for value in df["group"].dropna().unique()] if "group" in df.columns else []
    groups = [value for value in groups if value]
    if len(groups) == 1:
        parts.append(f"Universe: {groups[0]}")
    return " | ".join(parts) if parts else None


def _label_rows(df: pd.DataFrame, label_mode: str) -> pd.DataFrame:
    end_period = sorted(df["period"].dropna().unique().tolist())[-1]
    label_df = df[df["period"] == end_period].copy()
    if label_mode == "highlight_end":
        label_df = label_df[label_df["highlight_flag"] | label_df["peer_flag"]].copy()
    elif label_mode == "top_end":
        label_df = label_df.sort_values(["rank", "geo_name"]).head(8).copy()
    return label_df


def _endpoint_label_text(row: pd.Series) -> str:
    change = row.get("rank_change")
    if pd.isna(change):
        return f"{row['geo_name']} (#{int(row['rank'])})"
    delta = f"+{int(abs(change))}" if float(change) > 0 else f"-{int(abs(change))}" if float(change) < 0 else "0"
    return f"{row['geo_name']} (#{int(row['rank'])}, {delta})"
