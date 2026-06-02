# Data Dictionary: gold.tx_isd_metrics

## Overview
- **Table**: `gold.tx_isd_metrics`
- **Purpose**: Gold layer analytical output table.
- **Row count**: 1,010
- **KPI applicability**: Gold output table; may contain derived KPI fields.

## Grain & Keys
- **Declared grain (inferred)**: One row per `district_name`.
- **Primary key candidate (recommended)**: (`district_name`)
  - `district_name` => rows=1010, distinct=999, duplicates=11
- **Time coverage**: No standard time column detected.
- **Geo coverage**: No standard geography columns detected.

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `district_name` | `VARCHAR` | 0.0000 | 999 | len 7-33 | BIG SANDY ISD (2); CENTERVILLE ISD (2); CHAPEL HILL ISD (2); DAWSON ISD (2); EDGEWOOD ISD (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `county_number` | `VARCHAR` | 0.0000 | 250 | len 3-3 | 101 (19); 161 (18); 220 (16); 015 (15); 108 (15) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `county_name` | `VARCHAR` | 0.0000 | 250 | len 10-20 | HARRIS COUNTY (19); MCLENNAN COUNTY (18); TARRANT COUNTY (16); BEXAR COUNTY (15); HIDALGO COUNTY (15) | County or county-equivalent name from source. |
| `esc_region_served` | `VARCHAR` | 0.0000 | 20 | len 2-2 | 07 (94); 10 (80); 12 (77); 11 (76); 16 (60) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `district_city` | `VARCHAR` | 0.0000 | 904 | len 3-22 | SAN ANTONIO (12); CORPUS CHRISTI (6); FORT WORTH (6); HOUSTON (6); WACO (6) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `district_zip` | `VARCHAR` | 0.0000 | 1003 | len 5-10 | 75460 (2); 75647 (2); 76240 (2); 76401 (2); 77327 (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `district_type` | `VARCHAR` | 0.0000 | 1 | len 11-11 | INDEPENDENT (1010) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `nces_district_id` | `VARCHAR` | 0.0000 | 1010 | len 7-7 | 4800001 (1); 4800002 (1); 4800003 (1); 4800005 (1); 4800006 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `district_number` | `VARCHAR` | 0.0000 | 1010 | len 6-6 | 001902 (1); 001903 (1); 001904 (1); 001906 (1); 001907 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `enrollment` | `DOUBLE` | 0.0000 | 863 | min 9, max 176727 | 141.0 (5); 227.0 (5); 119.0 (4); 243.0 (4); 343.0 (4) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `enrollment_pct_rank` | `DOUBLE` | 0.0000 | 863 | min 0, max 1 | 0.057482656095143705 (5); 0.13974231912784935 (5); 0.030723488602576808 (4); 0.16154608523290387 (4); 0.22893954410307235 (4) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `number_of_schools` | `INTEGER` | 0.0000 | 70 | min 1, max 274 | 1 (193); 3 (186); 4 (125); 2 (115); 5 (86) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `avg_school_enrollment` | `DOUBLE` | 0.0000 | 862 | min -1, max 3075.25 | 141.0 (6); 119.0 (4); 163.0 (4); 116.0 (3); 129.0 (3) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `title_1_allocations` | `DOUBLE` | 0.0000 | 983 | min 0, max 169760890 | 0.0 (17); 21534.039622084958 (3); 104270.0865911482 (2); 107670.19811042478 (2); 20400.66911565943 (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `allocations_per_student` | `DOUBLE` | 0.0000 | 988 | min 0, max 2397.82 | 0.0 (17); 201.12 (2); 222.6 (2); 237.49 (2); 296.4 (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `student_allocation_pct_rank` | `DOUBLE` | 0.0000 | 988 | min 0, max 1 | 0.0 (17); 0.333994053518335 (2); 0.3865213082259663 (2); 0.42120911793855303 (2); 0.5609514370664024 (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `economically_disadvantaged_percent` | `DOUBLE` | 12.5743 | 819 | min 0.0054, max 1 | NULL (127); 0.3936 (3); 0.4919 (3); 0.6386 (3); 0.6522 (3) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `economic_disadvantaged_pct_rank` | `DOUBLE` | 12.5743 | 819 | min 0, max 1 | NULL (127); 0.16666666666666666 (3); 0.3333333333333333 (3); 0.6349206349206349 (3); 0.6643990929705216 (3) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `population` | `DOUBLE` | 0.0000 | 979 | min 53, max 1480398 | 1827.0 (3); 1003.0 (2); 10224.0 (2); 1070.0 (2); 1085.0 (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `population_growth_5yr` | `DOUBLE` | 1.1881 | 996 | min -0.7465619, max 1.720339 | NULL (12); 0.0 (3); -0.00013047088127149804 (1); -0.00015137753557372085 (1); -0.0004387339392040113 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `population_growth_pct_rank` | `DOUBLE` | 1.1881 | 996 | min 0, max 1 | NULL (12); 0.4242728184553661 (3); 0.0 (1); 0.0010030090270812437 (1); 0.0020060180541624875 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `pop_growth_quartile` | `BIGINT` | 1.1881 | 4 | min 1, max 4 | 1 (250); 2 (250); 3 (249); 4 (249); NULL (12) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `median_age` | `DOUBLE` | 0.0000 | 297 | min 16.7, max 68.1 | 35.8 (13); 36.2 (12); 36.4 (11); 36.8 (11); 38.3 (11) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `median_income` | `DOUBLE` | 0.9901 | 961 | min 19405, max 250001 | NULL (10); 58750.0 (4); 78750.0 (4); 61250.0 (3); 76250.0 (3) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `child_poverty_rate` | `DOUBLE` | 0.0000 | 951 | min 0, max 0.6962025 | 0.0 (54); 0.15217391304347827 (3); 0.07142857142857142 (2); 0.1232876712328767 (2); 0.21428571428571427 (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `child_poverty_pct_rank` | `DOUBLE` | 0.0000 | 951 | min 0, max 1 | 0.0 (54); 0.48562933597621405 (3); 0.2309217046580773 (2); 0.39345887016848363 (2); 0.6778989098116948 (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `no_higher_ed_share` | `DOUBLE` | 0.0000 | 1009 | min 0, max 0.9093484 | 0.7454100367197063 (2); 0.0 (1); 0.08550790986316703 (1); 0.138840546080365 (1); 0.1404833836858006 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `households_w_children_share` | `DOUBLE` | 0.0000 | 1002 | min 0.0072464, max 0.7225025 | 0.3333333333333333 (3); 0.16993464052287582 (2); 0.18421052631578946 (2); 0.2734741784037559 (2); 0.3380952380952381 (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `hispanic_any_share` | `DOUBLE` | 0.0000 | 1009 | min 0, max 0.9942645 | 0.0 (2); 0.002607561929595828 (1); 0.006032868733097566 (1); 0.008333333333333333 (1); 0.010138248847926268 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `diversity_index` | `DOUBLE` | 0.0000 | 1010 | min 0.0114052, max 0.7644864 | 0.011405193404980363 (1); 0.02391090916467209 (1); 0.024341076784253457 (1); 0.024358933648274017 (1); 0.02904752999952387 (1) | Diversity index, calculated as 1 - sum of squares of percent of races, lower score means less diversity, higher score means more diversity. |
| `numerator` | `DOUBLE` | 0.0000 | 1009 | min 0, max 0.9659187 | 0.4839444995044599 (2); 0.0 (1); 0.0002973240832507433 (1); 0.011000991080277502 (1); 0.019920713577799804 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `denom_weight` | `DECIMAL(16,2)` | 0.0000 | 2 | min 0.8, max 1 | 1.00 (883); 0.80 (127) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `lead_score` | `DOUBLE` | 0.0000 | 1009 | min 0, max 96.5918749 | 60.493062438057486 (2); 0.0 (1); 0.03716551040634291 (1); 1.3751238850346876 (1); 10.7817623250159 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `lead_score_growth_boost` | `DOUBLE` | 0.0000 | 1010 | min -1.7612351, max 98.5918749 | -1.7612350523294884 (1); 0.3613397787261583 (1); 1.0579781962338952 (1); 1.9813852200939834 (1); 10.491730884623422 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `lead_score_rank` | `BIGINT` | 0.0000 | 1009 | min 1, max 1010 | 297 (2); 1 (1); 10 (1); 100 (1); 1000 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `lead_score_growth_boost_rank` | `BIGINT` | 0.0000 | 1010 | min 1, max 1010 | 1 (1); 10 (1); 100 (1); 1000 (1); 1001 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
## Data Quality Notes
- Columns with non-zero null rates: economically_disadvantaged_percent=12.5743%, economic_disadvantaged_pct_rank=12.5743%, population_growth_5yr=1.1881%, population_growth_pct_rank=1.1881%, pop_growth_quartile=1.1881%, median_income=0.9901%
- Key uniqueness check for recommended PK (`district_name`) found 11 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_tx_school_district.sql:5:create or replace table metro_deep_dive.gold.tx_isd_metrics as `
   - `scripts/etl/gold/gold_tx_school_district.sql:180:from metro_deep_dive.gold.tx_isd_metrics `

## Known Gaps / To-Dos
- Add business definitions for high-priority consumption columns.
- Add automated DQ thresholds for row-count drift and key integrity.
- Add explicit source provenance fields in Gold tables where needed.
