# Parcel Standardization

This folder now centers on one manual county ETL:

- `../../data_platform/layers/04_parcel_standardization/state_scripts/fl_parcel_etl_manual_county.R`

That script is the working Florida parcel standardization path consumed by Section 05, but it is now owned by Layer 04.

## Sprint 3 Scope

Sprint 3 keeps parcel ETL manual.

The goal for this folder is not to automate county ingestion. The goal is to
make the manual county workflow explicit enough that downstream Section 05 runs
have a stable, reviewable input contract.

## Current Workflow

The current workflow is intentionally manual and county-first:

1. set county config directly in `data_platform/layers/04_parcel_standardization/state_scripts/fl_parcel_etl_manual_county.R`
2. read and clean one county tabular file
3. write county tabular rows into `rof_parcel.parcel_tabular_clean`
4. read and trim one county geometry file
5. write one county geometry `.rds`
6. run an in-memory tabular-to-geometry join check
7. write county QA artifacts locally

This keeps the expensive spatial data out of DuckDB and stores county geometry
as lightweight R artifacts instead.

## Section 05 Downstream Contract

Section 05 consumes a configured parcel standardized root. By default this is
controlled by shared config, and it can be overridden with
`ROF_PARCEL_STANDARDIZED_ROOT`.

Section 05 currently expects:

1. A parcel standardized root directory that exists.
2. A `parcel_ingest_manifest.rds` file when manifest-driven paths are being
used.
3. County analysis geometry artifacts at:
   `county_outputs/<county_tag>/parcel_geometries_analysis.rds`
4. County-level QA artifacts that make join quality reviewable before Section 05
consumption.

The minimum required columns in each county analysis geometry artifact are:

- `join_key`
- `parcel_id`
- `county`
- `county_name`
- `use_code`
- `land_value`
- `total_value`
- `sale_price1`
- `sale_yr1`
- `sale_mo1`
- `qa_missing_join_key`
- `qa_zero_county`
- `geometry`

Geometry requirements:

- storage CRS must be EPSG:4326
- empty geometries should not be present in the analysis artifact
- invalid geometries may still appear, but they should be visible in county QA
and treated as review items before downstream export or map publication

Manifest expectations:

- `parcel_ingest_manifest.rds` should identify county-level analysis artifacts
through an `analysis_path` field when available
- manifest rows should be county-grain, not mixed multi-county summaries
- county tags should be stable across reruns so manual refreshes replace the
intended county artifacts

## Active Files

- `fl_parcel_etl_manual_county.R`
  Lives in `data_platform/layers/04_parcel_standardization/state_scripts/fl_parcel_etl_manual_county.R`.
  Manual Florida county ETL used for current parcel onboarding and reruns.

- `fl_county_run_checklist.md`
  Florida county completion checklist for the current manual workflow.

## Output Contract

DuckDB:

- `rof_parcel.parcel_tabular_clean`
  County-scoped tabular rows, replaced one county at a time by `county_tag`.

Geometry on disk:

- preferred Sprint 3 Section 05 handoff:
  `<parcel_standardized_root>/county_outputs/<county_tag>/parcel_geometries_analysis.rds`
- older county geometry artifacts may still exist outside the standardized root,
  but they are no longer the preferred Section 05 contract

QA on disk:

- preferred Sprint 3 county QA handoff:
  `<parcel_standardized_root>/county_outputs/<county_tag>/parcel_geometry_join_qa.rds`
- optional unmatched review extracts may also be stored beside county QA outputs

## Notes

- Geometry duplicates are preserved in the current workflow.
- County geometry is stored for spatial analysis and plotting, not in DuckDB.
- If a county has problematic geometry, use `repair_invalid_geom <- TRUE` in
  `fl_parcel_etl_manual_county.R` only when needed.
- Before running Section 05, confirm the parcel standardized root, manifest, and
county analysis artifacts are aligned for the target manual refresh set.
