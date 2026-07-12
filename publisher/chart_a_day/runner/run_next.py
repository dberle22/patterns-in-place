"""CLI entrypoint for the Chart-A-Day queue workflow."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys

from chart_a_day.runner.queue_manager import QueueEntry, QueueManager


RUNNER_DIR = Path(__file__).resolve().parent
OUTPUT_ROOT = RUNNER_DIR.parent / "output"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", dest="question_id", help="Queue question ID to act on.")
    parser.add_argument(
        "--next",
        action="store_true",
        help="Select the next ready queue item.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Print counts by queue status and warn when ready entries are low.",
    )
    parser.add_argument(
        "--note",
        help="Append a timestamped reviewer note to chart_a_day/output/{id}/step_notes.md.",
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
        if entry is None:
            print("Use --id or --next with --note.", file=sys.stderr)
            return 2
        note_path = append_note(entry.id, args.note)
        print(f"Appended note for {entry.id} at {note_path}")
        return 0

    if args.next and entry is not None:
        print(f"Next ready question: {entry.id} | {entry.template_id} | {entry.question}")
        return 0

    print("Choose one action: --status, --note, or --next.", file=sys.stderr)
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
    print("Chart-A-Day Queue Status")
    print("========================")
    for status, count in counts.items():
        print(f"{status:>8}: {count}")
    print(f"{'total':>8}: {total}")
    if counts.get("ready", 0) < 5:
        print("warning: ready queue has fewer than 5 entries")


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


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
