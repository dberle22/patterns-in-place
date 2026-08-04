"""Streamlit shell for the Place Intelligence section."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


SECTION_ROOT = Path(__file__).resolve().parent
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from pages.d_market import render_page as render_market_page
from pages.d_methods import render_page as render_methods_page
from pages.d_overview import render_page as render_overview_page
from pages.d_people import render_page as render_people_page
from pages.d_place import render_page as render_place_page
from shared_ui import render_site_selector, require_built_artifacts


st.set_page_config(
    page_title="Place Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Place Intelligence")
st.caption(
    "Single-site context brief built on the Industry section pattern: thin app shell, shared prep payloads, "
    "and independently hideable blocks while the surface continues to evolve."
)

with st.sidebar:
    chosen_site_config = render_site_selector()
    page = st.radio(
        "Page",
        options=["overview", "people", "place", "market", "methods"],
        format_func=lambda value: {
            "overview": "1. Overview",
            "people": "2. People",
            "place": "3. Place",
            "market": "4. Market",
            "methods": "5. Methods",
        }[value],
    )

require_built_artifacts(str(chosen_site_config))

if page == "overview":
    render_overview_page(str(chosen_site_config))
elif page == "people":
    render_people_page(str(chosen_site_config))
elif page == "place":
    render_place_page(str(chosen_site_config))
elif page == "market":
    render_market_page(str(chosen_site_config))
else:
    render_methods_page(str(chosen_site_config))
