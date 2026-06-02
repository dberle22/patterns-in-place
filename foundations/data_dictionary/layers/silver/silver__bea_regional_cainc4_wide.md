# Data Dictionary: silver.bea_regional_cainc4_wide

## Overview
- **Table**: `silver.bea_regional_cainc4_wide`
- **Purpose**: Silver layer analytical table.
- **Row count**: 86,040
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`)
  - `geo_level + geo_id + period` => rows=86040, distinct=86040, duplicates=0
  - `geo_id + period` => rows=86040, distinct=86040, duplicates=0
  - `geo_level` => rows=86040, distinct=3, duplicates=86037
- **Time coverage**: `period` min=2000, max=2023
- **Geo coverage**: distinct_geo_levels=3; distinct_geo_id=3585

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 3 | len 4-6 | county (75360); cbsa (9240); state (1440) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 3585 | len 5-5 | 00000 (24); 00998 (24); 01000 (24); 01001 (24); 01003 (24) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 3585 | len 4-78 | Abbeville, SC (24); Abilene, TX (Metropolitan Statistical Area) (24); Acadia, LA (24); Accomack, VA (24); Ada, ID (24) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 24 | min 2000, max 2023 | 2000 (3585); 2001 (3585); 2002 (3585); 2003 (3585); 2004 (3585) | Time period for the observation (usually calendar year). |
| `table` | `VARCHAR` | 0.0000 | 1 | len 6-6 | CAINC4 (86040) | BEA source table identifier (for example, CAGDP2, CAGDP9, CAINC1, CAINC4, MARPP). |
| `pi_wages_salary` | `DOUBLE` | 0.0000 | 78890 | min 0, max 11716967000000 | 0.0 (663); 26705000.0 (5); 2027908000.0 (4); 208158000.0 (4); 21995000.0 (4) | Total Personal Income component for wages and salary disbursements (from BEA CAINC4 table). |
| `pi_supplements_wages_salary` | `DOUBLE` | 0.0000 | 72393 | min 0, max 2452724000000 | 0.0 (663); 13902000.0 (6); 25089000.0 (6); 11323000.0 (5); 13270000.0 (5) | Total Personal Income component for supplements to wages and salary disbursements (from BEA CAINC4 table). |
| `pi_proprietors` | `DOUBLE` | 0.0000 | 71141 | min -6315931000, max 1945530000000 | 0.0 (663); 19776000.0 (7); 26649000.0 (6); 27114000.0 (6); 28372000.0 (6) | Total Personal Income component for proprietors' income (from BEA CAINC4 table). |
| `pi_dividends_interest_rent` | `DOUBLE` | 0.0000 | 75725 | min 0, max 4806534000000 | 0.0 (663); 41783000.0 (5); 71603000.0 (5); 96472000.0 (5); 16462000.0 (4) | Total Personal Income component for dividends, interest, and rent (from BEA CAINC4 table). |
| `pi_transfer_receipts` | `DOUBLE` | 0.0000 | 77776 | min 0, max 4653728000000 | 0.0 (663); 228959000.0 (5); 101602000.0 (4); 11347000.0 (4); 2338267000.0 (4) | Total Personal Income component for transfer receipts (from BEA CAINC4 table). |
| `pi_net_earnings_residence` | `DOUBLE` | 0.0000 | 80015 | min 0, max 14305741000000 | 0.0 (663); 100373000.0 (3); 102240000.0 (3); 109087000.0 (3); 123341000.0 (3) | Total Personal Income component for net earnings by place of residence (from BEA CAINC4 table). |
| `pi_residence_adjustment` | `DOUBLE` | 0.0000 | 74482 | min -263181240000, max 79800665000 | 0.0 (715); 9165000.0 (8); 3966000.0 (6); 6483000.0 (6); 7651000.0 (6) | Total Personal Income component for residence adjustment (from BEA CAINC4 table). |
| `pi_earnings_workplace` | `DOUBLE` | 0.0000 | 79866 | min 0, max 16115221000000 | 0.0 (663); 121650000.0 (4); 133801000.0 (4); 134364000.0 (4); 42265000.0 (4) | Total Personal Income component for earnings by place of work (from BEA CAINC4 table). |
| `pi_employer_pension_insurance` | `DOUBLE` | 0.0000 | 69376 | min 0, max 1633075000000 | 0.0 (663); 17124000.0 (7); 13165000.0 (6); 17374000.0 (6); 17605000.0 (6) | Total Personal Income component for employer pension and insurance (from BEA CAINC4 table). |
| `pi_employer_social_insurance` | `DOUBLE` | 0.0000 | 58207 | min 0, max 819649000000 | 0.0 (663); 3906000.0 (10); 1689000.0 (9); 3188000.0 (9); 3423000.0 (9) | Total Personal Income component for employer contributions for government social insurance (from BEA CAINC4 table). |
| `pi_nonfarm` | `DOUBLE` | 0.0000 | 80737 | min 0, max 23279071000000 | 0.0 (663); 4971132000.0 (4); 111457000.0 (3); 1261469000.0 (3); 1662775000.0 (3) | Total Personal Income component for nonfarm earnings (from BEA CAINC4 table). |
| `pi_farm_proprietors` | `DOUBLE` | 12.4128 | 39061 | min -316596000, max 1920804000 | NULL (10680); 0.0 (2168); -4000.0 (18); -50000.0 (18); -39000.0 (17) | Total Personal Income component for farm proprietors (from BEA CAINC4 table). |
| `pi_nonfarm_proprietors` | `DOUBLE` | 12.4128 | 61625 | min -6305398000, max 69799913000 | NULL (10680); 0.0 (663); 13371000.0 (6); 13376000.0 (6); 18651000.0 (6) | Total Personal Income component for nonfarm proprietors (from BEA CAINC4 table). |
## Data Quality Notes
- Columns with non-zero null rates: pi_farm_proprietors=12.4128%, pi_nonfarm_proprietors=12.4128%
- Key uniqueness check for recommended PK (`geo_level + geo_id + period`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/bea_cainc4_silver.R:161:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_cainc4_wide"),`
   - `scripts/etl/gold/gold_economy_income.sql:71:from metro_deep_dive.silver.bea_regional_cainc4_wide`
   - `scripts/etl/gold/gold_economy_wide.sql:74:from metro_deep_dive.silver.bea_regional_cainc4_wide`

## Known Gaps / To-Dos
- Validate and harden grain/PK contracts with automated DQ checks.
- Add explicit business definitions for columns flagged as needs confirmation.
- Add enforced lineage metadata entries in `silver.metadata_topics` / `silver.metadata_vars` where missing.

## How To Extend (Next Table)
1. Run table-existence and row-count checks from DuckDB.
2. Pull schema from `information_schema.columns` and compute per-column profile metrics.
3. Run uniqueness checks for plausible key combinations.
4. Locate ETL lineage with `rg -n "<table_name>|dbWriteTable|CREATE TABLE" scripts notebooks documents`.
5. Write `data_dictionary/layers/<layer>/<schema>__<table>.md` and `.yml` artifacts.
6. Mark inferred statements explicitly and set `needs_confirmation` where definitions are unclear.
