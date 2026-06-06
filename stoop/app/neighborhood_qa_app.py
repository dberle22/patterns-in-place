"""Neighborhood data QA Streamlit app."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from nyc_property_finder.app.base_map import BaseMapData, prepare_base_map_data
from nyc_property_finder.app.neighborhood_qa import (
    build_curated_poi_coverage,
    build_metric_coverage,
    build_pipeline_timestamps,
    build_public_poi_coverage,
    build_source_status,
    build_table_status,
    format_coverage,
)
from nyc_property_finder.services.config import PROJECT_ROOT, load_config


st.set_page_config(page_title="Neighborhood Data QA", layout="wide")


@st.cache_data(show_spinner="Loading neighborhood QA inputs...")
def cached_prepare_base_map_data(
    database_path: str,
    tract_path: str,
    tract_id_col: str,
    metric: str,
) -> BaseMapData:
    """Cached wrapper around base-map assembly."""

    return prepare_base_map_data(
        database_path=database_path,
        tract_path=tract_path,
        tract_id_col=tract_id_col,
        metric=metric,
    )


@st.cache_data(show_spinner="Profiling neighborhood tables...")
def cached_table_status(database_path: str):
    return build_table_status(database_path)


@st.cache_data(show_spinner="Profiling metric coverage...")
def cached_metric_coverage(database_path: str, grain: str):
    return build_metric_coverage(database_path, grain)


@st.cache_data(show_spinner="Checking source paths...")
def cached_source_status(data_sources: dict):
    return build_source_status(data_sources)


@st.cache_data(show_spinner="Profiling curated POI coverage...")
def cached_curated_poi_coverage(database_path: str):
    return build_curated_poi_coverage(database_path)


@st.cache_data(show_spinner="Profiling public POI coverage...")
def cached_public_poi_coverage(database_path: str):
    return build_public_poi_coverage(database_path)


@st.cache_data(show_spinner="Collecting pipeline timestamps...")
def cached_pipeline_timestamps(database_path: str):
    return build_pipeline_timestamps(database_path)


def _render_readiness(database_path: str, tract_path: str, map_data: BaseMapData) -> None:
    stats = map_data.stats
    st.subheader("Readiness")
    metric_cols = st.columns(5)
    metric_cols[0].metric("Database", "ready" if Path(database_path).exists() else "missing")
    metric_cols[1].metric("Tract GeoJSON", "ready" if Path(tract_path).exists() else "missing")
    metric_cols[2].metric("Tracts", f"{stats['tract_count']:,}")
    metric_cols[3].metric("Neighborhoods", f"{stats['neighborhood_count']:,}")
    metric_cols[4].metric("Selected metric coverage", format_coverage(float(stats["metric_coverage"])))

    if not Path(database_path).exists():
        st.error("Database file is missing. Build the gold tables before using the apps.")
    if not Path(tract_path).exists():
        st.error("Census tract GeoJSON is missing.")


def _render_table_status(database_path: str) -> None:
    st.subheader("Gold Tables")
    st.dataframe(cached_table_status(database_path), use_container_width=True, hide_index=True)


def _render_metric_coverage(database_path: str) -> None:
    st.subheader("Metric Coverage")
    tract_tab, nta_tab = st.tabs(["Tracts", "Neighborhoods"])
    with tract_tab:
        st.dataframe(
            cached_metric_coverage(database_path, "tract"),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Coverage": st.column_config.ProgressColumn(
                    "Coverage",
                    format="%.1f",
                    min_value=0.0,
                    max_value=1.0,
                )
            },
        )
    with nta_tab:
        st.dataframe(
            cached_metric_coverage(database_path, "nta"),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Coverage": st.column_config.ProgressColumn(
                    "Coverage",
                    format="%.1f",
                    min_value=0.0,
                    max_value=1.0,
                )
            },
        )


def _render_source_status(data_sources: dict) -> None:
    st.subheader("Configured Sources")
    st.dataframe(cached_source_status(data_sources), use_container_width=True, hide_index=True)


def _render_curated_poi_coverage(database_path: str) -> None:
    coverage = cached_curated_poi_coverage(database_path)
    summary = coverage.attrs.get("summary", {})

    st.subheader("Curated POI Coverage")
    metric_cols = st.columns(6)
    metric_cols[0].metric("Expected inventory rows", f"{summary.get('expected_inventory_rows', 0):,}")
    metric_cols[1].metric(
        "Present expected",
        f"{summary.get('present_expected_categories', 0):,}",
    )
    metric_cols[2].metric(
        "Missing expected",
        f"{summary.get('missing_expected_categories', 0):,}",
    )
    metric_cols[3].metric("Curated rows", f"{summary.get('total_rows', 0):,}")
    metric_cols[4].metric(
        "Duplicate Place IDs",
        f"{summary.get('duplicate_place_ids', 0):,}",
    )
    metric_cols[5].metric(
        "Missing place details",
        f"{summary.get('rows_without_place_details', 0):,}",
    )
    if summary.get("unresolved_rows", 0):
        st.warning(
            f"{summary['unresolved_rows']:,} curated rows are blank or mapped to `other` and need review."
        )
    st.dataframe(coverage, use_container_width=True, hide_index=True)


def _render_public_poi_coverage(database_path: str) -> None:
    coverage = cached_public_poi_coverage(database_path)
    summary = coverage.attrs.get("summary", {})

    st.subheader("Public POI Coverage")
    metric_cols = st.columns(5)
    metric_cols[0].metric("Expected categories", f"{summary.get('expected_categories', 0):,}")
    metric_cols[1].metric(
        "Present expected",
        f"{summary.get('present_expected_categories', 0):,}",
    )
    metric_cols[2].metric(
        "Missing expected",
        f"{summary.get('missing_expected_categories', 0):,}",
    )
    metric_cols[3].metric("Public rows", f"{summary.get('total_rows', 0):,}")
    metric_cols[4].metric(
        "WS3 UI gaps",
        f"{summary.get('ws3_missing_categories', 0):,}",
    )
    latest_snapshot = summary.get("latest_snapshot")
    if pd.notna(latest_snapshot):
        st.caption(f"Latest public POI snapshot: `{pd.to_datetime(latest_snapshot)}`")
    st.dataframe(coverage, use_container_width=True, hide_index=True)


def _render_pipeline_timestamps(database_path: str) -> None:
    st.subheader("Pipeline Timestamps")
    st.dataframe(
        cached_pipeline_timestamps(database_path)[["Asset", "Timestamp label", "Source"]],
        use_container_width=True,
        hide_index=True,
    )


def main() -> None:
    """Render the Neighborhood Data QA application."""

    config = load_config()
    settings = config["settings"]
    data_sources = config["data_sources"]
    source_config = data_sources["sources"]
    database_path = str(PROJECT_ROOT / settings["database_path"])
    tract_source = source_config["census_tracts"]
    tract_path = str(PROJECT_ROOT / tract_source["path"])
    tract_id_col = tract_source.get("id_column", "GEOID")

    st.title("Neighborhood Data QA")
    st.caption(
        "Coverage, freshness, and readiness checks for the neighborhood foundation plus "
        "curated/public POI inventories."
    )

    with st.sidebar:
        st.header("Inputs")
        st.caption(f"Database: `{database_path}`")
        st.caption(f"Tracts: `{tract_path}`")
        selected_metric = st.selectbox(
            "Readiness metric",
            ["median_income", "median_rent", "median_home_value", "pct_bachelors_plus", "median_age"],
            format_func=lambda value: value.replace("_", " ").title(),
        )

    map_data = cached_prepare_base_map_data(
        database_path=database_path,
        tract_path=tract_path,
        tract_id_col=tract_id_col,
        metric=selected_metric,
    )

    _render_readiness(database_path, tract_path, map_data)
    _render_table_status(database_path)
    _render_metric_coverage(database_path)
    _render_curated_poi_coverage(database_path)
    _render_public_poi_coverage(database_path)
    _render_pipeline_timestamps(database_path)
    _render_source_status(data_sources)


if __name__ == "__main__":
    main()
