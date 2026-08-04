"""Standalone Streamlit entry point for Industry D2."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


SECTION_ROOT = Path(__file__).resolve().parent
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from pages.d2_spatial_clusters import render_page
from shared_ui import render_market_selector


st.set_page_config(
    page_title="Industry D2 — Spatial Clusters",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Industry D2 — Spatial Clusters")
st.caption(
    "Standalone D2 app for tract-level dominant-industry and selected-share maps, plus county GDP context."
)

with st.sidebar:
    chosen_market_id = render_market_selector()

render_page(chosen_market_id)
