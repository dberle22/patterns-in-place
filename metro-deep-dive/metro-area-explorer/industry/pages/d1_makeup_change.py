"""D1 page for the Industry explorer."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_prep import (
    build_benchmark_table_for_basis_rows,
    build_change_chart_for_basis_rows,
    build_current_mix_chart_for_basis_rows,
    get_benchmark_basis_frames,
    get_d1_basis_frames,
    get_d1_specialization_payload,
    get_available_years_for_basis_rows,
    get_latest_year_for_basis_rows,
    get_market_context,
    get_takeaway_for_basis_rows,
    has_sufficient_bump_history_for_basis_rows,
)
from shared_ui import format_jobs_cell, format_percent_cell


def _render_chart(chart_result) -> None:
    """Render chart-engine output through an inline Vega-Lite spec.

    Now that the local environment is pinned to the patched Streamlit release
    plus a pre-25 PyArrow build, we can use the native Streamlit Vega-Lite
    element again and keep the original interactive chart behavior.
    """
    spec = chart_result.chart.to_dict()
    st.vega_lite_chart(spec, width="stretch")


def _render_html_table(df: pd.DataFrame) -> None:
    """Render dense review tables without Streamlit's Arrow dataframe path."""
    st.markdown(df.fillna("—").to_html(index=False), unsafe_allow_html=True)


def _build_specialization_scatter(rows: pd.DataFrame):
    """Plot specialization as LQ versus recent employment growth."""
    if rows.empty or rows["growth_value"].notna().sum() == 0:
        return None

    plot_rows = rows.dropna(subset=["growth_value", "lq_value"]).copy()
    if plot_rows.empty:
        return None

    plot_rows["latest_share_label"] = plot_rows["latest_share"].map(format_percent_cell)
    plot_rows["growth_label_display"] = plot_rows["growth_value"].map(format_percent_cell)
    plot_rows["lq_label"] = plot_rows["lq_value"].map(lambda value: f"{float(value):.2f}x")
    plot_rows["latest_employment_label"] = plot_rows["latest_employment"].map(format_jobs_cell)

    fig = px.scatter(
        plot_rows,
        x="growth_value",
        y="lq_value",
        size="latest_employment",
        color="specialization_label",
        color_discrete_map={
            "Specialized": "#1D4ED8",
            "Below US mix": "#94A3B8",
        },
        text="sector_label",
        hover_name="sector_label",
        hover_data={
            "growth_label_display": True,
            "lq_label": True,
            "latest_share_label": True,
            "latest_employment_label": True,
            "growth_value": False,
            "lq_value": False,
            "latest_employment": False,
            "specialization_label": False,
        },
        labels={
            "growth_value": "Recent employment growth",
            "lq_value": "Location quotient",
            "specialization_label": "Specialization",
        },
        title="Specialization companion",
    )
    fig.add_hline(y=1.0, line_dash="dash", line_color="#64748B")
    fig.add_vline(x=0.0, line_dash="dot", line_color="#64748B")
    fig.update_traces(textposition="top center", marker=dict(opacity=0.8, line=dict(width=0.5, color="white")))
    fig.update_layout(
        margin=dict(l=20, r=20, t=55, b=20),
        legend_title_text="Specialization",
        xaxis_tickformat=".0%",
    )
    return fig


def _format_specialization_table(rows: pd.DataFrame, include_growth: bool) -> pd.DataFrame:
    """Format specialization rows for the fallback table or companion review."""
    if rows.empty:
        return rows

    display = rows[
        [
            "sector_label",
            "lq_value",
            "latest_share",
            "latest_employment",
        ]
    ].copy()
    display = display.rename(
        columns={
            "sector_label": "Sector",
            "lq_value": "LQ",
            "latest_share": "Current share",
            "latest_employment": "Latest employment",
        }
    )
    display["LQ"] = display["LQ"].map(lambda value: "—" if pd.isna(value) else f"{float(value):.2f}x")
    display["Current share"] = display["Current share"].map(format_percent_cell)
    display["Latest employment"] = display["Latest employment"].map(format_jobs_cell)

    if include_growth:
        display["Recent growth"] = rows["growth_value"].map(format_percent_cell)

    return display


def render_page(market_id: str) -> None:
    """Render the D1 current-mix and change page for one market."""
    frames = get_d1_basis_frames(market_id)
    benchmark_frames = get_benchmark_basis_frames(market_id)
    market_context = get_market_context(market_id)
    employment_rows = frames["employment_share"]
    gdp_rows = frames["gdp_share"]
    specialization_payload = get_d1_specialization_payload(market_id)

    if employment_rows.empty and gdp_rows.empty:
        st.error("No D1 industry rows were returned for this market.")
        st.stop()

    with st.sidebar:
        basis = st.radio(
            "Basis",
            options=["employment_share", "gdp_share"],
            format_func=lambda value: "Employment share" if value == "employment_share" else "GDP share",
        )

    selected_basis_rows = employment_rows if basis == "employment_share" else gdp_rows
    selected_benchmarks = benchmark_frames[basis]

    if selected_basis_rows.empty:
        st.warning("This basis is unavailable for the selected market.")
        return

    available_years = get_available_years_for_basis_rows(selected_basis_rows)
    default_year = get_latest_year_for_basis_rows(selected_basis_rows)
    selected_year = st.selectbox(
        "Current-mix year",
        available_years,
        index=available_years.index(default_year),
        key=f"{basis}_year",
    )

    latest_basis_year = int(selected_basis_rows["latest_available_year_for_basis"].iloc[0])
    source_label = selected_basis_rows["source_label"].iloc[0]
    vintage_note = selected_basis_rows["vintage_note"].iloc[0]

    metric_cols = st.columns(3)
    with metric_cols[0]:
        st.metric("Latest year for selected basis", latest_basis_year)
    with metric_cols[1]:
        st.metric(
            "Sector count",
            int(selected_basis_rows[selected_basis_rows["year"] == selected_year]["sector_id"].nunique()),
        )
    with metric_cols[2]:
        st.metric("Source", source_label)

    st.caption(vintage_note)

    current_mix = build_current_mix_chart_for_basis_rows(selected_basis_rows, selected_year)
    takeaway = get_takeaway_for_basis_rows(selected_basis_rows)
    change_chart = build_change_chart_for_basis_rows(selected_basis_rows)
    benchmark_table = build_benchmark_table_for_basis_rows(
        selected_basis_rows,
        selected_benchmarks,
        selected_year,
    )

    top_col, bottom_col = st.columns([1.2, 1])

    with top_col:
        st.subheader("Current mix")
        if current_mix is None:
            st.warning("Current-mix chart is unavailable for this basis.")
        else:
            _render_chart(current_mix)

    with bottom_col:
        st.subheader("Takeaway")
        if takeaway is None:
            st.info("At least two comparable years are required to compute a share-change takeaway.")
        else:
            st.write(takeaway)

    st.subheader("Benchmark context")
    if benchmark_table.empty:
        st.info("Benchmark rows are unavailable for the selected basis and year.")
    else:
        division_label = market_context.get("division_name") or "Division"
        display = benchmark_table.rename(
            columns={
                "sector_label": "Sector",
                "market_share": "Market share",
                "us_share": "US share",
                "us_delta": "Market vs US",
                "division_share": f"{division_label} share",
                "division_delta": f"Market vs {division_label}",
            }
        ).copy()
        for column in [column for column in display.columns if column != "Sector"]:
            display[column] = display[column].map(format_percent_cell)
        display = display.fillna("—")
        st.markdown(display.to_html(index=False), unsafe_allow_html=True)

    st.subheader("Change over time")
    if not has_sufficient_bump_history_for_basis_rows(selected_basis_rows):
        st.info(
            f"{selected_basis_rows['basis_label'].iloc[0]} has fewer than 3 comparable years for this market, "
            "so the bump chart is hidden for now."
        )
    elif change_chart is None:
        st.warning("The bump chart could not be rendered for this basis.")
    else:
        _render_chart(change_chart)

    st.subheader("Specialization companion")
    if basis != "employment_share":
        st.info("Specialization is only shown on the employment basis because the location quotients come from QCEW employment.")
    elif specialization_payload["mode"] == "empty":
        st.info("Latest-year specialization rows were unavailable for this market.")
    else:
        st.caption(
            "Current mix shows what is large. This companion shows which sectors are overrepresented versus the U.S. "
            "and, when the latest comparable QCEW pair exists, whether those specialized sectors are still growing."
        )
        if specialization_payload["summary"]:
            st.write(specialization_payload["summary"])

        if specialization_payload["mode"] == "scatter":
            scatter = _build_specialization_scatter(specialization_payload["rows"])
            if scatter is None:
                st.warning("The specialization scatter could not be rendered for this market.")
            else:
                st.plotly_chart(scatter, width="stretch")
            companion_table = _format_specialization_table(
                specialization_payload["rows"].head(8),
                include_growth=True,
            )
            _render_html_table(companion_table)
        else:
            st.info(
                "The latest-year LQ values are available, but the latest comparable QCEW growth pair is not, "
                "so D1 falls back to a ranked specialization table."
            )
            _render_html_table(
                _format_specialization_table(
                    specialization_payload["rows"],
                    include_growth=False,
                )
            )
        st.caption(specialization_payload["note"])

    with st.expander("Data notes"):
        st.markdown(
            "- Employment view uses QCEW private employment when coverage is sufficient, with ACS as an explicit fallback.\n"
            "- GDP view uses BEA real GDP shares and may lag employment by one year.\n"
            "- D1 specialization uses latest-year `lq_*` fields from `gold.economics_industry_wide` and the latest comparable QCEW year pair when growth is available.\n"
            "- US and division benchmarks are derived from state rows because `gold.economics_industry_wide` does not currently ship native division or US rows."
        )
