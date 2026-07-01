"""Deep Dive Research Tool — Streamlit entry point."""

from __future__ import annotations

import sys
from pathlib import Path

# Make shared/ importable as a package
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from dd_db import get_cbsa_list, get_candidate_list, get_full_profile
from config import FRAME_COLORS

st.set_page_config(
    page_title="Deep Dive Research Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Load CBSA list (cached)
# ---------------------------------------------------------------------------
cbsa_df = get_cbsa_list()
cbsa_df["cbsa_code"] = cbsa_df["cbsa_code"].astype(str)
cbsa_options = list(zip(cbsa_df["cbsa_name"] + " (" + cbsa_df["cbsa_code"] + ")", cbsa_df["cbsa_code"]))
cbsa_label_to_code = {label: code for label, code in cbsa_options}
cbsa_labels = [label for label, _ in cbsa_options]
cbsa_code_to_name = dict(zip(cbsa_df["cbsa_code"], cbsa_df["cbsa_name"]))

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "selected_cbsa" not in st.session_state:
    st.session_state.selected_cbsa = None
if "recently_viewed" not in st.session_state:
    st.session_state.recently_viewed = []

# ---------------------------------------------------------------------------
# Sidebar: recently viewed
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Recently Viewed")
    for code in st.session_state.recently_viewed[:5]:
        name = cbsa_code_to_name.get(code, code)
        if st.button(name, key=f"rv_{code}"):
            st.session_state.selected_cbsa = code

# ---------------------------------------------------------------------------
# Landing / selector
# ---------------------------------------------------------------------------
st.title("Deep Dive Research Tool")

if st.session_state.selected_cbsa is None:
    st.markdown("Select a metro to load its full profile across all three Intelligence frames.")

    col1, col2 = st.columns([2, 1])
    with col1:
        chosen_label = st.selectbox(
            "Search for a metro",
            options=[""] + cbsa_labels,
            format_func=lambda x: x if x else "— search by name —",
            key="cbsa_selector_landing",
        )
        if chosen_label:
            st.session_state.selected_cbsa = cbsa_label_to_code[chosen_label]
            rv = st.session_state.recently_viewed
            if st.session_state.selected_cbsa not in rv:
                rv.insert(0, st.session_state.selected_cbsa)
                st.session_state.recently_viewed = rv[:5]
            st.rerun()

    with col2:
        st.markdown("**Suggested markets**")
        try:
            cand = get_candidate_list().sort_values("candidate_rank").head(20)
            for _, row in cand.iterrows():
                code_str = str(row["cbsa_code"])
                if st.button(
                    f"{row['cbsa_name']} (#{int(row['candidate_rank'])})",
                    key=f"cand_{code_str}",
                    use_container_width=True,
                ):
                    st.session_state.selected_cbsa = code_str
                    rv = st.session_state.recently_viewed
                    if code_str not in rv:
                        rv.insert(0, code_str)
                        st.session_state.recently_viewed = rv[:5]
                    st.rerun()
        except Exception:
            st.caption("Candidate list unavailable")

    st.stop()

# ---------------------------------------------------------------------------
# Metro is selected — load profile
# ---------------------------------------------------------------------------
cbsa_code = st.session_state.selected_cbsa
cbsa_name = cbsa_code_to_name.get(cbsa_code, cbsa_code)

profile = get_full_profile(cbsa_code)
liv = profile.get("livability", {})
opp = profile.get("opportunity", {})
char = profile.get("character", {})
cf = profile.get("cross_frame", {})

# ---------------------------------------------------------------------------
# Header: name + cluster badges
# ---------------------------------------------------------------------------
col_name, col_change = st.columns([5, 1])
with col_name:
    st.markdown(f"# {cbsa_name}")
with col_change:
    if st.button("Change Metro", type="secondary"):
        st.session_state.selected_cbsa = None
        st.rerun()

badge_cols = st.columns(4)
with badge_cols[0]:
    lbl = liv.get("livability_cluster_name") or liv.get("livability_cluster", "—")
    st.metric("Livability Cluster", lbl)
with badge_cols[1]:
    lbl = opp.get("opportunity_cluster_name") or opp.get("opportunity_cluster", "—")
    st.metric("Opportunity Cluster", lbl)
with badge_cols[2]:
    lbl = char.get("character_cluster_name") or char.get("character_cluster", "—")
    st.metric("Character Cluster", lbl)
with badge_cols[3]:
    lbl = cf.get("cross_frame_cluster_name") or cf.get("combined_cluster", "—")
    st.metric("Cross-Frame Type", lbl)

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tabs = st.tabs([
    "Overview",
    "Livability",
    "Opportunity",
    "Character",
    "Trajectory",
    "Zone Map",
    "Peers",
    "Candidate List",
])

with tabs[0]:
    from components.overview_tab import render_overview
    render_overview(cbsa_code, cbsa_name, profile)

with tabs[1]:
    from components.livability_tab import render_livability
    render_livability(cbsa_code, cbsa_name, liv)

with tabs[2]:
    from components.opportunity_tab import render_opportunity
    render_opportunity(cbsa_code, cbsa_name, opp)

with tabs[3]:
    from components.character_tab import render_character
    render_character(cbsa_code, cbsa_name, char)

with tabs[4]:
    from components.trajectory_tab import render_trajectory
    render_trajectory(cbsa_code, cbsa_name)

with tabs[5]:
    from components.zone_map_tab import render_zone_map
    render_zone_map(cbsa_code, cbsa_name)

with tabs[6]:
    from components.peers_tab import render_peers
    render_peers(cbsa_code, cbsa_name, cf)

with tabs[7]:
    from components.candidate_tab import render_candidate_list
    render_candidate_list(cbsa_code)
