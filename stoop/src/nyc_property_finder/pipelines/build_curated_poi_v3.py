"""Promote classified curated places into the app-facing dim_user_poi_v3 table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from nyc_property_finder.services.config import PROJECT_ROOT, load_config
from nyc_property_finder.services.duckdb_service import DuckDBService


SOURCE_TABLE = "property_explorer_gold.dim_user_poi_v2"
CLASSIFIED_TABLE = "property_classification_mart.curated_places_classified"
TARGET_SCHEMA = "property_explorer_gold"
TARGET_TABLE = "dim_user_poi_v3"

V3_COLUMNS = [
    "poi_id",
    "source_system",
    "source_systems",
    "primary_source_system",
    "source_record_id",
    "source_list_names",
    "category",
    "subcategory",
    "detail_level_3",
    "categories",
    "primary_category",
    "subcategories",
    "primary_subcategory",
    "detail_level_3_values",
    "primary_detail_level_3",
    "name",
    "input_title",
    "note",
    "tags",
    "comment",
    "source_url",
    "google_place_id",
    "match_status",
    "address",
    "lat",
    "lon",
    "has_place_details",
    "details_fetched_at",
    "rating",
    "user_rating_count",
    "business_status",
    "editorial_summary",
    "editorial_summary_language_code",
    "price_level",
    "website_uri",
    "original_category",
    "original_subcategory",
    "original_detail_level_3",
    "classification_method",
    "classification_confidence",
    "classification_score",
    "classification_run_at",
]


def _default_database_path() -> Path:
    settings = load_config()["settings"]
    return PROJECT_ROOT / settings["database_path"]


def _json_array(value: object) -> str:
    if value is None or pd.isna(value):
        return json.dumps([])
    text = str(value).strip()
    if not text:
        return json.dumps([])
    return json.dumps([text])


def build_dim_user_poi_v3(source: pd.DataFrame, classified: pd.DataFrame) -> pd.DataFrame:
    """Return a v3 curated place dataframe with promoted classifications."""

    merged = source.merge(
        classified[
            [
                "poi_id",
                "final_category",
                "final_subcategory",
                "final_detail_level_3",
                "original_category",
                "original_subcategory",
                "original_detail_level_3",
                "classification_method",
                "classification_confidence",
                "classification_score",
                "classification_run_at",
            ]
        ],
        on="poi_id",
        how="left",
    )

    merged["category"] = merged["final_category"].combine_first(merged.get("category"))
    merged["primary_category"] = merged["final_category"].combine_first(merged.get("primary_category"))
    merged["subcategory"] = merged["final_subcategory"].combine_first(merged.get("subcategory"))
    merged["primary_subcategory"] = merged["final_subcategory"].combine_first(merged.get("primary_subcategory"))
    merged["detail_level_3"] = merged["final_detail_level_3"].combine_first(merged.get("detail_level_3"))
    merged["primary_detail_level_3"] = merged["final_detail_level_3"].combine_first(
        merged.get("primary_detail_level_3")
    )

    merged["categories"] = merged["primary_category"].apply(_json_array)
    merged["subcategories"] = merged["primary_subcategory"].apply(_json_array)
    merged["detail_level_3_values"] = merged["primary_detail_level_3"].apply(_json_array)

    for column in V3_COLUMNS:
        if column not in merged.columns:
            merged[column] = pd.NA

    return merged[V3_COLUMNS].copy()


def run(database_path: str | Path | None = None) -> pd.DataFrame:
    resolved_database_path = Path(database_path) if database_path is not None else _default_database_path()
    with DuckDBService(resolved_database_path) as duckdb_service:
        source = duckdb_service.query_df(f"select * from {SOURCE_TABLE}")
        classified = duckdb_service.query_df(f"select * from {CLASSIFIED_TABLE}")
        v3 = build_dim_user_poi_v3(source, classified)
        duckdb_service.write_dataframe(v3, TARGET_TABLE, schema=TARGET_SCHEMA, if_exists="replace")
    return v3


def main() -> None:
    parser = argparse.ArgumentParser(description="Build property_explorer_gold.dim_user_poi_v3.")
    parser.add_argument("--database", type=Path, default=None, help="Optional DuckDB path.")
    args = parser.parse_args()
    run(database_path=args.database)


if __name__ == "__main__":
    main()
