"""D6 page for the Industry explorer."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_prep import get_d6_page_payload
from shared_ui import format_jobs_cell, format_percent_cell


def _render_html_table(df: pd.DataFrame) -> None:
    """Render dense D6 review tables without relying on Arrow dataframe paths."""
    st.markdown(df.fillna("—").to_html(index=False), unsafe_allow_html=True)


def _build_sector_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Format the broad-sector scorecard for compact review."""
    if rows.empty:
        return rows

    display = rows[
        [
            "sector_label",
            "employment_share",
            "lq_value",
            "growth_value",
            "ai_exposure_score",
            "match_rate",
        ]
    ].rename(
        columns={
            "sector_label": "Sector",
            "employment_share": "Employment share",
            "lq_value": "LQ",
            "growth_value": "Recent growth",
            "ai_exposure_score": "AI exposure",
            "match_rate": "Felten match rate",
        }
    ).copy()
    display["Employment share"] = display["Employment share"].map(format_percent_cell)
    display["LQ"] = display["LQ"].map(lambda value: "—" if pd.isna(value) else f"{float(value):.2f}x")
    display["Recent growth"] = display["Recent growth"].map(format_percent_cell)
    display["AI exposure"] = display["AI exposure"].map(lambda value: "—" if pd.isna(value) else f"{float(value):.2f}")
    display["Felten match rate"] = display["Felten match rate"].map(format_percent_cell)
    return display


def _build_sector_detail_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Format the underlying 4-digit NAICS rows for the explanation panel."""
    if rows.empty:
        return rows

    display = rows[
        [
            "sector_label",
            "industry_code",
            "industry_title",
            "annual_avg_emplvl",
            "share_within_sector",
            "aiie_score",
        ]
    ].rename(
        columns={
            "sector_label": "Broad sector",
            "industry_code": "4-digit NAICS",
            "industry_title": "Industry",
            "annual_avg_emplvl": "Employment",
            "share_within_sector": "Share within sector",
            "aiie_score": "AIIE",
        }
    ).copy()
    display["Employment"] = display["Employment"].map(format_jobs_cell)
    display["Share within sector"] = display["Share within sector"].map(format_percent_cell)
    display["AIIE"] = display["AIIE"].map(lambda value: "—" if pd.isna(value) else f"{float(value):.2f}")
    return display


def _build_occupation_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Format the detailed occupation ranking table."""
    if rows.empty:
        return rows

    display = rows[
        [
            "soc_code",
            "soc_title",
            "occupation_bucket_label",
            "employment",
            "employment_share",
            "aioe_score",
            "annual_mean_wage",
        ]
    ].head(25).rename(
        columns={
            "soc_code": "SOC",
            "soc_title": "Occupation",
            "occupation_bucket_label": "Family",
            "employment": "Employment",
            "employment_share": "Employment share",
            "aioe_score": "AIOE",
            "annual_mean_wage": "Annual wage",
        }
    ).copy()
    display["Employment"] = display["Employment"].map(format_jobs_cell)
    display["Employment share"] = display["Employment share"].map(format_percent_cell)
    display["AIOE"] = display["AIOE"].map(lambda value: "—" if pd.isna(value) else f"{float(value):.2f}")
    display["Annual wage"] = display["Annual wage"].map(
        lambda value: "—" if pd.isna(value) else f"${int(round(float(value))):,}"
    )
    return display


def _build_family_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Format the lighter occupation-family summary surface."""
    if rows.empty:
        return rows

    display = rows[
        [
            "occupation_bucket_label",
            "employment_share",
            "family_lq",
            "family_ai_exposure_score",
            "matched_share",
        ]
    ].rename(
        columns={
            "occupation_bucket_label": "Family",
            "employment_share": "Employment share",
            "family_lq": "LQ",
            "family_ai_exposure_score": "AI exposure",
            "matched_share": "Felten match rate",
        }
    ).copy()
    display["Employment share"] = display["Employment share"].map(format_percent_cell)
    display["LQ"] = display["LQ"].map(lambda value: "—" if pd.isna(value) else f"{float(value):.2f}x")
    display["AI exposure"] = display["AI exposure"].map(lambda value: "—" if pd.isna(value) else f"{float(value):.2f}")
    display["Felten match rate"] = display["Felten match rate"].map(format_percent_cell)
    return display


def _build_sector_scatter(rows: pd.DataFrame):
    """Plot sector share against exposure so the scorecard has a visual companion."""
    if rows.empty:
        return None

    plot_rows = rows.dropna(subset=["employment_share", "ai_exposure_score"]).copy()
    if plot_rows.empty:
        return None

    fig = px.scatter(
        plot_rows,
        x="ai_exposure_score",
        y="employment_share",
        size="sector_employment",
        text="sector_label",
        color="lq_value",
        color_continuous_scale="Blues",
        hover_data={
            "employment_share": ":.1%",
            "lq_value": ":.2f",
            "growth_value": ":.1%",
            "ai_exposure_score": ":.2f",
            "sector_employment": ":,.0f",
        },
        labels={
            "ai_exposure_score": "Sector AI exposure score",
            "employment_share": "Employment share",
            "lq_value": "LQ",
        },
        title="Sector exposure companion",
    )
    fig.update_traces(textposition="top center", marker=dict(opacity=0.85, line=dict(width=0.5, color="white")))
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=20))
    return fig


def _build_occupation_scatter(rows: pd.DataFrame):
    """Plot detailed occupation exposure against employment relevance."""
    if rows.empty:
        return None

    plot_rows = rows.dropna(subset=["aioe_score", "employment_share"]).head(80).copy()
    if plot_rows.empty:
        return None

    fig = px.scatter(
        plot_rows,
        x="aioe_score",
        y="employment_share",
        size="employment",
        color="occupation_bucket_label",
        text="soc_title",
        hover_data={
            "employment": ":,.0f",
            "employment_share": ":.1%",
            "annual_mean_wage": ":,.0f",
            "location_quotient": ":.2f",
            "soc_title": False,
        },
        labels={
            "aioe_score": "Occupation AI exposure score",
            "employment_share": "Employment share",
            "occupation_bucket_label": "Family",
        },
        title="Occupation exposure companion",
    )
    fig.update_traces(textposition="top center", marker=dict(opacity=0.78, line=dict(width=0.4, color="white")))
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=20))
    return fig


def render_page(market_id: str) -> None:
    """Render the D6 AI exposure page for one market."""
    payload = get_d6_page_payload(market_id)
    sector_payload = payload["sector_payload"]
    occupation_payload = payload["occupation_payload"]

    st.header("D6 — AI Exposure Setup and Scorecard")

    with st.sidebar:
        d6_view = st.radio(
            "D6 view",
            options=["sector", "occupation"],
            format_func=lambda value: {
                "sector": "Sector scorecard",
                "occupation": "Occupation companion",
            }[value],
        )

    if d6_view == "sector":
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric("QCEW vintage", sector_payload.get("selected_year", "—"))
        with metric_cols[1]:
            st.metric("Broad sectors", len(sector_payload["scorecard_rows"]))
        with metric_cols[2]:
            st.metric(
                "Matched employment",
                format_percent_cell(sector_payload.get("coverage", {}).get("matched_share_total")),
            )

        if sector_payload.get("summary"):
            st.write(sector_payload["summary"])
        if payload.get("takeaway"):
            st.caption(payload["takeaway"])

        st.subheader("Sector scorecard")
        scorecard_table = _build_sector_table(sector_payload["scorecard_rows"])
        if scorecard_table.empty:
            st.info("The sector scorecard is unavailable for this market.")
        else:
            _render_html_table(scorecard_table)

        scatter = _build_sector_scatter(sector_payload["scorecard_rows"])
        if scatter is not None:
            st.plotly_chart(scatter, width="stretch")

        with st.expander("Data explanation and underlying 4-digit industries"):
            detail_table = _build_sector_detail_table(sector_payload["detail_rows"])
            if detail_table.empty:
                st.info("No underlying 4-digit industry rows were available.")
            else:
                _render_html_table(detail_table.head(60))
            for note in sector_payload["notes"]:
                st.markdown(f"- {note}")

    else:
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric("OEWS vintage", occupation_payload.get("selected_year", "—"))
        with metric_cols[1]:
            st.metric("Detailed occupations", len(occupation_payload["detail_rows"]))
        with metric_cols[2]:
            st.metric(
                "Matched employment",
                format_percent_cell(occupation_payload.get("coverage", {}).get("matched_share_total")),
            )

        if occupation_payload.get("summary"):
            st.write(occupation_payload["summary"])

        top_cols = st.columns([1.1, 0.9])
        with top_cols[0]:
            st.subheader("Detailed occupation ranking")
            occupation_table = _build_occupation_table(occupation_payload["detail_rows"])
            if occupation_table.empty:
                st.info("The detailed occupation ranking is unavailable for this market.")
            else:
                _render_html_table(occupation_table)

        with top_cols[1]:
            st.subheader("Occupation family summary")
            family_table = _build_family_table(occupation_payload["family_rows"])
            if family_table.empty:
                st.info("The occupation-family summary is unavailable for this market.")
            else:
                _render_html_table(family_table)

        scatter = _build_occupation_scatter(occupation_payload["detail_rows"])
        if scatter is not None:
            st.plotly_chart(scatter, width="stretch")

        with st.expander("Data explanation"):
            for note in occupation_payload["notes"]:
                st.markdown(f"- {note}")
