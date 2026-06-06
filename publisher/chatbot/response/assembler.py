"""Compose a lightweight text summary from query and chart outputs."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real

try:
    import pandas as pd
except ImportError:  # pragma: no cover - optional dependency in bare environments
    pd = None

from chatbot.charts.profiler import ResultProfile
from chatbot.charts.selector import ChartSelection
from chatbot.intent.parser import QueryPlan


@dataclass
class AssembledResponse:
    answer_text: str
    assumptions: list[str]


class ResponseAssembler:
    """Build a concise response summary for the current analytical result."""

    def assemble(
        self,
        *,
        question: str,
        query_plan: QueryPlan,
        dataframe: pd.DataFrame | None,
        profile: ResultProfile | None,
        selection: ChartSelection | None,
    ) -> AssembledResponse:
        if pd is None or dataframe is None or dataframe.empty:
            return AssembledResponse(
                answer_text="The query ran, but there were no rows to summarize yet.",
                assumptions=self._assumptions(query_plan, profile, selection),
            )

        metric_label = (
            dataframe["metric_label"].dropna().iloc[0]
            if "metric_label" in dataframe.columns and not dataframe["metric_label"].dropna().empty
            else (query_plan.metric_id or query_plan.base_metric_id or "metric")
        )

        if query_plan.template_id == "growth" and "growth_value" in dataframe.columns:
            top_row = dataframe.iloc[0]
            geo_name = top_row.get("geo_name", "The top geography")
            growth_value = top_row.get("growth_value")
            window_years = top_row.get("window_years", query_plan.window_years)
            answer = (
                f"{geo_name} ranks highest for {window_years}-year growth "
                f"at {self._format_percent(growth_value)}."
            )
            return AssembledResponse(
                answer_text=answer,
                assumptions=self._assumptions(query_plan, profile, selection),
            )

        if (
            query_plan.template_id == "trend"
            and self._looks_like_trend_comparison(question, query_plan, dataframe)
        ):
            answer = self._trend_comparison_answer(dataframe, metric_label)
        elif query_plan.question_type == "ranking":
            top_row = dataframe.iloc[0]
            geo_name = top_row.get("geo_name", "The top geography")
            metric_value = top_row.get("metric_value")
            answer = f"{geo_name} ranks highest for {metric_label} at {self._format_value(metric_value)}."
        elif query_plan.question_type in {"trend", "growth"} and "period" in dataframe.columns:
            geo_names = dataframe["geo_name"].dropna().unique().tolist() if "geo_name" in dataframe.columns else []
            periods = dataframe["period"].dropna()
            span = f"{int(periods.min())} to {int(periods.max())}"
            if len(geo_names) == 1:
                answer = f"{metric_label} spans {span} for {geo_names[0]}."
            else:
                value_col = "metric_value" if "metric_value" in dataframe.columns else None
                if value_col and "geo_name" in dataframe.columns:
                    last_period = int(periods.max())
                    end_df = dataframe[dataframe["period"].astype(int) == last_period]
                    if not end_df.empty:
                        top_row = end_df.loc[end_df[value_col].idxmax()]
                        top_geo = top_row.get("geo_name", "")
                        top_val = self._format_value(top_row.get(value_col))
                        answer = (
                            f"{metric_label} spans {span} across {len(geo_names)} geographies. "
                            f"By {last_period}, {top_geo} led with {top_val}."
                        )
                    else:
                        answer = f"{metric_label} spans {span} across the selected geographies."
                else:
                    answer = f"{metric_label} spans {span} across the selected geographies."
        elif query_plan.question_type == "distribution":
            value_col = "metric_value" if "metric_value" in dataframe.columns else None
            if value_col is not None and not dataframe[value_col].dropna().empty:
                vals = dataframe[value_col].dropna()
                high_row = dataframe.loc[vals.idxmax()]
                low_row = dataframe.loc[vals.idxmin()]
                median_val = self._format_value(vals.median())
                high_geo = high_row.get("geo_name", "Unknown")
                low_geo = low_row.get("geo_name", "Unknown")
                answer = (
                    f"The distribution of {metric_label} spans {len(dataframe)} geographies. "
                    f"{high_geo} had the highest value at {self._format_value(high_row.get(value_col))}. "
                    f"{low_geo} was lowest at {self._format_value(low_row.get(value_col))}. "
                    f"The median was {median_val}."
                )
            else:
                answer = f"The result shows the distribution of {metric_label} across {len(dataframe)} rows."
        elif query_plan.question_type == "benchmark" and "comparison_group" in dataframe.columns:
            answer = self._benchmark_answer(query_plan, dataframe, metric_label)
        elif query_plan.question_type == "comparison":
            answer = self._comparison_answer(dataframe, metric_label)
        else:
            answer = f"The result summarizes {metric_label} for the requested comparison."

        return AssembledResponse(
            answer_text=answer,
            assumptions=self._assumptions(query_plan, profile, selection),
        )

    def _assumptions(
        self,
        query_plan: QueryPlan,
        profile: ResultProfile | None,
        selection: ChartSelection | None,
    ) -> list[str]:
        assumptions = [f"Question type: {query_plan.question_type}."]
        if query_plan.geo_level is not None:
            assumptions.append(f"Geography level: {query_plan.geo_level}.")
        if query_plan.year is not None:
            assumptions.append(f"Point-in-time year: {query_plan.year}.")
        if profile is not None:
            assumptions.append(f"Inferred result shape: {profile.inferred_shape}.")
        if selection is not None:
            assumptions.append(f"Selected chart type: {selection.chart_type}.")
        return assumptions

    def _format_value(self, value: object) -> str:
        if isinstance(value, Real) and not isinstance(value, bool):
            if float(value).is_integer():
                return f"{int(value):,}"
            return f"{value:,.2f}"
        return str(value)

    def _format_percent(self, value: object) -> str:
        if isinstance(value, Real) and not isinstance(value, bool):
            return f"{float(value):.2%}"
        return str(value)

    def _comparison_answer(self, dataframe: pd.DataFrame, metric_label: str) -> str:
        if "metric_value" not in dataframe.columns or dataframe["metric_value"].dropna().empty:
            return f"The result summarizes {metric_label} for the requested comparison."

        ranked = dataframe.dropna(subset=["metric_value"]).sort_values(
            by=["metric_value", "geo_name"],
            ascending=[False, True],
        )
        if ranked.empty:
            return f"The result summarizes {metric_label} for the requested comparison."

        top_row = ranked.iloc[0]
        top_geo = top_row.get("geo_name", "The top geography")
        top_value = top_row.get("metric_value")
        if len(ranked) == 1 or not isinstance(top_value, Real) or float(top_value) == 0.0:
            return f"{top_geo} leads for {metric_label} at {self._format_value(top_value)}."

        comparisons: list[str] = []
        for _, row in ranked.iloc[1:].iterrows():
            geo_name = row.get("geo_name", "another geography")
            metric_value = row.get("metric_value")
            if not isinstance(metric_value, Real):
                comparisons.append(f"{geo_name} at {self._format_value(metric_value)}")
                continue
            pct_diff = (float(top_value) - float(metric_value)) / float(top_value)
            comparisons.append(
                f"{geo_name} ({self._format_value(metric_value)}), {self._format_percent(pct_diff)} lower"
            )

        return (
            f"{top_geo} leads for {metric_label} at {self._format_value(top_value)}. "
            f"Next are " + "; ".join(comparisons) + "."
        )

    def _benchmark_answer(self, query_plan: QueryPlan, dataframe: pd.DataFrame, metric_label: str) -> str:
        grouped = dataframe.dropna(subset=["comparison_group"])
        if grouped.empty or "metric_value" not in grouped.columns:
            return f"The result compares the target geography against its benchmark for {metric_label}."

        target_rows = grouped[grouped["comparison_group"] == "target"]
        benchmark_rows = grouped[grouped["comparison_group"] == "benchmark"]
        if target_rows.empty or benchmark_rows.empty:
            return f"The result compares the target geography against its benchmark for {metric_label}."

        target_row = target_rows.iloc[0]
        benchmark_row = benchmark_rows.iloc[0]
        target_name = target_row.get("geo_name", "The target geography")
        benchmark_name = benchmark_row.get("geo_name", "the benchmark")
        target_value = target_row.get("metric_value")
        benchmark_value = benchmark_row.get("metric_value")

        if (
            query_plan.benchmark_type == "us"
            and query_plan.metric_id in {"pop_total", "hu_total"}
            and isinstance(target_value, Real)
            and isinstance(benchmark_value, Real)
            and float(benchmark_value) != 0.0
        ):
            share = float(target_value) / float(benchmark_value)
            return (
                f"{target_name} accounts for {self._format_percent(share)} of {benchmark_name} "
                f"{metric_label}: {self._format_value(target_value)} out of {self._format_value(benchmark_value)}."
            )

        if not isinstance(target_value, Real) or not isinstance(benchmark_value, Real):
            return (
                f"{target_name} is compared with {benchmark_name} for {metric_label}: "
                f"{self._format_value(target_value)} versus {self._format_value(benchmark_value)}."
            )

        difference = float(target_value) - float(benchmark_value)
        if float(benchmark_value) == 0.0:
            relation = "above" if difference >= 0 else "below"
            delta_text = self._format_value(abs(difference))
        else:
            relation = "above" if difference >= 0 else "below"
            delta_text = self._format_percent(abs(difference) / abs(float(benchmark_value)))

        return (
            f"{target_name} is {relation} {benchmark_name} for {metric_label}: "
            f"{self._format_value(target_value)} versus {self._format_value(benchmark_value)}, "
            f"a gap of {delta_text}."
        )

    def _looks_like_trend_comparison(
        self,
        question: str,
        query_plan: QueryPlan,
        dataframe: pd.DataFrame,
    ) -> bool:
        if "period" not in dataframe.columns or "geo_name" not in dataframe.columns:
            return False
        if len(dataframe["geo_name"].dropna().unique()) < 2:
            return False
        normalized_question = question.lower()
        return (
            query_plan.question_type == "comparison"
            or "side-by-side" in normalized_question
            or "compare" in normalized_question
            or "comparison" in normalized_question
        )

    def _trend_comparison_answer(self, dataframe: pd.DataFrame, metric_label: str) -> str:
        cleaned = dataframe.dropna(subset=["period", "geo_name", "metric_value"]).copy()
        if cleaned.empty:
            return f"The result summarizes {metric_label} across the selected geographies over time."

        cleaned["period"] = cleaned["period"].astype(int)
        start_period = int(cleaned["period"].min())
        end_period = int(cleaned["period"].max())
        start_df = cleaned[cleaned["period"] == start_period].set_index("geo_name")
        end_df = cleaned[cleaned["period"] == end_period].set_index("geo_name")
        shared_geos = [geo for geo in end_df.index if geo in start_df.index]
        if not shared_geos:
            return f"{metric_label} spans {start_period} to {end_period} across the selected geographies."

        end_ranked = end_df.loc[shared_geos].sort_values(by="metric_value", ascending=False)
        lead_geo = end_ranked.index[0]
        lead_value = end_ranked.iloc[0]["metric_value"]

        changes: list[tuple[str, float, float]] = []
        for geo_name in shared_geos:
            start_value = start_df.loc[geo_name, "metric_value"]
            end_value = end_df.loc[geo_name, "metric_value"]
            if not isinstance(start_value, Real) or not isinstance(end_value, Real):
                continue
            absolute_change = float(end_value) - float(start_value)
            pct_change = 0.0 if float(start_value) == 0.0 else absolute_change / float(start_value)
            changes.append((geo_name, absolute_change, pct_change))

        if not changes:
            return (
                f"Across {start_period} to {end_period}, {lead_geo} led the selected geographies "
                f"at {self._format_value(lead_value)}."
            )

        biggest_gain_geo, biggest_gain_value, _ = max(changes, key=lambda item: item[1])
        fastest_growth_geo, _, fastest_growth_pct = max(changes, key=lambda item: item[2])
        return (
            f"Across {start_period} to {end_period}, {lead_geo} finished highest for {metric_label} "
            f"at {self._format_value(lead_value)}. {biggest_gain_geo} added the most in absolute terms "
            f"({self._format_value(biggest_gain_value)}), while {fastest_growth_geo} grew fastest "
            f"at {self._format_percent(fastest_growth_pct)}."
        )
