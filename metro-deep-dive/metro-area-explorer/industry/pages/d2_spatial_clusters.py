"""D2 page for the Industry explorer."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pydeck as pdk
import plotly.express as px
import streamlit as st

SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_prep import (
    COUNTY_GDP_SECTOR_COLUMNS,
    get_d2_county_gdp_map_payload,
    get_d2_sector_options,
    get_d2_tract_map_payload,
)
from shared_ui import format_gdp_total_cell, format_jobs_cell, format_percent_cell


_MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
_D2_INTENSITY_METRICS = {
    "Total jobs": "jobs_total",
    "Jobs per resident": "jobs_per_resident",
    "Jobs per sq mi": "jobs_per_sqmi",
}
_D2_MAP_MODE_LABELS = {
    "top_industry": "Top industry",
    "selected_industry": "Selected industry share",
    "jobs_density": "Jobs density",
}


def _build_geojson_layer(features, layer_id: str) -> pdk.Layer:
    """Render polygon features with precomputed fill colors from the D2 data layer."""
    return pdk.Layer(
        "GeoJsonLayer",
        {"type": "FeatureCollection", "features": features},
        id=layer_id,
        stroked=True,
        filled=True,
        get_fill_color="properties.fill_color",
        get_line_color=[88, 88, 88, 120],
        line_width_min_pixels=0.6,
        pickable=True,
        auto_highlight=True,
        opacity=0.85,
    )


def _build_map_tooltip(mode: str) -> dict[str, object]:
    """Keep tract and county hover copy concise and specific to the active map."""
    if mode == "top_industry":
        html = (
            "<b>{tract_name}</b><br/>"
            "Tract: {tract_geoid}<br/>"
            "Top sector: {dominant_sector_label}<br/>"
            "Top sector jobs: {selected_jobs}<br/>"
            "Top sector share: {selected_share_pct}<br/>"
            "Total jobs: {jobs_total}"
        )
    elif mode == "selected_industry":
        html = (
            "<b>{tract_name}</b><br/>"
            "Tract: {tract_geoid}<br/>"
            "Sector: {sector_label}<br/>"
            "Sector jobs: {selected_jobs}<br/>"
            "Sector share: {selected_share_pct}<br/>"
            "Total jobs: {jobs_total}"
        )
    elif mode == "jobs_density":
        html = (
            "<b>{tract_name}</b><br/>"
            "Tract: {tract_geoid}<br/>"
            "Dominant sector: {dominant_sector_label}<br/>"
            "Total jobs: {jobs_total}<br/>"
            "Population: {selected_jobs}<br/>"
            "Density metric: {selected_share_pct}"
        )
    else:
        html = (
            "<b>{county_name}</b><br/>"
            "County: {county_geoid}<br/>"
            "Sector: {sector_label}<br/>"
            "GDP share: {selected_gdp_share_pct}<br/>"
            "Real GDP total: {real_gdp_total}"
        )
    return {
        "html": html,
        "style": {
            "backgroundColor": "rgba(255, 255, 255, 0.96)",
            "color": "#1f2933",
            "fontSize": "12px",
        },
    }


def _render_map(payload: dict[str, object], layer_id: str, tooltip_mode: str) -> None:
    """Render the interactive D2 map when features are available."""
    features = payload.get("features", [])
    if not features:
        st.warning("No map features were available for this selection.")
        return

    view_state = payload["view_state"]
    deck = pdk.Deck(
        layers=[_build_geojson_layer(features, layer_id)],
        initial_view_state=pdk.ViewState(
            latitude=view_state["latitude"],
            longitude=view_state["longitude"],
            zoom=view_state["zoom"],
        ),
        tooltip=_build_map_tooltip(tooltip_mode),
        map_style=_MAP_STYLE,
    )
    st.pydeck_chart(deck, width="stretch")


def _format_density_cell(value) -> str:
    """Format density-like floats for compact D2 tables."""
    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "—"
    return f"{float(numeric_value):,.2f}"


def _render_html_table(df: pd.DataFrame) -> None:
    """Render compact review tables without going through Streamlit's Arrow dataframe path."""
    st.markdown(df.fillna("—").to_html(index=False), unsafe_allow_html=True)


def _build_jobs_intensity_scatter(rows: pd.DataFrame, ranking_metric_label: str):
    """Create a tract jobs intensity scatter with size driven by total jobs."""
    plot_rows = rows[
        [
            "tract_geoid",
            "tract_name",
            "jobs_total",
            "pop_total",
            "land_area_sqmi",
            "jobs_per_resident",
            "jobs_per_sqmi",
            "dominant_sector_label",
        ]
    ].copy()
    plot_rows = plot_rows.dropna(
        subset=["jobs_total", "jobs_per_resident", "jobs_per_sqmi"]
    )
    if plot_rows.empty:
        return None

    plot_rows["jobs_total_label"] = plot_rows["jobs_total"].map(format_jobs_cell)
    plot_rows["jobs_per_resident_label"] = plot_rows["jobs_per_resident"].map(_format_density_cell)
    plot_rows["jobs_per_sqmi_label"] = plot_rows["jobs_per_sqmi"].map(_format_density_cell)
    plot_rows["land_area_sqmi_label"] = plot_rows["land_area_sqmi"].map(_format_density_cell)
    plot_rows["pop_total_label"] = plot_rows["pop_total"].map(format_jobs_cell)

    fig = px.scatter(
        plot_rows,
        x="jobs_per_resident",
        y="jobs_per_sqmi",
        size="jobs_total",
        color="dominant_sector_label",
        hover_name="tract_name",
        hover_data={
            "tract_geoid": True,
            "jobs_total_label": True,
            "jobs_per_resident_label": True,
            "jobs_per_sqmi_label": True,
            "pop_total_label": True,
            "land_area_sqmi_label": True,
            "jobs_total": False,
            "jobs_per_resident": False,
            "jobs_per_sqmi": False,
            "dominant_sector_label": True,
        },
        labels={
            "jobs_per_resident": "Jobs per resident",
            "jobs_per_sqmi": "Jobs per sq mi",
            "dominant_sector_label": "Dominant sector",
        },
        title=f"Jobs intensity by tract | bubble size = total jobs | ranking focus = {ranking_metric_label}",
    )
    fig.update_traces(marker=dict(opacity=0.75, line=dict(width=0.5, color="white")))
    fig.update_layout(
        margin=dict(l=20, r=20, t=55, b=20),
        legend_title_text="Dominant sector",
    )
    return fig


def _build_jobs_density_map_payload(
    rows: pd.DataFrame,
    density_metric_label: str,
    view_state: dict[str, float],
) -> dict[str, object]:
    """Build a tract density map payload from the already prepared D2 tract surface."""
    if rows.empty:
        return {"features": [], "legend": pd.DataFrame(), "rows": rows}

    metric_column = _D2_INTENSITY_METRICS[density_metric_label]
    max_value = rows[metric_column].max(skipna=True)
    if pd.isna(max_value) or max_value <= 0:
        max_value = 1.0

    features: list[dict] = []
    for _, row in rows.iterrows():
        metric_value = row[metric_column]
        ratio = 0.0 if pd.isna(metric_value) else float(metric_value) / float(max_value)
        fill_color = [
            int(244 + ratio * (179 - 244)),
            int(244 + ratio * (18 - 244)),
            int(255 + ratio * (23 - 255)),
            195,
        ]
        features.append(
            {
                "type": "Feature",
                "geometry": row["geometry"],
                "properties": {
                    "tract_geoid": row["tract_geoid"],
                    "tract_name": row["tract_name"],
                    "jobs_total": format_jobs_cell(row["jobs_total"]),
                    "dominant_sector_label": row["dominant_sector_label"],
                    "selected_share_pct": _format_density_cell(metric_value),
                    "selected_jobs": format_jobs_cell(row["pop_total"]),
                    "fill_color": fill_color,
                },
            }
        )

    return {
        "features": features,
        "legend": pd.DataFrame(
            [
                {"Level": "Low", "Color": "#F4F4FF"},
                {"Level": "High", "Color": "#B31217"},
            ]
        ),
        "rows": rows,
        "view_state": view_state,
        "title": f"{density_metric_label} by tract",
        "subtitle": "Tract jobs intensity surface from the same D2 workplace dataset",
    }


def render_page(market_id: str) -> None:
    """Render the D2 spatial page for one market."""
    sector_options = get_d2_sector_options()
    sector_lookup = {label: sector_id for sector_id, label in sector_options}

    with st.sidebar:
        map_surface = st.radio(
            "D2 map surface",
            options=["tract", "county"],
            format_func=lambda value: "Tract employment map" if value == "tract" else "County GDP share map",
        )
        tract_mode = st.radio(
            "Tract map mode",
            options=["top_industry", "selected_industry", "jobs_density"],
            format_func=lambda value: _D2_MAP_MODE_LABELS[value],
            disabled=map_surface != "tract",
        )
        selected_sector_label = st.selectbox(
            "D2 selected sector",
            list(sector_lookup),
            index=next(
                (idx for idx, (sector_id, _) in enumerate(sector_options) if sector_id == "professional"),
                0,
            ),
        )
        selected_sector = sector_lookup[selected_sector_label]
        ranking_metric_label = st.selectbox(
            "Tract intensity ranking",
            list(_D2_INTENSITY_METRICS),
            disabled=map_surface != "tract",
        )
        ranking_metric = _D2_INTENSITY_METRICS[ranking_metric_label]

    st.header("D2 — Industrial Clusters and GDP Context")

    if map_surface == "tract":
        base_payload = get_d2_tract_map_payload(
            market_id,
            mode="top_industry" if tract_mode == "jobs_density" else tract_mode,
            selected_sector=selected_sector,
        )
        rows = base_payload.get("rows", pd.DataFrame())
        payload = (
            _build_jobs_density_map_payload(rows, ranking_metric_label, base_payload["view_state"])
            if tract_mode == "jobs_density"
            else base_payload
        )
        st.subheader(payload.get("title", "Tract industry map"))
        st.caption(payload.get("subtitle", ""))
        _render_map(payload, "industry_d2_tracts", tract_mode)

        legend = payload.get("legend")
        info_cols = st.columns([1.1, 1.5])
        with info_cols[0]:
            if isinstance(legend, pd.DataFrame) and not legend.empty:
                st.markdown("**Legend**")
                _render_html_table(legend)
        with info_cols[1]:
            if isinstance(rows, pd.DataFrame) and not rows.empty:
                st.markdown("**Top mapped tracts**")
                if tract_mode == "top_industry":
                    display = rows[
                        [
                            "tract_geoid",
                            "tract_name",
                            "dominant_sector_label",
                            "dominant_sector_jobs",
                            "dominant_sector_share",
                            "jobs_total",
                        ]
                    ].copy()
                    display = display.sort_values(
                        ["dominant_sector_share", "dominant_sector_jobs"],
                        ascending=[False, False],
                        kind="mergesort",
                    ).head(15)
                    display = display.rename(
                        columns={
                            "tract_geoid": "Tract",
                            "tract_name": "Name",
                            "dominant_sector_label": "Top sector",
                            "dominant_sector_jobs": "Top sector jobs",
                            "dominant_sector_share": "Top sector share",
                            "jobs_total": "Total jobs",
                        }
                    )
                elif tract_mode == "selected_industry":
                    share_column = f"d2_share_{selected_sector}"
                    jobs_column = f"d2_jobs_{selected_sector}"
                    display = rows[
                        [
                            "tract_geoid",
                            "tract_name",
                            jobs_column,
                            share_column,
                            "jobs_total",
                        ]
                    ].copy()
                    display = display.sort_values(
                        [share_column, jobs_column],
                        ascending=[False, False],
                        kind="mergesort",
                    ).head(15)
                    display = display.rename(
                        columns={
                            "tract_geoid": "Tract",
                            "tract_name": "Name",
                            jobs_column: f"{selected_sector_label} jobs",
                            share_column: f"{selected_sector_label} share",
                            "jobs_total": "Total jobs",
                        }
                    )
                else:
                    display = rows[
                        [
                            "tract_geoid",
                            "tract_name",
                            "dominant_sector_label",
                            "jobs_total",
                            "pop_total",
                            "land_area_sqmi",
                            "jobs_per_resident",
                            "jobs_per_sqmi",
                        ]
                    ].copy()
                    display = display.sort_values(
                        ranking_metric,
                        ascending=False,
                        kind="mergesort",
                        na_position="last",
                    ).head(15)
                    display = display.rename(
                        columns={
                            "tract_geoid": "Tract",
                            "tract_name": "Name",
                            "dominant_sector_label": "Dominant sector",
                            "jobs_total": "Total jobs",
                            "pop_total": "Population",
                            "land_area_sqmi": "Land area (sq mi)",
                            "jobs_per_resident": "Jobs per resident",
                            "jobs_per_sqmi": "Jobs per sq mi",
                        }
                    )
                for column in display.columns:
                    if "share" in column.lower():
                        display[column] = display[column].map(format_percent_cell)
                    elif "jobs" in column.lower():
                        display[column] = display[column].map(format_jobs_cell)
                    elif "population" in column.lower():
                        display[column] = display[column].map(format_jobs_cell)
                    elif "land area" in column.lower() or "per " in column.lower():
                        display[column] = display[column].map(_format_density_cell)
                _render_html_table(display)

        if isinstance(rows, pd.DataFrame) and not rows.empty:
            st.subheader("Jobs intensity")
            intensity_fig = _build_jobs_intensity_scatter(rows, ranking_metric_label)
            if intensity_fig is None:
                st.info("Jobs intensity metrics are unavailable for this market's tract surface.")
            else:
                st.plotly_chart(intensity_fig, width="stretch")

            density_display = rows[
                [
                    "tract_geoid",
                    "tract_name",
                    "dominant_sector_label",
                    "jobs_total",
                    "pop_total",
                    "land_area_sqmi",
                    "jobs_per_resident",
                    "jobs_per_sqmi",
                ]
            ].copy()
            density_display = density_display.sort_values(
                ranking_metric,
                ascending=False,
                kind="mergesort",
                na_position="last",
            ).head(20)
            density_display = density_display.rename(
                columns={
                    "tract_geoid": "Tract",
                    "tract_name": "Name",
                    "dominant_sector_label": "Dominant sector",
                    "jobs_total": "Total jobs",
                    "pop_total": "Population",
                    "land_area_sqmi": "Land area (sq mi)",
                    "jobs_per_resident": "Jobs per resident",
                    "jobs_per_sqmi": "Jobs per sq mi",
                }
            )
            density_display["Total jobs"] = density_display["Total jobs"].map(format_jobs_cell)
            density_display["Population"] = density_display["Population"].map(format_jobs_cell)
            density_display["Land area (sq mi)"] = density_display["Land area (sq mi)"].map(_format_density_cell)
            density_display["Jobs per resident"] = density_display["Jobs per resident"].map(_format_density_cell)
            density_display["Jobs per sq mi"] = density_display["Jobs per sq mi"].map(_format_density_cell)
            st.markdown(f"**Top tracts by {ranking_metric_label.lower()}**")
            _render_html_table(density_display)
    else:
        payload = get_d2_county_gdp_map_payload(
            market_id,
            selected_sector=selected_sector,
        )
        st.subheader(payload.get("title", "County GDP share map"))
        st.caption(payload.get("subtitle", ""))
        _render_map(payload, "industry_d2_counties", "county_gdp")

        legend = payload.get("legend")
        rows = payload.get("rows", pd.DataFrame())
        info_cols = st.columns([1.1, 1.5])
        with info_cols[0]:
            if isinstance(legend, pd.DataFrame) and not legend.empty:
                st.markdown("**Legend**")
                _render_html_table(legend)
        with info_cols[1]:
            if isinstance(rows, pd.DataFrame) and not rows.empty:
                gdp_column = COUNTY_GDP_SECTOR_COLUMNS[selected_sector]
                display = rows[
                    ["county_geoid", "county_name", gdp_column, "real_gdp_total"]
                ].copy()
                display = display.sort_values(gdp_column, ascending=False, kind="mergesort").head(15)
                display = display.rename(
                    columns={
                        "county_geoid": "County",
                        "county_name": "Name",
                        gdp_column: f"{selected_sector_label} GDP share",
                        "real_gdp_total": "Real GDP total",
                    }
                )
                display[f"{selected_sector_label} GDP share"] = display[
                    f"{selected_sector_label} GDP share"
                ].map(format_percent_cell)
                display["Real GDP total"] = display["Real GDP total"].map(format_gdp_total_cell)
                st.markdown("**Top counties in the selected GDP view**")
                _render_html_table(display)

    with st.expander("Data notes"):
        st.markdown(
            "- D2 tract maps use the latest tract-level LODES workplace jobs and collapse raw LODES industries into the broader D1 sector taxonomy.\n"
            "- D2 county maps use the latest county year with BEA GDP-share coverage, which is currently 2023 in the local DuckDB.\n"
            "- The jobs-intensity companion view uses the same tract surface and adds population plus tract land area so we can compare absolute job hubs against jobs-per-resident and jobs-per-square-mile intensity.\n"
            "- Geometry is simplified before export from DuckDB spatial so the interactive map payload stays lighter and more stable."
        )
