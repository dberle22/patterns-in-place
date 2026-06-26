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
    if intelligence_profile.get("top_gmm_cluster") is not None:
        st.write(
            "Top GMM Membership: "
            f"`Cluster {intelligence_profile['top_gmm_cluster']}` "
            f"({float(intelligence_profile.get('top_gmm_probability') or 0):.2f})"
        )
    if intelligence_profile.get("second_gmm_cluster") is not None:
        st.write(
            "Second GMM Membership: "
            f"`Cluster {intelligence_profile['second_gmm_cluster']}` "
            f"({float(intelligence_profile.get('second_gmm_probability') or 0):.2f})"
        )
    if intelligence_profile.get("cross_frame_divergence_flag") is not None:
        st.write(f"Divergence Flag: `{bool(intelligence_profile['cross_frame_divergence_flag'])}`")


def render_similarity_peers(peers_df) -> None:
    """Render the ranked similarity peer table for the selected CBSA."""
    st.divider()
    st.write("Top Similar Peers")

    if peers_df.empty:
        st.caption("Peer rankings are not available from the current Intelligence source.")
        return

    display_df = peers_df.copy()
    display_df["similarity"] = display_df["similarity"].round(3)
    st.dataframe(
        display_df[["peer_rank", "peer_cbsa_name", "similarity"]].rename(
            columns={"peer_rank": "rank", "peer_cbsa_name": "peer"}
        ),
        hide_index=True,
        use_container_width=True,
        height=260,
    )
