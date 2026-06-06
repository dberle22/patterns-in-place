"""Load reviewed place classification overrides from a CSV file."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import duckdb

from nyc_property_finder.services.config import PROJECT_ROOT, load_config


def _default_database_path() -> Path:
    settings = load_config()["settings"]
    return PROJECT_ROOT / settings["database_path"]


def _normalize_row(row: dict[str, str]) -> dict[str, str] | None:
    poi_id = row["poi_id"].strip()
    place_name = row["place_name"].strip()
    updated_category = row["updated_category"].strip().lower()
    updated_subcategory = row["updated_subcategory"].strip().lower()

    if not poi_id:
        return None

    if updated_category == "restaurants" and updated_subcategory in {"", "mixed_restaurants"}:
        return None

    category_map = {
        "bar": "bars",
        "pastries": "bakeries",
        "coffee_shops": "coffee_shops",
        "food_markets": "food_markets",
        "shopping": "shopping",
        "restaurants": "restaurants",
    }
    category = category_map.get(updated_category, updated_category)
    subcategory = updated_subcategory
    detail = ""

    if subcategory == "carribean":
        subcategory = "caribbean"

    if category == "bars":
        if subcategory in {"", "bar"}:
            subcategory = "bars"
        elif subcategory == "wine_bar":
            pass
        elif subcategory == "piano_bar":
            detail = "piano_bar"
            subcategory = "bars"
        elif subcategory == "dive_bar":
            detail = "dive_bar"
            subcategory = "bars"
        elif subcategory == "irish":
            subcategory = "irish_pub"

    elif category == "shopping":
        if subcategory == "liquor_store":
            detail = "liquor_store"
            subcategory = "shopping"
        elif not subcategory:
            subcategory = "shopping"

    elif category == "bakeries":
        if subcategory in {"pastries", "bakeries", ""}:
            detail = "pastries" if subcategory == "pastries" else ""
            subcategory = "bakeries"

    elif category == "coffee_shops":
        subcategory = "coffee_shops"

    elif category == "food_markets":
        subcategory = "food_markets"

    elif category == "restaurants":
        if subcategory == "fine_dining":
            detail = "fine_dining"
            subcategory = "restaurants"
        elif subcategory == "health_food":
            detail = "health_food"
            subcategory = "restaurants"
        elif subcategory == "fast_casual":
            detail = "fast_casual"
            subcategory = "restaurants"
        elif subcategory == "bistro":
            detail = "bistro"
            subcategory = "restaurants"
        elif subcategory == "new_american":
            detail = "new_american"
            subcategory = "american"
        elif subcategory == "gastropub":
            detail = "gastropub"
            subcategory = "restaurants"
        elif subcategory == "asian":
            detail = "asian"
            subcategory = "restaurants"
        elif subcategory == "european":
            detail = "european"
            subcategory = "restaurants"
        elif subcategory == "colombian":
            detail = "colombian"
            subcategory = "latin_american"
        elif subcategory == "southern":
            subcategory = "southern_soul"
        elif subcategory == "british":
            detail = "british"
            subcategory = "restaurants"
        elif subcategory == "russian":
            detail = "russian"
            subcategory = "eastern_european"
        elif subcategory == "irish":
            detail = "irish"
            subcategory = "restaurants"

    # Place-specific corrections for obvious mismatches in the review CSV.
    if place_name == "Lechonera La Piraña":
        category = "restaurants"
        subcategory = "caribbean"
        detail = "puerto_rican"
    elif place_name == "Charles Pan-Fried Chicken":
        category = "restaurants"
        subcategory = "southern_soul"
        detail = "fried_chicken"
    elif place_name == "Hudson Malone: A New York Joint":
        category = "bars"
        subcategory = "bars"
        detail = "gastropub"
    elif place_name == "Wilfie & Nell":
        category = "bars"
        subcategory = "irish_pub"
        detail = "gastropub"
    elif place_name == "Gold Star Beer Counter":
        category = "bars"
        subcategory = "bars"
        detail = "small_plates"
    elif place_name == "Lois":
        category = "bars"
        subcategory = "wine_bar"
        detail = "small_plates"
    elif place_name == "Grand Central Oyster Bar":
        category = "restaurants"
        subcategory = "seafood"
        detail = ""
    elif place_name == "Pommes Frites":
        category = "restaurants"
        subcategory = "restaurants"
        detail = "belgian"

    return {
        "poi_id": poi_id,
        "place_name": place_name,
        "override_category": category,
        "override_subcategory": subcategory,
        "override_detail_level_3": detail,
    }


def run(
    csv_path: str | Path,
    database_path: str | Path | None = None,
    normalized_output_path: str | Path | None = None,
) -> list[dict[str, str]]:
    resolved_database_path = Path(database_path) if database_path is not None else _default_database_path()
    input_path = Path(csv_path)
    if normalized_output_path is None:
        normalized_output_path = (
            PROJECT_ROOT / "data" / "interim" / "place_classification" / f"{input_path.stem}.normalized.csv"
        )
    normalized_output_path = Path(normalized_output_path)
    normalized_output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(input_path.open("r", encoding="utf-8", newline="")))
    normalized_rows = []
    for row in rows:
        normalized = _normalize_row(row)
        if normalized is not None:
            normalized_rows.append(normalized)

    with normalized_output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "poi_id",
                "place_name",
                "override_category",
                "override_subcategory",
                "override_detail_level_3",
            ],
        )
        writer.writeheader()
        writer.writerows(normalized_rows)

    connection = duckdb.connect(str(resolved_database_path))
    try:
        connection.execute(
            """
            delete from property_classification_mart.place_classification_overrides
            where override_reason = 'manual_review_csv_2026_05_03'
            """
        )
        connection.executemany(
            """
            insert or replace into property_classification_mart.place_classification_overrides (
                poi_id,
                override_category,
                override_subcategory,
                override_detail_level_3,
                override_reason,
                reviewed_by,
                active_flag,
                updated_at
            ) values (?, ?, ?, ?, 'manual_review_csv_2026_05_03', 'dan_manual_review', true, current_timestamp)
            """,
            [
                (
                    row["poi_id"],
                    row["override_category"],
                    row["override_subcategory"],
                    row["override_detail_level_3"],
                )
                for row in normalized_rows
            ],
        )
    finally:
        connection.close()

    return normalized_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Load reviewed place classification overrides from a CSV file.")
    parser.add_argument("csv_path", type=Path, help="Path to the reviewed CSV file.")
    parser.add_argument("--database", type=Path, default=None, help="Optional DuckDB path override.")
    parser.add_argument(
        "--normalized-output",
        type=Path,
        default=None,
        help="Optional path to write the normalized override CSV artifact.",
    )
    args = parser.parse_args()
    rows = run(args.csv_path, database_path=args.database, normalized_output_path=args.normalized_output)
    print(f"Loaded {len(rows)} overrides.")


if __name__ == "__main__":
    main()
