"""Pipeline for normalized curated web-scrape inputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import difflib
from pathlib import Path
import re
from typing import Any
import unicodedata

import pandas as pd

from nyc_property_finder.curated_poi.google_takeout.build_dim import DIM_USER_POI_V2_COLUMNS, build_dim_user_poi_v2
from nyc_property_finder.curated_poi.google_takeout.cache import merge_resolution_cache, read_resolution_cache, write_resolution_cache
from nyc_property_finder.curated_poi.google_takeout.client import get_place_details, search_text_place_id
from nyc_property_finder.curated_poi.google_takeout.config import (
    DEFAULT_DETAILS_CACHE_PATH,
    DEFAULT_MAX_DETAILS_CALLS,
    DEFAULT_MAX_TEXT_SEARCH_CALLS,
    DEFAULT_RESOLUTION_CACHE_PATH,
)
from nyc_property_finder.curated_poi.google_takeout.enrich import EnrichReport, enrich_place_details
from nyc_property_finder.curated_poi.google_takeout.enrich import DetailsFetcher
from nyc_property_finder.curated_poi.google_takeout.resolve import ResolveReport
from nyc_property_finder.curated_poi.shared.places import ResolutionFetcher
from nyc_property_finder.curated_poi.google_takeout.summary import (
    build_summary,
    write_qa_csv,
    write_summary,
)
from nyc_property_finder.curated_poi.shared.places import build_canonical_dim_from_stages, resolve_source_dataframe
from nyc_property_finder.curated_poi.web_scraping.normalize import read_normalized_scrape_csv
from nyc_property_finder.services.config import load_config
from nyc_property_finder.services.duckdb_service import DuckDBService

WEB_SCRAPE_STAGE_TABLE = "stg_user_poi_web_scrape"
GOOGLE_TAKEOUT_STAGE_TABLE = "stg_user_poi_google_takeout"
DEFAULT_SUMMARY_PATH = Path("data/interim/google_places/web_scrape_summary.json")
DEFAULT_QA_PATH = Path("data/interim/google_places/web_scrape_qa.csv")


@dataclass(frozen=True)
class WebScrapePipelineReport:
    """Summary of a complete normalized-scrape ingestion run."""

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
    canonical_pre_resolve_matches: int

    def to_dict(self) -> dict[str, Any]:
        output = asdict(self)
        output["resolve"] = self.resolve.to_dict()
        output["enrich"] = self.enrich.to_dict()
        return output


def run(
    csv_path: str | Path,
    database_path: str | Path | None = None,
    resolution_cache_path: str | Path = DEFAULT_RESOLUTION_CACHE_PATH,
    details_cache_path: str | Path = DEFAULT_DETAILS_CACHE_PATH,
    max_text_search_calls: int = DEFAULT_MAX_TEXT_SEARCH_CALLS,
    max_details_calls: int = DEFAULT_MAX_DETAILS_CALLS,
    api_key: str | None = None,
    resolution_fetcher: ResolutionFetcher = search_text_place_id,
    details_fetcher: DetailsFetcher = get_place_details,
    write_database: bool = True,
    table_name: str = "dim_user_poi_v2",
    schema: str = "property_explorer_gold",
    summary_path: str | Path = DEFAULT_SUMMARY_PATH,
    qa_path: str | Path = DEFAULT_QA_PATH,
) -> WebScrapePipelineReport:
    """Resolve, enrich, stage, and merge one normalized scrape CSV."""

    csv_path = Path(csv_path)
    source_rows = read_normalized_scrape_csv(csv_path)
    canonical_match_count = 0
    resolved_database_path = str(database_path) if database_path is not None else None
    possible_canonical_duplicates = pd.DataFrame()

    if database_path is None and write_database:
        database_path = load_config()["settings"]["database_path"]
        resolved_database_path = str(database_path)
    if database_path is not None:
        canonical_match_count = _prime_resolution_cache_from_canonical(
            source_rows=source_rows,
            database_path=database_path,
            resolution_cache_path=resolution_cache_path,
            schema=schema,
            table_name=table_name,
        )
        possible_canonical_duplicates = _find_possible_canonical_duplicates(
            source_rows=source_rows,
            database_path=database_path,
            schema=schema,
            table_name=table_name,
        )

    resolve_report = resolve_source_dataframe(
        source_rows,
        input_path=str(csv_path),
        api_key=api_key,
        resolution_cache_path=resolution_cache_path,
        max_text_search_calls=max_text_search_calls,
        fetcher=resolution_fetcher,
    )
    enrich_report = enrich_place_details(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        max_details_calls=max_details_calls,
        api_key=api_key,
        fetcher=details_fetcher,
    )
    source_record_ids = set(source_rows["source_record_id"].astype(str).tolist())
    web_scrape_stage = build_dim_user_poi_v2(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        source_record_ids=source_record_ids,
    )
    dim_user_poi = web_scrape_stage.copy()

    if write_database:
        with DuckDBService(database_path) as duckdb_service:
            existing_google_takeout_stage = _read_existing_stage(
                duckdb_service=duckdb_service,
                schema=schema,
                table_name=GOOGLE_TAKEOUT_STAGE_TABLE,
            )
            existing_web_scrape_stage = _read_existing_stage(
                duckdb_service=duckdb_service,
                schema=schema,
                table_name=WEB_SCRAPE_STAGE_TABLE,
            )
            merged_web_scrape_stage = build_canonical_dim_from_stages(
                [existing_web_scrape_stage, web_scrape_stage],
                canonical_columns=DIM_USER_POI_V2_COLUMNS,
            )
            dim_user_poi = build_canonical_dim_from_stages(
                [existing_google_takeout_stage, merged_web_scrape_stage],
                canonical_columns=DIM_USER_POI_V2_COLUMNS,
            )
            duckdb_service.write_dataframe(
                merged_web_scrape_stage,
                table_name=WEB_SCRAPE_STAGE_TABLE,
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
    summary["possible_canonical_duplicate_rows"] = int(len(possible_canonical_duplicates))
    summary["review_recommendations"] = _augment_review_recommendations(
        summary.get("review_recommendations", []),
        possible_canonical_duplicates,
    )
    write_summary(summary, summary_path)
    write_qa_csv(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        path=qa_path,
        source_record_ids=source_record_ids,
    )
    _append_possible_duplicate_rows_to_qa_csv(
        qa_path=qa_path,
        possible_duplicates=possible_canonical_duplicates,
    )

    return WebScrapePipelineReport(
        resolve=resolve_report,
        enrich=enrich_report,
        dim_rows=len(dim_user_poi),
        dim_with_coordinates=int(dim_user_poi[["lat", "lon"]].notna().all(axis=1).sum()) if not dim_user_poi.empty else 0,
        database_path=resolved_database_path,
        stage_table_name=f"{schema}.{WEB_SCRAPE_STAGE_TABLE}",
        table_name=f"{schema}.{table_name}",
        summary_path=str(summary_path),
        qa_path=str(qa_path),
        summary=summary,
        canonical_pre_resolve_matches=canonical_match_count,
    )


def _read_existing_stage(duckdb_service: DuckDBService, schema: str, table_name: str) -> pd.DataFrame:
    try:
        frame = duckdb_service.query_df(f"SELECT * FROM {schema}.{table_name}")
    except Exception:
        return pd.DataFrame(columns=DIM_USER_POI_V2_COLUMNS)
    if frame.empty:
        return pd.DataFrame(columns=DIM_USER_POI_V2_COLUMNS)
    for column in DIM_USER_POI_V2_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA
    return frame[DIM_USER_POI_V2_COLUMNS]


def _prime_resolution_cache_from_canonical(
    *,
    source_rows: pd.DataFrame,
    database_path: str | Path,
    resolution_cache_path: str | Path,
    schema: str,
    table_name: str,
) -> int:
    canonical = _read_existing_canonical_dim(
        database_path=database_path,
        schema=schema,
        table_name=table_name,
    )
    if canonical.empty or source_rows.empty:
        return 0

    cache = read_resolution_cache(resolution_cache_path)
    cached_source_ids = set(cache.loc[cache["google_place_id"] != "", "source_record_id"])
    unresolved = source_rows[~source_rows["source_record_id"].isin(cached_source_ids)].copy()
    if unresolved.empty:
        return 0

    canonical_lookup: dict[tuple[str, str], str] = {}
    for _, row in canonical.iterrows():
        google_place_id = str(row.get("google_place_id", "")).strip()
        if not google_place_id:
            continue
        key = (
            _normalize_match_text(row.get("input_title", "") or row.get("name", "")),
            _normalize_match_address(row.get("address", "")),
        )
        if key[0] and key[1]:
            canonical_lookup.setdefault(key, google_place_id)

    if not canonical_lookup:
        return 0

    matched_rows: list[dict[str, str]] = []
    for _, row in unresolved.iterrows():
        key = (
            _normalize_match_text(row.get("input_title", "")),
            _normalize_match_address(row.get("note", "") or row.get("raw_address", "")),
        )
        google_place_id = canonical_lookup.get(key)
        if not google_place_id:
            continue
        matched_rows.append(
            {
                "source_record_id": str(row.get("source_record_id", "")),
                "source_system": str(row.get("source_system", "")),
                "source_file": str(row.get("source_file", "")),
                "source_list_name": str(row.get("source_list_name", "")),
                "category": str(row.get("category", "")),
                "subcategory": str(row.get("subcategory", "")),
                "detail_level_3": str(row.get("detail_level_3", "")),
                "input_title": str(row.get("input_title", "")),
                "note": str(row.get("note", "")),
                "tags": str(row.get("tags", "")),
                "comment": str(row.get("comment", "")),
                "source_url": str(row.get("source_url", "")),
                "search_query": str(row.get("search_query", "")),
                "google_place_id": google_place_id,
                "match_status": "canonical_exact_match",
            }
        )

    if not matched_rows:
        return 0

    primed_cache = merge_resolution_cache(cache, pd.DataFrame(matched_rows))
    write_resolution_cache(primed_cache, resolution_cache_path)
    return len(matched_rows)


def _read_existing_canonical_dim(
    *,
    database_path: str | Path,
    schema: str,
    table_name: str,
) -> pd.DataFrame:
    try:
        with DuckDBService(database_path, read_only=True) as duckdb_service:
            return duckdb_service.query_df(
                f"""
                SELECT name, input_title, address, google_place_id
                FROM {schema}.{table_name}
                """
            )
    except Exception:
        return pd.DataFrame(columns=["name", "input_title", "address", "google_place_id"])


def _normalize_match_text(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _normalize_match_address(value: object) -> str:
    text = _normalize_match_text(value)
    text = re.sub(r"\busa\b", "", text)
    return " ".join(text.split())


def _same_house_number_and_zip(left: str, right: str) -> bool:
    left_house = re.search(r"\b(\d{1,6})\b", left)
    right_house = re.search(r"\b(\d{1,6})\b", right)
    left_zip = re.search(r"\b(\d{5})\b", left)
    right_zip = re.search(r"\b(\d{5})\b", right)
    return bool(
        left_house
        and right_house
        and left_zip
        and right_zip
        and left_house.group(1) == right_house.group(1)
        and left_zip.group(1) == right_zip.group(1)
    )


def _find_possible_canonical_duplicates(
    *,
    source_rows: pd.DataFrame,
    database_path: str | Path,
    schema: str,
    table_name: str,
) -> pd.DataFrame:
    canonical = _read_existing_canonical_dim(
        database_path=database_path,
        schema=schema,
        table_name=table_name,
    )
    if canonical.empty or source_rows.empty:
        return pd.DataFrame(columns=_possible_duplicate_columns())

    rows: list[dict[str, str]] = []
    for _, source_row in source_rows.iterrows():
        source_title = _normalize_match_text(source_row.get("input_title", ""))
        source_address = _normalize_match_address(source_row.get("note", "") or source_row.get("raw_address", ""))
        if not source_title or not source_address:
            continue

        best_candidate: dict[str, str] | None = None
        best_score = 0.0
        for _, canonical_row in canonical.iterrows():
            canonical_title = _normalize_match_text(canonical_row.get("input_title", "") or canonical_row.get("name", ""))
            canonical_address = _normalize_match_address(canonical_row.get("address", ""))
            if not canonical_title or not canonical_address:
                continue
            if source_title == canonical_title and source_address == canonical_address:
                continue

            title_similarity = _similarity(source_title, canonical_title)
            address_similarity = _similarity(source_address, canonical_address)
            reason = _possible_duplicate_reason(
                source_title=source_title,
                canonical_title=canonical_title,
                source_address=source_address,
                canonical_address=canonical_address,
                title_similarity=title_similarity,
                address_similarity=address_similarity,
            )
            if reason is None:
                continue

            score = max(title_similarity, address_similarity)
            if score < best_score:
                continue
            best_score = score
            best_candidate = {
                "qa_type": "possible_canonical_duplicate",
                "google_place_id": str(canonical_row.get("google_place_id", "")),
                "source_row_count": "",
                "input_titles": str(source_row.get("input_title", "")),
                "source_list_names": str(source_row.get("source_list_name", "")),
                "note": (
                    f"{reason}; source_address={source_row.get('note', '')}; "
                    f"canonical_name={canonical_row.get('name', '')}; canonical_address={canonical_row.get('address', '')}"
                ),
            }

        if best_candidate is not None:
            rows.append(best_candidate)

    if not rows:
        return pd.DataFrame(columns=_possible_duplicate_columns())

    output = pd.DataFrame(rows, columns=_possible_duplicate_columns())
    return output.drop_duplicates(subset=["input_titles", "google_place_id", "note"]).reset_index(drop=True)


def _possible_duplicate_reason(
    *,
    source_title: str,
    canonical_title: str,
    source_address: str,
    canonical_address: str,
    title_similarity: float,
    address_similarity: float,
) -> str | None:
    if source_address == canonical_address and source_title != canonical_title:
        return "same normalized address, different title"
    if source_title == canonical_title and source_address != canonical_address and address_similarity >= 0.72:
        return "same normalized title, similar address"
    if _same_house_number_and_zip(source_address, canonical_address) and title_similarity >= 0.72:
        return "same house number and zip, related title"
    if address_similarity >= 0.94 and title_similarity >= 0.72:
        return "very similar address and related title"
    if title_similarity >= 0.9 and address_similarity >= 0.82:
        return "similar normalized title and address"
    return None


def _similarity(left: str, right: str) -> float:
    return difflib.SequenceMatcher(a=left, b=right).ratio()


def _possible_duplicate_columns() -> list[str]:
    return [
        "qa_type",
        "google_place_id",
        "source_row_count",
        "input_titles",
        "source_list_names",
        "note",
    ]


def _append_possible_duplicate_rows_to_qa_csv(
    *,
    qa_path: str | Path,
    possible_duplicates: pd.DataFrame,
) -> None:
    qa_path = Path(qa_path)
    if possible_duplicates.empty:
        return

    base = pd.read_csv(qa_path, dtype=str).fillna("") if qa_path.exists() else pd.DataFrame(columns=_possible_duplicate_columns())
    combined = pd.concat([base, possible_duplicates], ignore_index=True)
    combined = combined[_possible_duplicate_columns()].drop_duplicates().reset_index(drop=True)
    combined.to_csv(qa_path, index=False)


def _augment_review_recommendations(existing: list[str], possible_duplicates: pd.DataFrame) -> list[str]:
    recommendations = list(existing)
    if not possible_duplicates.empty:
        note = "Review possible_canonical_duplicate rows in web_scrape_qa.csv before approving the article."
        if note not in recommendations:
            if recommendations == ["No duplicate place IDs or missing coordinates were detected."]:
                recommendations = []
            recommendations.append(note)
    if not recommendations:
        recommendations.append("No duplicate place IDs, missing coordinates, or possible canonical overlaps were detected.")
    return recommendations
