"""Profile panel component for selected-place context."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from shared.benchmark import format_metric_value, format_percentile


def render_profile_panel(metric_meta: dict, selected_row: pd.Series, intelligence_profile: dict) -> None:
    """Render the selected-place profile with metric and Intelligence context."""
    st.subheader(selected_row["geo_name"])
    st.metric("Metric Value", format_metric_value(selected_row["metric_value"], metric_meta.get("unit_format")))
    st.caption(
        f"National: {format_percentile(selected_row['national_pct_rank'])} | "
        f"Division: {format_percentile(selected_row['division_pct_rank'])}"
    )
    if pd.notna(selected_row.get("state_name")):
        st.write(f"State: `{selected_row['state_name']}`")
    if pd.notna(selected_row.get("division_name")):
        st.write(f"Division: `{selected_row['division_name']}`")

    if not intelligence_profile:
        st.info("Intelligence profile is not available from the current data source.")
        return

    st.divider()
    st.write(f"Character: `{intelligence_profile.get('character_cluster', 'NA')}`")
    st.write(f"Livability: `{intelligence_profile.get('livability_cluster', 'NA')}`")
    st.write(f"Opportunity: `{intelligence_profile.get('opportunity_cluster', 'NA')}`")
    if intelligence_profile.get("combined_cluster"):
        st.write(f"Combined: `{intelligence_profile['combined_cluster']}`")
    if intelligence_profile.get("combined_cluster"):
        st.write(
            "Primary Cluster Affinity: "
            f"`{intelligence_profile['combined_cluster']}` "
            f"({float(intelligence_profile.get('top_gmm_probability') or 0):.2f})"
        )
    if intelligence_profile.get("second_gmm_probability") is not None:
        st.write(
            "Secondary Cluster Probability: "
            f"({float(intelligence_profile.get('second_gmm_probability') or 0):.2f})"
        )
    if intelligence_profile.get("cross_frame_divergence_flag") is not None:
        st.write(f"Divergence Flag: `{bool(intelligence_profile['cross_frame_divergence_flag'])}`")


def render_peer_comparison_table(comparison_df: pd.DataFrame) -> None:
    """Render a compact key-metric table for the selected CBSA and its peers."""
    st.subheader("Peer Comparison")

    if comparison_df.empty:
        st.caption("Peer comparison metrics are not available for the current selection.")
        return

    display_df = comparison_df.copy()
    display_df["similarity"] = display_df["similarity"].round(3)
    display_df["pop_total"] = display_df["pop_total"].map(
        lambda value: format_metric_value(value, "integer") if pd.notna(value) else "NA"
    )
    display_df["median_hh_income"] = display_df["median_hh_income"].map(
        lambda value: format_metric_value(value, "currency") if pd.notna(value) else "NA"
    )
    display_df["rent_to_income"] = display_df["rent_to_income"].map(
        lambda value: format_metric_value(value, "ratio") if pd.notna(value) else "NA"
    )
    percentile_columns = [
        "character_percentile_rank",
        "livability_percentile_rank",
        "opportunity_percentile_rank",
    ]
    for column in percentile_columns:
        display_df[column] = display_df[column].map(
            lambda value: format_percentile(value) if pd.notna(value) else "NA"
        )

    st.dataframe(
        display_df[
            [
                "comparison_role",
                "peer_rank",
                "cbsa_name",
                "state_name_primary",
                "similarity",
                "pop_total",
                "median_hh_income",
                "rent_to_income",
                "character_percentile_rank",
                "livability_percentile_rank",
                "opportunity_percentile_rank",
            ]
        ].rename(
            columns={
                "comparison_role": "role",
                "peer_rank": "rank",
                "cbsa_name": "cbsa",
                "state_name_primary": "state",
                "pop_total": "population",
                "median_hh_income": "median_income",
                "rent_to_income": "rent_to_income",
                "character_percentile_rank": "character",
                "livability_percentile_rank": "livability",
                "opportunity_percentile_rank": "opportunity",
            }
        ),
        hide_index=True,
        use_container_width=True,
        height=260,
    )
