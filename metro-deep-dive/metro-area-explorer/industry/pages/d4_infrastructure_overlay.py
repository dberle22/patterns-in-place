"""D4 page for the Industry explorer."""

from __future__ import annotations

import pandas as pd
import pydeck as pdk
import streamlit as st

from data_prep import (
    D4_DEFAULT_BASE_SURFACE,
    D4_DEFAULT_BUFFER_MILES,
    D4_DEFAULT_SHORTLIST_COUNT,
    D4_LAYER_STYLES,
    get_d2_sector_options,
    get_d4_overlay_payload,
)
from shared_ui import format_jobs_cell


_MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"


def _build_base_geojson_layer(features) -> pdk.Layer:
    """Render the D2 tract fill beneath the D4 overlays."""
    return pdk.Layer(
        "GeoJsonLayer",
        {"type": "FeatureCollection", "features": features},
        id="d4-tract-fill",
        stroked=True,
        filled=True,
        get_fill_color="properties.fill_color",
        get_line_color=[110, 110, 110, 90],
        line_width_min_pixels=0.4,
        pickable=True,
        opacity=0.52,
    )


def _build_geojson_outline_layer(features, layer_id: str, color: list[int], fill_alpha: int = 0) -> pdk.Layer:
    """Render OSM line or polygon overlays from cached GeoJSON features."""
    return pdk.Layer(
        "GeoJsonLayer",
        {"type": "FeatureCollection", "features": features},
        id=layer_id,
        stroked=True,
        filled=fill_alpha > 0,
        get_line_color=color,
        get_fill_color=color[:3] + [fill_alpha],
        line_width_min_pixels=1.5,
        pickable=True,
        auto_highlight=True,
        opacity=0.85,
    )


def _build_scatter_layer(df: pd.DataFrame, layer_id: str, color: list[int], radius_column: str) -> pdk.Layer:
    """Render cached point-like layers through their stored centroids."""
    return pdk.Layer(
        "ScatterplotLayer",
        df.to_dict("records"),
        id=layer_id,
        get_position="[centroid_lon, centroid_lat]",
        get_fill_color=color,
        get_radius=f"properties.{radius_column}" if "properties" in df.columns else radius_column,
        pickable=True,
        stroked=True,
        line_width_min_pixels=0.6,
        get_line_color=[255, 255, 255, 180],
        opacity=0.85,
    )


def _prepare_marker_rows(rows: pd.DataFrame, metric_column: str) -> pd.DataFrame:
    """Normalize marker rows for pydeck use."""
    if rows.empty:
        return rows
    markers = rows.copy()
    markers["radius"] = markers[metric_column].fillna(0).clip(lower=0)
    max_radius = markers["radius"].max()
    if pd.isna(max_radius) or float(max_radius) <= 0:
        markers["radius"] = 300
    else:
        markers["radius"] = markers["radius"].apply(lambda value: 150 + 650 * (float(value) / float(max_radius)))
    return markers


def _render_html_table(df: pd.DataFrame) -> None:
    """Render small review tables without the heavier dataframe widget."""
    st.markdown(df.fillna("—").to_html(index=False), unsafe_allow_html=True)


def _render_interpretation_detail(detail: dict[str, object], buffer_miles: float) -> None:
    """Render the selected D4 tract read ahead of the companion map."""
    if not detail:
        st.info("No shortlisted tract is available for detailed D4 interpretation yet.")
        return

    st.subheader(f"Selected job center: {detail['tract_name']}")
    detail_cols = st.columns(4)
    with detail_cols[0]:
        st.metric("Typology read", detail["interpretation_type"])
    with detail_cols[1]:
        st.metric("Workplace jobs", detail["jobs_total_label"])
    with detail_cols[2]:
        st.metric("Jobs / workers", detail["jobs_to_workers_ratio_label"])
    with detail_cols[3]:
        st.metric(f"{detail['selected_sector_label']} share", detail["selected_sector_share_label"])

    st.caption(
        f"Shortlist rank #{int(detail['shortlist_rank'])}. Review uses a {buffer_miles:.1f}-mile straight-line "
        "buffer around the tract centroid, so this is a proximity read rather than network access."
    )
    st.markdown(detail["interpretation_rationale"])

    evidence = pd.DataFrame(
        [
            {"Signal": "Highways", "Count": int(detail.get("highways_count", 0) or 0)},
            {"Signal": "Rail", "Count": int(detail.get("rail_count", 0) or 0)},
            {"Signal": "Airports", "Count": int(detail.get("airports_count", 0) or 0)},
            {"Signal": "Ports", "Count": int(detail.get("ports_count", 0) or 0)},
            {"Signal": "Warehouses / logistics", "Count": int(detail.get("warehouses_logistics_count", 0) or 0)},
            {"Signal": "Hospitals", "Count": int(detail.get("hospitals_count", 0) or 0)},
            {"Signal": "Universities", "Count": int(detail.get("universities_count", 0) or 0)},
            {"Signal": "Schools", "Count": int(detail.get("schools_count", 0) or 0)},
            {"Signal": "Groceries", "Count": int(detail.get("groceries_count", 0) or 0)},
        ]
    )
    info_cols = st.columns([1.05, 1.35])
    with info_cols[0]:
        _render_html_table(evidence)
    with info_cols[1]:
        st.markdown("**Evidence summary**")
        st.write(detail["interpretation_evidence"])
        st.markdown("**Shortlist note**")
        st.write(detail["shortlist_note"])


def render_page(market_id: str) -> None:
    """Render the D4 infrastructure and POI overlay page."""
    sector_options = get_d2_sector_options()
    sector_lookup = {label: sector_id for sector_id, label in sector_options}

    with st.sidebar:
        selected_sector_label = st.selectbox(
            "D4 base tract surface",
            list(sector_lookup),
            index=next(
                (idx for idx, (sector_id, _) in enumerate(sector_options) if sector_id == "professional"),
                0,
            ),
        )
        selected_sector = sector_lookup[selected_sector_label]
        base_surface = st.radio(
            "D4 tract fill",
            options=["jobs_total", "selected_industry"],
            index=0 if D4_DEFAULT_BASE_SURFACE == "jobs_total" else 1,
            format_func=lambda value: {
                "jobs_total": "Total workplace jobs",
                "selected_industry": f"{selected_sector_label} share",
            }[value],
        )
        show_lines = st.checkbox("Show OSM lines", value=True)
        show_polygons = st.checkbox("Show OSM polygons", value=True)
        show_population = st.checkbox("Show population centers", value=True)
        show_job_centers = st.checkbox("Show job centers", value=True)
        shortlist_count = st.slider(
            "D4 shortlist size",
            min_value=3,
            max_value=12,
            value=D4_DEFAULT_SHORTLIST_COUNT,
        )
        buffer_miles = st.slider(
            "D4 buffer miles",
            min_value=0.5,
            max_value=5.0,
            value=float(D4_DEFAULT_BUFFER_MILES),
            step=0.5,
        )

    payload = get_d4_overlay_payload(
        market_id=market_id,
        selected_sector=selected_sector,
        base_surface=base_surface,
        interpretation_buffer_miles=float(buffer_miles),
        shortlist_count=int(shortlist_count),
    )
    base_payload = payload["base_payload"]
    interpretation = payload["interpretation"]
    shortlist = interpretation["shortlist"]

    st.header("D4 — Infrastructure and POI Overlay")
    st.caption(
        "D4 now starts with the market's tract job surface, then layers in lower-noise OSM infrastructure context. "
        "Overture POIs are still available behind the scenes for first-pass tract interpretation counts, but they are "
        "not rendered on the map because the current taxonomy is still too noisy."
    )

    st.subheader(base_payload.get("title", "D4 map"))
    st.caption(base_payload.get("subtitle", ""))

    layers = [_build_base_geojson_layer(base_payload["features"])]
    if show_lines and payload["osm_line_features"]:
        layers.append(
            _build_geojson_outline_layer(
                payload["osm_line_features"],
                "d4-osm-lines",
                D4_LAYER_STYLES["osm_lines"]["color"],
            )
        )
    if show_polygons and payload["osm_polygon_features"]:
        layers.append(
            _build_geojson_outline_layer(
                payload["osm_polygon_features"],
                "d4-osm-polygons",
                D4_LAYER_STYLES["osm_polygons"]["color"],
                fill_alpha=75,
            )
        )
    if show_population and not payload["population_markers"].empty:
        population_rows = _prepare_marker_rows(payload["population_markers"], "pop_total")
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                population_rows.to_dict("records"),
                id="d4-population-centers",
                get_position="[centroid_lon, centroid_lat]",
                get_fill_color=D4_LAYER_STYLES["population_markers"]["color"],
                get_radius="radius",
                pickable=True,
                stroked=True,
                get_line_color=[255, 255, 255, 180],
                line_width_min_pixels=0.6,
                opacity=0.55,
            )
        )
    if show_job_centers and not payload["job_center_markers"].empty:
        job_rows = _prepare_marker_rows(payload["job_center_markers"], "jobs_total")
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                job_rows.to_dict("records"),
                id="d4-job-centers",
                get_position="[centroid_lon, centroid_lat]",
                get_fill_color=D4_LAYER_STYLES["job_center_markers"]["color"],
                get_radius="radius",
                pickable=True,
                stroked=True,
                get_line_color=[255, 255, 255, 210],
                line_width_min_pixels=0.7,
                opacity=0.78,
            )
        )

    view_state = payload["view_state"]
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(
            latitude=view_state["latitude"],
            longitude=view_state["longitude"],
            zoom=view_state["zoom"],
        ),
        tooltip={
            "html": (
                "<b>{tract_name}</b><br/>"
                "Tract: {tract_geoid}<br/>"
                "Dominant sector: {dominant_sector_label}<br/>"
                "{label}: {metric}<br/>"
                "Layer feature: {feature_name}<br/>"
                "Layer group: {layer_group}"
            ),
            "style": {
                "backgroundColor": "rgba(255, 255, 255, 0.96)",
                "color": "#1f2933",
                "fontSize": "12px",
            },
        },
        map_style=_MAP_STYLE,
    )
    st.pydeck_chart(deck, width="stretch")

    if shortlist.empty:
        st.info("No D4 interpretation shortlist is available for this market yet.")
    else:
        shortlist_options = shortlist["tract_name"].tolist()
        selected_tract_name = st.selectbox(
            "Selected shortlisted tract",
            shortlist_options,
        )
        selected_rows = shortlist[shortlist["tract_name"] == selected_tract_name]
        selected_detail = selected_rows.iloc[0].to_dict() if not selected_rows.empty else interpretation["selected_detail"]
        _render_interpretation_detail(selected_detail, float(buffer_miles))

        st.subheader("Job-center interpretation shortlist")
        _render_html_table(interpretation["table"])

    if payload["notes"]:
        st.info(" | ".join(payload["notes"]))

    st.subheader("Cached layer summary")
    _render_html_table(payload["layer_summary"])

    manifest_layers = pd.DataFrame(payload["manifest"].get("layers", []))
    if not manifest_layers.empty:
        st.subheader("Manifest detail")
        manifest_display = manifest_layers.copy()
        if "row_count" in manifest_display.columns:
            manifest_display["row_count"] = manifest_display["row_count"].map(format_jobs_cell)
        _render_html_table(manifest_display)

    with st.expander("Data notes"):
        st.markdown(
            "- `ingest_spatial.py` owns raw acquisition and cache creation for D4.\n"
            "- `data_prep.py` only reads those cached parquet outputs and combines them with D2/D3 analytical layers.\n"
            "- OSM is the first-pass geometry backbone for roads, rail, and other infrastructure shapes.\n"
            "- Overture is a first-class POI input and remains separate from the OSM geometry caches even when both render in the same map."
        )
