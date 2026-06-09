# Data Dictionary: silver.broadband_kpi

## Overview
- **Table**: `silver.broadband_kpi`
- **Purpose**: Silver broadband KPI table (`kpi` type).
- **Row count**: 1,191,904
- **KPI applicability**: KPI table (or has KPI dictionary entries).

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
| `internet_total_hh` | `DOUBLE` | 0.0000 | 37,184 | min 0, max 129227496 | 0.0 (17432); 32.0 (992); 43.0 (945); 33.0 (943); 46.0 (943) | Total households in the broadband and internet-access universe. |
| `internet_with_subscription` | `DOUBLE` | 0.0000 | 34,236 | min 0, max 117749641 | 0.0 (20242); 15.0 (1273); 16.0 (1254); 22.0 (1253); 14.0 (1239) | Households with an internet subscription of any kind. |
| `internet_broadband_subscription` | `DOUBLE` | 0.0000 | 34,248 | min 0, max 117573073 | 0.0 (20356); 15.0 (1282); 14.0 (1260); 16.0 (1260); 21.0 (1247) | Households with a broadband internet subscription of any kind. |
| `internet_cellular_only` | `DOUBLE` | 0.0000 | 31,431 | min 0, max 110096978 | 0.0 (23773); 9.0 (1672); 8.0 (1671); 13.0 (1666); 14.0 (1655) | Households with only a cellular data plan and no other internet subscription. |
| `internet_access_no_subscription` | `DOUBLE` | 0.0000 | 6,600 | min 0, max 4343333 | 0.0 (239842); 9.0 (19431); 8.0 (19211); 10.0 (18222); 7.0 (17790) | Households with internet access but no paid internet subscription. |
| `internet_no_access` | `DOUBLE` | 0.0000 | 12,507 | min 0, max 20936125 | 0.0 (70110); 9.0 (7139); 10.0 (6756); 8.0 (6685); 11.0 (6615) | Households with no internet access. |
| `internet_with_any_access` | `DOUBLE` | 0.0000 | 34,926 | min 0, max 120820229 | 0.0 (19667); 15.0 (1201); 13.0 (1195); 24.0 (1192); 16.0 (1190) | Households with any form of internet access, whether subscribed or not. |
| `pct_internet_subscription` | `DOUBLE` | 1.4625 | 518,999 | min 0, max 1 | 1.0 (34632); NULL (17432); 0.0 (2810); 0.75 (1492); 0.6666666666666666 (1475) | Share of households with an internet subscription of any kind. |
| `pct_broadband_subscription` | `DOUBLE` | 1.4625 | 522,221 | min 0, max 1 | 1.0 (33204); NULL (17432); 0.0 (2924); 0.6666666666666666 (1502); 0.75 (1464) | Share of households with a broadband internet subscription. |
| `pct_cellular_only` | `DOUBLE` | 1.4625 | 602,702 | min 0, max 1 | NULL (17432); 1.0 (13678); 0.0 (6341); 0.5 (2181); 0.6666666666666666 (1756) | Share of households that rely on only a cellular data plan. |
| `pct_access_no_subscription` | `DOUBLE` | 1.4625 | 291,578 | min 0, max 1 | 0.0 (222410); NULL (17432); 0.029411764705882353 (610); 0.038461538461538464 (607); 0.03333333333333333 (580) | Share of households with internet access but no subscription. |
| `pct_no_internet_access` | `DOUBLE` | 1.4625 | 491,091 | min 0, max 1 | 0.0 (52678); NULL (17432); 1.0 (2235); 0.2 (1393); 0.25 (1354) | Share of households with no internet access. |
| `pct_any_internet_access` | `DOUBLE` | 1.4625 | 491,091 | min 0, max 1 | 1.0 (52678); NULL (17432); 0.0 (2235); 0.8 (1393); 0.75 (1354) | Share of households with any form of internet access. |
## Data Quality Notes
- Columns with non-zero null rates: pct_internet_subscription=1.4625%, pct_broadband_subscription=1.4625%, pct_cellular_only=1.4625%, pct_access_no_subscription=1.4625%, pct_no_internet_access=1.4625%, pct_any_internet_access=1.4625%
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `foundations/etl/silver/acs_broadband_silver.R writes silver.broadband_kpi from staging.acs_broadband_* with CBSA rebasing from county data via silver.xwalk_cbsa_county.`

## Known Gaps / To-Dos
- Validate and harden grain/PK contracts with automated DQ checks.
- Re-run the landed profile after major ACS topic changes and sync both this `.md` file and the companion `.yml` artifact.
