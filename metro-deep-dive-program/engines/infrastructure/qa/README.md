# Infrastructure QA Outputs

Epic 4 writes reproducible QA artifacts within each ignored local source run:
`validated/osm_core_v1/qa_summary.json`, a retained/rejected Parquet pair,
and `review_map.svg`. The SVG is a bounded qualitative sample (at most 500
features per group/type/form), not a display or analytical data product.

The QA summary includes source-run coverage, geometry validation outcomes,
feature and mapping counts, unmapped raw-tag evidence, and water count/area/
vertex-complexity profiles. DuckDB/Parquet products remain canonical; display
artifacts are review aids only.

Every source run must report source row accounting, market coverage,
identity completeness and duplicates, geometry type/CRS/emptiness/validity and
repair outcomes, clipping/rejections, mapping status and unmapped-tag
distributions, material overlaps, and qualitative samples as specified in
[the contract](../CONTRACT.md).
