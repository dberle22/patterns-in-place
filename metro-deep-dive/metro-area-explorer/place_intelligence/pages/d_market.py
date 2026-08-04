"""Market tab for the Place Intelligence brief."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st


SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from shared_ui import (
    build_simple_bar_chart,
    build_simple_line_chart,
    load_market_page_payload,
    render_chart_result,
    render_html_table,
    source_label,
)


def render_page(site_config_path: str) -> None:
    """Render the compact Jacksonville market context page."""

    payload = load_market_page_payload(site_config_path)
    employment = pd.DataFrame(payload.get("employment_mix", []))
    gdp = pd.DataFrame(payload.get("gdp_mix", []))
    housing = pd.DataFrame(payload.get("housing_context", []))
    meta = payload.get("meta", {})

    st.header("4. Market")
    st.caption(meta.get("candidate_note"))

    st.subheader("Industry mix")
    if employment.empty and gdp.empty:
        st.info("Market industry context is unavailable for this site.")
    else:
        basis = st.radio("Basis", options=["employment", "gdp"], horizontal=True)
        rows = employment if basis == "employment" else gdp
        value_label = "Employment share" if basis == "employment" else "GDP share"
        render_chart_result(
            build_simple_bar_chart(
                rows.head(10),
                entity_col="sector_label",
                value_col="share_value",
                title=f"Jacksonville CBSA {value_label}",
                subtitle=f"Latest available year {int(rows['year'].iloc[0])}" if not rows.empty else "",
                unit="percent",
                decimals=1,
            )
        )
        if not rows.empty:
            display = rows.head(10)[["sector_label", "share_value", "raw_value", "year", "source"]].copy()
            display = display.rename(columns={"sector_label": "Sector", "share_value": value_label, "raw_value": "Raw value", "year": "Year", "source": "Source"})
            display["Source"] = display["Source"].map(source_label)
            render_html_table(display)

    st.subheader("Housing market trend")
    if housing.empty:
        st.info("CBSA housing-market context is unavailable for this site.")
    else:
        zhvi_rows = housing[["year", "zhvi_annual_avg"]].dropna().copy()
        zhvi_rows["series"] = "ZHVI annual average"
        zori_rows = housing[["year", "zori_annual_avg"]].dropna().copy()
        zori_rows["series"] = "ZORI annual average"

        if not zhvi_rows.empty:
            render_chart_result(
                build_simple_line_chart(
                    zhvi_rows.rename(columns={"zhvi_annual_avg": "value"}),
                    period_col="year",
                    value_col="value",
                    series_col="series",
                    title="Home value trend",
                    subtitle="CBSA annual average ZHVI",
                    unit="currency",
                    decimals=0,
                )
            )
        if not zori_rows.empty:
            render_chart_result(
                build_simple_line_chart(
                    zori_rows.rename(columns={"zori_annual_avg": "value"}),
                    period_col="year",
                    value_col="value",
                    series_col="series",
                    title="Rent trend",
                    subtitle="CBSA annual average ZORI",
                    unit="currency",
                    decimals=0,
                )
            )
        render_html_table(housing)
