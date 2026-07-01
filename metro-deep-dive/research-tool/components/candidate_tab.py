"""Candidate List tab — Phase 6 ranked market selection surface."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from config import PATTERN_LABELS
from dd_db import get_candidate_list


def render_candidate_list(active_cbsa_code: str) -> None:
    st.subheader("Market Candidate List")
    st.caption(
        "All 401 CBSAs ranked by candidate score (cross-frame divergence × trajectory interest). "
        "Use filters to narrow. Click 'Open' to switch the active metro."
    )

    try:
        df = get_candidate_list()
    except Exception as e:
        st.error(f"Could not load candidate list: {e}")
        return

    # Filters
    with st.expander("Filters", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            divisions = sorted(df["census_division"].dropna().unique().tolist())
            sel_divisions = st.multiselect("Census Division", options=divisions)
        with fc2:
            patterns = list(PATTERN_LABELS.keys())
            sel_patterns = st.multiselect(
                "Pattern Flags",
                options=patterns,
                format_func=lambda x: PATTERN_LABELS[x],
            )
        with fc3:
            show_ct = st.checkbox("Include CBSAs with CT exclusion flag", value=False)

    filtered = df.copy()

    if sel_divisions:
        filtered = filtered[filtered["census_division"].isin(sel_divisions)]

    for pat in sel_patterns:
        filtered = filtered[filtered[pat].astype(bool)]

    if not show_ct:
        if "ct_exclusion_flag" in filtered.columns:
            filtered = filtered[~filtered["ct_exclusion_flag"].astype(bool)]

    filtered = filtered.sort_values("candidate_rank")

    # Build display table
    pattern_col_labels = {k: PATTERN_LABELS[k][:10] for k in PATTERN_LABELS}
    display_cols = {
        "candidate_rank": "Rank",
        "cbsa_name": "Metro",
        "census_division": "Division",
        "candidate_score": "Score",
        "cross_frame_percentile": "XF Pct",
        "overlap_profile": "Alignment",
        "signature": "Signature",
        "livability_direction": "Liv Dir",
        "opportunity_direction": "Opp Dir",
        "character_direction": "Char Dir",
        "opp_turn_signal": "Opp Turn",
    }

    for pat_col, pat_label in pattern_col_labels.items():
        if pat_col in filtered.columns:
            display_cols[pat_col] = pat_label

    display = filtered[[c for c in display_cols if c in filtered.columns]].rename(columns=display_cols)
    display["Score"] = display["Score"].map(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
    display["XF Pct"] = display["XF Pct"].map(lambda x: f"{x:.0f}th" if pd.notna(x) else "—")

    # Highlight active metro — use index label lookup, not positional .iloc
    active_row_indices = set(filtered.index[filtered["cbsa_code"] == active_cbsa_code].tolist()) if "cbsa_code" in filtered.columns else set()

    def highlight_active(row):
        active = row.name in active_row_indices
        return ["background-color: #FFF9C4" if active else "" for _ in row]

    st.dataframe(
        display.style.apply(highlight_active, axis=1),
        use_container_width=True,
        hide_index=True,
        height=600,
    )

    st.caption(f"Showing {len(display):,} of {len(df):,} CBSAs")

    # Export
    csv = filtered.to_csv(index=False).encode()
    st.download_button(
        "Download filtered list (CSV)",
        data=csv,
        file_name="deep_dive_candidates.csv",
        mime="text/csv",
    )

    # Quick-switch button: find the selected metro and offer jump
    if active_cbsa_code in filtered["cbsa_code"].values:
        active_row = filtered[filtered["cbsa_code"] == active_cbsa_code].iloc[0]
        st.info(
            f"Currently viewing: **{active_row['cbsa_name']}** "
            f"— Candidate rank #{int(active_row['candidate_rank'])}, "
            f"Score: {active_row['candidate_score']:.1f}"
        )
