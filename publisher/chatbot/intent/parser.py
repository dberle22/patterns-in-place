"""Intent parsing from natural language into structured query plans."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import logging
import os
from pathlib import Path
import re
from typing import Any

import yaml

from chatbot.llm.provider import LLMProvider
from chatbot.query.catalogs import REPO_ROOT, load_semantic_catalogs


QUESTION_CATALOG_PATH = Path(os.environ["FOUNDATIONS_PATH"]) / "semantic_layer" / "question_catalog.yml"
DEFAULT_FEW_SHOT_COUNT = 8
LOGGER = logging.getLogger(__name__)

QUESTION_TYPE_ALIASES = {
    "compare": "comparison",
    "comparison": "comparison",
    "rank": "ranking",
    "ranking": "ranking",
    "trend": "trend",
    "distribution": "distribution",
    "benchmark": "benchmark",
    "growth": "growth",
    "frame_lookup": "frame_lookup",
}


class ValidationError(ValueError):
    """Compatibility error type used when local schema validation fails."""


@dataclass
class QueryPlan:
    """Normalized intent schema used between parsing and SQL planning."""

    question_type: str
    subject_area: str | None = None
    metric_id: str | None = None
    base_metric_id: str | None = None
    source_table: str | None = None
    geo_level: str | None = None
    target_geo_level: str | None = None
    target_geo_id: str | None = None
    geo_ids: list[str] | None = None
    geo_filters: dict[str, Any] | None = None
    benchmark_type: str | None = None
    benchmark_geo_level: str | None = None
    benchmark_geo_ids: list[str] | None = None
    comparison_label: str | None = None
    year: int | None = None
    start_year: int | None = None
    end_year: int | None = None
    window_years: int | None = None
    sort_direction: str | None = None
    limit: int | None = None
    template_id: str | None = None

    def __post_init__(self) -> None:
        question_type = QUESTION_TYPE_ALIASES.get(self.question_type.lower())
        if question_type is None:
            raise ValidationError(f"Unsupported question_type: {self.question_type}")
        self.question_type = question_type

        if self.sort_direction is not None:
            self.sort_direction = self.sort_direction.lower()

        if self.template_id is None:
            if self.base_metric_id:
                self.template_id = "growth"
            elif self.question_type == "comparison":
                self.template_id = "compare_selected"
            else:
                self.template_id = self.question_type

    @classmethod
    def model_validate(cls, payload: dict[str, Any]) -> "QueryPlan":
        normalized = dict(payload)
        if "growth_window" in normalized and "window_years" not in normalized:
            normalized["window_years"] = normalized.pop("growth_window")
        try:
            return cls(**normalized)
        except TypeError as exc:
            raise ValidationError(str(exc)) from exc

    def model_dump(
        self,
        *,
        exclude_none: bool = False,
        by_alias: bool = False,
    ) -> dict[str, Any]:
        payload = asdict(self)
        if by_alias and payload.get("window_years") is not None:
            payload["growth_window"] = payload.pop("window_years")
        if exclude_none:
            payload = {key: value for key, value in payload.items() if value is not None}
        return payload


@dataclass
class ClarificationRequest:
    """Targeted clarification emitted when required intent slots are missing."""

    message: str
    missing_fields: list[str]
    partial_plan: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def model_validate(cls, payload: dict[str, Any]) -> "ClarificationRequest":
        try:
            return cls(**payload)
        except TypeError as exc:
            raise ValidationError(str(exc)) from exc

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ParseResult:
    """Union wrapper for a successful plan or a clarification request."""

    plan: QueryPlan | None = None
    clarification: ClarificationRequest | None = None
    matched_example_id: str | None = None
    provider_used: str | None = None
    raw_llm_response: str | None = None

    @property
    def needs_clarification(self) -> bool:
        return self.clarification is not None


class IntentParser:
    """Parse natural language questions using examples, catalogs, and an optional LLM."""

    def __init__(
        self,
        provider: LLMProvider | None = None,
        few_shot_count: int = DEFAULT_FEW_SHOT_COUNT,
    ) -> None:
        self.provider = provider
        self.few_shot_count = few_shot_count
        self.catalogs = load_semantic_catalogs()
        self.examples = self._load_examples()

    def parse(
        self,
        question: str,
        *,
        force_provider: bool = False,
    ) -> ParseResult:
        heuristic_plan: QueryPlan | None = None
        if not force_provider:
            example = self._match_example(question)
            if example is not None:
                plan = QueryPlan.model_validate(example["structured_query_plan"])
                return ParseResult(plan=plan, matched_example_id=example["example_id"])

            heuristic_plan = self._heuristic_parse(question)
            if heuristic_plan is not None:
                heuristic_result = self._finalize_plan(heuristic_plan)
                if not heuristic_result.needs_clarification:
                    return heuristic_result
        elif self.provider is None:
            heuristic_plan = self._heuristic_parse(question)
            if heuristic_plan is not None:
                heuristic_result = self._finalize_plan(heuristic_plan)
                if not heuristic_result.needs_clarification:
                    return heuristic_result

        if self.provider is not None:
            raw_llm_response: str | None = None
            try:
                payload = self.provider.complete_json(
                    system_prompt=self.build_system_prompt(),
                    user_prompt=self.build_user_prompt(question),
                )
                raw_llm_response = getattr(self.provider, "last_raw_response", None)
                provider_result = self._parse_provider_payload(question, payload)
            except Exception:
                LOGGER.exception("LLM provider parsing failed for question: %s", question)
                provider_result = None

            if provider_result is not None:
                provider_result.raw_llm_response = raw_llm_response
            if provider_result is not None and not provider_result.needs_clarification:
                return provider_result
            if not force_provider and heuristic_plan is not None:
                return self._finalize_plan(heuristic_plan)
            if provider_result is not None:
                return provider_result

        return self._build_clarification(
            partial_plan={"question_type": self._infer_question_type(question)},
            missing_fields=self._default_missing_fields_for_question_type(
                self._infer_question_type(question)
            ),
        )

    def build_system_prompt(self) -> str:
        metric_lines = [
            f"- {metric['metric_id']}: {metric['display_name']} "
            f"(subject_area={metric['subject_area']}, table={metric['source_table']})"
            for metric in self.catalogs["metric_catalog"]["metrics"]
            if metric.get("status") == "active"
        ]
        table_lines = [
            f"- {table['table_id']}: subject_area={table['subject_area']}, "
            f"geo_levels={', '.join(table['supported_geo_levels'])}"
            for table in self.catalogs["table_catalog"]["tables"]
            if table.get("status") == "active"
        ]
        geo_lines = [
            f"- {geo['geo_level']}: {geo['display_name']}"
            for geo in self.catalogs["geography_catalog"]["geo_levels"]
            if geo.get("supported_in_mvp")
        ]
        few_shots = "\n".join(self._few_shot_examples())
        return (
            "You convert user questions into a JSON query plan for a constrained analytics chatbot.\n"
            "Only use approved tables, metrics, and geographies from the catalogs below.\n"
            "If required slots are missing, return JSON with keys clarification_needed=true, "
            "missing_fields, message, and partial_plan.\n"
            "Otherwise return JSON with clarification_needed=false and a query_plan object.\n\n"
            "Supported question types: ranking, trend, comparison, distribution, benchmark, growth, frame_lookup.\n"
            "IMPORTANT question type guidance:\n"
            "- Use 'benchmark' when comparing ONE geography against the US, a national average, a regional "
            "average, or a named peer set (e.g. 'How does Texas compare to the US?', 'Is California above "
            "the national average?', 'How does Miami stack up against the national average?'). "
            "Set benchmark_type='us' when the comparison is against the United States or national average. "
            "For benchmark questions, use target_geo_level and target_geo_id for the focal geography.\n"
            "- Use 'comparison' only when the user lists 2+ specific peer geographies to compare against "
            "each other with no national/US reference. If the user asks for a side-by-side comparison over "
            "time, keep template_id='trend' but set question_type='comparison'.\n"
            "- Use 'ranking' when the user wants a top-N or bottom-N list (e.g. 'Which states have the "
            "highest population?').\n\n"
            "Approved tables:\n"
            f"{chr(10).join(table_lines)}\n\n"
            "Approved metrics:\n"
            f"{chr(10).join(metric_lines)}\n\n"
            "Approved geo levels:\n"
            f"{chr(10).join(geo_lines)}\n\n"
            "Few-shot examples:\n"
            f"{few_shots}"
        )

    def build_user_prompt(self, question: str) -> str:
        return (
            "Return only JSON.\n"
            f"Question: {question}\n"
        )

    def _parse_provider_payload(self, question: str, payload: dict[str, Any]) -> ParseResult:
        provider_name = type(self.provider).__name__
        if payload.get("clarification_needed"):
            partial_plan = self._normalize_provider_plan(question, payload.get("partial_plan") or {})
            if partial_plan:
                finalized = self._finalize_plan(partial_plan, provider_used=provider_name)
                if not finalized.needs_clarification:
                    return finalized
            clarification = ClarificationRequest.model_validate(
                {
                    "message": payload.get("message") or "Please clarify the missing intent slots.",
                    "missing_fields": payload.get("missing_fields") or [],
                    "partial_plan": partial_plan,
                }
            )
            return ParseResult(clarification=clarification, provider_used=provider_name)

        query_plan_payload = self._normalize_provider_plan(question, payload.get("query_plan", payload))
        try:
            plan = QueryPlan.model_validate(query_plan_payload)
        except ValidationError:
            heuristic_plan = self._heuristic_parse(json.dumps(query_plan_payload, sort_keys=True))
            if heuristic_plan is None:
                raise
            return self._finalize_plan(heuristic_plan, provider_used=provider_name)
        return self._finalize_plan(plan, provider_used=provider_name)

    def _finalize_plan(
        self,
        plan: QueryPlan | dict[str, Any],
        provider_used: str | None = None,
    ) -> ParseResult:
        query_plan = plan if isinstance(plan, QueryPlan) else QueryPlan.model_validate(plan)
        query_plan = self._hydrate_plan_defaults(query_plan)
        missing = self._required_missing_fields(query_plan)
        if missing:
            return self._build_clarification(query_plan.model_dump(exclude_none=True), missing, provider_used)
        return ParseResult(plan=query_plan, provider_used=provider_used)

    _FIELD_LABELS: dict[str, str] = {
        "geo_level": "which geography type (state, metro, county, etc.)",
        "geo_ids": "which specific location",
        "target_geo_id": "which specific location to compare",
        "target_geo_level": "which geography type for the target location",
        "metric_id": "which metric (population, income, home value, etc.)",
        "base_metric_id": "which metric",
        "benchmark_type": "what to benchmark against (US, region, or peer set)",
        "start_year": "the starting year",
        "end_year": "the ending year",
        "window_years": "how many years to look back",
        "sort_direction": "whether to sort highest-to-lowest or lowest-to-highest",
    }

    def _build_clarification(
        self,
        partial_plan: dict[str, Any],
        missing_fields: list[str],
        provider_used: str | None = None,
    ) -> ParseResult:
        readable = [self._FIELD_LABELS.get(f, f) for f in missing_fields if f != "year"]
        if not readable:
            readable = [self._FIELD_LABELS.get(f, f) for f in missing_fields]
        labels = ", ".join(readable)
        clarification = ClarificationRequest(
            message=f"I can help with that — I just need to know {labels}.",
            missing_fields=missing_fields,
            partial_plan=partial_plan,
        )
        return ParseResult(clarification=clarification, provider_used=provider_used)

    def _few_shot_examples(self) -> list[str]:
        rendered: list[str] = []
        for example in self.examples[: self.few_shot_count]:
            payload = {
                "clarification_needed": False,
                "query_plan": example["structured_query_plan"],
            }
            rendered.append(
                f"Q: {example['natural_language_question']}\nA: {json.dumps(payload, sort_keys=True)}"
            )
        return rendered

    def _match_example(self, question: str) -> dict[str, Any] | None:
        normalized_question = self._normalize_text(question)
        for example in self.examples:
            if self._normalize_text(example["natural_language_question"]) == normalized_question:
                return example
        return None

    def _heuristic_parse(self, question: str) -> QueryPlan | None:
        normalized = self._normalize_text(question)
        question_type = self._infer_question_type(normalized)
        metric = self._infer_metric(normalized)
        geo_level = self._infer_geo_level(normalized)
        year = self._infer_latest_year_reference(normalized)
        sort_direction = "desc"

        if metric is None and not any(token in normalized for token in ["growth", "growing", "increase", "gain"]):
            return None

        if (
            ("compare" in normalized or "side-by-side" in normalized)
            and any(token in normalized for token in ["over time", "trend"])
        ):
            geo_ids = self._infer_geo_ids(normalized, geo_level)
            if geo_ids and geo_level in {None, "us"}:
                geo_level = "state"
            return QueryPlan(
                question_type="comparison",
                metric_id=metric["metric_id"] if metric else None,
                source_table=metric["source_table"] if metric else None,
                subject_area=metric["subject_area"] if metric else None,
                geo_level=geo_level,
                geo_ids=geo_ids,
                start_year=2015,
                end_year=year or 2024,
                template_id="trend",
            )

        if "over time" in normalized or "trend" in normalized:
            return QueryPlan(
                question_type="trend",
                metric_id=metric["metric_id"] if metric else None,
                source_table=metric["source_table"] if metric else None,
                subject_area=metric["subject_area"] if metric else None,
                geo_level=geo_level,
                start_year=2015,
                end_year=year or 2024,
            )

        _us_ref = " us " in f" {normalized} " or "united states" in normalized or "national" in normalized or "nationwide" in normalized
        _benchmark_signals = (
            "benchmark" in normalized
            or " versus " in normalized
            or " vs " in normalized
            or "stack up" in normalized
            or ("compare" in normalized and _us_ref)
            or ("above" in normalized and ("average" in normalized or "us" in normalized or "national" in normalized))
            or ("below" in normalized and ("average" in normalized or "us" in normalized or "national" in normalized))
        )

        if _benchmark_signals:
            target_geo_id = self._infer_target_geo_id(normalized)
            target_geo_level = geo_level
            if target_geo_id is not None and target_geo_level in {None, "us"}:
                target_geo_level = "state"
            return QueryPlan(
                question_type="benchmark",
                metric_id=metric["metric_id"] if metric else None,
                source_table=metric["source_table"] if metric else None,
                subject_area=metric["subject_area"] if metric else None,
                target_geo_level=target_geo_level,
                target_geo_id=target_geo_id,
                year=year,
                benchmark_type="us" if _us_ref else None,
                benchmark_geo_level="us" if _us_ref else None,
                comparison_label="United States" if _us_ref else None,
            )

        if "compare" in normalized and "vs" not in normalized:
            geo_ids = self._infer_geo_ids(normalized, geo_level)
            if geo_ids and geo_level in {None, "us"}:
                geo_level = "state"
            return QueryPlan(
                question_type="comparison",
                metric_id=metric["metric_id"] if metric else None,
                source_table=metric["source_table"] if metric else None,
                subject_area=metric["subject_area"] if metric else None,
                geo_level=geo_level,
                geo_ids=geo_ids,
                year=year,
            )

        if "distribution" in normalized or "spread" in normalized:
            return QueryPlan(
                question_type="distribution",
                metric_id=metric["metric_id"] if metric else None,
                source_table=metric["source_table"] if metric else None,
                subject_area=metric["subject_area"] if metric else None,
                geo_level=geo_level,
                year=year,
            )

        if any(token in normalized for token in ["growth", "growing", "increase", "gain"]):
            base_metric = metric
            if base_metric is None:
                base_metric = self._default_growth_metric(normalized)
            start_year_match = re.search(r"\bsince\s+(20\d{2})\b", normalized)
            start_year = int(start_year_match.group(1)) if start_year_match else None
            end_year = year or 2024
            if start_year is not None and end_year == start_year:
                end_year = 2024
            window_years = 5 if "5 year" in normalized or "five year" in normalized else None
            if start_year is not None and end_year > start_year:
                window_years = end_year - start_year
            growth_question_type = (
                "trend"
                if any(token in normalized for token in ["over time", "trend"])
                else "ranking"
            )
            return QueryPlan(
                question_type=growth_question_type,
                base_metric_id=base_metric["metric_id"] if base_metric else None,
                source_table=base_metric["source_table"] if base_metric else None,
                subject_area=base_metric["subject_area"] if base_metric else None,
                geo_level=geo_level,
                end_year=end_year,
                window_years=window_years,
                sort_direction=sort_direction,
                limit=10,
                template_id="growth",
            )

        if question_type == "ranking":
            return QueryPlan(
                question_type="ranking",
                metric_id=metric["metric_id"] if metric else None,
                source_table=metric["source_table"] if metric else None,
                subject_area=metric["subject_area"] if metric else None,
                geo_level=geo_level,
                year=year,
                sort_direction=sort_direction,
                limit=10,
            )

        return None

    def _required_missing_fields(self, plan: QueryPlan) -> list[str]:
        if plan.template_id is None:
            return ["question_type"]

        template = self.catalogs["templates"].get(plan.template_id)
        if template is None:
            return ["question_type"]

        missing: list[str] = []
        payload = plan.model_dump(by_alias=False, exclude_none=True)
        for field in template.get("required_slots", []):
            if field not in payload or payload[field] in (None, [], ""):
                missing.append(field)
        return missing

    def _infer_question_type(self, question: str) -> str:
        if any(token in question for token in ["over time", "trend"]):
            return "trend"
        if any(token in question for token in ["distribution", "spread"]):
            return "distribution"
        if any(token in question for token in ["growth", "growing", "increase", "gain"]):
            return "growth"
        if "benchmark" in question or " vs " in f" {question} " or " versus " in question:
            return "benchmark"
        if "compare" in question:
            return "comparison"
        return "ranking"

    def _infer_metric(self, question: str) -> dict[str, Any] | None:
        normalized = question.replace("-", " ")
        metric_patterns = [
            ("rent to income", "rent_to_income"),
            ("population", "pop_total"),
            ("median age", "median_age"),
            ("hispanic", "pct_hispanic"),
            ("gross rent", "median_gross_rent"),
            ("rent burden", "pct_rent_burden_30plus"),
            ("home value", "median_home_value"),
            ("housing unit", "hu_total"),
            ("median household income", "median_hh_income"),
            ("household income", "median_hh_income"),
            ("per capita income", "calc_income_pc"),
            ("income", "calc_income_pc"),
        ]
        for pattern, metric_id in metric_patterns:
            if pattern in normalized:
                return self.catalogs["metrics"][metric_id]
        return None

    def _default_growth_metric(self, question: str) -> dict[str, Any] | None:
        if "population" in question:
            return self.catalogs["metrics"]["pop_total"]
        if "home value" in question:
            return self.catalogs["metrics"]["median_home_value"]
        if "rent" in question:
            return self.catalogs["metrics"]["median_gross_rent"]
        if "median household income" in question or "household income" in question:
            return self.catalogs["metrics"]["median_hh_income"]
        if "income" in question:
            return self.catalogs["metrics"]["calc_income_pc"]
        return self.catalogs["metrics"]["pop_total"]

    # Full state names only — 2-letter abbreviations are too ambiguous in natural language.
    _STATE_NAME_TO_FIPS: dict[str, str] = {
        "alabama": "01", "alaska": "02", "arizona": "04", "arkansas": "05",
        "california": "06", "colorado": "08", "connecticut": "09", "delaware": "10",
        "district of columbia": "11", "florida": "12", "georgia": "13",
        "hawaii": "15", "idaho": "16", "illinois": "17", "indiana": "18",
        "iowa": "19", "kansas": "20", "kentucky": "21", "louisiana": "22",
        "maine": "23", "maryland": "24", "massachusetts": "25", "michigan": "26",
        "minnesota": "27", "mississippi": "28", "missouri": "29", "montana": "30",
        "nebraska": "31", "nevada": "32", "new hampshire": "33", "new jersey": "34",
        "new mexico": "35", "new york": "36", "north carolina": "37",
        "north dakota": "38", "ohio": "39", "oklahoma": "40", "oregon": "41",
        "pennsylvania": "42", "rhode island": "44", "south carolina": "45",
        "south dakota": "46", "tennessee": "47", "texas": "48", "utah": "49",
        "vermont": "50", "virginia": "51", "washington": "53",
        "west virginia": "54", "wisconsin": "55", "wyoming": "56",
    }

    def _infer_target_geo_id(self, question: str) -> str | None:
        """Return a state FIPS code if the question names a US state."""
        for name, fips in self._STATE_NAME_TO_FIPS.items():
            if name in question:
                return fips
        return None

    def _infer_geo_ids(self, question: str, geo_level: str | None) -> list[str] | None:
        """Return ordered geography ids when multiple named geographies are present."""
        if geo_level not in {None, "state", "us"}:
            return None

        matches: list[tuple[int, str]] = []
        for name, fips in self._STATE_NAME_TO_FIPS.items():
            pattern = rf"\b{re.escape(name)}\b"
            match = re.search(pattern, question)
            if match is None:
                continue
            matches.append((match.start(), fips))

        if len(matches) < 2:
            return None

        ordered_geo_ids: list[str] = []
        seen: set[str] = set()
        for _, fips in sorted(matches, key=lambda item: item[0]):
            if fips in seen:
                continue
            ordered_geo_ids.append(fips)
            seen.add(fips)
        return ordered_geo_ids

    def _infer_geo_level(self, question: str) -> str | None:
        patterns = [
            ("states", "state"),
            ("state", "state"),
            ("cbsas", "cbsa"),
            ("cbsa", "cbsa"),
            ("metros", "cbsa"),
            ("metro", "cbsa"),
            ("counties", "county"),
            ("county", "county"),
            ("regions", "region"),
            ("region", "region"),
            ("divisions", "division"),
            ("division", "division"),
            ("places", "place"),
            ("place", "place"),
            ("cities", "place"),
            ("city", "place"),
            ("towns", "place"),
            ("town", "place"),
            ("us", "us"),
            ("united states", "us"),
        ]
        for pattern, geo_level in patterns:
            if pattern in question:
                return geo_level
        return None

    def _infer_latest_year_reference(self, question: str) -> int | None:
        match = re.search(r"\b(20\d{2})\b", question)
        if match:
            return int(match.group(1))
        if re.search(r"\b(last|past)\s+\d+\s+years?\b", question) or "over the last" in question or "over the past" in question:
            return 2024
        if "latest" in question or "current" in question or "most recent" in question:
            return 2024
        return None

    def _default_missing_fields_for_question_type(self, question_type: str) -> list[str]:
        if question_type == "growth":
            return ["base_metric_id", "geo_level", "end_year", "window_years"]
        if question_type == "trend":
            return ["metric_id", "geo_level", "start_year", "end_year"]
        return ["metric_id", "geo_level"]

    def _hydrate_plan_defaults(self, plan: QueryPlan) -> QueryPlan:
        payload = plan.model_dump(exclude_none=True)

        if "source_table" not in payload:
            metric_id = payload.get("metric_id") or payload.get("base_metric_id")
            if metric_id in self.catalogs["metrics"]:
                payload["source_table"] = self.catalogs["metrics"][metric_id]["source_table"]

        if payload.get("template_id") in ("ranking", "growth") and "geo_level" not in payload:
            payload["geo_level"] = "state"

        if payload.get("template_id") == "growth":
            payload.setdefault("question_type", "ranking")
            payload.setdefault("end_year", 2024)
            payload.setdefault("window_years", 5)
            payload.setdefault("sort_direction", "desc")
            payload.setdefault("limit", 10)

        if payload.get("template_id") == "benchmark":
            payload.setdefault("year", 2024)

        return QueryPlan.model_validate(payload)

    def _normalize_provider_plan(self, question: str, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(payload)
        question_normalized = self._normalize_text(question)

        if normalized.get("question_type") == "benchmark" or normalized.get("template_id") == "benchmark":
            if "target_geo_id" not in normalized and "geo_id" in normalized:
                normalized["target_geo_id"] = normalized.pop("geo_id")
            if "target_geo_level" not in normalized and "geo_level" in normalized:
                normalized["target_geo_level"] = normalized.pop("geo_level")
            if normalized.get("target_geo_id") and normalized.get("target_geo_level") in {None, "us"}:
                normalized["target_geo_level"] = "state"
            if normalized.get("benchmark_type") == "us":
                normalized.setdefault("benchmark_geo_level", "us")
                normalized.setdefault("comparison_label", "United States")
            normalized.setdefault("template_id", "benchmark")

        if (
            ("compare" in question_normalized or "side-by-side" in question_normalized)
            and any(token in question_normalized for token in ["over time", "trend"])
            and normalized.get("geo_ids")
        ):
            normalized["question_type"] = "comparison"
            normalized["template_id"] = "trend"

        growth_metric = normalized.get("metric_id")
        growth_override = self._precomputed_growth_override(growth_metric, question_normalized)
        if growth_override is not None:
            normalized.pop("metric_id", None)
            normalized["base_metric_id"] = growth_override["base_metric_id"]
            normalized["source_table"] = growth_override["source_table"]
            normalized["template_id"] = "growth"
            normalized["question_type"] = "trend" if normalized.get("question_type") == "trend" else "ranking"
            normalized.setdefault("end_year", normalized.pop("year", None) or self._infer_latest_year_reference(question_normalized) or 2024)
            normalized.setdefault("window_years", growth_override["window_years"])
            normalized.setdefault("sort_direction", "desc")
            normalized.setdefault("limit", 10)

        if normalized.get("template_id") == "growth" and (
            "median household income" in question_normalized or "household income" in question_normalized
        ):
            normalized["base_metric_id"] = "median_hh_income"
            normalized.setdefault("source_table", "economics_income_wide")

        return normalized

    def _precomputed_growth_override(
        self,
        metric_id: str | None,
        question: str,
    ) -> dict[str, Any] | None:
        if metric_id is None:
            return None
        if metric_id == "pop_growth_5yr":
            return {
                "base_metric_id": "pop_total",
                "source_table": "population_demographics",
                "window_years": 5,
            }
        if metric_id == "income_pc_growth_5yr":
            base_metric_id = "median_hh_income" if "household income" in question else "calc_income_pc"
            return {
                "base_metric_id": base_metric_id,
                "source_table": "economics_income_wide",
                "window_years": 5,
            }
        return None

    def _load_examples(self) -> list[dict[str, Any]]:
        payload = yaml.safe_load(QUESTION_CATALOG_PATH.read_text(encoding="utf-8"))
        return [q for q in payload["questions"] if "structured_query_plan" in q]

    def _normalize_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().lower())
