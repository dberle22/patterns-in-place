"""High-level Google Places POI v2 pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from nyc_property_finder.curated_poi.google_takeout.build_dim import DIM_USER_POI_V2_COLUMNS, build_dim_user_poi_v2
from nyc_property_finder.curated_poi.google_takeout.config import (
    DEFAULT_DETAILS_CACHE_PATH,
    DEFAULT_MAX_DETAILS_CALLS,
    DEFAULT_MAX_TEXT_SEARCH_CALLS,
    DEFAULT_RESOLUTION_CACHE_PATH,
    DEFAULT_SEARCH_CONTEXT,
)
from nyc_property_finder.curated_poi.google_takeout.dry_run import iter_input_csv_paths, plan_dry_run
from nyc_property_finder.curated_poi.google_takeout.enrich import EnrichReport, enrich_place_details
from nyc_property_finder.curated_poi.google_takeout.parse_takeout import parse_google_places_saved_list_csv
from nyc_property_finder.curated_poi.google_takeout.resolve import ResolveReport, resolve_place_ids
from nyc_property_finder.curated_poi.google_takeout.summary import (
    DEFAULT_QA_PATH,
    DEFAULT_SUMMARY_PATH,
    build_summary,
    write_qa_csv,
    write_summary,
)
from nyc_property_finder.curated_poi.shared.places import build_canonical_dim_from_stages
from nyc_property_finder.services.config import load_config
from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.curated_poi.google_takeout.cache import read_resolution_cache

GOOGLE_TAKEOUT_STAGE_TABLE = "stg_user_poi_google_takeout"


@dataclass(frozen=True)
class GooglePlacesPoiPipelineReport:
    """Summary of a complete Google Places POI v2 pipeline run."""

    resolve: ResolveReport
    enrich: EnrichReport
    dim_rows: int
    dim_with_coordinates: int
    database_path: str | None
    stage_table_name: str
    table_name: str
    summary_path: str
    qa_path: str
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict for logging, notebooks, or future CLI output."""

        output = asdict(self)
        output["resolve"] = self.resolve.to_dict()
        output["enrich"] = self.enrich.to_dict()
        return output


def run(
    csv_path: str | Path,
    database_path: str | Path | None = None,
    resolution_cache_path: str | Path = DEFAULT_RESOLUTION_CACHE_PATH,
    details_cache_path: str | Path = DEFAULT_DETAILS_CACHE_PATH,
    search_context: str = DEFAULT_SEARCH_CONTEXT,
    max_text_search_calls: int = DEFAULT_MAX_TEXT_SEARCH_CALLS,
    max_details_calls: int = DEFAULT_MAX_DETAILS_CALLS,
    api_key: str | None = None,
    write_database: bool = True,
    table_name: str = "dim_user_poi_v2",
    schema: str = "property_explorer_gold",
    summary_path: str | Path = DEFAULT_SUMMARY_PATH,
    qa_path: str | Path = DEFAULT_QA_PATH,
) -> GooglePlacesPoiPipelineReport:
    """Resolve, enrich, build, and optionally write dim_user_poi_v2."""

    resolve_report = resolve_place_ids(
        csv_path=csv_path,
        resolution_cache_path=resolution_cache_path,
        search_context=search_context,
        max_text_search_calls=max_text_search_calls,
        api_key=api_key,
    )
    enrich_report = enrich_place_details(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        max_details_calls=max_details_calls,
        api_key=api_key,
    )
    source_record_ids = _source_record_ids_for_csv_paths([Path(csv_path)], search_context=search_context)
    return _finalize_pipeline_report(
        resolve_report=resolve_report,
        enrich_report=enrich_report,
        database_path=database_path,
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        source_record_ids=source_record_ids,
        write_database=write_database,
        table_name=table_name,
        schema=schema,
        summary_path=summary_path,
        qa_path=qa_path,
    )


def run_input_dir(
    input_dir: str | Path,
    database_path: str | Path | None = None,
    resolution_cache_path: str | Path = DEFAULT_RESOLUTION_CACHE_PATH,
    details_cache_path: str | Path = DEFAULT_DETAILS_CACHE_PATH,
    search_context: str = DEFAULT_SEARCH_CONTEXT,
    max_text_search_calls: int = DEFAULT_MAX_TEXT_SEARCH_CALLS,
    max_details_calls: int = DEFAULT_MAX_DETAILS_CALLS,
    api_key: str | None = None,
    write_database: bool = True,
    table_name: str = "dim_user_poi_v2",
    schema: str = "property_explorer_gold",
    summary_path: str | Path = DEFAULT_SUMMARY_PATH,
    qa_path: str | Path = DEFAULT_QA_PATH,
) -> GooglePlacesPoiPipelineReport:
    """Resolve, enrich, build, and optionally write dim_user_poi_v2 from a directory."""

    input_dir = Path(input_dir)
    csv_paths = iter_input_csv_paths(input_dir)
    if not csv_paths:
        raise ValueError(f"No CSV files found under input_dir: {input_dir}")

    dry_runs = [
        plan_dry_run(
            csv_path=csv_path,
            resolution_cache_path=resolution_cache_path,
            details_cache_path=details_cache_path,
            search_context=search_context,
        )
        for csv_path in csv_paths
    ]
    estimated_text_search_calls = sum(report.estimated_text_search_calls for report in dry_runs)
    if estimated_text_search_calls > max_text_search_calls:
        raise ValueError(
            "Resolve run would exceed max_text_search_calls: "
            f"{estimated_text_search_calls} needed, cap is {max_text_search_calls}."
        )

    initial_resolved_cache_rows = _resolved_cache_row_count(resolution_cache_path)
    resolve_reports = [
        resolve_place_ids(
            csv_path=csv_path,
            resolution_cache_path=resolution_cache_path,
            search_context=search_context,
            max_text_search_calls=max_text_search_calls,
            api_key=api_key,
        )
        for csv_path in csv_paths
    ]
    aggregate_resolve_report = ResolveReport(
        input_path=str(input_dir),
        resolution_cache_path=str(resolution_cache_path),
        parsed_rows=sum(report.parsed_rows for report in resolve_reports),
        input_cache_hits=sum(report.input_cache_hits for report in resolve_reports),
        existing_resolved_cache_rows=initial_resolved_cache_rows,
        attempted_text_search_calls=sum(report.attempted_text_search_calls for report in resolve_reports),
        max_text_search_calls=max_text_search_calls,
        resolved=sum(report.resolved for report in resolve_reports),
        no_match=sum(report.no_match for report in resolve_reports),
    )

    enrich_report = enrich_place_details(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        max_details_calls=max_details_calls,
        api_key=api_key,
    )
    source_record_ids = _source_record_ids_for_csv_paths(csv_paths, search_context=search_context)
    return _finalize_pipeline_report(
        resolve_report=aggregate_resolve_report,
        enrich_report=enrich_report,
        database_path=database_path,
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        source_record_ids=source_record_ids,
        write_database=write_database,
        table_name=table_name,
        schema=schema,
        summary_path=summary_path,
        qa_path=qa_path,
    )


def _finalize_pipeline_report(
    resolve_report: ResolveReport,
    enrich_report: EnrichReport,
    database_path: str | Path | None,
    resolution_cache_path: str | Path,
    details_cache_path: str | Path,
    source_record_ids: set[str],
    write_database: bool,
    table_name: str,
    schema: str,
    summary_path: str | Path,
    qa_path: str | Path,
) -> GooglePlacesPoiPipelineReport:
    """Build, optionally write, and summarize the final dim output."""

    google_takeout_stage = build_dim_user_poi_v2(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        source_record_ids=source_record_ids,
    )
    dim_user_poi = build_canonical_dim_from_stages([google_takeout_stage], canonical_columns=DIM_USER_POI_V2_COLUMNS)

    resolved_database_path = str(database_path) if database_path is not None else None
    if write_database:
        if database_path is None:
            database_path = load_config()["settings"]["database_path"]
        resolved_database_path = str(database_path)
        with DuckDBService(database_path) as duckdb_service:
            duckdb_service.write_dataframe(
                google_takeout_stage,
                table_name=GOOGLE_TAKEOUT_STAGE_TABLE,
                schema=schema,
                if_exists="replace",
            )
            duckdb_service.write_dataframe(
                dim_user_poi,
                table_name=table_name,
                schema=schema,
                if_exists="replace",
            )

    summary = build_summary(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        source_record_ids=source_record_ids,
    )
    write_summary(summary, summary_path)
    write_qa_csv(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        path=qa_path,
        source_record_ids=source_record_ids,
    )

    return GooglePlacesPoiPipelineReport(
        resolve=resolve_report,
        enrich=enrich_report,
        dim_rows=len(dim_user_poi),
        dim_with_coordinates=int(dim_user_poi[["lat", "lon"]].notna().all(axis=1).sum()),
        database_path=resolved_database_path,
        stage_table_name=f"{schema}.{GOOGLE_TAKEOUT_STAGE_TABLE}",
        table_name=f"{schema}.{table_name}",
        summary_path=str(summary_path),
        qa_path=str(qa_path),
        summary=summary,
    )


def _resolved_cache_row_count(resolution_cache_path: str | Path) -> int:
    cache = read_resolution_cache(resolution_cache_path)
    if cache.empty:
        return 0
    return int((cache["google_place_id"] != "").sum())


def _source_record_ids_for_csv_paths(csv_paths: list[Path], search_context: str) -> set[str]:
    source_record_ids: set[str] = set()
    for csv_path in csv_paths:
        parsed = parse_google_places_saved_list_csv(csv_path, search_context=search_context)
        source_record_ids.update(parsed["source_record_id"].astype(str).tolist())
    return source_record_ids
