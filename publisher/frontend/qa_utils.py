"""Helpers for loading saved QA run artifacts for Streamlit review."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import pandas as pd

from chatbot.query.catalogs import REPO_ROOT


@dataclass
class RunArtifactBundle:
    """Structured view of one saved QA run directory."""

    run_id: str
    run_dir: Path
    collection: str
    query_plan: dict[str, Any] | None
    clarification: dict[str, Any] | None
    sql: str | None
    answer_text: str | None
    dataframe: pd.DataFrame | None
    chart_path: Path | None

    @property
    def question_type(self) -> str | None:
        payload = self.query_plan or self.partial_plan
        if payload is None:
            return None
        return payload.get("question_type")

    @property
    def template_id(self) -> str | None:
        payload = self.query_plan or self.partial_plan
        if payload is None:
            return None
        return payload.get("template_id")

    @property
    def metric_id(self) -> str | None:
        payload = self.query_plan or self.partial_plan
        if payload is None:
            return None
        return payload.get("metric_id") or payload.get("base_metric_id")

    @property
    def geo_level(self) -> str | None:
        payload = self.query_plan or self.partial_plan
        if payload is None:
            return None
        return payload.get("geo_level") or payload.get("target_geo_level")

    @property
    def row_count(self) -> int | None:
        if self.dataframe is None:
            return None
        return len(self.dataframe)

    @property
    def has_chart(self) -> bool:
        return self.chart_path is not None and self.chart_path.exists()

    @property
    def needs_clarification(self) -> bool:
        return self.clarification is not None

    @property
    def missing_fields(self) -> list[str]:
        if self.clarification is None:
            return []
        return list(self.clarification.get("missing_fields") or [])

    @property
    def clarification_message(self) -> str | None:
        if self.clarification is None:
            return None
        return self.clarification.get("message")

    @property
    def partial_plan(self) -> dict[str, Any] | None:
        if self.clarification is None:
            return None
        return self.clarification.get("partial_plan")

    def summary_row(self) -> dict[str, Any]:
        return {
            "collection": self.collection,
            "run_id": self.run_id,
            "question_type": self.question_type,
            "template_id": self.template_id,
            "metric_id": self.metric_id,
            "geo_level": self.geo_level,
            "row_count": self.row_count,
            "has_chart": self.has_chart,
            "needs_clarification": self.needs_clarification,
        }


def default_run_roots() -> list[Path]:
    """Return the default saved-run roots used during local QA."""

    return [
        REPO_ROOT / "publisher" / "output",
        REPO_ROOT / "runs" / "provider_qa",
        REPO_ROOT / "runs" / "phase45",
    ]


def load_run_collections(root_paths: list[Path] | None = None) -> list[RunArtifactBundle]:
    """Load every saved run directory from the requested roots."""

    bundles: list[RunArtifactBundle] = []
    for root in root_paths or default_run_roots():
        if not root.exists():
            continue
        for run_dir in sorted(path for path in root.iterdir() if path.is_dir()):
            bundle = load_run_bundle(run_dir, collection=root.name)
            if bundle is not None:
                bundles.append(bundle)
    return bundles


def load_run_bundle(run_dir: Path, *, collection: str | None = None) -> RunArtifactBundle | None:
    """Load one run directory if it contains the expected artifact set."""

    query_plan_path = run_dir / "query_plan.json"
    result_csv_path = run_dir / "result.csv"
    result_sql_path = run_dir / "result.sql"
    answer_path = run_dir / "answer.txt"
    chart_path = run_dir / "chart.png"
    clarification_path = run_dir / "clarification.json"

    if not any(
        path.exists()
        for path in [query_plan_path, result_csv_path, result_sql_path, answer_path, clarification_path]
    ):
        return None

    query_plan = _read_json(query_plan_path)
    clarification = _read_clarification(clarification_path)
    sql = _read_text(result_sql_path)
    answer_text = _read_text(answer_path)
    dataframe = _read_csv(result_csv_path)

    return RunArtifactBundle(
        run_id=run_dir.name,
        run_dir=run_dir,
        collection=collection or run_dir.parent.name,
        query_plan=query_plan,
        clarification=clarification,
        sql=sql,
        answer_text=answer_text,
        dataframe=dataframe,
        chart_path=chart_path if chart_path.exists() else None,
    )


def build_summary_frame(bundles: list[RunArtifactBundle]) -> pd.DataFrame:
    """Build a compact table used by the QA UI."""

    if not bundles:
        return pd.DataFrame(
            columns=[
                "collection",
                "run_id",
                "question_type",
                "template_id",
                "metric_id",
                "geo_level",
                "row_count",
                "has_chart",
                "needs_clarification",
            ]
        )
    return pd.DataFrame([bundle.summary_row() for bundle in bundles])


def _read_clarification(path: Path) -> dict[str, Any] | None:
    payload = _read_json(path)
    if payload is None:
        return None
    return payload.get("clarification")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _read_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)
