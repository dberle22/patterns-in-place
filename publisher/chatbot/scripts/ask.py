"""CLI wrapper for exercising the parser and orchestrator from the terminal."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import sys
import time
from typing import Any

from chatbot.charts.renderer import ChartRenderer
from chatbot.intent.parser import ParseResult
from chatbot.llm.provider import get_llm_provider
from chatbot.orchestrator import Orchestrator, OrchestrationResult
from chatbot.query.catalogs import REPO_ROOT
from chatbot.query.executor import QueryExecutor


MODEL_TEST_LOG_PATH = REPO_ROOT / "model_test.md"


@dataclass
class TimedParseResult:
    result: ParseResult
    timings_ms: dict[str, float]


@dataclass
class TimedOrchestrationResult:
    result: OrchestrationResult
    timings_ms: dict[str, float]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ask the analytics chatbot a question from the command line."
    )
    parser.add_argument("question", help="Natural-language analytical question to evaluate.")
    parser.add_argument(
        "--parser-only",
        action="store_true",
        help="Only run intent parsing and print the structured plan or clarification.",
    )
    parser.add_argument(
        "--render-chart",
        action="store_true",
        help="Render a chart PNG through the R visual library during full orchestration.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of a formatted summary.",
    )
    parser.add_argument(
        "--force-provider",
        action="store_true",
        help="Bypass exact-example matching and heuristic parsing so the request must go through the configured LLM provider.",
    )
    parser.add_argument(
        "--show-timings",
        action="store_true",
        help="Print per-stage timings in human-readable output.",
    )
    parser.add_argument(
        "--log-model-test",
        action="store_true",
        help="Append a test log entry to model_test.md after the run finishes.",
    )
    parser.add_argument(
        "--output-dir",
        help="Relative directory inside the repo where run artifacts should be saved.",
    )
    parser.add_argument(
        "--qa-case-id",
        dest="qa_case_id",
        help="QA case ID from qa_prompt_library.yml to tag this run.",
    )
    return parser


def build_orchestrator(*, render_chart: bool) -> Orchestrator:
    try:
        provider = get_llm_provider()
    except (ImportError, ValueError):
        provider = None
    executor = QueryExecutor()
    renderer = ChartRenderer() if render_chart else None
    return Orchestrator(provider=provider, executor=executor, renderer=renderer)


def parse_only(question: str, *, force_provider: bool = False) -> TimedParseResult:
    orchestrator = build_orchestrator(render_chart=False)
    started = time.perf_counter()
    result = orchestrator.parser.parse(question, force_provider=force_provider)
    timings_ms = {"parse": round((time.perf_counter() - started) * 1000, 1)}
    return TimedParseResult(result=result, timings_ms=timings_ms)


def run_question(
    question: str,
    *,
    render_chart: bool,
    force_provider: bool = False,
) -> TimedOrchestrationResult:
    orchestrator = build_orchestrator(render_chart=render_chart)
    timings_ms: dict[str, float] = {}

    started = time.perf_counter()
    parse_result = orchestrator.parser.parse(question, force_provider=force_provider)
    timings_ms["parse"] = round((time.perf_counter() - started) * 1000, 1)
    result = OrchestrationResult(question=question, parse_result=parse_result)
    if parse_result.needs_clarification:
        return TimedOrchestrationResult(result=result, timings_ms=timings_ms)

    assert parse_result.plan is not None
    result.query_plan = parse_result.plan

    started = time.perf_counter()
    result.planned_query = orchestrator.planner.build(parse_result.plan)
    timings_ms["plan"] = round((time.perf_counter() - started) * 1000, 1)

    started = time.perf_counter()
    result.rendered_query = orchestrator.generator.render(result.planned_query.plan)
    timings_ms["generate_sql"] = round((time.perf_counter() - started) * 1000, 1)

    started = time.perf_counter()
    result.validation = orchestrator.validator.validate(result.rendered_query)
    result.validation.raise_for_errors()
    timings_ms["validate_sql"] = round((time.perf_counter() - started) * 1000, 1)

    if orchestrator.executor is not None:
        started = time.perf_counter()
        result.dataframe = orchestrator.executor.execute(result.rendered_query)
        timings_ms["execute_sql"] = round((time.perf_counter() - started) * 1000, 1)

        started = time.perf_counter()
        result.result_profile = orchestrator.profiler.profile(result.dataframe)
        timings_ms["profile_result"] = round((time.perf_counter() - started) * 1000, 1)

        started = time.perf_counter()
        result.chart_selection = orchestrator.selector.select(
            result.query_plan.question_type,
            result.result_profile,
        )
        timings_ms["select_chart"] = round((time.perf_counter() - started) * 1000, 1)

        if orchestrator.renderer is not None:
            started = time.perf_counter()
            result.rendered_chart = orchestrator.renderer.render(
                result.dataframe,
                selection=result.chart_selection,
                query_plan=result.query_plan,
                profile=result.result_profile,
                sql=result.rendered_query.sql,
            )
            timings_ms["render_chart"] = round((time.perf_counter() - started) * 1000, 1)

        started = time.perf_counter()
        result.response = orchestrator.assembler.assemble(
            question=question,
            query_plan=result.query_plan,
            dataframe=result.dataframe,
            profile=result.result_profile,
            selection=result.chart_selection,
        )
        timings_ms["assemble_response"] = round((time.perf_counter() - started) * 1000, 1)

    timings_ms["total"] = round(sum(timings_ms.values()), 1)
    return TimedOrchestrationResult(result=result, timings_ms=timings_ms)


def serialize_parse_result(result: ParseResult, *, timings_ms: dict[str, float] | None = None) -> dict[str, Any]:
    return {
        "needs_clarification": result.needs_clarification,
        "matched_example_id": result.matched_example_id,
        "provider_used": result.provider_used,
        "plan": None if result.plan is None else result.plan.model_dump(exclude_none=True),
        "clarification": None
        if result.clarification is None
        else result.clarification.model_dump(),
        "timings_ms": timings_ms,
    }


def serialize_orchestration_result(
    result: OrchestrationResult,
    *,
    timings_ms: dict[str, float] | None = None,
) -> dict[str, Any]:
    return {
        "needs_clarification": result.needs_clarification,
        "provider_used": result.parse_result.provider_used,
        "matched_example_id": result.parse_result.matched_example_id,
        "query_plan": None
        if result.query_plan is None
        else result.query_plan.model_dump(exclude_none=True),
        "sql": result.sql,
        "row_count": None if result.dataframe is None else len(result.dataframe),
        "chart_type": None if result.chart_selection is None else result.chart_selection.chart_type,
        "chart_path": result.chart_path,
        "answer_text": result.answer_text,
        "clarification": None
        if result.clarification is None
        else result.clarification.model_dump(),
        "timings_ms": timings_ms,
    }


def resolve_output_dir(path_arg: str) -> Path:
    candidate = (REPO_ROOT / path_arg).resolve()
    repo_root = REPO_ROOT.resolve()
    if repo_root not in (candidate, *candidate.parents):
        raise ValueError("--output-dir must resolve to a location inside the repository")
    return candidate


def _derive_provider_mode(result: OrchestrationResult, *, force_provider: bool) -> str:
    pr = result.parse_result
    if pr.matched_example_id is not None:
        return "example_match"
    if pr.provider_used is not None:
        return "llm_forced" if force_provider else "llm_optional"
    return "heuristic"


def build_qa_run_json(
    result: OrchestrationResult,
    *,
    timings_ms: dict[str, float],
    force_provider: bool = False,
    qa_case_id: str | None = None,
    expected_outcome: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the canonical qa_run.json record for one pipeline run."""
    pr = result.parse_result
    if result.needs_clarification:
        parse_status = "clarification"
    elif result.query_plan is not None:
        parse_status = "parsed"
    else:
        parse_status = "error"

    result_preview: list[Any] | None = None
    if result.dataframe is not None and not result.dataframe.empty:
        preview_df = result.dataframe
        if result.result_profile is not None and result.result_profile.has_time_series:
            sort_cols = [c for c in ("year", "period", "geo_name") if c in preview_df.columns]
            if sort_cols:
                preview_df = preview_df.sort_values(list(sort_cols))
        result_preview = preview_df.head(5).to_dict(orient="records")

    return {
        "run_id": f"{time.strftime('%Y%m%d_%H%M%S')}_{qa_case_id or 'adhoc'}",
        "run_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "qa_case_id": qa_case_id,
        "question": result.question,
        "provider": pr.provider_used or "none",
        "provider_mode": _derive_provider_mode(result, force_provider=force_provider),
        "matched_example_id": pr.matched_example_id,
        "force_provider": force_provider,
        "parse_status": parse_status,
        "query_plan": None if result.query_plan is None else result.query_plan.model_dump(exclude_none=True),
        "clarification": None if result.clarification is None else result.clarification.model_dump(),
        "rendered_sql": result.sql,
        "result_row_count": None if result.dataframe is None else len(result.dataframe),
        "result_preview": result_preview,
        "result_profile": None if result.result_profile is None else result.result_profile.to_dict(),
        "chart_type": None if result.chart_selection is None else result.chart_selection.chart_type,
        "chart_path": result.chart_path,
        "answer_text": result.answer_text,
        "raw_llm_response": pr.raw_llm_response,
        "timings_ms": timings_ms,
        "expected_outcome": expected_outcome,
        "review_status": "unreviewed",
        "qa_notes": None,
        "scores": {
            "intent_score": None,
            "plan_score": None,
            "sql_score": None,
            "result_score": None,
            "chart_score": None,
            "answer_score": None,
            "clarification_score": None,
        },
    }


def save_run_artifacts(
    result: OrchestrationResult,
    output_dir: Path,
    *,
    timings_ms: dict[str, float] | None = None,
    force_provider: bool = False,
    qa_case_id: str | None = None,
    expected_outcome: dict[str, Any] | None = None,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    saved: dict[str, str] = {}

    qa_run = build_qa_run_json(
        result,
        timings_ms=timings_ms or {},
        force_provider=force_provider,
        qa_case_id=qa_case_id,
        expected_outcome=expected_outcome,
    )
    qa_run_path = output_dir / "qa_run.json"
    qa_run_path.write_text(json.dumps(qa_run, indent=2), encoding="utf-8")
    saved["qa_run_path"] = str(qa_run_path)

    if result.clarification is not None:
        clarification_path = output_dir / "clarification.json"
        clarification_path.write_text(
            json.dumps(result.clarification.model_dump(), indent=2), encoding="utf-8"
        )
        saved["clarification_path"] = str(clarification_path)
    else:
        clarification_path = output_dir / "clarification.json"
        if clarification_path.exists():
            clarification_path.unlink()

    if result.query_plan is not None:
        plan_path = output_dir / "query_plan.json"
        plan_path.write_text(
            json.dumps(result.query_plan.model_dump(exclude_none=True), indent=2),
            encoding="utf-8",
        )
        saved["query_plan_path"] = str(plan_path)

    if result.rendered_query is not None:
        sql_path = output_dir / "result.sql"
        sql_path.write_text(result.sql or "", encoding="utf-8")
        saved["sql_path"] = str(sql_path)

    if result.dataframe is not None:
        csv_path = output_dir / "result.csv"
        result.dataframe.to_csv(csv_path, index=False)
        saved["csv_path"] = str(csv_path)

    if result.response is not None:
        answer_path = output_dir / "answer.txt"
        answer_path.write_text(result.answer_text or "", encoding="utf-8")
        saved["answer_path"] = str(answer_path)

    if result.rendered_chart is not None and result.chart_path is not None:
        chart_dest = output_dir / "chart.png"
        shutil.copyfile(result.chart_path, chart_dest)
        saved["chart_path"] = str(chart_dest)

    return saved


def print_parse_summary(result: ParseResult, *, timings_ms: dict[str, float] | None = None) -> None:
    if result.needs_clarification:
        assert result.clarification is not None
        print("Clarification needed")
        print(result.clarification.message)
        print(f"Missing fields: {', '.join(result.clarification.missing_fields)}")
        if timings_ms:
            print(f"Timings (ms): {json.dumps(timings_ms, sort_keys=True)}")
        return

    assert result.plan is not None
    print("Structured plan")
    print(json.dumps(result.plan.model_dump(exclude_none=True), indent=2))
    if result.provider_used:
        print(f"Provider: {result.provider_used}")
    if result.matched_example_id:
        print(f"Matched example: {result.matched_example_id}")
    if timings_ms:
        print(f"Timings (ms): {json.dumps(timings_ms, sort_keys=True)}")


def print_run_summary(result: OrchestrationResult, *, timings_ms: dict[str, float] | None = None) -> None:
    if result.needs_clarification:
        assert result.clarification is not None
        print("Clarification needed")
        print(result.clarification.message)
        print(f"Missing fields: {', '.join(result.clarification.missing_fields)}")
        if timings_ms:
            print(f"Timings (ms): {json.dumps(timings_ms, sort_keys=True)}")
        return

    print("Answer")
    print(result.answer_text or "(no answer text)")
    print("")
    print("Summary")
    print(f"Question type: {result.query_plan.question_type if result.query_plan else 'unknown'}")
    print(f"Rows: {0 if result.dataframe is None else len(result.dataframe)}")
    print(f"Chart type: {result.chart_selection.chart_type if result.chart_selection else 'none'}")
    print(f"Chart path: {result.chart_path or 'not rendered'}")
    print("")
    print("SQL")
    print(result.sql or "(no sql)")
    if timings_ms:
        print("")
        print(f"Timings (ms): {json.dumps(timings_ms, sort_keys=True)}")


def append_model_test_log(
    *,
    question: str,
    command: str,
    parser_only: bool,
    timed_parse_result: TimedParseResult | None = None,
    timed_run_result: TimedOrchestrationResult | None = None,
    path: Path | None = None,
) -> None:
    if timed_parse_result is None and timed_run_result is None:
        raise ValueError("A parse result or orchestration result is required to log a test run.")
    resolved_path = MODEL_TEST_LOG_PATH if path is None else path

    if timed_parse_result is not None:
        result = timed_parse_result.result
        timings_ms = timed_parse_result.timings_ms
        matched_example_id = result.matched_example_id
        provider_used = result.provider_used
        chart_type = None
        chart_path = None
        outcome = "clarification" if result.needs_clarification else "parsed"
        notes = (
            result.clarification.message
            if result.needs_clarification and result.clarification is not None
            else json.dumps(result.plan.model_dump(exclude_none=True), sort_keys=True)
            if result.plan is not None
            else "No structured plan returned."
        )
    else:
        assert timed_run_result is not None
        result = timed_run_result.result
        timings_ms = timed_run_result.timings_ms
        matched_example_id = result.parse_result.matched_example_id
        provider_used = result.parse_result.provider_used
        chart_type = None if result.chart_selection is None else result.chart_selection.chart_type
        chart_path = result.chart_path
        outcome = "clarification" if result.needs_clarification else "pass"
        notes = (
            result.clarification.message
            if result.needs_clarification and result.clarification is not None
            else result.answer_text or "No answer text returned."
        )

    mode = "parser-only" if parser_only else "full-pipeline"
    entry = (
        "\n"
        "### Run\n"
        f"- Date: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        f"- Command: `{command}`\n"
        f"- Mode: {mode}\n"
        f"- Question: {question}\n"
        f"- matched_example_id: {matched_example_id}\n"
        f"- provider_used: {provider_used}\n"
        f"- chart_type: {chart_type}\n"
        f"- chart_path: {chart_path}\n"
        f"- timings_ms: `{json.dumps(timings_ms, sort_keys=True)}`\n"
        f"- Result: {outcome}\n"
        f"- Notes: {notes}\n"
    )
    with resolved_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = " ".join(
        ["python -m app.scripts.ask"]
        + [json.dumps(arg) if " " in arg else arg for arg in (argv or sys.argv[1:])]
    )

    try:
        if args.parser_only:
            timed_result = parse_only(
                args.question,
                force_provider=args.force_provider,
            )
            payload = serialize_parse_result(
                timed_result.result,
                timings_ms=timed_result.timings_ms,
            )
            if args.json:
                print(json.dumps(payload, indent=2))
            else:
                print_parse_summary(
                    timed_result.result,
                    timings_ms=timed_result.timings_ms if args.show_timings else None,
                )
            if args.log_model_test:
                append_model_test_log(
                    question=args.question,
                    command=command,
                    parser_only=True,
                    timed_parse_result=timed_result,
                )
            return 0

        timed_result = run_question(
            args.question,
            render_chart=args.render_chart,
            force_provider=args.force_provider,
        )
        artifact_paths = None
        if args.output_dir:
            output_dir = resolve_output_dir(args.output_dir)
            artifact_paths = save_run_artifacts(
                timed_result.result,
                output_dir,
                timings_ms=timed_result.timings_ms,
                force_provider=args.force_provider,
                qa_case_id=getattr(args, "qa_case_id", None),
            )
        payload = serialize_orchestration_result(
            timed_result.result,
            timings_ms=timed_result.timings_ms,
        )
        if artifact_paths is not None:
            payload["saved_artifacts"] = artifact_paths
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print_run_summary(
                timed_result.result,
                timings_ms=timed_result.timings_ms if args.show_timings else None,
            )
            if artifact_paths is not None:
                print("")
                print(f"Saved artifacts: {output_dir}")
        if args.log_model_test:
            append_model_test_log(
                question=args.question,
                command=command,
                parser_only=False,
                timed_run_result=timed_result,
            )
        return 0
    except Exception as exc:  # pragma: no cover - exercised via CLI behavior
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
