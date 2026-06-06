"""Lightweight data readers for the Stoop Explore app."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from nyc_property_finder.app.explorer import load_optional_table


CHARACTER_PROFILE_TABLE = "neighborhood_character_mart.nta_character_profile"
CATEGORY_CONTROLS_TABLE = "neighborhood_character_mart.nta_category_controls"
CATEGORY_DENSITY_TABLE = "neighborhood_character_mart.nta_category_density"

CATEGORY_CONTROL_COLUMNS = [
    "category",
    "include_in_explore_v1",
    "known_for_enabled",
    "min_nyc_category_total",
    "display_label",
    "notes",
]

CHARACTER_PROFILE_COLUMNS = [
    "nta_id",
    "nta_name",
    "borough",
    "area_sqkm",
    "total_curated_poi_count",
    "destination_categories",
    "strong_categories",
    "top_category",
    "top_subcategory",
    "subway_station_count",
    "bus_stop_count",
    "grocery_store_count",
    "pharmacy_count",
    "park_count",
    "public_library_count",
    "public_school_count",
    "built_at",
]

CATEGORY_DENSITY_COLUMNS = [
    "nta_id",
    "nta_name",
    "borough",
    "area_sqkm",
    "source",
    "category",
    "poi_count",
    "poi_density_per_sqkm",
    "subcategory_diversity",
    "nyc_category_total",
    "nyc_percentile",
    "concentration_tier",
    "meets_evidence_threshold",
]


@dataclass(frozen=True)
class ExploreCategoryOption:
    """Configuration-backed Explore category metadata."""

    category: str
    display_label: str
    known_for_enabled: bool
    min_nyc_category_total: int | None
    notes: str


def parse_pipe_list(value: object) -> list[str]:
    """Split a pipe-delimited mart column into display values."""

    if value is None or pd.isna(value):
        return []
    values = []
    for item in str(value).split("|"):
        cleaned = item.strip()
        if cleaned and cleaned not in values:
            values.append(cleaned)
    return values


def load_explore_category_controls(database_path: str | Path) -> pd.DataFrame:
    """Return configured Stoop Explore categories that should be visible in v1."""

    controls = load_optional_table(
        database_path,
        CATEGORY_CONTROLS_TABLE,
        CATEGORY_CONTROL_COLUMNS,
    )
    if controls.empty:
        return controls

    output = controls.copy()
    output["include_in_explore_v1"] = output["include_in_explore_v1"].fillna(False).astype(bool)
    output["known_for_enabled"] = output["known_for_enabled"].fillna(False).astype(bool)
    output["min_nyc_category_total"] = pd.to_numeric(
        output["min_nyc_category_total"],
        errors="coerce",
    ).astype("Int64")
    output["display_label"] = output["display_label"].fillna(output["category"]).astype(str)
    output["notes"] = output["notes"].fillna("").astype(str)
    output = output.loc[output["include_in_explore_v1"]].copy()
    return output.sort_values(["display_label", "category"]).reset_index(drop=True)


def load_explore_category_options(database_path: str | Path) -> list[ExploreCategoryOption]:
    """Return typed Explore category options for app controls."""

    controls = load_explore_category_controls(database_path)
    return [
        ExploreCategoryOption(
            category=str(row["category"]),
            display_label=str(row["display_label"]),
            known_for_enabled=bool(row["known_for_enabled"]),
            min_nyc_category_total=(
                None if pd.isna(row["min_nyc_category_total"]) else int(row["min_nyc_category_total"])
            ),
            notes=str(row["notes"]),
        )
        for _, row in controls.iterrows()
    ]


def load_all_nta_character_profiles(database_path: str | Path) -> pd.DataFrame:
    """Return all NTA character profiles for app selection controls."""

    profiles = load_optional_table(
        database_path,
        CHARACTER_PROFILE_TABLE,
        CHARACTER_PROFILE_COLUMNS,
    )
    if profiles.empty:
        return profiles

    output = profiles.copy()
    output["nta_id"] = output["nta_id"].fillna("").astype(str)
    output["nta_name"] = output["nta_name"].fillna("").astype(str)
    output["borough"] = output["borough"].fillna("").astype(str)
    output["total_curated_poi_count"] = pd.to_numeric(
        output["total_curated_poi_count"],
        errors="coerce",
    ).fillna(0)
    return output.sort_values(
        ["total_curated_poi_count", "nta_name"],
        ascending=[False, True],
        na_position="last",
    ).reset_index(drop=True)


def load_explore_rankings(
    database_path: str | Path,
    category: str,
    *,
    limit: int = 10,
) -> pd.DataFrame:
    """Return the app-facing Top neighborhoods for X ranking."""

    density = load_optional_table(
        database_path,
        CATEGORY_DENSITY_TABLE,
        CATEGORY_DENSITY_COLUMNS,
    )
    controls = load_explore_category_controls(database_path)[["category", "display_label"]]
    if density.empty:
        return pd.DataFrame(
            columns=[
                "nta_id",
                "nta_name",
                "borough",
                "category",
                "display_label",
                "poi_count",
                "subcategory_diversity",
                "nyc_percentile",
                "concentration_tier",
            ]
        )

    output = density.copy()
    output["source"] = output["source"].fillna("").astype(str)
    output["category"] = output["category"].fillna("").astype(str)
    output["meets_evidence_threshold"] = output["meets_evidence_threshold"].fillna(False).astype(bool)
    output["poi_count"] = pd.to_numeric(output["poi_count"], errors="coerce")
    output["subcategory_diversity"] = pd.to_numeric(output["subcategory_diversity"], errors="coerce")
    output["nyc_percentile"] = pd.to_numeric(output["nyc_percentile"], errors="coerce")
    output = output.merge(controls, on="category", how="inner")
    output = output.loc[
        (output["source"] == "curated")
        & (output["category"] == category)
        & output["meets_evidence_threshold"]
    ].copy()
    if output.empty:
        return output
    output = output.sort_values(
        ["nyc_percentile", "poi_count", "subcategory_diversity", "nta_name"],
        ascending=[False, False, False, True],
        na_position="last",
    )
    return output.head(limit).reset_index(drop=True)


def load_nta_character_profile(database_path: str | Path, nta_id: str) -> dict[str, object] | None:
    """Return a single app-facing character profile for the selected NTA."""

    profiles = load_all_nta_character_profiles(database_path)
    if profiles.empty:
        return None

    matches = profiles.loc[profiles["nta_id"].fillna("").astype(str) == str(nta_id)].copy()
    if matches.empty:
        return None

    row = matches.iloc[0].to_dict()
    row["destination_category_list"] = parse_pipe_list(row.get("destination_categories"))
    row["strong_category_list"] = parse_pipe_list(row.get("strong_categories"))
    return row
