"""Queue helpers for the daily data publisher."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


VALID_STATUSES = ("ready", "ran", "reviewed", "posted")
DEFAULT_QUEUE_PATH = Path(__file__).resolve().parent / "question_queue.yaml"


@dataclass
class QueueEntry:
    """Structured view of one publisher queue row."""

    id: str
    question: str
    template_id: str
    geo_level: str
    status: str
    platform: str
    notes: str | None = None
    scheduled: str | None = None
    ran_at: str | None = None
    posted_at: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "QueueEntry":
        return cls(**payload)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "template_id": self.template_id,
            "geo_level": self.geo_level,
            "status": self.status,
            "platform": self.platform,
            "notes": self.notes,
            "scheduled": self.scheduled,
            "ran_at": self.ran_at,
            "posted_at": self.posted_at,
        }


class QueueManager:
    """Load, inspect, and update the publisher backlog in place."""

    def __init__(self, queue_path: Path | None = None) -> None:
        self.queue_path = queue_path or DEFAULT_QUEUE_PATH

    def load_queue(self) -> list[QueueEntry]:
        if not self.queue_path.exists():
            raise FileNotFoundError(f"Queue file not found: {self.queue_path}")
        payload = yaml.safe_load(self.queue_path.read_text(encoding="utf-8")) or []
        return [QueueEntry.from_dict(entry) for entry in payload]

    def save_queue(self, entries: list[QueueEntry]) -> None:
        serializable = [entry.to_dict() for entry in entries]
        self.queue_path.write_text(
            yaml.safe_dump(serializable, sort_keys=False, allow_unicode=False),
            encoding="utf-8",
        )

    def get_entry(self, question_id: str) -> QueueEntry:
        for entry in self.load_queue():
            if entry.id == question_id:
                return entry
        raise KeyError(f"Unknown question id: {question_id}")

    def list_by_status(self, status: str) -> list[QueueEntry]:
        self._validate_status(status)
        return [entry for entry in self.load_queue() if entry.status == status]

    def status_counts(self) -> dict[str, int]:
        counts = {status: 0 for status in VALID_STATUSES}
        for entry in self.load_queue():
            counts.setdefault(entry.status, 0)
            counts[entry.status] += 1
        return counts

    def next_ready_entry(self) -> QueueEntry | None:
        for entry in self.load_queue():
            if entry.status == "ready":
                return entry
        return None

    def update_status(self, question_id: str, status: str) -> QueueEntry:
        self._validate_status(status)
        entries = self.load_queue()
        updated: QueueEntry | None = None
        for entry in entries:
            if entry.id != question_id:
                continue
            entry.status = status
            timestamp = self._now()
            if status == "ran":
                entry.ran_at = timestamp
            if status == "posted":
                entry.posted_at = timestamp
            updated = entry
            break
        if updated is None:
            raise KeyError(f"Unknown question id: {question_id}")
        self.save_queue(entries)
        return updated

    def update_fields(self, question_id: str, **fields: Any) -> QueueEntry:
        entries = self.load_queue()
        updated: QueueEntry | None = None
        for entry in entries:
            if entry.id != question_id:
                continue
            for key, value in fields.items():
                if not hasattr(entry, key):
                    raise KeyError(f"Unknown queue field: {key}")
                setattr(entry, key, value)
            updated = entry
            break
        if updated is None:
            raise KeyError(f"Unknown question id: {question_id}")
        self.save_queue(entries)
        return updated

    def _validate_status(self, status: str) -> None:
        if status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status {status!r}. Expected one of: {', '.join(VALID_STATUSES)}"
            )

    def _now(self) -> str:
        return datetime.now().replace(microsecond=0).isoformat(sep=" ")
