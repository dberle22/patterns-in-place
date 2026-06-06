"""Build the Stoop place classification mart in ordered SQL stages."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

from nyc_property_finder.services.config import PROJECT_ROOT, load_config


SQL_BUILD_ORDER = [
    PROJECT_ROOT / "sql" / "ddl" / "003_property_classification_mart.sql",
    PROJECT_ROOT / "sql" / "marts" / "place_classification" / "place_classification_text.sql",
    PROJECT_ROOT / "sql" / "marts" / "place_classification" / "place_word_profile.sql",
    PROJECT_ROOT / "sql" / "marts" / "place_classification" / "place_phrase_profile.sql",
    PROJECT_ROOT / "sql" / "marts" / "place_classification" / "place_keyword_mapping_seed.sql",
    PROJECT_ROOT / "sql" / "marts" / "place_classification" / "place_keyword_matches.sql",
    PROJECT_ROOT / "sql" / "marts" / "place_classification" / "place_matched_keywords.sql",
    PROJECT_ROOT / "sql" / "marts" / "place_classification" / "place_classification_scores.sql",
    PROJECT_ROOT / "sql" / "marts" / "place_classification" / "place_classification_recommendations.sql",
    PROJECT_ROOT / "sql" / "marts" / "place_classification" / "place_classification_review_queue.sql",
    PROJECT_ROOT / "sql" / "marts" / "place_classification" / "curated_places_classified.sql",
]


SUMMARY_QUERIES = {
    "restaurant_classification_summary": """
        select
            classification_method,
            classification_confidence,
            count(*) as poi_count
        from property_classification_mart.curated_places_classified
        where original_category = 'restaurants'
        group by all
        order by classification_method, classification_confidence
    """,
    "mixed_restaurant_recommendations": """
        select
            recommended_subcategory,
            recommended_detail_level_3,
            classification_confidence,
            count(*) as poi_count
        from property_classification_mart.place_classification_recommendations
        where current_category = 'restaurants'
          and current_subcategory = 'mixed_restaurants'
        group by all
        order by poi_count desc, recommended_subcategory, recommended_detail_level_3
        limit 20
    """,
    "mixed_restaurant_rollup": """
        select
            count(*) as mixed_restaurant_source_count,
            count(case when final_subcategory <> 'mixed_restaurants' then 1 end) as moved_out_of_mixed_restaurants,
            count(case when final_subcategory = 'mixed_restaurants' then 1 end) as remaining_mixed_restaurants
        from property_classification_mart.curated_places_classified
        where original_category = 'restaurants'
          and original_subcategory = 'mixed_restaurants'
    """,
    "review_queue_summary": """
        select
            review_reason,
            count(*) as poi_count
        from property_classification_mart.place_classification_review_queue
        group by review_reason
        order by poi_count desc, review_reason
        limit 20
    """,
}


def _default_database_path() -> Path:
    settings = load_config()["settings"]
    return PROJECT_ROOT / settings["database_path"]


def _print_rows(title: str, columns: list[str], rows: list[tuple[object, ...]]) -> None:
    print(f"\n[{title}]")
    if not rows:
        print("(no rows)")
        return
    print(" | ".join(columns))
    for row in rows:
        print(" | ".join("" if value is None else str(value) for value in row))


def run(database_path: str | Path | None = None) -> dict[str, list[tuple[object, ...]]]:
    """Execute the classification mart SQL build order and return summary rows."""

    resolved_database_path = Path(database_path) if database_path is not None else _default_database_path()
    summaries: dict[str, list[tuple[object, ...]]] = {}

    connection = duckdb.connect(str(resolved_database_path))
    try:
        for sql_path in SQL_BUILD_ORDER:
            connection.execute(sql_path.read_text(encoding="utf-8"))
            print(f"Executed: {sql_path.relative_to(PROJECT_ROOT)}")

        for summary_name, query in SUMMARY_QUERIES.items():
            cursor = connection.execute(query)
            columns = [item[0] for item in cursor.description]
            rows = cursor.fetchall()
            summaries[summary_name] = rows
            _print_rows(summary_name, columns, rows)
    finally:
        connection.close()

    return summaries


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Stoop place classification mart.")
    parser.add_argument(
        "--database",
        type=Path,
        default=None,
        help="Optional path to the DuckDB database file. Defaults to config/settings.yaml.",
    )
    args = parser.parse_args()
    run(database_path=args.database)


if __name__ == "__main__":
    main()
