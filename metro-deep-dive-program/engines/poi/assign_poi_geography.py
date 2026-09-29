#!/usr/bin/env python3
"""Assign classified POIs to governed tract, county, Place, and postal-ZIP surfaces."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb

from normalize_overture_places import latest_source_run
from acquire_overture_places import ENGINE_DIR, configure_extensions, database_path, sql_literal


PLACE_METHOD = "direct_point_in_place_strict_interior_v1"


def require_place_geometry(con: duckdb.DuckDBPyConnection) -> int:
    """Confirm that the governed analytical Place interface is available."""
    exists = con.execute("""
        SELECT count(*) FROM information_schema.tables
        WHERE table_schema = 'geo' AND table_name = 'places_analysis'
    """).fetchone()[0]
    if not exists:
        raise RuntimeError(
            "Missing Geography dependency geo.places_analysis. Build the governed Census Place "
            "analytical geometry before assigning POIs; geo.places_display is display-only and "
            "cannot be substituted."
        )
    vintage = con.execute("SELECT min(boundary_vintage) FROM geo.places_analysis").fetchone()[0]
    if vintage is None:
        raise RuntimeError("Geography dependency geo.places_analysis is empty; refresh its governed Place geometry.")
    return int(vintage)


def assignment_sql(places: Path, cbsa: str, place_vintage: int) -> str:
    """Build assignments while keeping direct Point-to-Place outcomes explicit."""
    # A Place is assigned only for one strict-interior polygon match. A touched
    # boundary or overlapping candidate set remains reviewable rather than being
    # resolved alphabetically. No candidate is the expected unincorporated result.
    return f"""
    WITH p AS (
        SELECT source_record_key, source_run_id, market_id, longitude, latitude,
               source_address, source_postal_zip, record_status, coordinate_status,
               mapping_status, category
        FROM read_parquet({sql_literal(str(places))})
    ), point AS (
        SELECT *, CASE WHEN record_status = 'retained' AND coordinate_status = 'valid'
                              AND longitude BETWEEN -180 AND 180 AND latitude BETWEEN -90 AND 90
                         THEN ST_Point(longitude, latitude) END AS geom
        FROM p
    ), counties AS (
        SELECT c.county_geoid, c.geom FROM geo.counties c
        JOIN mart_geography.rollup_county_to_cbsa x ON c.county_geoid = x.county_geoid
        WHERE x.cbsa_code = {sql_literal(cbsa)}
    ), tracts AS (
        SELECT t.tract_geoid, t.geom FROM geo.tracts_all_us t
        JOIN mart_geography.rollup_tract_to_cbsa x ON t.tract_geoid = x.tract_geoid
        WHERE x.cbsa_code = {sql_literal(cbsa)}
    ), place_scope AS (
        -- A retained market point cannot belong to a Place in another state.
        -- This narrows the spatial index scan without using a tract-to-Place edge.
        SELECT p.* FROM geo.places_analysis p
        WHERE state_fips IN (SELECT DISTINCT substr(county_geoid, 1, 2) FROM counties)
    ), tract_hits AS (
        SELECT p.source_record_key, t.tract_geoid,
               row_number() OVER (PARTITION BY p.source_record_key ORDER BY t.tract_geoid) AS rn
        FROM point p LEFT JOIN tracts t ON ST_Intersects(p.geom, t.geom)
    ), tract_assign AS (
        SELECT source_record_key, 'tract' AS geo_level, tract_geoid AS geo_id,
               2020 AS boundary_vintage, 'point_in_polygon' AS assignment_method,
               CASE WHEN tract_geoid IS NULL THEN 'unassigned' ELSE 'assigned' END AS assignment_status
        FROM tract_hits WHERE rn = 1
    ), county_hits AS (
        SELECT p.source_record_key, c.county_geoid,
               row_number() OVER (PARTITION BY p.source_record_key ORDER BY c.county_geoid) AS rn
        FROM point p LEFT JOIN counties c ON ST_Intersects(p.geom, c.geom)
    ), county_assign AS (
        SELECT source_record_key, 'county' AS geo_level, county_geoid AS geo_id,
               2023 AS boundary_vintage, 'point_in_polygon' AS assignment_method,
               CASE WHEN county_geoid IS NULL THEN 'unassigned' ELSE 'assigned' END AS assignment_status
        FROM county_hits WHERE rn = 1
    ), place_candidates AS (
        SELECT p.source_record_key, place_geoid,
               ST_Contains(g.geom, p.geom) AS is_strict_interior,
               ST_Touches(g.geom, p.geom) AS is_boundary
        FROM point p JOIN place_scope g
          ON p.geom IS NOT NULL
         AND (ST_Contains(g.geom, p.geom) OR ST_Touches(g.geom, p.geom))
    ), place_hits AS (
        SELECT source_record_key, count(*) AS candidate_count,
               count_if(is_strict_interior) AS interior_count,
               min(place_geoid) FILTER (WHERE is_strict_interior) AS interior_place_geoid,
               bool_or(is_boundary) AS has_boundary_candidate
        FROM place_candidates GROUP BY 1
    ), place_assign AS (
        SELECT p.source_record_key, 'place' AS geo_level,
               CASE WHEN h.interior_count = 1 AND h.candidate_count = 1 THEN h.interior_place_geoid END AS geo_id,
               {place_vintage} AS boundary_vintage, {sql_literal(PLACE_METHOD)} AS assignment_method,
               CASE
                   WHEN p.record_status != 'retained' OR p.coordinate_status != 'valid' OR p.geom IS NULL THEN 'invalid_or_unassignable'
                   WHEN coalesce(h.candidate_count, 0) = 0 THEN 'no_census_place'
                   WHEN h.interior_count = 1 AND h.candidate_count = 1 THEN 'assigned'
                   WHEN h.has_boundary_candidate OR h.candidate_count > 1 THEN 'boundary_ambiguous'
                   ELSE 'boundary_ambiguous'
               END AS assignment_status
        FROM point p LEFT JOIN place_hits h USING (source_record_key)
    ), zip_assign AS (
        SELECT source_record_key, 'zip' AS geo_level,
               coalesce(nullif(trim(source_postal_zip), ''),
                        nullif(regexp_extract(source_address, '([0-9]{{5}})(?:-[0-9]{{4}})?', 1), '')) AS geo_id,
               NULL::INTEGER AS boundary_vintage, 'source_address_postal_zip' AS assignment_method,
               CASE WHEN coalesce(nullif(trim(source_postal_zip), ''),
                                  nullif(regexp_extract(source_address, '([0-9]{{5}})(?:-[0-9]{{4}})?', 1), '')) IS NOT NULL
                    THEN 'address_supplied' ELSE 'unassigned' END AS assignment_status
        FROM p
    )
    SELECT {sql_literal(cbsa)} AS cbsa_code, * FROM (
        SELECT * FROM tract_assign UNION ALL SELECT * FROM county_assign
        UNION ALL SELECT * FROM place_assign UNION ALL SELECT * FROM zip_assign
    )
    """


def main() -> None:
    """Write reusable assignments and explicit Place coverage QA for one source run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True)
    parser.add_argument("--source-run-dir", type=Path)
    parser.add_argument("--output-root", type=Path, default=ENGINE_DIR / "outputs")
    parser.add_argument("--db-path", type=Path)
    args = parser.parse_args()
    run_dir = args.source_run_dir or latest_source_run(args.output_root, args.market)
    run = json.loads((run_dir / "source_run_manifest.json").read_text(encoding="utf-8"))
    places = run_dir / "classified" / "poi_classified_place.parquet"
    if not places.exists():
        raise FileNotFoundError("Run classification before geography assignment.")
    out = run_dir / "geography"
    out.mkdir(exist_ok=True)
    destination = out / "poi_geography_assignment.parquet"
    qa_destination = out / "poi_place_assignment_qa.parquet"

    with duckdb.connect(str(database_path(args.db_path)), read_only=True) as con:
        configure_extensions(con, "local.parquet")
        place_vintage = require_place_geometry(con)
        query = assignment_sql(places, str(run["market_id"]), place_vintage)
        con.execute(f"COPY ({query}) TO {sql_literal(str(destination))} (FORMAT PARQUET, COMPRESSION ZSTD)")
        # QA makes no-Place a visible coverage outcome rather than a category zero.
        qa_query = f"""
        WITH source_places AS (
            SELECT source_record_key, source_run_id, market_id, mapping_status,
                   coalesce(category, 'Unclassified') AS governed_category
            FROM read_parquet({sql_literal(str(places))})
        ), place_assignments AS (
            SELECT source_record_key, assignment_status FROM read_parquet({sql_literal(str(destination))})
            WHERE geo_level = 'place'
        )
        SELECT p.source_run_id, p.market_id, p.mapping_status, p.governed_category,
               a.assignment_status AS place_assignment_status, count(*) AS poi_count
        FROM source_places p JOIN place_assignments a USING (source_record_key)
        GROUP BY 1, 2, 3, 4, 5 ORDER BY 1, 2, 3, 4, 5
        """
        con.execute(f"COPY ({qa_query}) TO {sql_literal(str(qa_destination))} (FORMAT PARQUET, COMPRESSION ZSTD)")
        summary = con.execute(f"SELECT geo_level, assignment_status, count(*) AS count FROM ({query}) GROUP BY 1, 2 ORDER BY 1, 2").fetchall()
        accounting = con.execute(f"""
            WITH source_places AS (
                SELECT source_record_key, record_status, coordinate_status, longitude, latitude
                FROM read_parquet({sql_literal(str(places))})
            ), place_assignments AS (
                SELECT source_record_key, assignment_status FROM read_parquet({sql_literal(str(destination))})
                WHERE geo_level = 'place'
            )
            SELECT count(*),
                   count_if(record_status = 'retained' AND coordinate_status = 'valid' AND longitude BETWEEN -180 AND 180 AND latitude BETWEEN -90 AND 90),
                   count(a.source_record_key), count_if(a.assignment_status = 'assigned'),
                   count_if(a.assignment_status = 'no_census_place'), count_if(a.assignment_status = 'boundary_ambiguous'),
                   count_if(a.assignment_status = 'invalid_or_unassignable')
            FROM source_places p LEFT JOIN place_assignments a USING (source_record_key)
        """).fetchone()
        if accounting[1] != accounting[2] - accounting[5]:
            raise RuntimeError("Place assignment row accounting failed: retained valid POIs do not reconcile.")

        # This review-only cross-tab compares the direct Point-to-Place outcome
        # with the existing tract outcome. It never derives a Place from tract
        # membership or allocation, so no disagreement changes the Place result.
        if str(run["market_id"]) == "40060":
            smoke_path = out / "richmond_place_tract_smoke.parquet"
            smoke_query = f"""
            WITH assignments AS (SELECT * FROM read_parquet({sql_literal(str(destination))})),
            place_rows AS (SELECT source_record_key, geo_id AS place_geoid, assignment_status FROM assignments WHERE geo_level = 'place'),
            tract_rows AS (SELECT source_record_key, geo_id AS tract_geoid, assignment_status FROM assignments WHERE geo_level = 'tract')
            SELECT {sql_literal(run['source_run_id'])} AS source_run_id,
                   p.assignment_status AS place_assignment_status, t.assignment_status AS tract_assignment_status,
                   count(*) AS poi_count
            FROM place_rows p JOIN tract_rows t USING (source_record_key)
            GROUP BY 1, 2, 3 ORDER BY 2, 3
            """
            con.execute(f"COPY ({smoke_query}) TO {sql_literal(str(smoke_path))} (FORMAT PARQUET, COMPRESSION ZSTD)")

    coverage = round(100 * accounting[3] / accounting[1], 2) if accounting[1] else None
    manifest = {
        "source_run_id": run["source_run_id"], "place_interface": "geo.places_analysis",
        "place_boundary_vintage": place_vintage, "place_assignment_method": PLACE_METHOD,
        "boundary_policy": "Assign only one strict-interior match; preserve touched boundaries or multiple candidates as boundary_ambiguous.",
        "rows": [dict(zip(["geo_level", "assignment_status", "count"], row)) for row in summary],
        "place_row_accounting": dict(zip([
            "input_records", "retained_valid_points", "place_assignment_rows", "assigned_points",
            "no_census_place_points", "boundary_ambiguous_points", "invalid_or_unassignable_points",
        ], accounting)),
        "place_assignment_coverage_pct": coverage, "qa_artifact": qa_destination.name,
        "richmond_tract_smoke_artifact": "richmond_place_tract_smoke.parquet" if str(run["market_id"]) == "40060" else None,
        "zip_note": "Postal ZIP comes from the source address; it is not a Census ZCTA point-in-polygon assignment.",
    }
    (out / "assignment_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
