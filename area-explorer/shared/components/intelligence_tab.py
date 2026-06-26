"""Intelligence tab renderers for the internal CBSA explorer."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_intelligence_tab(
    intelligence_df: pd.DataFrame,
    membership_df: pd.DataFrame,
    selected_geo_id: str,
    intelligence_profile: dict,
) -> None:
    """Render the cross-frame scatter and membership table views.

    The roadmap calls for a primary scatter plus a secondary membership table.
    This keeps both in the tab so Dan can switch between the "where does this
    metro sit?" view and the "how is the model grouping places?" view.
    """
    if intelligence_df.empty:
        st.info("Intelligence data is not available from the current database or fallback parquet files.")
        return

    selected_intelligence = intelligence_df.loc[intelligence_df["cbsa_code"] == selected_geo_id]
    scatter = px.scatter(
        intelligence_df,
        x="livability_percentile_rank",
        y="opportunity_percentile_rank",
        color="character_cluster",
        hover_name="cbsa_name",
        hover_data=["state_name", "division_name", "combined_cluster"],
        height=500,
        title="Livability vs Opportunity",
    )
    if not selected_intelligence.empty:
        selected_point = selected_intelligence.iloc[0]
        scatter.add_trace(
            go.Scatter(
                x=[selected_point["livability_percentile_rank"]],
                y=[selected_point["opportunity_percentile_rank"]],
                mode="markers+text",
                text=[selected_point["cbsa_name"]],
                textposition="top center",
                marker=dict(size=14, color="#d94801", line=dict(width=2, color="white")),
                showlegend=False,
            )
        )
    st.plotly_chart(scatter, use_container_width=True)

    if intelligence_profile:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "frame": "Character",
                        "percentile_rank": intelligence_profile.get("character_percentile_rank"),
                        "cluster": intelligence_profile.get("character_cluster"),
                    },
                    {
                        "frame": "Livability",
                        "percentile_rank": intelligence_profile.get("livability_percentile_rank"),
                        "cluster": intelligence_profile.get("livability_cluster"),
                    },
                    {
                        "frame": "Opportunity",
                        "percentile_rank": intelligence_profile.get("opportunity_percentile_rank"),
                        "cluster": intelligence_profile.get("opportunity_cluster"),
                    },
                ]
            ),
            hide_index=True,
            use_container_width=True,
        )

    st.subheader("Cluster Membership Table")
    if membership_df.empty:
        st.caption("Cluster membership rows are not available from the current Intelligence source.")
        return

    display_df = membership_df.copy()
    for column in ["top_gmm_probability", "second_gmm_probability"]:
        if column in display_df.columns:
            display_df[column] = display_df[column].round(3)
    st.dataframe(display_df, hide_index=True, use_container_width=True, height=320)
