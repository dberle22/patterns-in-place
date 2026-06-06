"""Durable Streamlit entry point for Stoop Explore."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import streamlit_analytics2 as streamlit_analytics
from streamlit_app_v2 import main


if __name__ == "__main__":
    with streamlit_analytics.track():
        main()
