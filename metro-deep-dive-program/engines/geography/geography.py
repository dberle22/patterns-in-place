"""Narrow, metric-safe query helpers for the governed geography mart."""

from __future__ import annotations

from pathlib import Path
from typing import Literal


AllocationBasis = Literal["population", "housing_units", "land_area"]
GeometryRole = Literal["display", "analysis"]


def allocation_edges(con, target_level: Literal["place", "zcta"], basis: AllocationBasis):
    """Return a declared tract allocation; the caller still aggregates its metric."""
    return con.execute(
        """
        SELECT * FROM mart_geography.allocation_edges
        WHERE source_geo_level = 'tract' AND target_geo_level = ? AND weight_basis = ?
        """,
        [target_level, basis],
    )


def temporal_edges(con, basis: AllocationBasis):
    """Return 2010-to-2020 tract restatement edges for one explicit basis."""
    return con.execute(
        """
        SELECT * FROM mart_geography.temporal_edges
        WHERE from_geo_level = 'tract' AND to_geo_level = 'tract'
          AND from_boundary_vintage = 2010 AND to_boundary_vintage = 2020
          AND weight_basis = ?
        """,
        [basis],
    )


def place_membership(con, target_level: Literal["county", "cbsa"], basis: AllocationBasis):
    """Return weighted 2020 Place membership in counties or CBSAs.

    The relationship is not containment. `target_share_in_place` tells how
    much of a Place falls in a target; `place_share_in_target` tells how much
    of that target falls in the Place. Keep membership and quality flags when
    displaying direct Place measures.
    """
    return con.execute(
        """
        SELECT * FROM mart_geography.place_membership
        WHERE target_geo_level = ? AND weight_basis = ?
        """,
        [target_level, basis],
    )


def place_primary_cbsa_association(con):
    """Return population-share primary CBSA labels without discarding splits."""
    return con.execute("SELECT * FROM mart_geography.place_primary_cbsa_association")


def geometry_catalog(con, role: GeometryRole = "display"):
    """Discover geometry carrying one explicit governed role."""
    return con.execute(
        "SELECT * FROM mart_geography.geometry_catalog WHERE geometry_role = ?",
        [role],
    )


def get_geometry(con, table_name: str, role: GeometryRole = "display"):
    """Return an explicitly selected governed geometry relation.

    The catalog check makes table selection data-driven but prevents arbitrary
    SQL identifiers. The caller must explicitly request analysis geometry; it
    is never inferred from a display request.
    """
    allowed = con.execute(
        "SELECT table_name FROM mart_geography.geometry_catalog WHERE geometry_role = ?",
        [role],
    ).fetchall()
    allowed_names = {row[0] for row in allowed}
    if table_name not in allowed_names:
        raise ValueError(f"{table_name!r} is not an approved {role} geometry table")

    return con.execute(f"SELECT * FROM geo.{table_name}")


def assign_point_to_place(con, longitude: float, latitude: float):
    """Assign a WGS84 point using governed Place analysis geometry.

    Returns every matching Place and one explicit status: ``within`` for one
    strict interior match, ``boundary`` for one touched boundary, ``overlap``
    for multiple candidates, and ``no_place`` when unincorporated or otherwise
    outside every Place. Invalid source geometry fails the build, not this read.
    """
    get_geometry(con, "places_analysis", role="analysis")
    return con.execute(
        """
        WITH point AS (SELECT ST_Point(?, ?) AS geom), candidates AS (
          SELECT p.place_geoid, p.place_name,
                 CASE WHEN ST_Contains(p.geom, q.geom) THEN 'within' ELSE 'boundary' END AS match_type
          FROM geo.places_analysis p CROSS JOIN point q
          WHERE ST_Contains(p.geom, q.geom) OR ST_Touches(p.geom, q.geom)
        ), classified AS (
          SELECT *, count(*) OVER () AS candidate_count FROM candidates
        )
        SELECT place_geoid, place_name,
               CASE WHEN candidate_count > 1 THEN 'overlap' ELSE match_type END AS assignment_status
        FROM classified
        UNION ALL
        SELECT NULL, NULL, 'no_place'
        WHERE NOT EXISTS (SELECT 1 FROM candidates)
        """,
        [longitude, latitude],
    )


def place_line_intersections(con, wkb: bytes):
    """Return governed Places intersecting a supplied WGS84 line or polygon WKB."""
    get_geometry(con, "places_analysis", role="analysis")
    return con.execute(
        """SELECT place_geoid, place_name, boundary_vintage
           FROM geo.places_analysis
           WHERE ST_Intersects(geom, ST_GeomFromWKB(?))""",
        [wkb],
    )


def export_geometry(con, table_name: str, output_path: str | Path, role: GeometryRole = "display") -> None:
    """Write a selected governed geometry table as a scoped Parquet artifact."""
    geometry = get_geometry(con, table_name, role)
    # Execute the validated relation before COPY so the function fails before
    # creating an artifact if the selected materialization disappeared.
    geometry.fetch_record_batch(1)

    destination = Path(output_path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    escaped_destination = str(destination).replace("'", "''")
    con.execute(f"COPY (SELECT * FROM geo.{table_name}) TO '{escaped_destination}' (FORMAT PARQUET)")
