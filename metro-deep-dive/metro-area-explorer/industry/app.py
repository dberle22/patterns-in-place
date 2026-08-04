"""Combined Streamlit shell for the Industry explorer pages."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


SECTION_ROOT = Path(__file__).resolve().parent
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from pages.d1_makeup_change import render_page as render_d1_page
from pages.d2_spatial_clusters import render_page as render_d2_page
from pages.d3_job_centers import render_page as render_d3_page
from pages.d4_infrastructure_overlay import render_page as render_d4_page
from pages.d5_regional_fit import render_page as render_d5_page
from pages.d6_ai_exposure import render_page as render_d6_page
from shared_ui import render_market_selector


st.set_page_config(
    page_title="Industry Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Industry Explorer")
st.caption(
    "Combined shell for the Industry section. Each major deliverable now has its own smaller app surface, "
    "and this entry point ties those pages together."
)

with st.sidebar:
    chosen_market_id = render_market_selector()
    page = st.radio(
        "Page",
        options=["d1", "d2", "d3", "d4", "d5", "d6"],
        format_func=lambda value: {
            "d1": "D1 — Makeup and Change",
            "d2": "D2 — Spatial Clusters",
            "d3": "D3 — Job Centers",
            "d4": "D4 — Infrastructure Overlay",
            "d5": "D5 — Regional Fit",
            "d6": "D6 — AI Exposure",
        }[value],
    )

if page == "d1":
    st.header("D1 — Makeup and Change")
    render_d1_page(chosen_market_id)
elif page == "d2":
    render_d2_page(chosen_market_id)
elif page == "d3":
    render_d3_page(chosen_market_id)
elif page == "d4":
    st.header("D4 — Infrastructure Overlay")
    render_d4_page(chosen_market_id)
elif page == "d5":
    render_d5_page(chosen_market_id)
else:
    render_d6_page(chosen_market_id)
