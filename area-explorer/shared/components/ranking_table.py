"""Ranking table component for the selected metric distribution."""

from __future__ import annotations

import streamlit as st


def render_ranking_table(ranking_df, height: int = 280) -> None:
    """Render the sortable ranking surface for the selected metric."""
    st.dataframe(
        ranking_df[["rank", "geo_name", "state_name", "display_value", "national_pct_rank"]],
        hide_index=True,
        use_container_width=True,
        height=height,
    )
