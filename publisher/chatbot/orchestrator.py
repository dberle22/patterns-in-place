"""End-to-end orchestration for the Phase 4 question-to-chart pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    import pandas as pd
except ImportError:  # pragma: no cover - optional dependency in bare environments
    pd = None

from chatbot.charts.profiler import ResultProfile, ResultProfiler
from chatbot.charts.renderer import ChartRenderer, RenderedChart
from chatbot.charts.selector import ChartSelection, ChartSelector
from chatbot.intent.parser import ClarificationRequest, IntentParser, ParseResult, QueryPlan
from chatbot.llm.provider import LLMProvider, get_llm_provider
from chatbot.query.executor import QueryExecutor
from chatbot.query.generator import QueryGenerator, RenderedQuery
from chatbot.query.planner import PlannedQuery, QueryPlanner
from chatbot.query.validator import QueryValidator, ValidationResult
from chatbot.response.assembler import AssembledResponse, ResponseAssembler


@dataclass
class OrchestrationResult:
    """Full Phase 4 pipeline output for one user question."""

    question: str
    parse_result: ParseResult
    query_plan: QueryPlan | None = None
    planned_query: PlannedQuery | None = None
    rendered_query: RenderedQuery | None = None
    validation: ValidationResult | None = None
    dataframe: pd.DataFrame | None = None
    result_profile: ResultProfile | None = None
    chart_selection: ChartSelection | None = None
    rendered_chart: RenderedChart | None = None
    response: AssembledResponse | None = None

    @property
    def clarification(self) -> ClarificationRequest | None:
        return self.parse_result.clarification

    @property
    def needs_clarification(self) -> bool:
        return self.parse_result.needs_clarification

    @property
    def sql(self) -> str | None:
        return None if self.rendered_query is None else self.rendered_query.sql

    @property
    def chart_path(self) -> str | None:
        return None if self.rendered_chart is None else self.rendered_chart.output_path

    @property
    def answer_text(self) -> str | None:
        return None if self.response is None else self.response.answer_text


class Orchestrator:
    """Wire intent parsing through validated SQL execution and chart rendering."""

    def __init__(
        self,
        *,
        parser: IntentParser | None = None,
        planner: QueryPlanner | None = None,
        generator: QueryGenerator | None = None,
        validator: QueryValidator | None = None,
        executor: QueryExecutor | None = None,
        profiler: ResultProfiler | None = None,
        selector: ChartSelector | None = None,
        renderer: ChartRenderer | None = None,
        assembler: ResponseAssembler | None = None,
        provider: LLMProvider | None = None,
    ) -> None:
        self.parser = parser or IntentParser(provider=provider)
        self.planner = planner or QueryPlanner()
        self.generator = generator or QueryGenerator()
        self.validator = validator or QueryValidator()
        self.executor = executor
        self.profiler = profiler or ResultProfiler()
        self.selector = selector or ChartSelector()
        self.renderer = renderer
        self.assembler = assembler or ResponseAssembler()

    @classmethod
    def from_env(cls) -> "Orchestrator":
        """Construct an orchestrator using the configured LLM provider and database."""

        provider = get_llm_provider()
        return cls(provider=provider, executor=QueryExecutor())

    def run(self, question: str) -> OrchestrationResult:
        parse_result = self.parser.parse(question)
        result = OrchestrationResult(question=question, parse_result=parse_result)
        if parse_result.needs_clarification:
            return result

        assert parse_result.plan is not None
        result.query_plan = parse_result.plan
        result.planned_query = self.planner.build(parse_result.plan)
        result.rendered_query = self.generator.render(result.planned_query.plan)
        result.validation = self.validator.validate(result.rendered_query)
        result.validation.raise_for_errors()

        if self.executor is not None:
            result.dataframe = self.executor.execute(result.rendered_query)
            result.result_profile = self.profiler.profile(result.dataframe)
            result.chart_selection = self.selector.select(
                result.query_plan.question_type,
                result.result_profile,
            )
            if self.renderer is not None:
                chart_dataframe = self._chart_dataframe(result)
                result.rendered_chart = self.renderer.render(
                    chart_dataframe,
                    selection=result.chart_selection,
                    query_plan=result.query_plan,
                    profile=result.result_profile,
                    sql=result.rendered_query.sql,
                )
            result.response = self.assembler.assemble(
                question=question,
                query_plan=result.query_plan,
                dataframe=result.dataframe,
                profile=result.result_profile,
                selection=result.chart_selection,
            )

        return result

    def preview(self, question: str) -> dict[str, Any]:
        """Convenience method for REPL debugging."""

        result = self.run(question)
        return {
            "needs_clarification": result.needs_clarification,
            "clarification": None
            if result.clarification is None
            else result.clarification.model_dump(),
            "query_plan": None
            if result.query_plan is None
            else result.query_plan.model_dump(exclude_none=True),
            "sql": result.sql,
            "row_count": None if result.dataframe is None else len(result.dataframe),
            "chart_type": None if result.chart_selection is None else result.chart_selection.chart_type,
            "chart_path": result.chart_path,
            "answer_text": result.answer_text,
        }

    def _chart_dataframe(self, result: OrchestrationResult) -> pd.DataFrame | None:
        dataframe = result.dataframe
        query_plan = result.query_plan
        if dataframe is None or query_plan is None:
            return dataframe
        if query_plan.template_id != "trend" or query_plan.geo_ids:
            return dataframe
        if "period" not in dataframe.columns or "geo_name" not in dataframe.columns or "metric_value" not in dataframe.columns:
            return dataframe

        unique_geos = dataframe["geo_name"].dropna().unique().tolist()
        if len(unique_geos) <= 10:
            return dataframe

        latest_period = dataframe["period"].dropna().max()
        latest_rows = dataframe[dataframe["period"] == latest_period]
        if latest_rows.empty:
            return dataframe
        top_geos = (
            latest_rows.sort_values(by=["metric_value", "geo_name"], ascending=[False, True])
            .head(10)["geo_name"]
            .tolist()
        )
        return dataframe[dataframe["geo_name"].isin(top_geos)].copy()
