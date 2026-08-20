"""D5 page for the Industry explorer."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_prep import D5_DEFAULT_PEER_COUNT, build_d5_mix_chart, get_d5_page_payload
from shared_ui import format_gdp_total_cell


def _render_chart(chart_result) -> None:
    """Render chart-engine output through Streamlit Vega-Lite."""
    spec = chart_result.chart.to_dict()
    st.vega_lite_chart(spec, width="stretch")


def _render_html_table(df: pd.DataFrame) -> None:
    """Render compact HTML tables for dense review surfaces."""
    st.markdown(df.fillna("—").to_html(index=False), unsafe_allow_html=True)


def _build_mix_chart(rows: pd.DataFrame):
    """Render D5 mix comparison as full-width vertical stacked bars."""
    if rows.empty:
        return None

    plot_rows = rows.copy().sort_values(
        ["entity_order", "display_order", "series"],
        ascending=[True, True, True],
        kind="mergesort",
    )
    fig = px.bar(
        plot_rows,
        x="entity",
        y="share_value",
        color="series",
        custom_data=["raw_value_label", "time_window", "source"],
        labels={
            "entity": "",
            "share_value": "Share of total",
            "series": "Sector",
        },
        title="Peer mix comparison",
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Sector: %{fullData.name}<br>"
            "Share: %{y:.1%}<br>"
            "Raw value: %{customdata[0]}<br>"
            "Year: %{customdata[1]}<br>"
            "Source: %{customdata[2]}<extra></extra>"
        )
    )
    fig.update_layout(
        barmode="stack",
        margin=dict(l=20, r=20, t=55, b=20),
        legend_title_text="Sector",
        yaxis_tickformat=".0%",
        xaxis={"categoryorder": "array", "categoryarray": plot_rows["entity"].drop_duplicates().tolist()},
    )
    return fig


def _format_currency_per_capita(value) -> str:
    """Format per-person dollar values compactly for D5 context tables."""
    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "—"
    return f"${float(numeric_value):,.0f}"


def _format_hhi(value) -> str:
    """Format concentration HHI values compactly for D5 context tables."""
    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "—"
    return f"{float(numeric_value):.3f}"


def _format_context_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Format the D5 economic context rows for compact display."""
    if rows.empty:
        return rows

    display = rows[
        [
            "entity",
            "entity_type",
            "real_gdp_total",
            "gdp_per_capita",
            "wages_salaries_per_job",
            "compensation_per_job",
            "industry_concentration_hhi",
            "bea_proprietors_income",
            "market_population",
        ]
    ].copy()
    display = display.rename(
        columns={
            "entity": "Entity",
            "entity_type": "Type",
            "real_gdp_total": "Real GDP total",
            "gdp_per_capita": "GDP per resident",
            "wages_salaries_per_job": "Wages / private job",
            "compensation_per_job": "Compensation / private job",
            "industry_concentration_hhi": "Industry HHI",
            "bea_proprietors_income": "Proprietors income",
            "market_population": "Population",
        }
    )
    display["Type"] = display["Type"].map(
        {
            "market": "Market",
            "peer": "Peer",
        }
    )
    display["Real GDP total"] = display["Real GDP total"].map(format_gdp_total_cell)
    display["GDP per resident"] = display["GDP per resident"].map(_format_currency_per_capita)
    display["Wages / private job"] = display["Wages / private job"].map(_format_currency_per_capita)
    display["Compensation / private job"] = display["Compensation / private job"].map(_format_currency_per_capita)
    display["Industry HHI"] = display["Industry HHI"].map(_format_hhi)
    display["Proprietors income"] = display["Proprietors income"].map(format_gdp_total_cell)
    display["Population"] = display["Population"].map(lambda value: "—" if pd.isna(pd.to_numeric(value, errors="coerce")) else f"{int(round(float(value))):,}")
    return display


def _format_peer_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Format the selected peer list and cosine similarities for review."""
    if rows.empty:
        return rows

    display = rows.rename(
        columns={
            "peer_rank": "Rank",
            "peer_geo_name": "Peer",
            "similarity": "Cosine similarity",
        }
    )[["Rank", "Peer", "Cosine similarity"]].copy()
    display["Cosine similarity"] = display["Cosine similarity"].map(
        lambda value: "—" if pd.isna(value) else f"{float(value):.3f}"
    )
    return display


def render_page(market_id: str) -> None:
    """Render the D5 regional-fit page for one market."""
    initial_payload = get_d5_page_payload(market_id, basis="employment_share")
    available_peer_rows = initial_payload["available_peer_rows"]
    peer_label_to_id = {
        f"{row['peer_geo_name']} ({row['peer_market_id']})": str(row["peer_market_id"])
        for _, row in available_peer_rows.iterrows()
    }
    peer_labels = list(peer_label_to_id)
    default_labels = peer_labels[:D5_DEFAULT_PEER_COUNT]

    with st.sidebar:
        basis = st.radio(
            "D5 basis",
            options=["employment_share", "gdp_share"],
            format_func=lambda value: "Employment share" if value == "employment_share" else "GDP share",
        )
        selected_peer_labels = st.multiselect(
            "D5 peers",
            peer_labels,
            default=default_labels,
        )

    selected_peer_ids = [peer_label_to_id[label] for label in selected_peer_labels]
    payload = get_d5_page_payload(market_id, basis=basis, peer_market_ids=selected_peer_ids)
    mix_payload = payload["mix_payload"]
    context_payload = payload["context_payload"]

    st.header("D5 — Regional Fit and Peer Benchmarking")

    metric_cols = st.columns(3)
    with metric_cols[0]:
        st.metric("Mix panel latest year", mix_payload["selected_year"] if mix_payload["selected_year"] is not None else "—")
    with metric_cols[1]:
        st.metric("Context panel latest year", context_payload["selected_year"] if context_payload["selected_year"] is not None else "—")
    with metric_cols[2]:
        st.metric("Selected peers", len(payload["peer_rows"]))

    if payload["takeaway"]:
        st.caption(payload["takeaway"])

    st.subheader(payload["mix_title"])
    st.caption(payload["mix_subtitle"])
    mix_chart = _build_mix_chart(mix_payload["chart_rows"])
    if mix_chart is None:
        st.info("The D5 industry/GDP comparison panel is unavailable for this selection.")
    else:
        st.plotly_chart(mix_chart, width="stretch")

    st.subheader(payload["context_title"])
    st.caption(payload["context_subtitle"])
    context_table = _format_context_table(context_payload["rows"])
    if context_table.empty:
        st.info("The D5 market context panel is unavailable for this selection.")
    else:
        _render_html_table(context_table)

    lower_cols = st.columns([0.9, 1.1])
    with lower_cols[0]:
        st.markdown("**Selected peers**")
        peer_table = _format_peer_table(payload["peer_rows"])
        if peer_table.empty:
            st.info("No Cross-Frame peer defaults were available for this market.")
        else:
            _render_html_table(peer_table)

    with lower_cols[1]:
        st.markdown("**Context interpretation**")
        st.markdown(
            "D5 now treats broad comparison as economic context rather than a CBSA jobs-to-workers contest. "
            "The tract-scale jobs-to-workers read still lives in D3 and D4, where it stays analytically useful. "
            "This panel now also carries pay and diversification context so a market can be read as high-employment, high-wage, diversified, or concentrated rather than just large."
        )

    with st.expander("Data notes"):
        for note in mix_payload["notes"]:
            st.markdown(f"- {note}")
        for note in context_payload["notes"]:
            st.markdown(f"- {note}")
        st.markdown("- Peer defaults come from the promoted Cross-Frame Intelligence similarity bundle in `mart_intelligence.intelligence_cross_frame`.")
