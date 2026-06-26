"""Landing page for Area Explorer apps."""

from __future__ import annotations

import streamlit as st


st.set_page_config(layout="centered", page_title="Area Explorer")


def main() -> None:
    """Render the landing page scaffold."""
    st.title("Area Explorer")
    st.write("Metric-first dashboards for exploring Patterns in Place data.")
    st.markdown("- `CBSA Internal`")
    st.markdown("- `CBSA Public`")
    st.markdown("- `County Explorer`")


if __name__ == "__main__":
    main()

