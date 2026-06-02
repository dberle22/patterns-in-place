# Data Dictionary: silver.income_base

## Overview
- **Table**: `silver.income_base`
- **Purpose**: Silver income table (`base` type).
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
| `median_hh_incomeE` | `DOUBLE` | 6.0525 | 122343 |  | NULL (61792); 46250.0 (2140); 48750.0 (2115); 41250.0 (2063); 51250.0 (2020) | ACS 2024 Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19013_001]: Median household income in the past 12 months (in 2024 inflation-adjusted dollars) (estimate). |
| `per_capita_incomeE` | `DOUBLE` | 2.0314 | 90038 |  | NULL (20739); 22937.0 (69); 22485.0 (68); 23844.0 (68); 24771.0 (66) | ACS 2024 Per Capita Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19301_001]: Per capita income in the past 12 months (in 2024 inflation-adjusted dollars) (estimate). |
| `pov_universeE` | `DOUBLE` | 0.0069 | 79624 | min 0, max 327079190 | 0.0 (14548); 61.0 (616); 74.0 (614); 115.0 (610); 69.0 (604) | ACS 2024 Poverty Status in the Past 12 Months by Sex by Age [B17001_001]: Total: (estimate). |
| `pov_belowE` | `DOUBLE` | 0.0069 | 29390 | min 0, max 47755606 | 0.0 (59343); 10.0 (4274); 9.0 (4232); 8.0 (4160); 6.0 (4060) | ACS 2024 Poverty Status in the Past 12 Months by Sex by Age [B17001_002]: Total:, Income in the past 12 months below poverty level: (estimate). |
| `hh_inc_totalE` | `DOUBLE` | 0.0069 | 45115 | min 0, max 129227500 | 0.0 (15641); 33.0 (1475); 32.0 (1463); 39.0 (1453); 43.0 (1445) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_001]: Total: (estimate). |
| `hh_inc_lt10kE` | `DOUBLE` | 0.0069 | 12227 | min 0, max 8421482 | 0.0 (129824); 2.0 (15910); 4.0 (14334); 3.0 (13851); 5.0 (13696) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_002]: Total:, Less than $10,000 (estimate). |
| `hh_inc_10k_15kE` | `DOUBLE` | 0.0069 | 10167 | min 0, max 6260673 | 0.0 (152138); 2.0 (16445); 4.0 (15059); 3.0 (15009); 5.0 (14898) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_003]: Total:, $10,000 to $14,999 (estimate). |
| `hh_inc_15k_20kE` | `DOUBLE` | 0.0069 | 10112 | min 0, max 6236898 | 0.0 (144422); 2.0 (16851); 4.0 (15213); 3.0 (14762); 6.0 (14749) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_004]: Total:, $15,000 to $19,999 (estimate). |
| `hh_inc_20k_25kE` | `DOUBLE` | 0.0069 | 10238 | min 0, max 6231706 | 0.0 (138080); 2.0 (16134); 4.0 (14990); 5.0 (14527); 6.0 (14323) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_005]: Total:, $20,000 to $24,999 (estimate). |
| `hh_inc_25k_30kE` | `DOUBLE` | 0.0069 | 10097 | min 0, max 6004724 | 0.0 (137919); 2.0 (16243); 4.0 (14920); 6.0 (14720); 5.0 (14687) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_006]: Total:, $25,000 to $29,999 (estimate). |
| `hh_inc_30k_35kE` | `DOUBLE` | 0.0069 | 10175 | min 0, max 6000199 | 0.0 (137019); 2.0 (16172); 4.0 (14916); 5.0 (14836); 6.0 (14735) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_007]: Total:, $30,000 to $34,999 (estimate). |
| `hh_inc_35k_40kE` | `DOUBLE` | 0.0069 | 9862 | min 0, max 5469262 | 0.0 (143405); 2.0 (16944); 4.0 (15761); 6.0 (15387); 3.0 (15303) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_008]: Total:, $35,000 to $39,999 (estimate). |
| `hh_inc_40k_45kE` | `DOUBLE` | 0.0069 | 9801 | min 0, max 5507464 | 0.0 (143407); 2.0 (17249); 4.0 (15762); 6.0 (15503); 5.0 (15259) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_009]: Total:, $40,000 to $44,999 (estimate). |
| `hh_inc_45k_50kE` | `DOUBLE` | 0.0069 | 9467 | min 0, max 4847697 | 0.0 (153920); 2.0 (18565); 3.0 (16670); 4.0 (16349); 6.0 (16220) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_010]: Total:, $45,000 to $49,999 (estimate). |
| `hh_inc_50k_60kE` | `DOUBLE` | 0.0069 | 12766 | min 0, max 9307672 | 0.0 (96884); 6.0 (11211); 7.0 (11182); 8.0 (11124); 9.0 (11086) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_011]: Total:, $50,000 to $59,999 (estimate). |
| `hh_inc_60k_75kE` | `DOUBLE` | 0.0069 | 14373 | min 0, max 11911889 | 0.0 (84402); 8.0 (9921); 6.0 (9870); 7.0 (9800); 9.0 (9631) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_012]: Total:, $60,000 to $74,999 (estimate). |
| `hh_inc_75k_100kE` | `DOUBLE` | 0.0069 | 16055 | min 0, max 16319799 | 0.0 (78520); 8.0 (9066); 9.0 (8946); 7.0 (8786); 6.0 (8609) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_013]: Total:, $75,000 to $99,999 (estimate). |
| `hh_inc_100k_125kE` | `DOUBLE` | 0.0069 | 13732 | min 0, max 13068961 | 0.0 (117440); 2.0 (13797); 4.0 (12678); 3.0 (12376); 6.0 (12175) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_014]: Total:, $100,000 to $124,999 (estimate). |
| `hh_inc_125k_150kE` | `DOUBLE` | 0.0069 | 11335 | min 0, max 9601960 | 0.0 (185000); 2.0 (19929); 3.0 (16888); 4.0 (16138); 5.0 (15282) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_015]: Total:, $125,000 to $149,999 (estimate). |
| `hh_inc_150k_200kE` | `DOUBLE` | 0.0069 | 11822 | min 0, max 12405370 | 0.0 (215461); 2.0 (20790); 3.0 (17909); 4.0 (16023); 5.0 (15128) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_016]: Total:, $150,000 to $199,999 (estimate). |
| `hh_inc_200k_plusE` | `DOUBLE` | 0.0069 | 12999 | min 0, max 17266233 | 0.0 (264806); 2.0 (22804); 3.0 (19131); 4.0 (16565); 5.0 (15229) | ACS 2024 Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) [B19001_017]: Total:, $200,000 or more (estimate). |
| `gini_indexE` | `DOUBLE` | 2.4890 | 13071 |  | NULL (25411); 0.4121 (716); 0.4077 (714); 0.4032 (712); 0.4083 (707) | ACS 2024 Gini Index of Income Inequality [B19083_001]: Gini Index (estimate). |
## Data Quality Notes
- Columns with non-zero null rates: median_hh_incomeE=6.0525%, per_capita_incomeE=2.0314%, pov_universeE=0.0069%, pov_belowE=0.0069%, hh_inc_totalE=0.0069%, hh_inc_lt10kE=0.0069%, hh_inc_10k_15kE=0.0069%, hh_inc_15k_20kE=0.0069%, hh_inc_20k_25kE=0.0069%, hh_inc_25k_30kE=0.0069% ...
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_income_silver.R:144:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="income_base"),`

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
