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
    load_methods_payload,
    render_html_table,
)


def render_page(site_config_path: str) -> None:
    """Render the methods, diagnostics, and availability notes page."""

    payload = load_methods_payload(site_config_path)
    site = payload.get("site", {})
    resolved = payload.get("resolved_site", {})
    coverage = pd.DataFrame(payload.get("coverage_diagnostic", []))
    skip_reasons = pd.DataFrame(payload.get("skip_reasons", []))
    source_vintages = pd.DataFrame(payload.get("source_vintages", []))
    method_notes = payload.get("method_notes", [])

    st.header("5. Methods")

    st.subheader("Apportionment and reliability")
    if coverage.empty:
        st.info("Coverage diagnostics are unavailable for this site.")
    else:
        render_html_table(coverage)

    st.subheader("Geocode provenance")
    render_html_table(
        pd.DataFrame(
            [
                {
                    "Address": site.get("address"),
                    "Matched address": resolved.get("matched_address"),
                    "Match type": resolved.get("match_type"),
                    "Geocode source": resolved.get("geocode_source"),
                    "Tract": resolved.get("tract_geoid"),
                    "Latitude": resolved.get("lat"),
                    "Longitude": resolved.get("lon"),
                }
            ]
        )
    )

    st.subheader("Unavailable metrics and skip reasons")
    if skip_reasons.empty:
        st.info("No D2 metrics were skipped for the current catalog.")
    else:
        render_html_table(skip_reasons)

    st.subheader("Source vintages")
    if source_vintages.empty:
        st.info("No catchment rows are available to summarize source vintages.")
    else:
        render_html_table(source_vintages.rename(columns={"metric_label": "Metric", "year": "Year", "source_table": "Source"}))

    st.subheader("Method notes")
    st.markdown("\n".join(f"- {note}" for note in method_notes))
