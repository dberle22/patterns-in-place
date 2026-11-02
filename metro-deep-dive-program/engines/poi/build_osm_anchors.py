#!/usr/bin/env python3
"""Build place-like OSM anchors for New York in their own POI source lane.

Usage:
    python metro-deep-dive-program/engines/poi/build_osm_anchors.py

Rail stations, subway entrances, ferry terminals and bus stations from the
cached statewide OSM file, clipped to the state and assigned to county, tract,
CBSA and Place. The cached file covers New York only, so the NJ counties of the
NYC CBSA have no anchors. Records stay separate from Overture and are not merged
with it. A matching run is refused; publish it with publish_osm_anchors.py.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

import duckdb
import yaml

from acquire_overture_places import ENGINE_DIR, REPO_ROOT, configure_extensions, database_path, sha256, sql_literal


OSM_CONFIG = ENGINE_DIR.parent / "infrastructure" / "sources" / "osm_infrastructure.yml"
OSM_MARKET = "new_york_state"
OUTPUT_SLUG = "new_york_state_osm_anchors"
MAPPING_VERSION = "osm_anchor_v1"
# A key in the non-CBSA market's synthetic namespace, shared with Overture runs.
NON_CBSA_CODE = "SYNTH-NY"
STATE_FIPS = "36"
# About 3 km at New York's latitude, enough to reach a pier from the shoreline.
NEAREST_COUNTY_DEGREES = 0.03
# GDAL promotes railway to a column on this layer and leaves amenity in other_tags.
ANCHOR_TYPE = """CASE
    WHEN railway = 'station' THEN 'rail_station'
    WHEN railway = 'subway_entrance' THEN 'subway_entrance'
    WHEN other_tags LIKE '%"amenity"=>"ferry_terminal"%' THEN 'ferry_terminal'
    WHEN other_tags LIKE '%"amenity"=>"bus_station"%' THEN 'bus_station'
END"""


def source_sql(adapter: Path) -> str:
    """Select anchor points from the cached statewide adapter."""

    return f"""
    SELECT * FROM (
        SELECT NULLIF(TRIM(osm_id), '') AS source_id, name AS source_name, {ANCHOR_TYPE} AS anchor_type,
            to_json(struct_pack(railway := railway, other_tags := other_tags)) AS source_tags,
            geometry
        FROM ST_Read({sql_literal(str(adapter))}, layer='points')
    ) WHERE anchor_type IS NOT NULL
    """


def assigned_sql(release: str, run_id: str, extracted_at: str, checksum: str, vintage: int) -> str:
    """Assign kept anchors with the same strict-interior Place rule as Overture POIs."""

    state = sql_literal(STATE_FIPS)
    return f"""
    WITH county_hits AS (
        SELECT a.source_id, min(c.county_geoid) AS county_geoid
        FROM kept a JOIN geo.counties c ON c.state_fips = {state} AND ST_Intersects(a.geometry, c.geom)
        GROUP BY 1
    ), county_nearest AS (
        -- County polygons stop at the shoreline, so a ferry pier can sit just
        -- outside every county. It takes the nearest county, labelled as such.
        SELECT a.source_id, arg_min(c.county_geoid, ST_Distance(a.geometry, c.geom)) AS county_geoid
        FROM kept a JOIN geo.counties c
          ON c.state_fips = {state} AND ST_DWithin(a.geometry, c.geom, {NEAREST_COUNTY_DEGREES})
        WHERE a.source_id NOT IN (SELECT source_id FROM county_hits)
        GROUP BY 1
    ), tract_hits AS (
        SELECT a.source_id, min(t.tract_geoid) AS tract_geoid
        FROM kept a JOIN geo.tracts_all_us t ON t.county_geoid LIKE {state} || '%' AND ST_Intersects(a.geometry, t.geom)
        GROUP BY 1
    ), place_hits AS (
        SELECT a.source_id, count(*) AS interior_count, min(p.place_geoid) AS place_geoid
        FROM kept a JOIN geo.places_analysis p ON p.state_fips = {state} AND ST_Contains(p.geom, a.geometry)
        GROUP BY 1
    )
    SELECT
        CASE WHEN coalesce(c.county_geoid, n.county_geoid) IS NULL THEN NULL ELSE coalesce(x.cbsa_code, {sql_literal(NON_CBSA_CODE)}) END AS cbsa_code,
        'osm' AS source_system,
        {sql_literal(release)} AS source_release,
        a.source_id,
        concat('osm|', {sql_literal(release)}, '|points|', a.source_id) AS source_record_key,
        a.source_name,
        a.anchor_type,
        {sql_literal(MAPPING_VERSION)} AS mapping_version,
        a.source_tags,
        a.geometry,
        ST_X(a.geometry) AS longitude,
        ST_Y(a.geometry) AS latitude,
        coalesce(c.county_geoid, n.county_geoid) AS county_geoid,
        t.tract_geoid,
        CASE WHEN p.interior_count = 1 THEN p.place_geoid END AS place_geoid,
        CASE WHEN p.interior_count = 1 THEN 'assigned' WHEN p.interior_count > 1 THEN 'boundary_ambiguous' ELSE 'no_census_place' END AS place_assignment_status,
        CASE WHEN c.county_geoid IS NOT NULL THEN 'assigned'
             WHEN n.county_geoid IS NOT NULL THEN 'nearest_county'
             ELSE 'unassigned' END AS county_assignment_status,
        {vintage} AS market_boundary_vintage,
        {sql_literal(run_id)} AS source_run_id,
        {sql_literal(extracted_at)} AS extracted_at,
        {sql_literal(checksum)} AS source_asset_checksum
    FROM kept a
    LEFT JOIN county_hits c USING (source_id)
    LEFT JOIN county_nearest n USING (source_id)
    LEFT JOIN tract_hits t USING (source_id)
    LEFT JOIN place_hits p USING (source_id)
    LEFT JOIN mart_geography.rollup_county_to_cbsa x ON coalesce(c.county_geoid, n.county_geoid) = x.county_geoid
    """


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ENGINE_DIR / "outputs")
    parser.add_argument("--db-path", type=Path)
    args = parser.parse_args()

    market = yaml.safe_load(OSM_CONFIG.read_text(encoding="utf-8"))["markets"][OSM_MARKET]
    adapter, source_asset = REPO_ROOT / market["source_adapter_path"], REPO_ROOT / market["source_asset_path"]
    release = market["source_release"]
    checksum = sha256(source_asset)
    token = re.sub(r"[^A-Za-z0-9]+", "-", release).strip("-").lower()
    run_id = f"osm-anchors-{STATE_FIPS}-{token}-{checksum[:12]}"
    run_dir = args.output_root / OUTPUT_SLUG / run_id
    if run_dir.exists():
        raise FileExistsError(f"Run already exists and will not be overwritten: {run_dir}")
    extracted_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with duckdb.connect(str(database_path(args.db_path)), read_only=True) as con:
        configure_extensions(con, "local.parquet")
        state_row = con.execute("SELECT ST_AsWKB(geom), boundary_vintage FROM geo.states_analysis WHERE state_fips = ?", [STATE_FIPS]).fetchone()
        if not state_row:
            raise RuntimeError(f"Geography returned no boundary for state {STATE_FIPS}.")
        boundary, vintage = state_row[0], int(state_row[1])
        con.execute(f"CREATE TEMP TABLE source_points AS {source_sql(adapter)}")
        inside = f"ST_Intersects(geometry, ST_GeomFromWKB(from_hex({sql_literal(boundary.hex())})))"
        con.execute(f"""
            CREATE TEMP TABLE kept AS
            SELECT * FROM source_points WHERE source_id IS NOT NULL AND {inside}
        """)
        duplicates = con.execute("SELECT count(*) - count(DISTINCT source_id) FROM kept").fetchone()[0]
        if duplicates:
            raise RuntimeError(f"{duplicates} duplicate OSM point IDs in the kept anchors.")
        artifact = run_dir / "poi_osm_anchor.parquet"
        rejected = run_dir / "poi_osm_anchor_rejected.parquet"
        run_dir.mkdir(parents=True)
        con.execute(f"COPY ({assigned_sql(release, run_id, extracted_at, checksum, vintage)}) TO {sql_literal(str(artifact))} (FORMAT PARQUET, COMPRESSION ZSTD)")
        con.execute(f"""
            COPY (
                SELECT *, CASE WHEN source_id IS NULL THEN 'missing_source_id' ELSE 'outside_state_boundary' END AS rejection_reason
                FROM source_points WHERE source_id IS NULL OR NOT {inside}
            ) TO {sql_literal(str(rejected))} (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        source_rows = con.execute("SELECT count(*) FROM source_points").fetchone()[0]
        retained = con.execute(f"SELECT count(*) FROM read_parquet({sql_literal(str(artifact))})").fetchone()[0]
        rejected_rows = con.execute(f"SELECT rejection_reason, count(*) FROM read_parquet({sql_literal(str(rejected))}) GROUP BY 1").fetchall()
        by_type = con.execute(f"SELECT anchor_type, count(*) FROM read_parquet({sql_literal(str(artifact))}) GROUP BY 1 ORDER BY 1").fetchall()
        assignment = con.execute(f"SELECT county_assignment_status, place_assignment_status, count(*) FROM read_parquet({sql_literal(str(artifact))}) GROUP BY 1, 2 ORDER BY 1, 2").fetchall()

    if source_rows != retained + sum(count for _, count in rejected_rows):
        raise RuntimeError("OSM anchor row accounting does not reconcile.")
    manifest = {
        "source_run_id": run_id, "source_system": "osm", "source_release": release, "mapping_version": MAPPING_VERSION,
        "source_asset": {"uri": market["source_asset_uri"], "sha256": checksum},
        "boundary": {"geo_level": "state", "state_fips": STATE_FIPS, "boundary_vintage": vintage},
        "row_counts": {"source": source_rows, "retained": retained, "rejected": dict(rejected_rows)},
        "by_anchor_type": dict(by_type),
        "assignment": [dict(zip(("county", "place", "count"), row)) for row in assignment],
        "cache": {"uri": str(artifact.relative_to(REPO_ROOT)), "sha256": sha256(artifact)},
        "extracted_at": extracted_at,
    }
    (run_dir / "osm_anchor_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
