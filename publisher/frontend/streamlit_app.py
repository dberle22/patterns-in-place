"""QA-focused Streamlit app for reviewing saved chatbot runs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from frontend.qa_utils import (
    RunArtifactBundle,
    build_summary_frame,
    default_run_roots,
    load_run_collections,
)


st.set_page_config(
    page_title="Metro Chatbot QA Review",
    layout="wide",
)


def main() -> None:
    st.title("Metro Deep Dive Chatbot QA Review")
    st.caption("Inspect saved LLM and deterministic runs without digging through artifact folders.")

    with st.sidebar:
        st.header("Run Sources")
        default_roots = "\n".join(str(path) for path in default_run_roots())
        root_input = st.text_area(
            "Artifact roots",
            value=default_roots,
            help="One repo-relative or absolute path per line.",
            height=120,
        )
        selected_roots = [_resolve_root(line) for line in root_input.splitlines() if line.strip()]
        bundles = load_run_collections(selected_roots)

        st.metric("Runs loaded", len(bundles))

        summary = build_summary_frame(bundles)
        question_types = sorted(value for value in summary["question_type"].dropna().unique()) if not summary.empty else []
        collections = sorted(value for value in summary["collection"].dropna().unique()) if not summary.empty else []

        selected_collections = st.multiselect(
            "Collections",
            options=collections,
            default=collections,
        )
        selected_types = st.multiselect(
            "Question types",
            options=question_types,
            default=question_types,
        )

    filtered_bundles = [
        bundle
        for bundle in bundles
        if (not selected_collections or bundle.collection in selected_collections)
        and (not selected_types or bundle.question_type in selected_types)
    ]
    filtered_summary = build_summary_frame(filtered_bundles)

    left, right = st.columns([1.1, 1.9], gap="large")

    with left:
        st.subheader("Run Index")
        if filtered_summary.empty:
            st.info("No saved runs matched the current filters.")
            return

        st.dataframe(
            filtered_summary,
        )

        run_labels = [
            f"{bundle.collection} / {bundle.run_id} ({bundle.question_type or 'unknown'})"
            for bundle in filtered_bundles
        ]
        selected_label = st.selectbox("Inspect run", run_labels)
        selected_bundle = filtered_bundles[run_labels.index(selected_label)]

        st.markdown("**Quick Facts**")
        facts = {
            "Collection": selected_bundle.collection,
            "Question type": selected_bundle.question_type or "n/a",
            "Template": selected_bundle.template_id or "n/a",
            "Metric": selected_bundle.metric_id or "n/a",
            "Geography": selected_bundle.geo_level or "n/a",
            "Rows": selected_bundle.row_count if selected_bundle.row_count is not None else "n/a",
            "Chart saved": "yes" if selected_bundle.has_chart else "no",
            "Needs clarification": "yes" if selected_bundle.needs_clarification else "no",
        }
        st.json(facts)

    with right:
        render_detail_tabs(selected_bundle)


def render_detail_tabs(bundle: RunArtifactBundle) -> None:
    tabs = st.tabs(["Answer", "Clarification", "Chart", "Query Plan", "SQL", "Result", "Files"])

    with tabs[0]:
        st.subheader("Answer Text")
        st.text(bundle.answer_text or "No answer artifact saved.")

    with tabs[1]:
        st.subheader("Clarification")
        if not bundle.needs_clarification:
            st.info("This run completed without a clarification request.")
        else:
            st.warning(bundle.clarification_message or "Clarification requested.")
            if bundle.missing_fields:
                st.write("Missing fields:", ", ".join(bundle.missing_fields))
            if bundle.partial_plan is not None:
                st.code(json.dumps(bundle.partial_plan, indent=2), language="json")

    with tabs[2]:
        st.subheader("Rendered Chart")
        if bundle.has_chart:
            st.image(str(bundle.chart_path), use_container_width=True)
        else:
            st.info("No chart artifact saved for this run.")

    with tabs[3]:
        st.subheader("Query Plan")
        if bundle.query_plan is None:
            st.info("No query plan artifact saved for this run.")
        else:
            st.code(json.dumps(bundle.query_plan, indent=2), language="json")

    with tabs[4]:
        st.subheader("Generated SQL")
        st.code(bundle.sql or "-- no SQL artifact saved --", language="sql")

    with tabs[5]:
        st.subheader("Result Preview")
        if bundle.dataframe is None:
            st.info("No result CSV artifact saved for this run.")
        else:
            st.dataframe(bundle.dataframe)
            csv_bytes = bundle.dataframe.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                data=csv_bytes,
                file_name=f"{bundle.run_id}.csv",
                mime="text/csv",
            )

    with tabs[6]:
        st.subheader("Artifact Paths")
        file_map = {
            "Run directory": str(bundle.run_dir),
            "Chart": str(bundle.chart_path) if bundle.chart_path is not None else "not saved",
            "Query plan": str(bundle.run_dir / "query_plan.json"),
            "Clarification": str(bundle.run_dir / "clarification.json"),
            "SQL": str(bundle.run_dir / "result.sql"),
            "CSV": str(bundle.run_dir / "result.csv"),
            "Answer": str(bundle.run_dir / "answer.txt"),
        }
        st.json(file_map)


def _resolve_root(raw_path: str) -> Path:
    candidate = Path(raw_path.strip())
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    return candidate.resolve()


if __name__ == "__main__":
    main()
