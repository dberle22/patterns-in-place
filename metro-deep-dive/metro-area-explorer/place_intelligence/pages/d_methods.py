"""Methods tab for the Place Intelligence brief."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st


SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from shared_ui import (
    load_d2_payload,
    load_site_base_payload,
    render_html_table,
)


def render_page(site_config_path: str) -> None:
    """Render the methods, diagnostics, and availability notes page."""

    base = load_site_base_payload(site_config_path)
    d2_payload = load_d2_payload(site_config_path)
    resolved = base["resolved_site"]

    st.header("5. Methods")

    st.subheader("Apportionment and reliability")
    coverage = base["coverage_diagnostic"]
    if coverage.empty:
        st.info("Coverage diagnostics are unavailable for this site.")
    else:
        render_html_table(coverage)

    st.subheader("Geocode provenance")
    render_html_table(
        pd.DataFrame(
            [
                {
                    "Address": base["site"].address,
                    "Matched address": resolved.matched_address,
                    "Match type": resolved.match_type,
                    "Geocode source": resolved.geocode_source,
                    "Tract": resolved.tract_geoid,
                    "Latitude": resolved.lat,
                    "Longitude": resolved.lon,
                }
            ]
        )
    )

    st.subheader("Unavailable metrics and skip reasons")
    skip_reasons = d2_payload["skip_reasons"]
    if skip_reasons.empty:
        st.info("No D2 metrics were skipped for the current catalog.")
    else:
        render_html_table(skip_reasons)

    st.subheader("Source vintages")
    metric_long = d2_payload.get("metric_long", pd.DataFrame())
    catchment = metric_long.loc[metric_long["record_type"] == "catchment"].copy() if not metric_long.empty and "record_type" in metric_long.columns else d2_payload["catchment_profile"]
    if catchment.empty:
        st.info("No catchment rows are available to summarize source vintages.")
    else:
        vintages = catchment[["metric_label", "year", "source_table"]].drop_duplicates().sort_values(["source_table", "metric_label"])
        render_html_table(vintages.rename(columns={"metric_label": "Metric", "year": "Year", "source_table": "Source"}))

    st.subheader("Method notes")
    st.markdown(
        "\n".join(
            [
                "- Catchment numbers are tract-apportioned using areal weights rather than centroid inclusion.",
                "- Straight-line rings remain the baseline context surface; the barrier screen is a heuristic, not a routing model.",
                "- D4 traffic counts and D5 FEMA layers stay fail-soft, so temporary source outages do not break the rest of the brief.",
                "- The Market tab is intentionally compact and is a candidate for a reusable Metro Deep Dive summary component.",
            ]
        )
    )
