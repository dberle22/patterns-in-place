#!/usr/bin/env python3
"""Append one new market's POI run to the DuckDB marts, never deleting a row.

`publish_poi_mart.py` replaces a market's rows on a rerun. This script refuses
any market that already has rows, so a published market can only be changed by
a deliberate separate step. Each market publishes in one transaction: a failure
leaves no partial market behind, and the publish can simply be retried.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb

from normalize_overture_places import latest_source_run
from acquire_overture_places import ENGINE_DIR, configure_extensions, database_path, sql_literal


def run_artifacts(run: Path) -> dict[str, Path]:
    """Map each existing mart table to its artifact in one source run."""

    return {
        "poi_source_place": run / "normalized" / "poi_source_place.parquet",
        "poi_classified_place": run / "classified" / "poi_classified_place.parquet",
        "poi_geography_assignment": run / "geography" / "poi_geography_assignment.parquet",
        "poi_taxonomy_hierarchy_tag_profile": run / "classified" / "taxonomy_profile" / "poi_taxonomy_hierarchy_tag.parquet",
    }


def artifact_select(con: duckdb.DuckDBPyConnection, path: Path, cbsa: str) -> str:
    """Select an artifact with `cbsa_code`, whichever of three shapes it arrives in."""

    source = f"read_parquet({sql_literal(str(path))})"
    columns = {row[0] for row in con.execute(f"DESCRIBE SELECT * FROM {source}").fetchall()}
    if "cbsa_code" in columns:
        return f"SELECT * FROM {source}"
    if "market_id" in columns:
        return f"SELECT market_id AS cbsa_code, * FROM {source}"
    return f"SELECT {sql_literal(cbsa)} AS cbsa_code, * FROM {source}"


def append_market(con: duckdb.DuckDBPyConnection, cbsa: str, artifacts: dict[str, Path]) -> dict[str, int]:
    """Append every artifact for one market in one transaction and return row counts."""

    missing = [str(path) for path in artifacts.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing POI artifacts: " + ", ".join(missing))

    # All guards run first, so a refused market writes nothing to any table.
    selects = {}
    for table, path in artifacts.items():
        select = artifact_select(con, path, cbsa)
        existing = con.execute(f"SELECT count(*) FROM mart_poi.{table} WHERE cbsa_code = ?", [cbsa]).fetchone()[0]
        if existing:
            raise RuntimeError(f"Refusing to append: mart_poi.{table} already has {existing:,} rows for {cbsa}.")
        # BY NAME fills an absent column with null, so require an exact match.
        target = {row[0] for row in con.execute(f"DESCRIBE mart_poi.{table}").fetchall()}
        incoming = {row[0] for row in con.execute(f"DESCRIBE {select}").fetchall()}
        if target != incoming:
            raise RuntimeError(f"mart_poi.{table} columns differ from its artifact: {sorted(target ^ incoming)}.")
        selects[table] = select

    appended = {}
    con.execute("BEGIN TRANSACTION")
    try:
        for table, select in selects.items():
            expected = con.execute(f"SELECT count(*) FROM ({select})").fetchone()[0]
            con.execute(f"INSERT INTO mart_poi.{table} BY NAME {select}")
            actual = con.execute(f"SELECT count(*) FROM mart_poi.{table} WHERE cbsa_code = ?", [cbsa]).fetchone()[0]
            if actual != expected:
                raise RuntimeError(f"mart_poi.{table} has {actual:,} rows for {cbsa}; expected {expected:,}.")
            appended[table] = actual
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    return appended


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True)
    parser.add_argument("--source-run-dir", type=Path)
    parser.add_argument("--output-root", type=Path, default=ENGINE_DIR / "outputs")
    parser.add_argument("--db-path", type=Path)
    args = parser.parse_args()

    run = args.source_run_dir or latest_source_run(args.output_root, args.market)
    manifest = json.loads((run / "source_run_manifest.json").read_text(encoding="utf-8"))
    cbsa = str(manifest["market_id"])
    with duckdb.connect(str(database_path(args.db_path))) as con:
        # Load spatial first so geometry arrives as GEOMETRY rather than BLOB.
        configure_extensions(con, "local.parquet")
        appended = append_market(con, cbsa, run_artifacts(run))
    for table, rows in appended.items():
        print(f"mart_poi.{table}: appended {rows:,} rows for {cbsa}")


if __name__ == "__main__":
    main()
