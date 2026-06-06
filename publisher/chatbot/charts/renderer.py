"""Subprocess bridge for rendering approved charts through the R visual library."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any

try:
    import pandas as pd
except ImportError:  # pragma: no cover - optional dependency in bare environments
    pd = None

from chatbot.charts.profiler import ResultProfile
from chatbot.charts.selector import ChartSelection
from chatbot.intent.parser import QueryPlan
from chatbot.query.catalogs import REPO_ROOT, load_semantic_catalogs


FOUNDATIONS_DIR = Path(os.environ["FOUNDATIONS_PATH"])
RENDER_SCRIPT_DIR = FOUNDATIONS_DIR / "visual_library" / "shared" / "render"
SUPPORTED_CHART_TYPES = {
    "bar",
    "line",
    "scatter",
    "boxplot",
    "heatmap_table",
    "slopegraph",
}


@dataclass
class RenderedChart:
    chart_type: str
    output_path: str
    config_path: str
    data_path: str
    command: list[str]


class ChartRenderer:
    """Render a chart by writing temp artifacts and invoking the R renderer."""

    def __init__(self, rscript_bin: str = "Rscript") -> None:
        self.rscript_bin = rscript_bin
        self.catalogs = load_semantic_catalogs()

    def render(
        self,
        dataframe: pd.DataFrame,
        *,
        selection: ChartSelection,
        query_plan: QueryPlan,
        profile: ResultProfile,
        sql: str | None = None,
    ) -> RenderedChart:
        if pd is None:
            raise ImportError("pandas is required to render charts")
        if dataframe.empty:
            raise ValueError("Cannot render a chart from an empty result set")
        if selection.chart_type not in SUPPORTED_CHART_TYPES:
            raise ValueError(f"Unsupported chart type: {selection.chart_type}")

        render_dir = Path(tempfile.mkdtemp(prefix="metro_chart_"))
        data_path = render_dir / "chart_data.csv"
        config_path = render_dir / "chart_config.json"
        output_path = render_dir / "chart_output.png"
        runner_path = render_dir / "run_render.R"

        render_frame = self._prepare_dataframe(
            dataframe.copy(),
            chart_type=selection.chart_type,
            profile=profile,
            query_plan=query_plan,
        )
        render_frame.to_csv(data_path, index=False)

        config = self._build_config(
            dataframe=render_frame,
            chart_type=selection.chart_type,
            query_plan=query_plan,
            profile=profile,
            sql=sql,
        )
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        runner_path.write_text(self._runner_script(), encoding="utf-8")

        script_path = RENDER_SCRIPT_DIR / f"render_{selection.chart_type}.R"
        command = [
            self.rscript_bin,
            str(runner_path),
            str(script_path),
            str(config_path),
            str(data_path),
            str(output_path),
            selection.chart_type,
        ]
        subprocess.run(
            command,
            cwd=str(FOUNDATIONS_DIR),
            check=True,
            capture_output=True,
            text=True,
        )

        return RenderedChart(
            chart_type=selection.chart_type,
            output_path=str(output_path),
            config_path=str(config_path),
            data_path=str(data_path),
            command=command,
        )

    def _runner_script(self) -> str:
        return """
args <- commandArgs(trailingOnly = TRUE)
script_path <- args[[1]]
config_path <- args[[2]]
data_path <- args[[3]]
output_path <- args[[4]]
chart_type <- args[[5]]

source(script_path)

config <- jsonlite::fromJSON(config_path, simplifyVector = TRUE)
data <- utils::read.csv(data_path, stringsAsFactors = FALSE)
render_fn <- get(paste0("render_", chart_type), mode = "function")
plot <- render_fn(data, config = config)

width <- if (!is.null(config$width)) config$width else 11
height <- if (!is.null(config$height)) config$height else 7
dpi <- if (!is.null(config$dpi)) config$dpi else 300

ggplot2::ggsave(output_path, plot = plot, width = width, height = height, dpi = dpi, bg = "white")
""".strip()

    def _prepare_dataframe(
        self,
        dataframe: pd.DataFrame,
        *,
        chart_type: str,
        profile: ResultProfile,
        query_plan: QueryPlan,
    ) -> pd.DataFrame:
        if "metric_label" not in dataframe.columns:
            dataframe["metric_label"] = self._metric_label(query_plan)

        if chart_type == "line":
            if "period" not in dataframe.columns and "year" in dataframe.columns:
                dataframe["period"] = dataframe["year"]
            if "highlight_flag" not in dataframe.columns:
                dataframe["highlight_flag"] = False
            return dataframe

        if chart_type == "bar":
            if "growth_value" in dataframe.columns:
                dataframe["metric_value"] = dataframe["growth_value"]
                window_years = query_plan.window_years or dataframe.get("window_years")
                if isinstance(window_years, int):
                    dataframe["metric_label"] = f"{window_years}-Year Growth Rate"
                else:
                    dataframe["metric_label"] = "Growth Rate"
            if "highlight_flag" not in dataframe.columns:
                dataframe["highlight_flag"] = dataframe.get("comparison_group", "") == "target"
            if "comparison_group" in dataframe.columns:
                benchmark_rows = dataframe[dataframe["comparison_group"] == "benchmark"]
                if not benchmark_rows.empty:
                    dataframe["benchmark_value"] = float(benchmark_rows["metric_value"].iloc[0])
                    dataframe["show_benchmark"] = True
            return dataframe

        if chart_type == "boxplot":
            dataframe["box_group"] = dataframe.get("geo_level", query_plan.geo_level or "geography")
            if "highlight_flag" not in dataframe.columns:
                target_geo_id = getattr(query_plan, "target_geo_id", None)
                if "geo_id" in dataframe.columns and target_geo_id is not None:
                    dataframe["highlight_flag"] = dataframe["geo_id"].astype(str) == str(target_geo_id)
                else:
                    dataframe["highlight_flag"] = False
            return dataframe

        if chart_type == "slopegraph":
            if "period" not in dataframe.columns and "year" in dataframe.columns:
                dataframe["period"] = dataframe["year"]
            if "highlight_flag" not in dataframe.columns:
                dataframe["highlight_flag"] = False
            return dataframe

        if chart_type == "scatter":
            return dataframe

        if chart_type == "heatmap_table":
            dataframe["row_label"] = dataframe.get("geo_name", dataframe.index.astype(str))
            dataframe["column_label"] = dataframe.get("metric_label", "Metric")
            dataframe["fill_value"] = dataframe.get("metric_value")
            dataframe["missing_flag"] = dataframe["fill_value"].isna()
            dataframe["fill_label"] = dataframe["metric_value"].astype(str)
            return dataframe

        return dataframe

    def _build_config(
        self,
        *,
        dataframe: pd.DataFrame,
        chart_type: str,
        query_plan: QueryPlan,
        profile: ResultProfile,
        sql: str | None,
    ) -> dict[str, Any]:
        metric_label = self._metric_label(query_plan)
        title = self._title_for_chart(chart_type, dataframe, metric_label, query_plan)
        subtitle = self._subtitle_for_chart(profile, query_plan)
        config: dict[str, Any] = {
            "title": title,
            "subtitle": subtitle,
            "caption_side_note": f"Generated from approved {query_plan.question_type} query.",
            "caption_footer_note": None if sql is None else "SQL attached in the application output.",
            "width": 11,
            "height": 7,
            "dpi": 300,
        }

        if chart_type == "bar":
            config["label_style"] = self._label_style(query_plan)
            config["sort_desc"] = query_plan.sort_direction != "asc"
            if "benchmark_value" in dataframe.columns:
                benchmark_values = dataframe["benchmark_value"].dropna().unique().tolist()
                if benchmark_values:
                    config["show_benchmark"] = True
                    config["benchmark_value"] = float(benchmark_values[0])
                    config["benchmark_label"] = "Benchmark"

        if chart_type == "line":
            config["label_style"] = self._label_style(query_plan)
            config["color_mode"] = "highlight_flag" if dataframe["highlight_flag"].any() else "geo_name"

        if chart_type == "boxplot":
            config["value_field"] = "metric_value"
            config["group_field"] = "box_group"
            config["group_label"] = query_plan.geo_level or "geography"
            config["label_style"] = self._label_style(query_plan)
            config["show_highlights"] = bool(dataframe["highlight_flag"].any())

        if chart_type == "slopegraph":
            config["label_style"] = self._label_style(query_plan)

        if chart_type == "heatmap_table":
            config["legend_title"] = metric_label

        if chart_type == "scatter":
            config["title"] = title
            config["subtitle"] = subtitle
            config["highlight_mode"] = "labels"
            config["add_trend_line"] = True

        return config

    def _metric_label(self, query_plan: QueryPlan) -> str:
        metric_id = query_plan.metric_id or query_plan.base_metric_id
        if metric_id is None:
            return "Metric"
        metric = self.catalogs["metrics"].get(metric_id)
        if metric is None:
            return metric_id
        return metric["display_name"]

    def _label_style(self, query_plan: QueryPlan) -> str:
        if query_plan.template_id == "growth":
            return "percent"
        metric_id = query_plan.metric_id or query_plan.base_metric_id
        metric = None if metric_id is None else self.catalogs["metrics"].get(metric_id)
        unit_format = None if metric is None else metric.get("unit_format")
        if unit_format in {"percent"}:
            return "percent"
        if unit_format in {"currency"}:
            return "dollar"
        if unit_format in {"integer"}:
            return "integer"
        return "number"

    def _title_for_chart(
        self,
        chart_type: str,
        dataframe: pd.DataFrame,
        metric_label: str,
        query_plan: QueryPlan,
    ) -> str:
        if chart_type == "bar":
            year = query_plan.year or query_plan.end_year
            geo_level = (query_plan.geo_level or query_plan.target_geo_level or "geography").title()
            if year is not None:
                return f"{metric_label} across {geo_level}s in {year}"
            return f"{metric_label} across selected {geo_level}s"
        if chart_type == "line":
            names = dataframe["geo_name"].dropna().unique().tolist() if "geo_name" in dataframe.columns else []
            if len(names) == 1:
                return f"{metric_label}: {names[0]}"
            return f"{metric_label} over time"
        if chart_type == "boxplot":
            geo_level = (query_plan.geo_level or "geography").title()
            return f"{metric_label} distribution across {geo_level}s"
        if chart_type == "slopegraph":
            return f"{metric_label} change across selected geographies"
        if chart_type == "scatter":
            return f"{metric_label} relationship"
        return metric_label

    def _subtitle_for_chart(self, profile: ResultProfile, query_plan: QueryPlan) -> str | None:
        parts: list[str] = []
        if profile.has_time_series and query_plan.start_year and query_plan.end_year:
            parts.append(f"Period: {query_plan.start_year}-{query_plan.end_year}")
        elif query_plan.year is not None:
            parts.append(f"Year: {query_plan.year}")
        if query_plan.geo_level is not None:
            parts.append(f"Level: {query_plan.geo_level}")
        return " | ".join(parts) or None
