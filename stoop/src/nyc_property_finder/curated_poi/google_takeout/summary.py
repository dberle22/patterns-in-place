"""Run summary and lightweight QA for Google Places POI ingestion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from nyc_property_finder.curated_poi.google_takeout.build_dim import build_dim_user_poi_v2
from nyc_property_finder.curated_poi.google_takeout.cache import read_resolution_cache
from nyc_property_finder.curated_poi.google_takeout.config import (
    DEFAULT_DETAILS_CACHE_PATH,
    DEFAULT_GOOGLE_PLACES_INTERIM_DIR,
    DEFAULT_RESOLUTION_CACHE_PATH,
)


DEFAULT_SUMMARY_PATH = DEFAULT_GOOGLE_PLACES_INTERIM_DIR / "place_pipeline_summary.json"
DEFAULT_QA_PATH = DEFAULT_GOOGLE_PLACES_INTERIM_DIR / "place_pipeline_qa.csv"


def build_summary(
    resolution_cache_path: str | Path = DEFAULT_RESOLUTION_CACHE_PATH,
    details_cache_path: str | Path = DEFAULT_DETAILS_CACHE_PATH,
    source_record_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Build count-based QA from cache artifacts and the v2 dim output."""

    resolution_cache = read_resolution_cache(resolution_cache_path)
    if source_record_ids is not None:
        resolution_cache = resolution_cache[resolution_cache["source_record_id"].isin(source_record_ids)].copy()
    dim = build_dim_user_poi_v2(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        source_record_ids=source_record_ids,
    )
    duplicate_groups = _duplicate_place_groups(resolution_cache)
    missing_coordinates = dim[dim[["lat", "lon"]].isna().any(axis=1)] if not dim.empty else dim

    # "New places" here means source rows that have a cached place ID and are
    # therefore ready for dim_user_poi_v2. Per-run new-call counts live in the
    # pipeline ResolveReport and EnrichReport.
    return {
        "source_rows": int(len(resolution_cache)),
        "resolved_source_rows": int((resolution_cache["google_place_id"] != "").sum())
        if not resolution_cache.empty
        else 0,
        "unique_google_place_ids": int(resolution_cache["google_place_id"].replace("", pd.NA).nunique())
        if not resolution_cache.empty
        else 0,
        "dim_rows": int(len(dim)),
        "dim_rows_with_coordinates": int(dim[["lat", "lon"]].notna().all(axis=1).sum())
        if not dim.empty
        else 0,
        "duplicate_place_groups": int(len(duplicate_groups)),
        "duplicate_source_rows": int(duplicate_groups["source_row_count"].sum())
        if not duplicate_groups.empty
        else 0,
        "missing_coordinate_rows": int(len(missing_coordinates)),
        "review_recommendations": _review_recommendations(duplicate_groups, missing_coordinates),
    }


def write_summary(
    summary: dict[str, Any],
    path: str | Path = DEFAULT_SUMMARY_PATH,
) -> None:
    """Write the machine-readable run summary."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_qa_csv(
    resolution_cache_path: str | Path = DEFAULT_RESOLUTION_CACHE_PATH,
    details_cache_path: str | Path = DEFAULT_DETAILS_CACHE_PATH,
    path: str | Path = DEFAULT_QA_PATH,
    source_record_ids: set[str] | None = None,
) -> None:
    """Write a human-readable QA CSV for duplicates and missing coordinates."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    resolution_cache = read_resolution_cache(resolution_cache_path)
    if source_record_ids is not None:
        resolution_cache = resolution_cache[resolution_cache["source_record_id"].isin(source_record_ids)].copy()
    dim = build_dim_user_poi_v2(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        source_record_ids=source_record_ids,
    )
    duplicate_groups = _duplicate_place_groups(resolution_cache)

    rows: list[dict[str, Any]] = []
    for _, group in duplicate_groups.iterrows():
        rows.append(
            {
                "qa_type": "duplicate_place_id",
                "google_place_id": group["google_place_id"],
                "source_row_count": group["source_row_count"],
                "input_titles": group["input_titles"],
                "source_list_names": group["source_list_names"],
                "note": "Multiple source rows resolved to one Google place ID.",
            }
        )

    if not dim.empty:
        missing_coordinates = dim[dim[["lat", "lon"]].isna().any(axis=1)]
        for _, row in missing_coordinates.iterrows():
            rows.append(
                {
                    "qa_type": "missing_coordinates",
                    "google_place_id": row["google_place_id"],
                    "source_row_count": "",
                    "input_titles": row["input_title"],
                    "source_list_names": row["source_list_names"],
                    "note": "Place Details did not return both latitude and longitude.",
                }
            )

    pd.DataFrame(
        rows,
        columns=[
            "qa_type",
            "google_place_id",
            "source_row_count",
            "input_titles",
            "source_list_names",
            "note",
        ],
    ).to_csv(path, index=False)


def _duplicate_place_groups(resolution_cache: pd.DataFrame) -> pd.DataFrame:
    if resolution_cache.empty:
        return pd.DataFrame(
            columns=["google_place_id", "source_row_count", "input_titles", "source_list_names"]
        )

    resolved = resolution_cache[resolution_cache["google_place_id"] != ""].copy()
    if resolved.empty:
        return pd.DataFrame(
            columns=["google_place_id", "source_row_count", "input_titles", "source_list_names"]
        )

    groups = (
        resolved.groupby("google_place_id", as_index=False)
        .agg(
            source_row_count=("source_record_id", "count"),
            input_titles=("input_title", lambda values: json.dumps(_unique_strings(values))),
            source_list_names=("source_list_name", lambda values: json.dumps(_unique_strings(values))),
        )
        .query("source_row_count > 1")
        .sort_values(["source_row_count", "google_place_id"], ascending=[False, True])
    )
    return groups


def _unique_strings(values: pd.Series) -> list[str]:
    output: list[str] = []
    for value in values.fillna("").astype(str):
        value = value.strip()
        if value and value not in output:
            output.append(value)
    return output


def _review_recommendations(duplicate_groups: pd.DataFrame, missing_coordinates: pd.DataFrame) -> list[str]:
    recommendations: list[str] = []
    if not duplicate_groups.empty:
        recommendations.append(
            "Review duplicate_place_id rows in place_pipeline_qa.csv; they may be true duplicates or bad top-candidate matches."
        )
    if not missing_coordinates.empty:
        recommendations.append("Review rows missing coordinates before using them in maps or scoring.")
    if not recommendations:
        recommendations.append("No duplicate place IDs or missing coordinates were detected.")
    return recommendations
