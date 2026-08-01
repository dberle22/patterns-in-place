"""People tab for the Place Intelligence brief."""

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
    render_chart_result,
    format_count_cell,
    format_percent_cell,
    format_ratio_cell,
    load_d2_payload,
    load_d3_payload,
    load_site_base_payload,
    render_html_table,
)


def render_page(site_config_path: str) -> None:
    """Render the people and daytime-population view."""

    base = load_site_base_payload(site_config_path)
    d2_payload = load_d2_payload(site_config_path)
    d3_payload = load_d3_payload(site_config_path)
    site = base["site"]
    summary = d2_payload.get("metric_summary", pd.DataFrame())
    profile = d2_payload["catchment_profile"]
    daytime = d3_payload["daytime_population"]

    st.header("2. People")

    st.subheader("Ring gradient")
    has_profile_schema = {"metric", "ring_mi", "metric_label", "value"}.issubset(profile.columns)
    selected_metrics = profile.loc[
        profile["metric"].isin(["pop_total", "households", "median_hh_income", "pct_ba_plus", "median_age"])
    ].copy() if has_profile_schema and not profile.empty else pd.DataFrame()
    if selected_metrics.empty:
        st.info("Catchment profile rows are unavailable for this site.")
    else:
        selected_metric_label = st.selectbox(
            "Metric",
            options=selected_metrics["metric"].drop_duplicates().tolist(),
            format_func=lambda metric: selected_metrics.loc[selected_metrics["metric"] == metric, "metric_label"].iloc[0],
        )
        metric_rows = selected_metrics.loc[selected_metrics["metric"] == selected_metric_label].copy()
        chart = build_simple_bar_chart(
            metric_rows,
            entity_col="ring_mi",
            value_col="value",
            title=f"{metric_rows['metric_label'].iloc[0]} by ring",
            subtitle=f"Apportioned catchment read | source {metric_rows['source_table'].iloc[0]} | {int(metric_rows['year'].iloc[0])}",
            unit="percent" if "pct_" in selected_metric_label else "currency" if "income" in selected_metric_label else "count",
            decimals=1 if "pct_" in selected_metric_label else 0,
        )
        render_chart_result(chart)

        change_rows = metric_rows.loc[metric_rows["change_5yr"].notna()].copy()
        if change_rows.empty:
            st.info("5-year change is unavailable for this metric.")
        else:
            change_chart = build_simple_bar_chart(
                change_rows,
                entity_col="ring_mi",
                value_col="change_5yr",
                title=f"{metric_rows['metric_label'].iloc[0]} 5-year change",
                subtitle=metric_rows["change_5yr_period"].dropna().iloc[0],
                unit="count",
                decimals=1,
            )
            render_chart_result(change_chart)

    st.subheader("Benchmark companion")
    primary_rows = profile.loc[profile["ring_mi"] == site.primary_ring_mi].copy() if has_profile_schema and not profile.empty else pd.DataFrame()
    if not summary.empty:
        display = summary[
            [
                "metric_label",
                "primary_value",
                "primary_cbsa_percentile",
                "primary_cbsa_percentile_denominator",
                "source_table",
                "primary_year",
            ]
        ].copy()
        display = display.rename(
            columns={
                "metric_label": "Metric",
                "primary_value": "3-mile value",
                "primary_cbsa_percentile": "CBSA percentile",
                "primary_cbsa_percentile_denominator": "Tract denominator",
                "source_table": "Source",
                "primary_year": "Year",
            }
        )
        display["3-mile value"] = display["3-mile value"].map(lambda value: f"{float(value):,.1f}" if pd.notna(value) else "—")
        display["CBSA percentile"] = display["CBSA percentile"].map(lambda value: "—" if pd.isna(value) else f"{float(value):.0f}th")
        render_html_table(display)
    elif primary_rows.empty:
        st.info("Primary-ring benchmark rows are unavailable for this site.")
    else:
        display = primary_rows[["metric_label", "value", "cbsa_percentile", "cbsa_percentile_denominator", "source_table", "year"]].copy()
        display = display.rename(
            columns={
                "metric_label": "Metric",
                "value": "3-mile value",
                "cbsa_percentile": "CBSA percentile",
                "cbsa_percentile_denominator": "Tract denominator",
                "source_table": "Source",
                "year": "Year",
            }
        )
        display["3-mile value"] = display["3-mile value"].map(lambda value: f"{float(value):,.1f}" if pd.notna(value) else "—")
        display["CBSA percentile"] = display["CBSA percentile"].map(lambda value: "—" if pd.isna(value) else f"{float(value):.0f}th")
        render_html_table(display)

    st.subheader("Day and night divergence")
    if daytime.empty:
        st.info("Daytime population rows are unavailable for this site.")
    else:
        ratio_chart = build_simple_bar_chart(
            daytime,
            entity_col="ring_mi",
            value_col="jobs_to_workers_ratio",
            title="Jobs to resident workers by ring",
            subtitle=f"Directly observed LEHD workplace and resident-worker counts | {int(daytime['year'].iloc[0])}",
            unit="ratio",
            decimals=2,
        )
        render_chart_result(ratio_chart)
        display = daytime[
            ["ring_mi", "jobs_total", "workers_total", "jobs_to_workers_ratio", "daytime_net_change"]
        ].copy()
        display = display.rename(
            columns={
                "ring_mi": "Ring (mi)",
                "jobs_total": "Jobs",
                "workers_total": "Resident workers",
                "jobs_to_workers_ratio": "Jobs / workers",
                "daytime_net_change": "Net daytime change",
            }
        )
        display["Jobs"] = display["Jobs"].map(format_count_cell)
        display["Resident workers"] = display["Resident workers"].map(format_count_cell)
        display["Jobs / workers"] = display["Jobs / workers"].map(format_ratio_cell)
        display["Net daytime change"] = display["Net daytime change"].map(format_count_cell)
        render_html_table(display)

    st.subheader("Workplace industry breakout")
    if daytime.empty:
        st.info("Industry breakout rows are unavailable for this site.")
    else:
        selected_ring = st.selectbox("Industry breakout ring", options=daytime["ring_mi"].tolist(), key="people_breakout_ring")
        ring_row = daytime.loc[daytime["ring_mi"] == selected_ring].head(1)
        breakout = pd.DataFrame(
            [
                {"industry": "Retail", "jobs": ring_row["jobs_retail"].iloc[0]},
                {"industry": "Accommodation / food", "jobs": ring_row["jobs_accommodation_food"].iloc[0]},
                {"industry": "Health care", "jobs": ring_row["jobs_health_care"].iloc[0]},
                {"industry": "Professional / scientific", "jobs": ring_row["jobs_professional_scientific"].iloc[0]},
            ]
        )
        render_chart_result(
            build_simple_bar_chart(
                breakout,
                entity_col="industry",
                value_col="jobs",
                title=f"Workplace jobs by industry | {selected_ring}-mile ring",
                subtitle=f"Direct LEHD workplace jobs | {int(daytime['year'].iloc[0])}",
                unit="count",
                decimals=0,
            )
        )
