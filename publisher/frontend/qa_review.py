"""QA batch review app — score and annotate runs produced by qa_batch.py."""

from __future__ import annotations

import json
import time
from pathlib import Path
import sys
from typing import Any

import pandas as pd
import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BATCH_ROOT = REPO_ROOT / "runs" / "qa_batch"

CATEGORY_OPTIONS: dict[str, list[str]] = {
    "intent": ["—", "correct", "wrong_type", "wrong_metric", "wrong_geo", "wrong_benchmark_type", "clarification_appropriate"],
    "plan": ["—", "correct", "incomplete", "wrong_template"],
    "sql": ["—", "correct", "wrong_filter", "wrong_metric_col", "invalid"],
    "result": ["—", "correct", "empty", "wrong_shape", "implausible_values"],
    "chart": ["—", "correct", "wrong_type", "formatting_error", "missing_label"],
    "answer": ["—", "accurate", "vague", "contradicts_data", "wrong_metric_cited", "misses_insight"],
    "clarification": ["—", "appropriate", "missing_context", "unnecessary"],
}

PASS_CATEGORIES = {"correct", "clarification_appropriate", "accurate", "appropriate"}

SCORE_FROM_CATEGORY: dict[str, int | None] = {
    cat: (1 if cat in PASS_CATEGORIES else 0)
    for cats in CATEGORY_OPTIONS.values()
    for cat in cats
    if cat != "—"
}
SCORE_FROM_CATEGORY["—"] = None


# --- Data helpers ---

def list_batches() -> list[str]:
    if not BATCH_ROOT.exists():
        return []
    return sorted(
        d.name for d in BATCH_ROOT.iterdir()
        if d.is_dir() and (d / "batch_summary.json").exists()
    )


def load_batch_cases(batch_id: str) -> list[dict[str, Any]]:
    batch_dir = BATCH_ROOT / batch_id
    cases = []
    for case_dir in sorted(d for d in batch_dir.iterdir() if d.is_dir()):
        qa_run_path = case_dir / "qa_run.json"
        if qa_run_path.exists():
            cases.append(json.loads(qa_run_path.read_text(encoding="utf-8")))
    return cases


def load_review(case_dir: Path) -> dict[str, Any]:
    review_path = case_dir / "qa_review.json"
    if review_path.exists():
        return json.loads(review_path.read_text(encoding="utf-8"))
    return {
        "review_status": "unreviewed",
        "qa_notes": "",
        "intent_category": "—",
        "plan_category": "—",
        "sql_category": "—",
        "result_category": "—",
        "chart_category": "—",
        "answer_category": "—",
        "clarification_category": "—",
    }


def save_review(case_dir: Path, qa_case_id: str, form: dict[str, Any]) -> None:
    scores = {
        f"{layer}_score": SCORE_FROM_CATEGORY.get(form.get(f"{layer}_category", "—"))
        for layer in ["intent", "plan", "sql", "result", "chart", "answer", "clarification"]
    }
    review = {
        "qa_case_id": qa_case_id,
        "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "review_status": form["review_status"],
        "qa_notes": form.get("qa_notes", ""),
        **{f"{layer}_category": form.get(f"{layer}_category", "—") for layer in CATEGORY_OPTIONS},
        "scores": scores,
    }
    (case_dir / "qa_review.json").write_text(json.dumps(review, indent=2), encoding="utf-8")


def suggest_status(form: dict[str, Any]) -> str:
    scores = [
        SCORE_FROM_CATEGORY.get(form.get(f"{layer}_category", "—"))
        for layer in ["intent", "plan", "sql", "result", "chart", "answer", "clarification"]
    ]
    non_null = [s for s in scores if s is not None]
    if not non_null:
        return "unreviewed"
    if all(s == 1 for s in non_null):
        return "pass"
    if any(s == 0 for s in non_null) and any(s == 1 for s in non_null):
        return "partial"
    return "fail"


def build_overview_df(cases: list[dict[str, Any]], reviews: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for case in cases:
        cid = case["qa_case_id"]
        rev = reviews.get(cid, {})
        scores = rev.get("scores", {})

        def cell(key: str) -> str:
            v = scores.get(key)
            return "✅" if v == 1 else "❌" if v == 0 else "—"

        rows.append({
            "case": cid,
            "category": case.get("expected_outcome", {}).get("category", ""),
            "parse": case.get("parse_status", ""),
            "intent": cell("intent_score"),
            "plan": cell("plan_score"),
            "sql": cell("sql_score"),
            "result": cell("result_score"),
            "chart": cell("chart_score"),
            "answer": cell("answer_score"),
            "clarif.": cell("clarification_score"),
            "status": rev.get("review_status", "unreviewed"),
        })
    return pd.DataFrame(rows)


def match_icon(actual: Any, expected: Any) -> str:
    if expected is None:
        return ""
    return "✅" if str(actual) == str(expected) else "❌"


# --- UI sections ---

def render_overview(cases: list[dict[str, Any]], reviews: dict[str, dict[str, Any]]) -> None:
    df = build_overview_df(cases, reviews)
    total = len(df)
    reviewed = sum(1 for r in reviews.values() if r.get("review_status") != "unreviewed")
    passed = sum(1 for r in reviews.values() if r.get("review_status") == "pass")
    failed = sum(1 for r in reviews.values() if r.get("review_status") == "fail")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total cases", total)
    c2.metric("Reviewed", f"{reviewed}/{total}")
    c3.metric("Pass", passed)
    c4.metric("Fail", failed)

    st.dataframe(df, use_container_width=True, hide_index=True)


def render_case_review(
    case: dict[str, Any],
    review: dict[str, Any],
    case_dir: Path,
) -> None:
    qa_case_id = case["qa_case_id"]
    parse_status = case.get("parse_status", "")
    is_clarification = parse_status == "clarification"
    has_chart = bool(case.get("chart_path")) or (case_dir / "chart.png").exists()
    expected = case.get("expected_outcome") or {}

    st.subheader(f"`{qa_case_id}` — {case.get('question', '')}")

    # --- Meta row ---
    col_a, col_b = st.columns(2)
    with col_a:
        st.caption("**Run info**")
        st.write(f"Provider mode: `{case.get('provider_mode', '—')}`")
        st.write(f"Parse status: `{parse_status}`")
        if case.get("matched_example_id"):
            st.write(f"Example match: `{case['matched_example_id']}`")
        st.write(f"Rows: `{case.get('result_row_count', '—')}`  Chart: `{case.get('chart_type', '—')}`")

    with col_b:
        st.caption("**Expected vs actual**")
        plan = case.get("query_plan") or {}
        partial = (case.get("clarification") or {}).get("partial_plan") or {}
        effective = plan or partial
        for field, exp_key in [
            ("question_type", "question_type_expected"),
            ("metric_id", "metric_expected"),
            ("geo_level", "geo_level_expected"),
            ("template_id", "template_expected"),
        ]:
            actual_val = effective.get(field, "—")
            expected_val = expected.get(exp_key)
            icon = match_icon(actual_val, expected_val)
            exp_str = f" (expected: `{expected_val}`)" if expected_val else ""
            st.write(f"{icon} `{field}`: `{actual_val}`{exp_str}")

    st.divider()

    # --- Scoring form ---
    with st.form(key=f"review_form_{qa_case_id}"):
        st.markdown("**Layer scores**")

        col1, col2 = st.columns(2)

        with col1:
            intent_cat = st.selectbox(
                "Intent",
                CATEGORY_OPTIONS["intent"],
                index=_idx("intent", review),
                help="Did the system pick the right question type, metric, geo, and benchmark type?",
            )
            plan_cat = st.selectbox(
                "Plan",
                CATEGORY_OPTIONS["plan"],
                index=_idx("plan", review),
                help="Is the query plan complete and mapped to the right template?",
                disabled=is_clarification,
            )
            sql_cat = st.selectbox(
                "SQL",
                CATEGORY_OPTIONS["sql"],
                index=_idx("sql", review),
                help="Does the SQL match the plan and use correct columns/filters?",
                disabled=is_clarification,
            )
            result_cat = st.selectbox(
                "Result",
                CATEGORY_OPTIONS["result"],
                index=_idx("result", review),
                help="Did the query return the right rows with plausible values?",
                disabled=is_clarification,
            )

        with col2:
            chart_cat = st.selectbox(
                "Chart",
                CATEGORY_OPTIONS["chart"],
                index=_idx("chart", review),
                help="Is the chart type appropriate and correctly formatted?",
                disabled=is_clarification or not has_chart,
            )
            answer_cat = st.selectbox(
                "Answer text",
                CATEGORY_OPTIONS["answer"],
                index=_idx("answer", review),
                help="Does the written answer accurately describe the result?",
                disabled=is_clarification,
            )
            clarif_cat = st.selectbox(
                "Clarification",
                CATEGORY_OPTIONS["clarification"],
                index=_idx("clarification", review),
                help="If clarification was requested, was it appropriate?",
                disabled=not is_clarification,
            )

        st.markdown("**Review**")
        form_snapshot = {
            "intent_category": intent_cat,
            "plan_category": plan_cat,
            "sql_category": sql_cat,
            "result_category": result_cat,
            "chart_category": chart_cat,
            "answer_category": answer_cat,
            "clarification_category": clarif_cat,
        }
        suggested = suggest_status(form_snapshot)
        status_options = ["unreviewed", "pass", "partial", "fail"]
        current_status = review.get("review_status", "unreviewed")
        status_idx = status_options.index(suggested) if current_status == "unreviewed" else status_options.index(current_status)

        review_status = st.selectbox("Review status", status_options, index=status_idx)
        qa_notes = st.text_area("Notes", value=review.get("qa_notes", ""), height=80)

        submitted = st.form_submit_button("Save review", type="primary")
        if submitted:
            save_review(case_dir, qa_case_id, {**form_snapshot, "review_status": review_status, "qa_notes": qa_notes})
            st.success("Saved.")
            st.rerun()

    # --- Artifacts (collapsed by default) ---
    st.divider()
    with st.expander("Answer text"):
        st.write(case.get("answer_text") or "_no answer_")

    with st.expander("Clarification"):
        clarif = case.get("clarification")
        if clarif:
            st.warning(clarif.get("message", ""))
            st.write("Missing fields:", ", ".join(clarif.get("missing_fields") or []))
            if clarif.get("partial_plan"):
                st.code(json.dumps(clarif["partial_plan"], indent=2), language="json")
        else:
            st.info("No clarification for this run.")

    with st.expander("SQL"):
        st.code(case.get("rendered_sql") or "— no SQL —", language="sql")

    with st.expander("Result preview"):
        preview = case.get("result_preview")
        if preview:
            st.dataframe(pd.DataFrame(preview), use_container_width=True)
        else:
            st.info("No result preview.")

    with st.expander("Chart"):
        chart_file = case_dir / "chart.png"
        if chart_file.exists():
            st.image(str(chart_file), use_container_width=True)
        else:
            st.info("No chart rendered for this run.")

    with st.expander("Raw LLM response"):
        raw = case.get("raw_llm_response")
        st.code(raw or "— not captured (example match or heuristic path) —")

    with st.expander("Full qa_run.json"):
        st.code(json.dumps(case, indent=2), language="json")


def _idx(layer: str, review: dict[str, Any]) -> int:
    key = f"{layer}_category"
    current = review.get(key, "—")
    options = CATEGORY_OPTIONS[layer]
    return options.index(current) if current in options else 0


# --- Main ---

def main() -> None:
    st.set_page_config(page_title="QA Review", layout="wide")
    st.title("QA Batch Review")

    batches = list_batches()
    if not batches:
        st.error(f"No batch runs found in {BATCH_ROOT}. Run `qa_batch.py` first.")
        return

    with st.sidebar:
        st.header("Batch")
        selected_batch = st.selectbox("Run", batches, index=len(batches) - 1)
        st.caption(f"`runs/qa_batch/{selected_batch}`")

        category_filter = st.multiselect(
            "Category",
            ["golden", "provider_paraphrase", "clarification"],
            default=["golden", "provider_paraphrase", "clarification"],
        )
        status_filter = st.multiselect(
            "Review status",
            ["unreviewed", "pass", "partial", "fail"],
            default=["unreviewed", "pass", "partial", "fail"],
        )

    batch_dir = BATCH_ROOT / selected_batch
    all_cases = load_batch_cases(selected_batch)
    reviews = {
        case["qa_case_id"]: load_review(batch_dir / case["qa_case_id"])
        for case in all_cases
    }

    filtered_cases = [
        c for c in all_cases
        if (c.get("expected_outcome") or {}).get("category", "") in category_filter
        and reviews.get(c["qa_case_id"], {}).get("review_status", "unreviewed") in status_filter
    ]

    tab_overview, tab_review = st.tabs(["Overview", "Case Review"])

    with tab_overview:
        render_overview(all_cases, reviews)

    with tab_review:
        if not filtered_cases:
            st.info("No cases match the current filters.")
            return

        case_options = {c["qa_case_id"]: c for c in filtered_cases}
        selected_id = st.selectbox(
            "Case",
            list(case_options.keys()),
            format_func=lambda cid: f"{cid}  —  {case_options[cid].get('question', '')[:60]}",
        )
        selected_case = case_options[selected_id]
        selected_review = reviews.get(selected_id, load_review(batch_dir / selected_id))

        render_case_review(selected_case, selected_review, batch_dir / selected_id)


if __name__ == "__main__":
    main()
