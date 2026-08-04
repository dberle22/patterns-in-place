"""D3 page for the Industry explorer."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st

SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_prep import (
    D3_DEFAULT_TRACT_JOBS_FLOOR,
    D3_MAP_MODE_LABELS,
    get_d2_sector_options,
    get_d3_map_payload,
    get_d3_page_payload,
)
from shared_ui import format_jobs_cell, format_percent_cell, format_ratio_cell


_MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"


def _render_html_table(df: pd.DataFrame) -> None:
    """Render compact review tables without the heavier dataframe widget."""
    st.markdown(df.fillna("—").to_html(index=False), unsafe_allow_html=True)


def _build_geojson_layer(features, layer_id: str) -> pdk.Layer:
    """Render D3 tract polygons with precomputed fill and line colors."""
    return pdk.Layer(
        "GeoJsonLayer",
        {"type": "FeatureCollection", "features": features},
        id=layer_id,
        stroked=True,
        filled=True,
        get_fill_color="properties.fill_color",
        get_line_color="properties.line_color",
        line_width_min_pixels=0.7,
        pickable=True,
        auto_highlight=True,
        opacity=0.9,
    )


def _render_map(payload: dict[str, object]) -> None:
    """Render the D3 tract job-center map."""
    features = payload.get("features", [])
    if not features:
        st.info("No tract map features were available for this selection.")
        return

    selected_sector_label = payload["selected_sector_label"]
    tooltip = {
        "html": (
            "<b>{tract_name}</b><br/>"
            "Tract: {tract_geoid}<br/>"
            "Status: {highlight_status}<br/>"
            "Dominant sector: {dominant_sector_label}<br/>"
            "Workplace jobs: {jobs_total}<br/>"
            "Resident workers: {workers_total}<br/>"
            "Jobs / workers: {jobs_to_workers_ratio_label}<br/>"
            f"{selected_sector_label} jobs: {{selected_sector_jobs}}<br/>"
            f"{selected_sector_label} share: {{selected_sector_share_pct}}"
        ),
        "style": {
            "backgroundColor": "rgba(255, 255, 255, 0.96)",
            "color": "#1f2933",
            "fontSize": "12px",
        },
    }
    view_state = payload["view_state"]
    deck = pdk.Deck(
        layers=[_build_geojson_layer(features, "industry_d3_tracts")],
        initial_view_state=pdk.ViewState(
            latitude=view_state["latitude"],
            longitude=view_state["longitude"],
            zoom=view_state["zoom"],
        ),
        tooltip=tooltip,
        map_style=_MAP_STYLE,
    )
    st.pydeck_chart(deck, width="stretch")


def _build_imbalance_chart(rows: pd.DataFrame):
    """Render the workplace-minus-resident industry gap as a horizontal bar chart."""
    plot_rows = rows.copy()
    if plot_rows.empty:
        return None
    plot_rows["direction"] = plot_rows["share_gap"].apply(
        lambda value: "Workplace-heavy" if float(value) >= 0 else "Residence-heavy"
    )
    fig = px.bar(
        plot_rows,
        x="share_gap",
        y="industry_label",
        orientation="h",
        color="direction",
        color_discrete_map={
            "Workplace-heavy": "#2563EB",
            "Residence-heavy": "#C2410C",
        },
        hover_data={
            "share_gap": ":.1%",
            "jobs_total": ":,.0f",
            "workers_total": ":,.0f",
        },
        labels={
            "share_gap": "Workplace share minus resident-worker share",
            "industry_label": "",
        },
        title="Industry imbalance within the CBSA",
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=55, b=20),
        legend_title_text="Gap direction",
        yaxis={"categoryorder": "total ascending"},
    )
    return fig


def _format_job_center_table(rows: pd.DataFrame, table_type: str) -> pd.DataFrame:
    """Format one D3 tract ranking for compact HTML display."""
    if rows.empty:
        return rows

    display = rows[
        [
            "tract_geoid",
            "tract_name",
            "dominant_sector_label",
            "jobs_total",
            "workers_total",
            "jobs_to_workers_ratio",
        ]
    ].copy()
    display = display.rename(
        columns={
            "tract_geoid": "Tract",
            "tract_name": "Name",
            "dominant_sector_label": "Dominant sector",
            "jobs_total": "Workplace jobs",
            "workers_total": "Resident workers",
            "jobs_to_workers_ratio": "Jobs / workers",
        }
    )
    if table_type == "ratio":
        display = display.sort_values(
            ["Jobs / workers", "Workplace jobs"],
            ascending=[False, False],
            kind="mergesort",
            na_position="last",
        )
    else:
        display = display.sort_values(
            ["Workplace jobs", "Jobs / workers"],
            ascending=[False, False],
            kind="mergesort",
            na_position="last",
        )
    display["Workplace jobs"] = display["Workplace jobs"].map(format_jobs_cell)
    display["Resident workers"] = display["Resident workers"].map(format_jobs_cell)
    display["Jobs / workers"] = display["Jobs / workers"].map(format_ratio_cell)
    return display


def _format_selected_sector_table(
    rows: pd.DataFrame,
    selected_sector_jobs_column: str,
    selected_sector_share_column: str,
    selected_sector_label: str,
) -> pd.DataFrame:
    """Format the selected-sector tract ranking for D3."""
    if rows.empty:
        return rows

    display = rows[
        [
            "tract_geoid",
            "tract_name",
            selected_sector_jobs_column,
            selected_sector_share_column,
            "jobs_total",
            "jobs_to_workers_ratio",
        ]
    ].copy()
    display = display.rename(
        columns={
            "tract_geoid": "Tract",
            "tract_name": "Name",
            selected_sector_jobs_column: f"{selected_sector_label} jobs",
            selected_sector_share_column: f"{selected_sector_label} share",
            "jobs_total": "Workplace jobs",
            "jobs_to_workers_ratio": "Jobs / workers",
        }
    )
    display[f"{selected_sector_label} jobs"] = display[f"{selected_sector_label} jobs"].map(format_jobs_cell)
    display[f"{selected_sector_label} share"] = display[f"{selected_sector_label} share"].map(format_percent_cell)
    display["Workplace jobs"] = display["Workplace jobs"].map(format_jobs_cell)
    display["Jobs / workers"] = display["Jobs / workers"].map(format_ratio_cell)
    return display


def render_page(market_id: str) -> None:
    """Render the D3 job-centers page for one market."""
    sector_options = get_d2_sector_options()
    sector_lookup = {label: sector_id for sector_id, label in sector_options}

    with st.sidebar:
        min_jobs_total = st.number_input(
            "D3 minimum tract jobs",
            min_value=0,
            step=500,
            value=D3_DEFAULT_TRACT_JOBS_FLOOR,
        )
        selected_sector_label = st.selectbox(
            "D3 selected sector",
            list(sector_lookup),
            index=next(
                (idx for idx, (sector_id, _) in enumerate(sector_options) if sector_id == "professional"),
                0,
            ),
        )
        selected_sector = sector_lookup[selected_sector_label]
        map_mode = st.radio(
            "D3 map mode",
            options=["top_jobs", "top_ratio", "top_selected_sector"],
            format_func=lambda value: D3_MAP_MODE_LABELS[value],
        )

    payload = get_d3_page_payload(
        market_id=market_id,
        min_jobs_total=int(min_jobs_total),
        selected_sector=selected_sector,
    )
    map_payload = get_d3_map_payload(
        market_id=market_id,
        min_jobs_total=int(min_jobs_total),
        selected_sector=selected_sector,
        mode=map_mode,
    )
    summary = payload["summary"]
    tract_payload = payload["tract_payload"]
    imbalance = payload["imbalance"]

    st.header("D3 — Job Centers and Internal Employment Pull")

    if not summary:
        st.error("No D3 labor-pull summary was returned for this market.")
        return

    metrics = st.columns(4)
    with metrics[0]:
        st.metric("Latest LODES year", int(summary["year"]))
    with metrics[1]:
        st.metric("Jobs / resident workers", summary["jobs_to_workers_ratio_label"])
    with metrics[2]:
        st.metric("Jobs minus workers", summary["jobs_minus_workers_label"])
    with metrics[3]:
        st.metric("Workplace jobs", summary["jobs_total_label"])

    if payload["takeaway"]:
        st.caption(payload["takeaway"])

    st.subheader(map_payload["title"])
    st.caption(map_payload["subtitle"])
    _render_map(map_payload)

    map_info_cols = st.columns([1.0, 1.5])
    with map_info_cols[0]:
        legend = map_payload.get("legend")
        if isinstance(legend, pd.DataFrame) and not legend.empty:
            st.markdown("**Legend**")
            _render_html_table(legend)
    with map_info_cols[1]:
        highlight_rows = map_payload.get("highlight_rows", pd.DataFrame())
        if isinstance(highlight_rows, pd.DataFrame) and not highlight_rows.empty:
            st.markdown("**Highlighted tracts on the map**")
            if map_mode == "top_ratio":
                display = _format_job_center_table(highlight_rows, "ratio")
            elif map_mode == "top_selected_sector":
                display = _format_selected_sector_table(
                    highlight_rows,
                    tract_payload["selected_sector_jobs_column"],
                    tract_payload["selected_sector_share_column"],
                    tract_payload["selected_sector_label"],
                )
            else:
                display = _format_job_center_table(highlight_rows, "jobs")
            _render_html_table(display.head(12))

    ranking_cols = st.columns(2)
    with ranking_cols[0]:
        st.subheader("Largest tract job centers")
        top_jobs_display = _format_job_center_table(tract_payload["top_jobs"], "jobs")
        if top_jobs_display.empty:
            st.info("No tract rows met the current jobs floor.")
        else:
            _render_html_table(top_jobs_display)
    with ranking_cols[1]:
        st.subheader("Highest jobs-to-workers tracts")
        top_ratio_display = _format_job_center_table(tract_payload["top_ratio"], "ratio")
        if top_ratio_display.empty:
            st.info("No tract rows with valid worker counts met the current jobs floor.")
        else:
            _render_html_table(top_ratio_display)

    st.subheader(f"{selected_sector_label} workplace centers")
    selected_sector_display = _format_selected_sector_table(
        tract_payload["top_selected_sector"],
        tract_payload["selected_sector_jobs_column"],
        tract_payload["selected_sector_share_column"],
        tract_payload["selected_sector_label"],
    )
    if selected_sector_display.empty:
        st.info("No tract rows met the current jobs floor for the selected sector view.")
    else:
        _render_html_table(selected_sector_display)

    st.subheader("Industry imbalance")
    imbalance_chart = _build_imbalance_chart(imbalance)
    if imbalance_chart is None:
        st.info("Industry imbalance rows are unavailable for this market.")
    else:
        st.plotly_chart(imbalance_chart, width="stretch")

    imbalance_display = imbalance[
        ["industry_label", "jobs_total", "workers_total", "share_gap"]
    ].copy()
    imbalance_display = imbalance_display.rename(
        columns={
            "industry_label": "Industry",
            "jobs_total": "Workplace jobs",
            "workers_total": "Resident workers",
            "share_gap": "Share gap",
        }
    )
    imbalance_display["Workplace jobs"] = imbalance_display["Workplace jobs"].map(format_jobs_cell)
    imbalance_display["Resident workers"] = imbalance_display["Resident workers"].map(format_jobs_cell)
    imbalance_display["Share gap"] = imbalance_display["Share gap"].map(format_percent_cell)
    _render_html_table(imbalance_display)

    with st.expander("Data notes"):
        st.markdown(
            "- D3 uses the same latest-year tract WAC/RAC surface as D2, then interprets it through tract rankings and a highlighted tract map.\n"
            "- The jobs-to-workers ranking applies a minimum workplace-jobs floor so tiny tracts do not dominate on ratio alone.\n"
            "- Positive industry gaps mean the CBSA hosts a larger share of workplace jobs in that industry than resident workers; negative gaps mean the market looks more residence-heavy in that industry.\n"
            "- This page uses WAC/RAC only. It does not claim explicit origin-destination commute flows.\n"
            "- The current repo does not yet materialize place boundary geometry in DuckDB, so the map is tract-based for now. Place overlays can be added cleanly once a governed place geometry table exists."
        )
