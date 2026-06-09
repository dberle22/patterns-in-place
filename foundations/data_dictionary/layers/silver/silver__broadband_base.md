# Data Dictionary: silver.broadband_base

## Overview
- **Table**: `silver.broadband_base`
- **Purpose**: Silver broadband base table (`base` type).
- **Row count**: 1,191,904
- **KPI applicability**: Base/source-aligned Silver table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + geo_name + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `geo_name`, `year`)
  - `geo_level + geo_id + geo_name + year` => rows=1191904, distinct=1191904, duplicates=0
  - `geo_level + geo_id + year` => rows=1191904, distinct=1191904, duplicates=0
  - `geo_id + year` => rows=1191904, distinct=1177273, duplicates=14631
  - `geo_level` => rows=1191904, distinct=9, duplicates=1191895
- **Time coverage**: `year` min=2017, max=2024
- **Geo coverage**: distinct_geo_levels=9; distinct_geo_id=165542

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 9 | len 2-8 | tract (641212); zcta (267572); place (249379); county (25768); cbsa (7445) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 165,542 | len 1-11 | 1 (24); 01001 (16); 01003 (16); 01005 (16); 01007 (16) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 251,047 | len 4-81 | Alexandria city, Virginia (16); Baltimore city, Maryland (16); Bristol city, Virginia (16); Buena Vista city, Virginia (16); Carson City, Nevada (16) | Geographic name (from ACS NAME) |
| `year` | `INTEGER` | 0.0000 | 8 | min 2017, max 2024 | 2024 (154726); 2023 (154720); 2022 (154598); 2021 (154311); 2020 (153657) | Observation year or period year for the row. |
| `internet_total_hhE` | `DOUBLE` | 0.0000 | 37,184 | min 0, max 129227496 | 0.0 (17432); 32.0 (992); 43.0 (945); 33.0 (943); 46.0 (943) | Total households in the broadband and internet-access universe. |
| `internet_with_subscriptionE` | `DOUBLE` | 0.0000 | 34,236 | min 0, max 117749641 | 0.0 (20242); 15.0 (1273); 16.0 (1254); 22.0 (1253); 14.0 (1239) | Households with an internet subscription of any kind. |
| `internet_dial_up_onlyE` | `DOUBLE` | 0.0000 | 2,149 | min 0, max 732848 | 0.0 (765443); 9.0 (21706); 8.0 (21685); 2.0 (20657); 7.0 (19059) | Households with dial-up internet service only. |
| `internet_broadband_anyE` | `DOUBLE` | 0.0000 | 34,248 | min 0, max 117573073 | 0.0 (20356); 15.0 (1282); 14.0 (1260); 16.0 (1260); 21.0 (1247) | Households with a broadband internet subscription of any kind. |
| `internet_cellular_data_onlyE` | `DOUBLE` | 0.0000 | 31,431 | min 0, max 110096978 | 0.0 (23773); 9.0 (1672); 8.0 (1671); 13.0 (1666); 14.0 (1655) | Households with only a cellular data plan and no other internet subscription. |
| `internet_cellular_and_otherE` | `DOUBLE` | 0.0000 | 11,735 | min 0, max 14818703 | 0.0 (64403); 9.0 (6229); 10.0 (6102); 8.0 (6079); 7.0 (6054) | Households with a cellular data plan plus one or more non-broadband internet subscriptions. |
| `internet_broadband_and_cellularE` | `DOUBLE` | 0.0000 | 31,115 | min 0, max 97727353 | 0.0 (27677); 9.0 (1881); 10.0 (1833); 12.0 (1828); 16.0 (1815) | Households with a broadband subscription and a cellular data plan. |
| `internet_broadband_no_cellularE` | `DOUBLE` | 0.0000 | 12,439 | min 0, max 30809298 | 0.0 (80782); 9.0 (7755); 8.0 (7605); 10.0 (7491); 7.0 (7325) | Households with a broadband subscription and no cellular data plan. |
| `internet_satellite_onlyE` | `DOUBLE` | 0.0000 | 9,040 | min 0, max 8561203 | 0.0 (87473); 9.0 (10342); 8.0 (10208); 7.0 (9980); 10.0 (9966) | Households with a satellite internet subscription only. |
| `internet_satellite_and_otherE` | `DOUBLE` | 0.0000 | 2,970 | min 0, max 1562113 | 0.0 (606769); 8.0 (22409); 9.0 (22017); 10.0 (20022); 7.0 (19957) | Households with satellite internet plus another non-cellular subscription type. |
| `internet_other_serviceE` | `DOUBLE` | 0.0000 | 1,438 | min 0, max 264731 | 0.0 (990077); 2.0 (11878); 3.0 (10657); 8.0 (10623); 9.0 (10362) | Households with another internet service type not captured by the named categories. |
| `internet_access_no_subscriptionE` | `DOUBLE` | 0.0000 | 6,600 | min 0, max 4343333 | 0.0 (239842); 9.0 (19431); 8.0 (19211); 10.0 (18222); 7.0 (17790) | Households with internet access but no paid internet subscription. |
| `internet_no_accessE` | `DOUBLE` | 0.0000 | 12,507 | min 0, max 20936125 | 0.0 (70110); 9.0 (7139); 10.0 (6756); 8.0 (6685); 11.0 (6615) | Households with no internet access. |
## Data Quality Notes
- No columns with non-zero null rates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `foundations/etl/silver/acs_broadband_silver.R writes silver.broadband_base from staging.acs_broadband_* with CBSA rebasing from county data via silver.xwalk_cbsa_county.`

## Known Gaps / To-Dos
- Validate and harden grain/PK contracts with automated DQ checks.
- Re-run the landed profile after major ACS topic changes and sync both this `.md` file and the companion `.yml` artifact.
