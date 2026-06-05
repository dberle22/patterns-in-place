# Data Dictionary: gold.dim_policy_designations

## Overview
- **Table**: `gold.dim_policy_designations`
- **Purpose**: Canonical Gold dimension for tract-oriented policy designation flags used in investor-lens analytics.
- **KPI applicability**: static Opportunity Zone joins plus annual FHFA underserved joins at tract grain.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
- **Current scope**: tract-only
- **Shape note**: static Opportunity Zone rows intentionally carry `year = NULL`; annual FHFA underserved rows carry the FHFA release year.

## Columns

| Column | Type | Definition |
| --- | --- | --- |
| `geo_level` | `VARCHAR` | Geographic level for the row. Current Gold scope is tract-only. |
| `geo_id` | `VARCHAR` | Geographic identifier for the row. |
| `geo_name` | `VARCHAR` | Geographic display name for the row. |
| `year` | `INTEGER` | FHFA underserved release year for annual rows. Null for the static Opportunity Zone rows. |
| `is_opportunity_zone` | `BOOLEAN` | Opportunity Zone designation flag for tract rows. Null for FHFA rows. |
| `oz_tract_count` | `INTEGER` | Opportunity Zone tract count on static OZ rows. Current tract-only scope is `1` when designated and `0` otherwise. |
| `total_tract_count` | `INTEGER` | Number of tracts represented by the row in the contributing Silver source. Current tract-only scope is always `1`. |
| `pct_oz_tracts` | `DOUBLE` | Share of designated tracts on static OZ rows. Current tract-only scope is `1` when designated and `0` otherwise. |
| `is_underserved` | `BOOLEAN` | Combined FHFA underserved designation flag for tract rows in the annual FHFA slice. |
| `is_low_income_area` | `BOOLEAN` | FHFA low-income-area designation flag for tract rows in the annual FHFA slice. |
| `is_minority_area` | `BOOLEAN` | FHFA minority-tract designation flag for tract rows in the annual FHFA slice. |
| `is_disaster_area` | `BOOLEAN` | FHFA designated-disaster-area flag for tract rows in the annual FHFA slice. |
| `underserved_tract_count` | `INTEGER` | FHFA underserved tract count on annual FHFA rows. Current tract-only scope is `1` when designated and `0` otherwise. |
| `pct_underserved_tracts` | `DOUBLE` | Share of underserved tracts on annual FHFA rows. Current tract-only scope is `1` when designated and `0` otherwise. |

## Data Quality Notes
- This Gold table is an extension-point dimension, not a replacement for `gold.dim_geo` and not a housing fact mart.
- Opportunity Zone rows are static and intentionally separated from the annual FHFA rows by leaving `year` null.
- `total_tract_count` is carried from the contributing Silver source even though current Gold scope is tract-only.

## Lineage
1. `silver.opportunity_zones` supplies the static Opportunity Zone slice.
2. `silver.fhfa_underserved` supplies the current-year FHFA underserved slice.
3. `foundations/etl/gold/gold_policy_designations.sql` unions the two slices into `gold.dim_policy_designations`.
