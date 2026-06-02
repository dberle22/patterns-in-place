# Data Dictionary: silver.income_kpi

## Overview
- **Table**: `silver.income_kpi`
- **Purpose**: Silver income table (`kpi` type).
- **Row count**: 1,020,930
- **KPI applicability**: KPI table (or has KPI dictionary entries).

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + geo_name + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `geo_name`, `year`)
  - `geo_level + geo_id + geo_name + year` => rows=1020930, distinct=1020930, duplicates=0
  - `geo_level + geo_id + year` => rows=1020930, distinct=1020930, duplicates=0
  - `geo_id + year` => rows=1020930, distinct=998787, duplicates=22143
  - `geo_level` => rows=1020930, distinct=9, duplicates=1020921
- **Time coverage**: `year` min=2012, max=2024
- **Geo coverage**: distinct_geo_levels=9; distinct_geo_id=115976

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 9 | len 2-8 | zcta (433172); place (397094); tract (135851); county (41870); cbsa (12085) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 115976 | len 1-11 | 1 (39); 2 (26); 3 (26); 4 (26); 01001 (25) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 97125 | len 4-66 | Alexandria city, Virginia (26); Baltimore city, Maryland (26); Bristol city, Virginia (26); Buena Vista city, Virginia (26); Carson City, Nevada (26) | Geographic name (from ACS NAME) |
| `year` | `INTEGER` | 0.0000 | 13 | min 2012, max 2024 | 2024 (82276); 2023 (82271); 2022 (82134); 2021 (81848); 2020 (81194) | Observation year or period year for the row. |
| `median_hh_income` | `DOUBLE` | 6.0525 | 122343 |  | NULL (61792); 46250.0 (2140); 48750.0 (2115); 41250.0 (2063); 51250.0 (2020) | Median household income in the past 12 months. |
| `per_capita_income` | `DOUBLE` | 2.0314 | 90038 |  | NULL (20739); 22937.0 (69); 22485.0 (68); 23844.0 (68); 24771.0 (66) | Per capita income in the past 12 months. |
| `pov_universe` | `DOUBLE` | 0.0069 | 79624 | min 0, max 327079190 | 0.0 (14548); 61.0 (616); 74.0 (614); 115.0 (610); 69.0 (604) | Total Poverty Universe, used as base for poverty rates. |
| `pov_below` | `DOUBLE` | 0.0069 | 29390 | min 0, max 47755606 | 0.0 (59343); 10.0 (4274); 9.0 (4232); 8.0 (4160); 6.0 (4060) | Total population below poverty level, used as numerator for poverty rates. |
| `pov_rate` | `DOUBLE` | 0.0069 | 617276 |  | 0.0 (44795); -nan (14548); 1.0 (2172); 0.16666666666666666 (718); 0.25 (684) | Poverty Rate, dervied from pov_below and pov_universe. (from silver.kpi_dictionary). |
| `gini_index` | `DOUBLE` | 2.4890 | 13071 |  | NULL (25411); 0.4121 (716); 0.4077 (714); 0.4032 (712); 0.4083 (707) | Ratio of Gini Index, a meaure of economic equality (0=perfect equality, 1=perfect inequality). |
| `pct_hh_lt25k` | `DOUBLE` | 0.0069 | 474906 |  | 0.0 (33590); -nan (15641); 1.0 (3651); 0.3333333333333333 (2423); 0.25 (2375) | Share of Households earning less than $25k Per Year. |
| `pct_hh_25k_50k` | `DOUBLE` | 0.0069 | 444993 |  | 0.0 (27873); -nan (15641); 1.0 (3394); 0.25 (3064); 0.3333333333333333 (3058) | Share of Households earning between $25k and $50k Per Year. |
| `pct_hh_50k_100k` | `DOUBLE` | 0.0069 | 446204 |  | 0.0 (22523); -nan (15641); 1.0 (4009); 0.3333333333333333 (3776); 0.25 (2582) | Share of Households earning between $50k and $100k Per Year. |
| `pct_hh_100k_plus` | `DOUBLE` | 0.0069 | 485883 |  | 0.0 (52382); -nan (15641); 1.0 (2789); 0.2 (1627); 0.25 (1598) | Share of Households earning more than $100k Per Year. |
## Data Quality Notes
- Columns with non-zero null rates: median_hh_income=6.0525%, per_capita_income=2.0314%, pov_universe=0.0069%, pov_below=0.0069%, pov_rate=0.0069%, gini_index=2.489%, pct_hh_lt25k=0.0069%, pct_hh_25k_50k=0.0069%, pct_hh_50k_100k=0.0069%, pct_hh_100k_plus=0.0069%
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_economy_income.sql:32:from metro_deep_dive.silver.income_kpi `
   - `scripts/etl/gold/gold_economy_gdp.sql:31:from metro_deep_dive.silver.income_kpi `
   - `scripts/etl/gold/gold_economy_wide.sql:35:from metro_deep_dive.silver.income_kpi `
   - `scripts/etl/silver/acs_income_silver.R:147:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="income_kpi"),`
2. **Downstream usage (examples)**:
   - `notebooks/retail_opportunity_finder/tract_features.sql:85:  FROM metro_deep_dive.silver.income_kpi`

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
