"""Standalone Streamlit entry point for Industry D1."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


SECTION_ROOT = Path(__file__).resolve().parent
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from pages.d1_makeup_change import render_page
from shared_ui import render_market_selector


st.set_page_config(
    page_title="Industry D1 — Makeup and Change",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Industry D1 — Makeup and Change")
st.caption(
    "Standalone D1 app for current mix, benchmark context, and change-over-time review."
)

with st.sidebar:
    chosen_market_id = render_market_selector()

render_page(chosen_market_id)
