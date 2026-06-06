# Section 05 Parcel Pipeline Strategy And Approach

This document is the canonical design and operator runbook for the Retail Opportunity Finder parcel preprocessing workflow.

It replaces and consolidates:
- `sections/05_parcels/parcel_standardization/parcel_data_pipeline.md`
- `sections/05_parcels/parcel_standardization/parcel_data_ingestion_and_enrichment.md`

The intended operating model is a single manual ETL script that a user runs in RStudio one county at a time.

## Sprint 3 status note

For Sprint 3, this document should be read as a manual workflow and contract
document, not an automation roadmap.

The active Sprint 3 requirement is:
- keep county ETL manual
- harden the parcel input contract that Section 05 consumes
- make county outputs, manifests, and QA artifacts explicit enough that
multi-market ROF runs have dependable parcel inputs

The active Sprint 3 non-goal is:
- do not build a fully automated county batch ETL framework in this sprint

## 1. Core Design Decision

The parcel workflow should be treated as one visible ETL flow, not as a set of separately operated scripts with hidden control flow.

The preferred operator experience is:
1. Open one parcel ETL script in RStudio.
2. Set config at the top.
3. Read and standardize parcel tabular data.
4. Read one county shapefile and build county geometry outputs.
5. Inspect intermediate objects and county QA.
6. Write or refresh DuckDB outputs incrementally for that county.
7. Change only the county input and repeat.

This design is intentionally flatter than a typical abstracted pipeline because manual debugging and inspectability are more important here than elegant reuse.

## 2. Why The Previous Design Was Too Abstract

The older workflow created several practical problems:
- too many helper functions for simple path and config work
- major ETL logic wrapped inside `run_*()` functions
- geometry processing coupled to batch statewide loops
- county failures harder to isolate
- intermediate objects harder to inspect in RStudio
- multiple overlapping documents describing similar flows

The rebuild should optimize for:
- line-by-line execution
- county-by-county control
- visible config
- visible intermediate objects
- safe county reruns
- incremental DuckDB refresh

## 3. End-State Workflow

The intended end-state flow is:

```text
raw parcel CSVs + metadata + one county shapefile
  -> standardized parcel attributes
  -> county raw joined geometry
  -> county analysis geometry
  -> county QA outputs
  -> incremental DuckDB county refresh
  -> aggregate QA / manifest refresh in DuckDB
  -> Section 05 parcel inputs
```

Important operating rule:
- county is the unit of geometry processing, QA review, rerun, and DuckDB replacement

Important state rule:
- local disk stores county artifacts for inspection
- DuckDB stores the aggregate cross-county state

## 3A. Section 05 consumption contract

Section 05 does not consume arbitrary parcel folders. It consumes a configured
parcel standardized root with a predictable county output layout.

Minimum downstream handoff requirements:
- parcel standardized root exists and is pointed to by shared config or
  `ROF_PARCEL_STANDARDIZED_ROOT`
- county analysis artifacts exist at
  `county_outputs/<county_tag>/parcel_geometries_analysis.rds`
- county QA artifacts exist and are reviewable before downstream use
- `parcel_ingest_manifest.rds` exists when manifest-driven analysis paths are
  expected

Minimum required columns in county analysis artifacts:
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

Geometry requirements for Section 05 handoff:
- storage CRS must be EPSG:4326
- empty geometries should not be present
- invalid geometries may be retained only when surfaced in QA for follow-up

## 4. Recommended Script Shape

The primary operator-facing workflow should live in one manual script with four sections:

1. `Config`
2. `Read Parcel Tabular`
3. `Build Parcel Geom`
4. `Write To DuckDB And Final QA`

Each section should be runnable on its own in RStudio.

The script should not hide major flow control inside orchestration functions.

## 5. Section 1: Config

The top of the script should expose all runtime controls directly.

Recommended config fields:
- `property_tax_root`
- `property_state`
- `property_data_root`
- `property_metadata_root`
- `parcel_standardized_root`
- `county_shp`
- `county_tag_override`
- `duckdb_path`
- `transform_version`
- `target_storage_epsg`
- `unmatched_threshold`
- `write_local_rds`
- `publish_to_duckdb`
- `refresh_duckdb_qa`
- `rebuild_tabular_each_run`
- `reuse_existing_attribute_artifact`

Recommended constants:
- parcel output filenames
- DuckDB schema name
- DuckDB table names
- QA warning thresholds

Minimal helpers that are still worth keeping in the same script:
- `normalize_join_key()`
- `first_nonempty_value()`
- `duckdb_id()`
- optional `write_manifest_pair()`

Helpers that should not drive the workflow:
- `run_tabular_ingest()`
- `run_geometry_build()`
- `run_publish()`
- large path resolver wrappers that hide actual file paths from the operator

## 6. Section 2: Read Parcel Tabular

This section prepares the statewide parcel attribute layer used by the county geometry join.

### What it should read

- raw parcel CSV files under the parcel data root
- metadata lookup files under the parcel docs root

### What it should do

- enumerate parcel CSV inputs
- read source columns as character first
- normalize source column variants into one shared schema
- standardize names and types
- derive parcel join key candidates from `parcel_id` and `alt_key`
- join metadata lookups for county, use code, and sale qualification context
- attach lineage fields such as source file, ingest timestamp, state, and transform version

### What it should write

- `parcel_attributes_standardized.rds`
- `parcel_attribute_file_manifest.rds`
- `parcel_attribute_file_manifest.csv`

### What should stay visible inline

- source-to-standardized column mapping
- type coercion logic
- lookup joins
- lineage field creation

### What should not be abstracted away

- which input files were found
- which columns were mapped
- what the standardized output columns are

## 7. Section 3: Build Parcel Geom

This is the main county-first working block.

### What it should read

- `parcel_attributes_standardized.rds`
- one county shapefile from `county_shp`

### What it should do

1. Read the county shapefile.
2. Check CRS and transform to the shared storage CRS when possible.
3. Derive a geometry-side `join_key`.
4. Derive `county_tag`.
5. Join standardized parcel attributes onto raw geometry.
6. Create a county raw geometry artifact for audit and troubleshooting.
7. Create a county analysis geometry artifact for downstream Section 05 use.
8. Compute county QA metrics.
9. Write county outputs to disk.

### Duplicate geometry handling

For one county:
1. Split records into valid-key and missing-key groups.
2. Count geometry pieces by county grouping fields plus `join_key`.
3. Keep single-piece keys as-is.
4. Dissolve duplicate-piece keys to one analysis row per key.
5. Append missing-key rows back as flagged records.

This logic should remain visible inside the script because it is one of the main debugging surfaces.

### What it should write per county

- `county_outputs/<county_tag>/parcel_geometries_raw.rds`
- `county_outputs/<county_tag>/parcel_geometries_analysis.rds`
- `county_outputs/<county_tag>/parcel_geometry_join_qa.rds`

### County QA expectations

County QA should record at least:
- `generated_at`
- `source_shp`
- `county_tag`
- `total_rows_raw`
- `unmatched_rows_raw`
- `unmatched_rate_raw`
- `total_rows_analysis`
- `unmatched_rows_analysis`
- `unmatched_rate_analysis`
- `unmatched_threshold`
- `pass`

### Warning policy

- warn when `unmatched_rate_raw > 1%`
- keep unmatched rows in outputs
- treat county QA as monitoring and triage metadata, not an automatic hard stop

## 8. Section 4: Write To DuckDB And Final QA

DuckDB should be the aggregate state store for all completed county loads.

This section should not require a separate manifest-refresh script for normal operator use.

### What it should read

- in-memory standardized attribute data or `parcel_attributes_standardized.rds`
- current county analysis geometry
- current county QA summary
- optional existing DuckDB tables for replacement logic

### What it should do

1. Connect to DuckDB.
2. Ensure the parcel schema exists.
3. Replace statewide standardized attributes when appropriate.
4. Remove existing rows for the current `county_tag` from county-grain geometry and publish tables.
5. Insert current county rows.
6. Update county QA and county load log tables.
7. Refresh aggregate QA and manifest tables or views.
8. Rebuild the spatial view used by downstream analysis.

### Incremental load rule

The replacement grain should be `county_tag`.

That means a county rerun should:
1. delete prior rows for the county
2. insert the newly built rows for the county
3. update county QA state
4. refresh aggregate views or summary tables

This makes county reruns safe and prevents duplicate accumulation.

## 9. Recommended DuckDB Objects

Schema:
- `rof_parcel`

Recommended persistent tables:
- `rof_parcel.parcel_attributes_standardized`
- `rof_parcel.parcel_geometry_standardized`
- `rof_parcel.parcel_publish_ready`
- `rof_parcel.parcel_county_qa`
- `rof_parcel.parcel_county_load_log`
- `rof_parcel.parcel_ingest_manifest`
- `rof_parcel.parcel_publish_contract`

Recommended view:
- `rof_parcel.parcel_publish_ready_spatial`

### Table responsibilities

`parcel_attributes_standardized`
- statewide standardized attribute layer
- may be replaced wholesale when tabular ingest is rerun

`parcel_geometry_standardized`
- county-grain geometry table derived from analysis geometry outputs
- replaced incrementally by county

`parcel_publish_ready`
- ROF-facing parcel publish table
- replaced incrementally by county

`parcel_county_qa`
- one current QA row per loaded county
- supports aggregate quality monitoring

`parcel_county_load_log`
- operational run tracking for county loads
- should record timestamps, source files, transform version, and load status

`parcel_ingest_manifest`
- aggregate manifest of currently loaded county outputs
- should be derived from current county-level state, not manually maintained in multiple places

`parcel_publish_contract`
- current downstream field contract for publish-ready parcel outputs

## 10. Local Outputs Versus Aggregate Outputs

### Local disk outputs

State-level local artifacts:
- `parcel_attributes_standardized.rds`
- `parcel_attribute_file_manifest.rds`
- `parcel_attribute_file_manifest.csv`

County-level local artifacts:
- `county_outputs/<county_tag>/parcel_geometries_raw.rds`
- `county_outputs/<county_tag>/parcel_geometries_analysis.rds`
- `county_outputs/<county_tag>/parcel_geometry_join_qa.rds`

### Aggregate DuckDB outputs

- `rof_parcel.parcel_attributes_standardized`
- `rof_parcel.parcel_geometry_standardized`
- `rof_parcel.parcel_publish_ready`
- `rof_parcel.parcel_publish_ready_spatial`
- `rof_parcel.parcel_county_qa`
- `rof_parcel.parcel_county_load_log`
- `rof_parcel.parcel_ingest_manifest`
- `rof_parcel.parcel_publish_contract`

### Optional compatibility exports

If Section 05 still depends on file-based manifests, the ETL may also export:
- `parcel_ingest_manifest.rds`
- `parcel_ingest_manifest.csv`

If written, these should be treated as exports of the aggregate DuckDB state rather than the primary source of truth.

## 11. Section 05 Compatibility Guidance

Section 05 should continue consuming standardized parcel outputs rather than raw county source files.

Near-term compatibility expectations:
- preserve `county_outputs/<county_tag>/parcel_geometries_analysis.rds`
- preserve `county_outputs/<county_tag>/parcel_geometries_raw.rds`
- preserve enough manifest structure for Section 05 to resolve county analysis files cleanly

Recommended compatibility rule:
- if file-based manifest export is still needed, generate it from DuckDB aggregate state after each county load

This avoids maintaining one manifest on disk and another manifest in SQL by hand.

## 12. Validation Checkpoints

### After tabular ingest

Confirm:
- standardized attribute artifact exists
- attribute manifest exists
- expected standardized columns exist
- row count is plausible relative to the raw CSV inputs
- join key coverage is known

### After county geometry build

Confirm:
- shapefile row count is known
- CRS was transformed successfully or explicitly left unresolved
- `join_key` coverage is known
- raw join unmatched rate is known
- analysis row count is plausible relative to raw geometry rows
- county QA object exists
- county output folder contains the expected three files

### After DuckDB write

Confirm:
- county rows exist in `parcel_geometry_standardized`
- county rows exist in `parcel_publish_ready`
- county QA exists in `parcel_county_qa`
- county load log updated correctly
- aggregate manifest and QA state refresh successfully
- spatial view reconstructs geometry successfully

## 13. Manual RStudio Workflow

Recommended manual workflow:

1. Open the single parcel ETL script.
2. Set config at the top:
   - parcel roots
   - county shapefile
   - county tag override if needed
   - DuckDB path
3. Run the tabular block if attributes need to be rebuilt.
4. Otherwise load the existing attribute artifact and skip ahead.
5. Run the county geometry block.
6. Inspect:
   - `shape`
   - `joined_raw`
   - `analysis_shapes`
   - `joined_analysis`
   - `qa`
7. If the county output looks acceptable, run the DuckDB block.
8. Confirm the county appears in the DuckDB QA and publish tables.
9. Change `county_shp` and repeat for the next county.

This should be the default operating model until a stable batch wrapper is added later.

## 14. Backward Compatibility And Tradeoffs

Preserve where reasonable:
- county output filenames
- county output folder layout
- core DuckDB table names already used downstream
- the existing parcel publish contract unless a clear downstream change is required

Acceptable tradeoffs:
- more repeated code in one script
- less elegant abstraction
- less separation between stages in exchange for easier inspection

This is the correct tradeoff for this workflow because county-level debugging is the dominant operator need.

## 15. What Not To Abstract

Do not hide these steps behind generic helper layers:
- config values and resolved paths
- raw-to-standardized column mapping
- shapefile read and CRS handling
- join-key derivation
- county-tag derivation
- duplicate geometry handling
- county QA calculations
- county-level delete and reinsert logic in DuckDB

These are the steps the operator most needs to see and debug directly.

## 16. Future Expansion

Once the single-script county workflow is stable, batch execution can be added as a thin wrapper around the same county logic.

That later wrapper should:
- loop over county inputs
- call the same visible county processing sections in order
- preserve county-level restartability
- avoid introducing a second competing definition of the workflow

## 17. Document Status

This file is the single maintained source of truth for the Section 05 parcel preprocessing workflow.
