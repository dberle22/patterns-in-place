"""Standalone Streamlit entry point for the Place Intelligence Methods page."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


SECTION_ROOT = Path(__file__).resolve().parent
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from pages.d_methods import render_page
from shared_ui import render_site_selector, require_built_artifacts


st.set_page_config(page_title="Place Intelligence - Methods", layout="wide", initial_sidebar_state="expanded")
st.title("Place Intelligence")
st.caption("Standalone Methods page for faster loading and review.")

with st.sidebar:
    chosen_site_config = render_site_selector()

require_built_artifacts(str(chosen_site_config))
render_page(str(chosen_site_config))
