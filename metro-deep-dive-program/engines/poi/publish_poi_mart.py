#!/usr/bin/env python3
"""Publish one market's POI run artifacts as queryable DuckDB tables.

Each table is keyed by `cbsa_code`, so markets accumulate rather than
overwrite. Re-running a market replaces only that market's rows: POI history is
not retained, so the newest run for a CBSA is the only one served.

The taxonomy rules are not published here. They live in the versioned YAML seed
and are read directly from it; a second copy in the mart could drift from the
contract silently.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb

from normalize_overture_places import latest_source_run
from acquire_overture_places import ENGINE_DIR, database_path, sql_literal


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--market', required=True)
    parser.add_argument('--source-run-dir', type=Path)
    parser.add_argument('--output-root', type=Path, default=ENGINE_DIR / 'outputs')
    parser.add_argument('--db-path', type=Path)
    args = parser.parse_args()

    run = args.source_run_dir or latest_source_run(args.output_root, args.market)
    manifest = json.loads((run / 'source_run_manifest.json').read_text(encoding='utf-8'))
    cbsa = str(manifest['market_id'])

    artifacts = {
        'poi_source_place': run / 'normalized' / 'poi_source_place.parquet',
        'poi_classified_place': run / 'classified' / 'poi_classified_place.parquet',
        'poi_geography_assignment': run / 'geography' / 'poi_geography_assignment.parquet',
        'poi_taxonomy_hierarchy_tag_profile': run / 'classified' / 'taxonomy_profile' / 'poi_taxonomy_hierarchy_tag.parquet',
    }
    missing = [str(p) for p in artifacts.values() if not p.exists()]
    if missing:
        raise FileNotFoundError('Missing POI artifacts: ' + ', '.join(missing))

    with duckdb.connect(str(database_path(args.db_path))) as con:
        con.execute('CREATE SCHEMA IF NOT EXISTS mart_poi')
        for table, path in artifacts.items():
            source = f'read_parquet({sql_literal(str(path))})'
            # Every served table keys on cbsa_code, so it is normalized here
            # rather than assumed. Artifacts arrive in three shapes: carrying
            # cbsa_code already, carrying the same value as market_id, or
            # carrying no market column at all.
            columns = [
                row[0] for row in con.execute(f'DESCRIBE SELECT * FROM {source}').fetchall()
            ]
            if 'cbsa_code' in columns:
                select = f'SELECT * FROM {source}'
            elif 'market_id' in columns:
                select = f'SELECT market_id AS cbsa_code, * FROM {source}'
            else:
                select = f'SELECT {sql_literal(cbsa)} AS cbsa_code, * FROM {source}'
            exists = con.execute(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = 'mart_poi' AND table_name = ?",
                [table],
            ).fetchone()[0]
            if exists:
                # Delete-then-insert, never a bare insert: re-running a market
                # must replace its rows rather than double them.
                con.execute(
                    f'DELETE FROM mart_poi.{table} WHERE cbsa_code = {sql_literal(cbsa)}'
                )
                con.execute(f'INSERT INTO mart_poi.{table} {select}')
            else:
                con.execute(f'CREATE TABLE mart_poi.{table} AS {select}')
            rows = con.execute(
                f'SELECT count(*) FROM mart_poi.{table} WHERE cbsa_code = {sql_literal(cbsa)}'
            ).fetchone()[0]
            total = con.execute(f'SELECT count(*) FROM mart_poi.{table}').fetchone()[0]
            print(f'mart_poi.{table}: {rows:,} rows for CBSA {cbsa} ({total:,} total)')


if __name__ == '__main__':
    main()
