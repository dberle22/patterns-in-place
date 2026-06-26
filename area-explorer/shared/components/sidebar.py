"""Sidebar rendering for the metric-first explorer flow."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_metric_sidebar(
    theme_lookup: dict[str, dict[str, Any]],
    state_options: list[tuple[str, str]],
    metric_meta_lookup,
) -> dict[str, Any]:
    """Render the metric picker sidebar and return the current selection state.

    The sidebar stays data-driven from the catalog tree so we can reuse it
    across the CBSA apps without hardcoding metric lists in the UI layer.
    """
    state_label_to_fips = {name: fips for name, fips in state_options}
    theme_ids = list(theme_lookup)

    with st.sidebar:
        st.subheader("Metric Picker")

        selected_theme_id = st.selectbox(
            "Theme",
            theme_ids,
            format_func=lambda theme_id: theme_lookup[theme_id]["display_name"],
        )
        selected_theme = theme_lookup[selected_theme_id]

        subject_lookup = {subject["subject_id"]: subject for subject in selected_theme["subjects"]}
        selected_subject_id = st.selectbox(
            "Subject",
            list(subject_lookup),
            format_func=lambda subject_id: subject_lookup[subject_id]["display_name"],
        )
        selected_subject = subject_lookup[selected_subject_id]

        topic_lookup = {topic["topic_id"]: topic for topic in selected_subject["topics"]}
        selected_topic_id = st.selectbox(
            "Topic",
            list(topic_lookup),
            format_func=lambda topic_id: topic_lookup[topic_id]["display_name"],
        )
        selected_topic = topic_lookup[selected_topic_id]

        metric_options = selected_topic["metrics"]
        selected_metric_id = st.selectbox(
            "Metric",
            [metric["metric_id"] for metric in metric_options],
            format_func=lambda metric_id: metric_meta_lookup(metric_id)["display_name"],
        )

        selected_state_labels = st.multiselect(
            "State Filter",
            [label for label, _ in state_options],
            default=[],
        )
        color_scale_mode = st.selectbox("Color Scale", ["Auto", "Quantile", "Raw"], index=0)

    return {
        "theme_id": selected_theme_id,
        "subject_id": selected_subject_id,
        "topic_id": selected_topic_id,
        "metric_id": selected_metric_id,
        "state_labels": selected_state_labels,
        "state_fips": tuple(state_label_to_fips[label] for label in selected_state_labels),
        "color_scale_mode": color_scale_mode,
    }
