#!/usr/bin/env python3
"""Assign classified POIs to governed tract, county, and postal-ZIP surfaces."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import duckdb
from normalize_overture_places import latest_source_run
from acquire_overture_places import ENGINE_DIR, database_path, configure_extensions, sql_literal

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--market', required=True); parser.add_argument('--source-run-dir', type=Path)
    parser.add_argument('--output-root', type=Path, default=ENGINE_DIR/'outputs'); parser.add_argument('--db-path', type=Path)
    args=parser.parse_args(); run_dir=args.source_run_dir or latest_source_run(args.output_root,args.market)
    run=json.loads((run_dir/'source_run_manifest.json').read_text()); places=run_dir/'classified'/'poi_classified_place.parquet'
    if not places.exists(): raise FileNotFoundError('Run classification before geography assignment.')
    out=run_dir/'geography'; out.mkdir(exist_ok=True); destination=out/'poi_geography_assignment.parquet'
    with duckdb.connect(str(database_path(args.db_path)), read_only=True) as con:
      configure_extensions(con,'local.parquet')
      # Limit both geometry candidates to the governed CBSA before spatial joins.
      # Every assignment carries its CBSA so markets can be loaded and filtered
      # independently rather than overwriting one shared table.
      cbsa=sql_literal(str(run['market_id']))
      q=f"""WITH p AS (SELECT source_record_key, longitude, latitude, source_address, source_postal_zip FROM read_parquet({sql_literal(str(places))})),
      point AS (SELECT *, ST_Point(longitude, latitude) AS geom FROM p),
      counties AS (SELECT c.county_geoid, c.geom FROM geo.counties c JOIN mart_geography.rollup_county_to_cbsa x ON c.county_geoid=x.county_geoid WHERE x.cbsa_code={sql_literal(str(run['market_id']))}),
      tracts AS (SELECT t.tract_geoid, t.geom FROM geo.tracts_all_us t JOIN mart_geography.rollup_tract_to_cbsa x ON t.tract_geoid=x.tract_geoid WHERE x.cbsa_code={sql_literal(str(run['market_id']))}),
      tract_hits AS (SELECT p.source_record_key, t.tract_geoid, row_number() OVER (PARTITION BY p.source_record_key ORDER BY t.tract_geoid) AS rn FROM point p LEFT JOIN tracts t ON ST_Intersects(p.geom,t.geom)),
      tract_assign AS (SELECT source_record_key, 'tract' geo_level, tract_geoid geo_id, 2020 boundary_vintage, 'point_in_polygon' assignment_method, CASE WHEN tract_geoid IS NULL THEN 'unassigned' ELSE 'assigned' END assignment_status FROM tract_hits WHERE rn=1),
      county_hits AS (SELECT p.source_record_key, c.county_geoid, row_number() OVER (PARTITION BY p.source_record_key ORDER BY c.county_geoid) AS rn FROM point p LEFT JOIN counties c ON ST_Intersects(p.geom,c.geom)),
      county_assign AS (SELECT source_record_key, 'county' geo_level, county_geoid geo_id, 2023 boundary_vintage, 'point_in_polygon' assignment_method, CASE WHEN county_geoid IS NULL THEN 'unassigned' ELSE 'assigned' END assignment_status FROM county_hits WHERE rn=1),
      zip_assign AS (SELECT source_record_key, 'zip' geo_level, coalesce(nullif(trim(source_postal_zip), ''), nullif(regexp_extract(source_address, '([0-9]{{5}})(?:-[0-9]{{4}})?', 1), '')) geo_id, NULL::INTEGER boundary_vintage, 'source_address_postal_zip' assignment_method, CASE WHEN coalesce(nullif(trim(source_postal_zip), ''), nullif(regexp_extract(source_address, '([0-9]{{5}})(?:-[0-9]{{4}})?', 1), '')) IS NOT NULL THEN 'address_supplied' ELSE 'unassigned' END assignment_status FROM p)
      SELECT {cbsa} AS cbsa_code, * FROM (SELECT * FROM tract_assign UNION ALL SELECT * FROM county_assign UNION ALL SELECT * FROM zip_assign)"""
      con.execute(f"COPY ({q}) TO {sql_literal(str(destination))} (FORMAT PARQUET, COMPRESSION ZSTD)")
      summary=con.execute(f"SELECT geo_level, assignment_status, count(*) FROM ({q}) GROUP BY 1,2 ORDER BY 1,2").fetchall()
    (out/'assignment_manifest.json').write_text(json.dumps({'source_run_id':run['source_run_id'],'rows':[dict(zip(['geo_level','assignment_status','count'],r)) for r in summary],'zip_note':'Postal ZIP comes from the source address; it is not a ZCTA point-in-polygon assignment.'},indent=2)+'\n')
    print(json.dumps([dict(zip(['geo_level','assignment_status','count'],r)) for r in summary],indent=2))
if __name__=='__main__': main()
