# Data Dictionary: gold.dim_policy_designations

## Overview
- **Table**: `gold.dim_policy_designations`
- **Purpose**: Canonical Gold dimension for tract-oriented policy designation flags used in investor-lens analytics.
- **KPI applicability**: static Opportunity Zone joins plus annual FHFA underserved joins across the geography levels each contributing Silver table publishes.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
- **Current scope**: static Opportunity Zone rows at `tract`, `county`, and `cbsa`; annual FHFA underserved rows at the geography levels published by `silver.fhfa_underserved`
- **Shape note**: static Opportunity Zone rows intentionally carry `year = NULL`; annual FHFA underserved rows carry the FHFA release year.

## Columns

| Column | Type | Definition |
| --- | --- | --- |
| `geo_level` | `VARCHAR` | Geographic level for the row. Opportunity Zone rows now include tract, county, and CBSA overlays. |
| `geo_id` | `VARCHAR` | Geographic identifier for the row. |
| `geo_name` | `VARCHAR` | Geographic display name for the row. |
| `year` | `INTEGER` | FHFA underserved release year for annual rows. Null for the static Opportunity Zone rows. |
| `is_opportunity_zone` | `BOOLEAN` | Opportunity Zone designation flag for tract rows. Null for FHFA rows and OZ rollup rows. |
| `oz_tract_count` | `INTEGER` | Opportunity Zone tract count on static OZ rows. Tract rows are `1` when designated and `0` otherwise; county and CBSA rows carry the aggregated designated-tract count. |
| `total_tract_count` | `INTEGER` | Number of tracts represented by the row in the contributing Silver source. Tract rows equal `1`; county and CBSA rows carry aggregated tract counts. |
| `pct_oz_tracts` | `DOUBLE` | Share of designated tracts on static OZ rows. |
| `oz_population` | `DOUBLE` | Population living in designated Opportunity Zone tracts on static OZ rows, using the latest tract `silver.age_kpi.pop_total` snapshot as the denominator backbone. Null for FHFA rows. |
| `total_population` | `DOUBLE` | Total tract population represented by the static OZ row, using the latest tract `silver.age_kpi.pop_total` snapshot. Null for FHFA rows. |
| `pct_population_in_oz` | `DOUBLE` | Share of the geography's tract population living in designated Opportunity Zone tracts. Null for FHFA rows. |
| `is_underserved` | `BOOLEAN` | Combined FHFA underserved designation flag for tract rows in the annual FHFA slice. |
| `is_low_income_area` | `BOOLEAN` | FHFA low-income-area designation flag for tract rows in the annual FHFA slice. |
| `is_minority_area` | `BOOLEAN` | FHFA minority-tract designation flag for tract rows in the annual FHFA slice. |
| `is_disaster_area` | `BOOLEAN` | FHFA designated-disaster-area flag for tract rows in the annual FHFA slice. |
| `underserved_tract_count` | `INTEGER` | FHFA underserved tract count on annual FHFA rows. Current tract-only scope is `1` when designated and `0` otherwise. |
| `pct_underserved_tracts` | `DOUBLE` | Share of underserved tracts on annual FHFA rows. Current tract-only scope is `1` when designated and `0` otherwise. |

## Data Quality Notes
- This Gold table is an extension-point dimension, not a replacement for `gold.dim_geo` and not a housing fact mart.
- Opportunity Zone rows are static and intentionally separated from the annual FHFA rows by leaving `year` null.
- Opportunity Zone population metrics use the latest tract `silver.age_kpi.pop_total` snapshot available at ETL runtime.
- `total_tract_count` is carried from the contributing Silver source so tract-share designation metrics remain interpretable on rollup rows.

## Lineage
1. `silver.opportunity_zones` supplies the static Opportunity Zone slice.
2. `silver.fhfa_underserved` supplies the current-year FHFA underserved slice.
3. `foundations/etl/gold/gold_policy_designations.sql` unions the two slices into `gold.dim_policy_designations`.
