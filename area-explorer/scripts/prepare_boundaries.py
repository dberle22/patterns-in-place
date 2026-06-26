"""Convert Census cartographic boundary shapefiles into app-local GeoJSON files."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "data" / "raw"
OUTPUT_ROOT = ROOT / "data"


def _fetch_features(shapefile_path: Path, select_sql: str) -> list[dict]:
    """Read features from a shapefile and return GeoJSON-ready records."""
    connection = duckdb.connect()
    connection.execute("LOAD spatial")
    query = f"""
        SELECT
            {select_sql},
            ST_AsGeoJSON(geom) AS geometry_json
        FROM ST_Read('{shapefile_path.as_posix()}')
    """
    cursor = connection.execute(query)
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    connection.close()

    geometry_index = columns.index("geometry_json")
    property_columns = [column for column in columns if column != "geometry_json"]

    features = []
    for row in rows:
        properties = {
            column: row[index]
            for index, column in enumerate(columns)
            if column != "geometry_json"
        }
        features.append(
            {
                "type": "Feature",
                "properties": properties,
                "geometry": json.loads(row[geometry_index]),
            }
        )
    return features


def _write_feature_collection(path: Path, features: list[dict]) -> None:
    payload = {"type": "FeatureCollection", "features": features}
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def build_cbsa_boundaries() -> None:
    shapefile_path = RAW_ROOT / "cb_2023_us_cbsa_20m" / "cb_2023_us_cbsa_20m.shp"
    features = _fetch_features(
        shapefile_path,
        """
        CBSAFP AS cbsa_code,
        GEOID AS geoid,
        NAME AS cbsa_name,
        NAMELSAD AS cbsa_label,
        ALAND AS aland,
        AWATER AS awater
        """,
    )
    _write_feature_collection(OUTPUT_ROOT / "cbsa_boundaries.geojson", features)


def build_state_boundaries() -> None:
    shapefile_path = RAW_ROOT / "cb_2023_us_state_20m" / "cb_2023_us_state_20m.shp"
    features = _fetch_features(
        shapefile_path,
        """
        STATEFP AS state_fips,
        GEOID AS geoid,
        STUSPS AS state_abbrev,
        NAME AS state_name,
        ALAND AS aland,
        AWATER AS awater
        """,
    )
    _write_feature_collection(OUTPUT_ROOT / "state_boundaries.geojson", features)


def build_county_boundaries() -> None:
    shapefile_path = RAW_ROOT / "cb_2023_us_county_20m" / "cb_2023_us_county_20m.shp"
    features = _fetch_features(
        shapefile_path,
        """
        STATEFP AS state_fips,
        COUNTYFP AS county_fips_component,
        GEOID AS county_fips,
        STUSPS AS state_abbrev,
        STATE_NAME AS state_name,
        NAME AS county_name,
        NAMELSAD AS county_label,
        ALAND AS aland,
        AWATER AS awater
        """,
    )
    _write_feature_collection(OUTPUT_ROOT / "county_boundaries.geojson", features)


def main() -> None:
    """Build all boundary GeoJSON outputs."""
    build_cbsa_boundaries()
    build_state_boundaries()
    build_county_boundaries()
    print("Wrote CBSA, state, and county GeoJSON files to area-explorer/data/.")


if __name__ == "__main__":
    main()
