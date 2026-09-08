#!/usr/bin/env python3
"""Apply approved Overture taxonomy rules to one normalized source run."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import duckdb, yaml
from normalize_overture_places import latest_source_run
from acquire_overture_places import ENGINE_DIR, sql_literal

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--market', required=True); parser.add_argument('--source-run-dir', type=Path)
    parser.add_argument('--output-root', type=Path, default=ENGINE_DIR / 'outputs')
    parser.add_argument('--rules', type=Path, default=ENGINE_DIR / 'taxonomy' / 'q4_overture_v1.yml')
    args = parser.parse_args(); source_dir = args.source_run_dir or latest_source_run(args.output_root, args.market)
    normalized = source_dir / 'normalized' / 'poi_source_place.parquet'; rules = yaml.safe_load(args.rules.read_text())
    values = ', '.join('(' + ', '.join(sql_literal(str(rule[key])) for key in ('rule_id','source_taxonomy_primary','governed_category')) + ')' for rule in rules['rules'])
    query = f"""WITH rules(rule_id, source_taxonomy_primary, governed_category) AS (VALUES {values})
    SELECT p.*, {sql_literal(rules['mapping_version'])} AS mapping_version, CASE WHEN r.rule_id IS NULL THEN 'unmapped' ELSE 'mapped' END AS mapping_status, r.rule_id AS mapping_rule_id, r.governed_category, CASE WHEN r.rule_id IS NULL THEN NULL ELSE concat('exact taxonomy.primary = ', p.source_taxonomy_primary) END AS mapping_evidence, CASE WHEN r.rule_id IS NULL THEN 'needs_review' ELSE 'approved_rule' END AS review_status FROM read_parquet({sql_literal(str(normalized))}) p LEFT JOIN rules r ON p.source_taxonomy_primary = r.source_taxonomy_primary"""
    out = source_dir / 'classified'; out.mkdir(exist_ok=True)
    with duckdb.connect() as con:
        con.execute(f"COPY ({query}) TO {sql_literal(str(out / 'poi_classified_place.parquet'))} (FORMAT PARQUET, COMPRESSION ZSTD)")
        con.execute(f"COPY (SELECT * FROM ({query}) WHERE mapping_status = 'unmapped') TO {sql_literal(str(out / 'poi_unmapped_review.parquet'))} (FORMAT PARQUET, COMPRESSION ZSTD)")
        con.execute(f"COPY (SELECT * FROM ({query}) WHERE FALSE) TO {sql_literal(str(out / 'poi_ambiguous_review.parquet'))} (FORMAT PARQUET, COMPRESSION ZSTD)")
        summary = con.execute(f"SELECT mapping_status, count(*) FROM ({query}) GROUP BY 1").fetchall()
    (out / 'classification_manifest.json').write_text(json.dumps({'mapping_version': rules['mapping_version'], 'rules': len(rules['rules']), 'counts': dict(summary), 'note': 'No overrides or ambiguous automated rules in v1.'}, indent=2) + '\n')
    print(json.dumps(dict(summary), indent=2))
if __name__ == '__main__': main()
