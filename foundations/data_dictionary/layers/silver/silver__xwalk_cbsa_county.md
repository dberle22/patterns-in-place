# Data Dictionary: silver.xwalk_cbsa_county

## Overview
- **Table**: `silver.xwalk_cbsa_county`
- **Purpose**: Crosswalk between Core-Based Statistical Areas (CBSAs) and counties, including CBSA type, CSA context, and county role (central/outlying).
- **Row count**: 1,915
- **Built from**: OMB 2023 CBSA-county source file via `scripts/etl/silver/geo_crosswalks_silver.R`.
- **KPI applicability**: Not a KPI table (dimension/crosswalk table).

## Grain & Keys
- **Declared grain (inferred from ETL logic and observed uniqueness)**: One row per CBSA-county relationship for vintage 2023.
- **Primary key candidate (recommended)**: (`cbsa_code`, `county_geoid`)
  - Uniqueness check: 1,915 distinct of 1,915 rows.
- **Alternate observed unique key (current snapshot only)**: `county_geoid`
  - Note: This is unique in the current table, but should be treated as a snapshot behavior, not a durable contractual PK for multi-vintage data.
- **Current vintage coverage**: 2023 only (`min(vintage)=max(vintage)=2023`).
- **Geo coverage**:
  - 935 distinct CBSAs
  - 1,915 distinct counties included in CBSAs
  - 52 distinct state/territory FIPS values in table
  - `silver.xwalk_county_state` comparison indicates 1,320 counties are not in any CBSA and therefore are expectedly absent from this table.

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `cbsa_code` | `VARCHAR` | 0.0000 | 935 | len 5-5 | 41980 (40); 12060 (29); 47900 (23); 35620 (22); 47260 (18) | 5-digit CBSA code from OMB source. |
| `cbsa_name` | `VARCHAR` | 0.0000 | 935 | len 7-46 | San Juan-Bayamon-Caguas, PR (40); Atlanta-Sandy Springs-Roswell, GA (29); Washington-Arlington-Alexandria, DC-VA-MD-WV (23); New York-Newark-Jersey City, NY-NJ (22); Virginia Beach-Chesapeake-Norfolk, VA-NC (18) | CBSA title from source file. |
| `csa_code` | `VARCHAR` | 29.9739 | 184 | len 3-3 | NULL (574); 490 (50); 122 (42); 548 (42); 408 (30) | 3-digit Combined Statistical Area code where applicable. |
| `csa_name` | `VARCHAR` | 29.9739 | 184 | len 15-51 | NULL (574); San Juan-Bayamon, PR (50); Atlanta--Athens-Clarke County--Sandy Springs, GA-AL (42); Washington-Baltimore-Arlington, DC-MD-VA-WV-PA (42); New York-Newark, NY-NJ-CT-PA (30) | Combined Statistical Area name where applicable. |
| `cbsa_type` | `VARCHAR` | 0.0000 | 2 | len 29-29 | Metropolitan Statistical Area (1252); Micropolitan Statistical Area (663) | OMB CBSA type classification. |
| `county_name` | `VARCHAR` | 0.0000 | 1314 | len 10-46 | Jefferson County (20); Washington County (20); Franklin County (14); Madison County (14); Lincoln County (12) | County or county-equivalent name from source. |
| `state_name` | `VARCHAR` | 0.0000 | 52 | len 4-20 | Texas (133); Georgia (106); Virginia (86); North Carolina (71); Puerto Rico (71) | State/territory name from source. |
| `state_fips` | `VARCHAR` | 0.0000 | 52 | len 2-2 | 48 (133); 13 (106); 51 (86); 37 (71); 72 (71) | 2-digit state FIPS code from source. |
| `county_fips` | `VARCHAR` | 0.0000 | 244 | len 3-3 | 005 (35); 013 (33); 003 (32); 015 (32); 019 (32) | 3-digit county FIPS code (within state). |
| `county_flag` | `VARCHAR` | 0.0000 | 2 | len 7-8 | Central (1325); Outlying (590) | County role in CBSA as provided by OMB source. |
| `county_geoid` | `VARCHAR` | 0.0000 | 1915 | len 5-5 | 01001 (1); 01003 (1); 01005 (1); 01007 (1); 01009 (1) | 5-digit county GEOID derived as zero-padded state_fips + county_fips. |
| `vintage` | `INTEGER` | 0.0000 | 1 | min 2023, max 2023 | 2023 (1915) | Reference year assigned by ETL. |
| `source` | `VARCHAR` | 0.0000 | 1 | len 8-8 | OMB_2023 (1915) | Provenance label assigned by ETL. |
## Data Quality Notes
- No nulls in 11/13 columns; nulls are concentrated in CSA fields (`csa_code`, `csa_name`) at 29.9739%, consistent with non-CSA CBSAs.
- Observed uniqueness supports (`cbsa_code`, `county_geoid`) as the durable row identifier.
- `county_geoid` is currently unique in this table, indicating one-CBSA assignment per included county in this vintage snapshot.
- The table is a CBSA coverage subset, not a full county universe.

## Lineage
1. **Primary build script**: `scripts/etl/silver/geo_crosswalks_silver.R`
   - Environment and DB target setup: lines 13-21.
   - Upstream raw read: `read_excel(".../demographics/raw/crosswalks/cbsa_county_xwalk_census.xlsx", skip = 2)` at lines 25-26.
   - Column standardization + transforms: lines 28-48.
     - Renames from raw OMB fields to canonical names.
     - Filter: `filter(!is.na(cbsa_name))`.
     - Type normalization: `cbsa_code` and `csa_code` cast to character.
     - Derived key: `county_geoid = sprintf("%02d%03d", as.integer(state_fips), as.integer(county_fips))`.
     - Metadata injection: `vintage = 2023L`, `source = "OMB_2023"`.
   - Write target: `dbWriteTable(... schema="silver", table="xwalk_cbsa_county", overwrite = TRUE)` at lines 50-51.
2. **Design documentation corroboration**: `documents/database_design/XWALK_README.md` section "CBSA ⇔ County" (lines 66-109).
3. **Downstream consumption (examples)**:
   - `scripts/etl/silver/acs_age_silver.R:45`
   - `scripts/etl/silver/acs_income_silver.R:45`
   - `scripts/etl/gold/gold_housing_core.sql:67`
   - `notebooks/national_analyses/real_personal_income/real_personal_income_base.sql:24`

## Known Gaps / To-Dos
- `silver.metadata_topics`, `silver.metadata_vars`, and `silver.kpi_dictionary` exist but currently have no entries for `xwalk_cbsa_county`; add metadata rows to make this table discoverable by metadata-first tooling.
- Primary/foreign keys are not enforced as DB constraints; consider adding integrity tests in ETL.
- Current build hard-codes 2023 and overwrites table; consider parameterizing vintage and preserving historical snapshots.

## How To Extend (Next Table)
1. Pick a target table (for example `silver.xwalk_tract_county`).
2. Run table-existence and row-count checks from DuckDB.
3. Pull schema from `information_schema.columns` and compute per-column profile metrics:
   - null %, distinct count, numeric min/max or text length min/max, top-5 values.
4. Run uniqueness checks for plausible key combinations.
5. Locate ETL lineage with `rg -n "<table_name>|dbWriteTable|CREATE TABLE" scripts notebooks documents`.
6. Capture source file path(s), major transforms, and write statements with file:line references.
7. Write artifacts:
   - `data_dictionary/<schema>__<table>.md`
   - `data_dictionary/<schema>__<table>.yml`
8. Mark any inferred statements explicitly and add `needs confirmation` flags where definitions are unclear.
