"""Public CBSA explorer entry point."""

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

from config import APP_TITLE


st.set_page_config(layout="wide", page_title=APP_TITLE)


def main() -> None:
    """Render the public app scaffold."""
    st.title(APP_TITLE)
    st.caption("Scaffold only. Public-facing labels and benchmark language land in Phase 2.")
    st.info("This app will share the Phase 1A foundation and disable Intelligence-specific surfaces.")


if __name__ == "__main__":
    main()
