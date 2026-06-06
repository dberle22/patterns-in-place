"""Batch QA runner — executes all prompts in qa_prompt_library.yml and saves one folder per run."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from chatbot.charts.renderer import ChartRenderer
from chatbot.llm.provider import get_llm_provider
from chatbot.orchestrator import Orchestrator, OrchestrationResult
from chatbot.query.catalogs import REPO_ROOT
from chatbot.query.executor import QueryExecutor
from chatbot.scripts.ask import build_qa_run_json, run_question, save_run_artifacts


QA_LIBRARY_PATH = REPO_ROOT / "qa" / "qa_prompt_library.yml"
RUNS_ROOT = REPO_ROOT / "runs" / "qa_batch"

# Categories that should bypass example matching and go through the LLM.
FORCE_PROVIDER_CATEGORIES = {"provider_paraphrase"}


def load_prompt_library() -> list[dict[str, Any]]:
    payload = yaml.safe_load(QA_LIBRARY_PATH.read_text(encoding="utf-8"))
    return payload["cases"]


def build_expected_outcome(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "question_type_expected": case.get("question_type_expected"),
        "metric_expected": case.get("metric_expected"),
        "geo_level_expected": case.get("geo_level_expected"),
        "template_expected": case.get("template_expected"),
        "benchmark_type_expected": case.get("benchmark_type_expected"),
        "category": case.get("category"),
        "notes": case.get("notes"),
    }


def run_case(
    case: dict[str, Any],
    *,
    batch_dir: Path,
    render_chart: bool,
) -> dict[str, Any]:
    qa_case_id = case["qa_case_id"]
    question = case["question"]
    force_provider = case.get("category") in FORCE_PROVIDER_CATEGORIES
    expected_outcome = build_expected_outcome(case)

    print(f"  [{qa_case_id}] {question}")
    case_dir = batch_dir / qa_case_id

    try:
        timed = run_question(question, render_chart=render_chart, force_provider=force_provider)
        save_run_artifacts(
            timed.result,
            case_dir,
            timings_ms=timed.timings_ms,
            force_provider=force_provider,
            qa_case_id=qa_case_id,
            expected_outcome=expected_outcome,
        )
        parse_status = "clarification" if timed.result.needs_clarification else "parsed"
        row_count = None if timed.result.dataframe is None else len(timed.result.dataframe)
        chart_type = None if timed.result.chart_selection is None else timed.result.chart_selection.chart_type
        error = None
    except Exception as exc:
        parse_status = "error"
        row_count = None
        chart_type = None
        error = str(exc)
        # Write a minimal qa_run.json even for errors
        error_run = {
            "run_id": f"{time.strftime('%Y%m%d_%H%M%S')}_{qa_case_id}",
            "run_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "qa_case_id": qa_case_id,
            "question": question,
            "parse_status": "error",
            "error": error,
            "expected_outcome": expected_outcome,
            "review_status": "unreviewed",
        }
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "qa_run.json").write_text(json.dumps(error_run, indent=2), encoding="utf-8")

    status_label = "ERROR" if error else parse_status.upper()
    suffix = f"  rows={row_count} chart={chart_type}" if parse_status == "parsed" else ""
    print(f"         → {status_label}{suffix}")

    return {
        "qa_case_id": qa_case_id,
        "category": case.get("category"),
        "question": question,
        "parse_status": parse_status,
        "row_count": row_count,
        "chart_type": chart_type,
        "error": error,
        "run_dir": str(case_dir),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run all QA prompts from qa_prompt_library.yml and save structured artifacts."
    )
    parser.add_argument(
        "--collection",
        default=None,
        help="Label for this batch run. Defaults to a timestamp.",
    )
    parser.add_argument(
        "--render-chart",
        action="store_true",
        help="Render chart PNGs via the R visual library.",
    )
    parser.add_argument(
        "--cases",
        nargs="+",
        help="Run only specific qa_case_id values (e.g. --cases qa_b_001 qa_r_001).",
    )
    parser.add_argument(
        "--category",
        choices=["golden", "provider_paraphrase", "clarification"],
        help="Run only cases from one category.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    cases = load_prompt_library()

    if args.cases:
        cases = [c for c in cases if c["qa_case_id"] in args.cases]
    if args.category:
        cases = [c for c in cases if c.get("category") == args.category]

    if not cases:
        print("No matching QA cases found.", file=sys.stderr)
        return 1

    batch_id = args.collection or time.strftime("%Y%m%d_%H%M%S")
    batch_dir = RUNS_ROOT / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)

    print(f"QA batch: {batch_id}")
    print(f"Cases: {len(cases)}  |  Render chart: {args.render_chart}")
    print(f"Output: {batch_dir}")
    print()

    results: list[dict[str, Any]] = []
    total_started = time.perf_counter()

    for case in cases:
        result = run_case(case, batch_dir=batch_dir, render_chart=args.render_chart)
        results.append(result)

    elapsed_s = round(time.perf_counter() - total_started, 1)

    parsed = sum(1 for r in results if r["parse_status"] == "parsed")
    clarifications = sum(1 for r in results if r["parse_status"] == "clarification")
    errors = sum(1 for r in results if r["parse_status"] == "error")

    summary = {
        "batch_id": batch_id,
        "run_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_cases": len(results),
        "parsed": parsed,
        "clarification": clarifications,
        "error": errors,
        "elapsed_s": elapsed_s,
        "cases": results,
    }
    summary_path = batch_dir / "batch_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print()
    print(f"Done in {elapsed_s}s  |  parsed={parsed}  clarification={clarifications}  error={errors}")
    print(f"Summary: {summary_path}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
