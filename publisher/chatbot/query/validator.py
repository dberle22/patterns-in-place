"""Validation for generated SQL and referenced semantic entities."""

from __future__ import annotations

from dataclasses import dataclass
import re

from chatbot.query.catalogs import load_semantic_catalogs, load_table_columns
from chatbot.query.generator import RenderedQuery


FORBIDDEN_SQL_PATTERNS = [
    r"\binsert\b",
    r"\bupdate\b",
    r"\bdelete\b",
    r"\bdrop\b",
    r"\balter\b",
    r"\bcreate\b",
    r"\btruncate\b",
    r"\battach\b",
    r"\bcopy\b",
]


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]

    def raise_for_errors(self) -> None:
        if self.errors:
            raise ValueError("; ".join(self.errors))


class QueryValidator:
    """Check generated SQL against semantic-layer rules."""

    def __init__(self) -> None:
        self.catalogs = load_semantic_catalogs()
        self.table_columns = load_table_columns()

    def validate(self, rendered_query: RenderedQuery) -> ValidationResult:
        errors: list[str] = []
        plan = rendered_query.plan

        self._validate_sql_is_read_only(rendered_query.sql, errors)
        self._validate_tables(rendered_query.tables_used, errors)
        self._validate_fields(rendered_query.fields_used, errors)
        self._validate_joins(rendered_query.joins_used, errors)
        self._validate_geo_levels(rendered_query, errors)
        self._validate_metrics(plan, errors)

        return ValidationResult(is_valid=not errors, errors=errors)

    def _validate_sql_is_read_only(self, sql: str, errors: list[str]) -> None:
        lowered = sql.lower()
        for pattern in FORBIDDEN_SQL_PATTERNS:
            if re.search(pattern, lowered):
                errors.append(f"SQL contains forbidden statement matching {pattern!r}")

    def _validate_tables(self, tables_used: list[str], errors: list[str]) -> None:
        for table_id in tables_used:
            table = self.catalogs["tables"].get(table_id)
            if table is None:
                errors.append(f"Unknown table referenced: {table_id}")
                continue
            if table.get("status") != "active":
                errors.append(f"Inactive table referenced: {table_id}")

    def _validate_fields(
        self, fields_used: dict[str, set[str]], errors: list[str]
    ) -> None:
        for table_id, fields in fields_used.items():
            known_fields = self.table_columns.get(table_id, set())
            if not known_fields:
                errors.append(f"No data dictionary columns loaded for table {table_id}")
                continue
            missing = sorted(field for field in fields if field not in known_fields)
            if missing:
                errors.append(
                    f"Unknown columns for {table_id}: {', '.join(missing)}"
                )

    def _validate_joins(self, joins_used: list[str], errors: list[str]) -> None:
        for join_id in joins_used:
            if join_id not in self.catalogs["joins"]:
                errors.append(f"Join is not approved in join_catalog.yml: {join_id}")

    def _validate_geo_levels(
        self, rendered_query: RenderedQuery, errors: list[str]
    ) -> None:
        if rendered_query.geo_level is None:
            return

        for table_id in rendered_query.tables_used:
            table = self.catalogs["tables"].get(table_id)
            if table is None:
                continue
            if rendered_query.geo_level not in table.get("supported_geo_levels", []):
                errors.append(
                    f"Geo level {rendered_query.geo_level} is not supported by {table_id}"
                )

    def _validate_metrics(self, plan: dict, errors: list[str]) -> None:
        metric_ids = []
        if "metric_id" in plan:
            metric_ids.append(plan["metric_id"])
        if "base_metric_id" in plan:
            metric_ids.append(plan["base_metric_id"])

        for metric_id in metric_ids:
            metric = self.catalogs["metrics"].get(metric_id)
            if metric is None:
                errors.append(f"Unknown metric_id: {metric_id}")
                continue
            if metric.get("status") != "active":
                errors.append(f"Inactive metric_id: {metric_id}")

            requested_geo_level = plan.get("geo_level") or plan.get("target_geo_level")
            if (
                requested_geo_level
                and requested_geo_level not in metric.get("valid_geo_levels", [])
            ):
                errors.append(
                    f"Metric {metric_id} does not support geo level {requested_geo_level}"
                )

            if "window_years" in plan and not metric.get("growth_eligible"):
                errors.append(f"Metric {metric_id} is not growth eligible")
            if "window_years" in plan:
                if int(plan["window_years"]) not in metric.get("growth_windows", []):
                    errors.append(
                        f"Metric {metric_id} does not support growth window {plan['window_years']}"
                    )
