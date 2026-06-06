"""CLI entrypoint for the daily data publisher."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys

from publisher.packager import verify_output_folder
from publisher.queue_manager import QueueEntry, QueueManager


PUBLISHER_DIR = Path(__file__).resolve().parent
OUTPUT_ROOT = PUBLISHER_DIR / "output"
STEP_CHOICES = ("parse", "sql", "chart", "summarize")
SUMMARIZE_MODE_CHOICES = ("template", "llm")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", dest="question_id", help="Queue question ID to act on.")
    parser.add_argument(
        "--next",
        action="store_true",
        help="Select the next ready queue item. If used with --step, run that step on it.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Print counts by queue status and warn when ready entries are low.",
    )
    parser.add_argument(
        "--step",
        choices=STEP_CHOICES,
        help="Run a single pipeline step for the selected queue item.",
    )
    parser.add_argument(
        "--note",
        help="Append a timestamped reviewer note to publisher/output/{id}/step_notes.md.",
    )
    parser.add_argument(
        "--summarize-mode",
        choices=SUMMARIZE_MODE_CHOICES,
        default="template",
        help="Reserved for summarizer mode switching.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    queue_manager = QueueManager()

    if args.status:
        print_status(queue_manager)
        return 0

    try:
        entry = resolve_entry(queue_manager, question_id=args.question_id, use_next=args.next)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.note:
        note_path = append_note(entry.id, args.note)
        print(f"Appended note for {entry.id} at {note_path}")
        return 0

    if args.step:
        try:
            run_step(entry, step=args.step, summarize_mode=args.summarize_mode, queue_manager=queue_manager)
        except NotImplementedError as exc:
            print(str(exc), file=sys.stderr)
            return 3
        except Exception as exc:  # pragma: no cover - CLI guardrail
            print(f"{args.step} failed for {entry.id}: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.next and entry is not None:
        print(f"Next ready question: {entry.id} | {entry.template_id} | {entry.question}")
        return 0

    print("Choose one action: --status, --note, --step, or --next.", file=sys.stderr)
    return 2


def resolve_entry(
    queue_manager: QueueManager,
    *,
    question_id: str | None,
    use_next: bool,
) -> QueueEntry | None:
    if question_id and use_next:
        raise ValueError("Use either --id or --next, not both.")
    if question_id:
        return queue_manager.get_entry(question_id)
    if use_next:
        entry = queue_manager.next_ready_entry()
        if entry is None:
            raise ValueError("No ready queue entries found.")
        return entry
    return None


def print_status(queue_manager: QueueManager) -> None:
    counts = queue_manager.status_counts()
    total = sum(counts.values())
    print("Publisher Queue Status")
    print("======================")
    for status, count in counts.items():
        print(f"{status:>8}: {count}")
    print(f"{'total':>8}: {total}")
    if counts.get("ready", 0) < 5:
        print("warning: ready queue has fewer than 5 entries")


def run_step(
    entry: QueueEntry,
    *,
    step: str,
    summarize_mode: str,
    queue_manager: QueueManager,
) -> None:
    if step == "parse":
        run_parse_step(entry)
    elif step == "sql":
        run_sql_step(entry)
        queue_manager.update_status(entry.id, "ran")
    elif step == "chart":
        run_chart_step(entry)
    elif step == "summarize":
        raise NotImplementedError(
            "Summarize step is scheduled for Sprint 3. Template and llm modes are not wired yet."
        )
    else:  # pragma: no cover - argparse enforces choices
        raise ValueError(f"Unsupported step: {step}")

    check = verify_output_folder(OUTPUT_ROOT / entry.id, step)
    completeness = "complete" if check.is_complete else "incomplete"
    print(f"{entry.id} {step} finished; artifacts are {completeness}.")
    if check.missing_files:
        print("Missing artifacts:")
        for name in check.missing_files:
            print(f"- {name}")


def run_parse_step(entry: QueueEntry) -> Path:
    from chatbot.intent.parser import IntentParser
    from chatbot.llm.provider import get_llm_provider

    try:
        provider = get_llm_provider()
    except (ImportError, ValueError):
        provider = None

    parser = IntentParser(provider=provider)
    parse_result = parser.parse(entry.question)
    if parse_result.needs_clarification or parse_result.plan is None:
        raise ValueError(
            f"Parser needs clarification for {entry.id}: {parse_result.clarification.message if parse_result.clarification else 'unknown issue'}"
        )
    output_dir = ensure_output_dir(entry.id)
    output_path = output_dir / "query_plan.json"
    output_path.write_text(
        json.dumps(parse_result.plan.model_dump(exclude_none=True), indent=2),
        encoding="utf-8",
    )
    return output_path


def run_sql_step(entry: QueueEntry) -> None:
    from chatbot.charts.profiler import ResultProfiler
    from chatbot.charts.selector import ChartSelector
    from chatbot.query.executor import QueryExecutor
    from chatbot.query.generator import QueryGenerator
    from chatbot.query.planner import QueryPlanner
    from chatbot.query.validator import QueryValidator
    from chatbot.response.assembler import ResponseAssembler

    output_dir = ensure_output_dir(entry.id)
    query_plan = load_query_plan(output_dir / "query_plan.json")

    planner = QueryPlanner()
    generator = QueryGenerator()
    validator = QueryValidator()
    executor = QueryExecutor()
    assembler = ResponseAssembler()

    planned = planner.build(query_plan)
    rendered = generator.render(planned.plan)
    validation = validator.validate(rendered)
    validation.raise_for_errors()
    dataframe = executor.execute(rendered)
    profile = ResultProfiler().profile(dataframe)
    selection = ChartSelector().select(query_plan.question_type, profile)
    response = assembler.assemble(
        question=entry.question,
        query_plan=query_plan,
        dataframe=dataframe,
        profile=profile,
        selection=selection,
    )

    (output_dir / "result.sql").write_text(rendered.sql + "\n", encoding="utf-8")
    dataframe.to_csv(output_dir / "result.csv", index=False)
    (output_dir / "answer.txt").write_text(response.answer_text + "\n", encoding="utf-8")


def run_chart_step(entry: QueueEntry) -> Path:
    import pandas as pd

    from chatbot.charts.profiler import ResultProfiler
    from chatbot.charts.renderer import ChartRenderer
    from chatbot.charts.selector import ChartSelector

    output_dir = ensure_output_dir(entry.id)
    query_plan = load_query_plan(output_dir / "query_plan.json")
    dataframe = pd.read_csv(output_dir / "result.csv")

    profiler = ResultProfiler()
    profile = profiler.profile(dataframe)
    selection = ChartSelector().select(query_plan.question_type, profile)
    rendered = ChartRenderer().render(
        dataframe,
        selection=selection,
        query_plan=query_plan,
        profile=profile,
        sql=(output_dir / "result.sql").read_text(encoding="utf-8"),
    )

    chart_path = output_dir / "chart.png"
    shutil.copyfile(rendered.output_path, chart_path)
    return chart_path


def append_note(question_id: str, note: str) -> Path:
    output_dir = ensure_output_dir(question_id)
    note_path = output_dir / "step_notes.md"
    timestamp = datetime.now().replace(microsecond=0).isoformat(sep=" ")
    with note_path.open("a", encoding="utf-8") as handle:
        if handle.tell() == 0:
            handle.write(f"# Step Notes for {question_id}\n\n")
        handle.write(f"- [{timestamp}] {note}\n")
    return note_path


def ensure_output_dir(question_id: str) -> Path:
    output_dir = OUTPUT_ROOT / question_id
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def load_query_plan(path: Path):
    from chatbot.intent.parser import QueryPlan

    payload = json.loads(path.read_text(encoding="utf-8"))
    return QueryPlan.model_validate(payload)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
