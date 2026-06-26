"""County explorer entry point."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
AREA_EXPLORER_ROOT = APP_DIR.parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
if str(AREA_EXPLORER_ROOT) not in sys.path:
    sys.path.insert(0, str(AREA_EXPLORER_ROOT))

from config import APP_TITLE, REQUIRE_STATE_FILTER


st.set_page_config(layout="wide", page_title=APP_TITLE)


def main() -> None:
    """Render the county app scaffold."""
    st.title(APP_TITLE)
    st.caption("Scaffold only. County-specific state filtering and benchmark logic land in Phase 3.")
    if REQUIRE_STATE_FILTER:
        st.info("This app will require a state selection before rendering the county choropleth.")


if __name__ == "__main__":
    main()
