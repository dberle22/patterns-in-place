"""Deterministic chart selection from approved semantic rules."""

from __future__ import annotations

from dataclasses import dataclass

from chatbot.charts.profiler import ResultProfile


QUESTION_TYPE_ALIASES = {
    "compare": "comparison",
    "compare_selected": "comparison",
    "comparison": "comparison",
    "ranking": "ranking",
    "trend": "trend",
    "distribution": "distribution",
    "benchmark": "benchmark",
    "growth": "trend",
}


@dataclass
class ChartSelection:
    chart_type: str
    rule_id: str
    question_type: str
    inferred_shape: str
    rationale: str
    fallback_chart_types: list[str]


class ChartSelector:
    """Choose the best approved chart type for a profiled result set."""

    def __init__(self) -> None:
        self.chart_rules_catalog = self._load_chart_rules()

    def select(self, question_type: str, profile: ResultProfile) -> ChartSelection:
        resolved_question_type = QUESTION_TYPE_ALIASES.get(question_type, question_type)
        fallback_question_type = QUESTION_TYPE_ALIASES.get(
            profile.inferred_shape,
            profile.inferred_shape,
        )
        matching_rule = next(
            (
                rule
                for rule in self.chart_rules_catalog["rules"]
                if rule["question_type"] == resolved_question_type
            ),
            None,
        )
        if matching_rule is None:
            matching_rule = next(
                (
                    rule
                    for rule in self.chart_rules_catalog["rules"]
                    if rule["question_type"] == fallback_question_type
                ),
                None,
            )
        if matching_rule is None:
            raise ValueError(
                "No chart rule configured for "
                f"question_type={resolved_question_type} or inferred_shape={fallback_question_type}"
            )

        preferred_types = matching_rule["approved_chart_types"] + matching_rule.get(
            "fallback_chart_types", []
        )
        chart_type = next(
            (
                candidate
                for candidate in preferred_types
                if self._satisfies_constraints(candidate, profile)
            ),
            "heatmap_table",
        )

        return ChartSelection(
            chart_type=chart_type,
            rule_id=matching_rule["rule_id"],
            question_type=resolved_question_type,
            inferred_shape=profile.inferred_shape,
            rationale=matching_rule["rationale"],
            fallback_chart_types=matching_rule.get("fallback_chart_types", []),
        )

    def _satisfies_constraints(self, chart_type: str, profile: ResultProfile) -> bool:
        if chart_type == "slopegraph":
            return profile.time_point_count == 2
        if chart_type == "boxplot":
            return profile.row_count >= 8
        if chart_type == "scatter":
            return profile.measure_count >= 2
        return True

    def _load_chart_rules(self) -> dict[str, object]:
        import yaml

        from chatbot.query.catalogs import SEMANTIC_DIR

        path = SEMANTIC_DIR / "chart_rules.yml"
        return yaml.safe_load(path.read_text(encoding="utf-8"))
