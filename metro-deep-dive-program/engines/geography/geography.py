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
