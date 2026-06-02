# Data Dictionary: silver.acs_tx_school_metrics

## Overview
- **Table**: `silver.acs_tx_school_metrics`
- **Purpose**: Silver layer analytical table.
- **Row count**: 12,243
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
  - `geo_level + geo_id + year` => rows=12243, distinct=12243, duplicates=0
  - `geo_id + year` => rows=12243, distinct=12243, duplicates=0
  - `geo_level` => rows=12243, distinct=1, duplicates=12242
- **Time coverage**: `year` min=2012, max=2023
- **Geo coverage**: distinct_geo_levels=1; distinct_geo_id=1027

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 1 | len 25-25 | School District (Unified) (12243) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 1027 | len 7-7 | 4800001 (12); 4800002 (12); 4800003 (12); 4800005 (12); 4800006 (12) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 1045 | len 25-82 | Abbott Independent School District, Texas (12); Abernathy Independent School District, Texas (12); Abilene Independent School District, Texas (12); Academy Independent School District, Texas (12); Adrian Independent School District, Texas (12) | Geographic name (from ACS NAME) |
| `year` | `INTEGER` | 0.0000 | 12 | min 2012, max 2023 | 2012 (1022); 2013 (1022); 2014 (1021); 2015 (1021); 2019 (1021) | Observation year or period year for the row. |
| `population` | `DOUBLE` | 0.0000 | 9029 | min 24, max 1494221 | 714.0 (8); 1025.0 (7); 1040.0 (7); 1180.0 (7); 2728.0 (7) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `median_age` | `DOUBLE` | 0.0000 | 451 | min 8.4, max 70.1 | 35.1 (99); 35.2 (95); 34.6 (91); 37.6 (90); 37.7 (90) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `median_income` | `DOUBLE` | 0.2450 | 9489 | min 15917, max 250001 | NULL (30); 61250.0 (27); 56250.0 (24); 46250.0 (22); 53750.0 (22) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `child_poverty_rate` | `DOUBLE` | 0.0000 | 11061 |  | 0.0 (426); 0.2 (15); 0.3333333333333333 (15); 0.16666666666666666 (12); 0.125 (9) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `edu_assoc_share` | `DOUBLE` | 0.0000 | 11638 | min 0, max 0.3125 | 0.0 (64); 0.1 (9); 0.07142857142857142 (8); 0.06666666666666667 (7); 0.047619047619047616 (6) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `edu_bach_share` | `DOUBLE` | 0.0000 | 11856 | min 0, max 0.7374101 | 0.08333333333333333 (9); 0.14285714285714285 (9); 0.1 (8); 0.16666666666666666 (8); 0.0 (7) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `edu_masters_plus` | `DOUBLE` | 0.0000 | 11621 | min 0, max 0.5 | 0.0 (62); 0.03225806451612903 (9); 0.04 (8); 0.022988505747126436 (6); 0.029411764705882353 (6) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `edu_no_higher_ed` | `DOUBLE` | 0.0000 | 11998 | min 0, max 1 | 0.7 (7); 0.7142857142857143 (7); 0.75 (7); 0.8 (7); 0.7272727272727273 (5) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `households_w_children_share` | `DOUBLE` | 0.0000 | 11632 | min 0, max 1 | 0.3333333333333333 (27); 0.25 (18); 0.2857142857142857 (14); 0.36363636363636365 (9); 0.375 (9) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `white_nonhisp_share` | `DOUBLE` | 0.0000 | 12139 | min 0, max 1 | 1.0 (18); 0.0 (6); 0.625 (6); 0.8333333333333334 (6); 0.5 (4) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `black_nonhisp_share` | `DOUBLE` | 0.0000 | 10202 | min 0, max 0.7339045 | 0.0 (1889); 0.0019011406844106464 (3); 0.0024630541871921183 (3); 0.0028089887640449437 (3); 0.00641025641025641 (3) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `amind_nonhisp_share` | `DOUBLE` | 0.0000 | 7547 | min 0, max 0.2567948 | 0.0 (4428); 0.003861003861003861 (5); 0.0047169811320754715 (5); 0.002680965147453083 (4); 0.005714285714285714 (4) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `asian_nonhisp_share` | `DOUBLE` | 0.0000 | 7773 | min 0, max 0.466683 | 0.0 (4289); 0.0026666666666666666 (4); 0.000724112961622013 (3); 0.0015349194167306216 (3); 0.0017452006980802793 (3) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `pacisl_nonhisp_share` | `DOUBLE` | 0.0000 | 2680 | min 0, max 0.0951242 | 0.0 (9552); 0.007874015748031496 (3); 0.0006150061500615006 (2); 0.000676246830092984 (2); 0.0007165890361877463 (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `other_nonhisp_share` | `DOUBLE` | 0.0000 | 4130 | min 0, max 0.0650823 | 0.0 (8078); 0.0006489292667099286 (3); 0.002336448598130841 (3); 0.0003151591553734636 (2); 0.00034518467380048324 (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `two_plus_nonhisp_share` | `DOUBLE` | 0.0000 | 10384 | min 0, max 0.625 | 0.0 (1487); 0.013513513513513514 (5); 0.0136986301369863 (5); 0.017543859649122806 (5); 0.024390243902439025 (5) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `hispanic_any_share` | `DOUBLE` | 0.0000 | 12083 | min 0, max 1 | 0.0 (55); 0.09090909090909091 (5); 0.16666666666666666 (5); 1.0 (5); 0.1 (4) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `racial_diversity_index` | `DOUBLE` | 0.0000 | 12216 | min 0.2353113, max 1 | 1.0 (23); 0.7222222222222223 (3); 0.6755829903978052 (2); 0.8167430237401083 (2); 0.8541319478482503 (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
## Data Quality Notes
- Columns with non-zero null rates: median_income=0.245%
- Key uniqueness check for recommended PK (`geo_level + geo_id + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_tx_school_district.sql:47:from metro_deep_dive.silver.acs_tx_school_metrics`

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
