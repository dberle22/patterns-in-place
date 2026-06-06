"""Normalize parsed intent plans into generator-ready query plan dictionaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from chatbot.intent.parser import QueryPlan
from chatbot.query.catalogs import load_semantic_catalogs


@dataclass
class PlannedQuery:
    """Generator-ready plan plus a few planning notes for debugging."""

    plan: dict[str, Any]
    notes: list[str]


class QueryPlanner:
    """Fill deterministic defaults after intent parsing."""

    def __init__(self) -> None:
        self.catalogs = load_semantic_catalogs()

    def build(self, query_plan: QueryPlan | dict[str, Any]) -> PlannedQuery:
        parsed_plan = (
            query_plan if isinstance(query_plan, QueryPlan) else QueryPlan.model_validate(query_plan)
        )
        payload = parsed_plan.model_dump(by_alias=False, exclude_none=True)
        notes: list[str] = []

        if "source_table" not in payload:
            metric_id = payload.get("metric_id") or payload.get("base_metric_id")
            if metric_id:
                payload["source_table"] = self.catalogs["metrics"][metric_id]["source_table"]
                notes.append("Filled source_table from metric catalog.")

        template_id = payload.get("template_id") or parsed_plan.template_id
        payload["template_id"] = template_id

        if template_id == "growth":
            payload.setdefault("sort_direction", "desc")
            payload.setdefault("limit", 10)
        elif template_id == "ranking":
            payload.setdefault("sort_direction", "desc")
            payload.setdefault("limit", 10)

        if template_id == "benchmark":
            if "target_geo_level" not in payload and "geo_level" in payload:
                payload["target_geo_level"] = payload["geo_level"]
                notes.append("Copied geo_level into target_geo_level for benchmark query.")
            if payload.get("benchmark_type") in self.catalogs["geo_levels"] and "benchmark_geo_level" not in payload:
                payload["benchmark_geo_level"] = payload["benchmark_type"]
                notes.append("Filled benchmark_geo_level from benchmark_type.")

        return PlannedQuery(plan=payload, notes=notes)
