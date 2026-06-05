# Data Dictionary: silver.opportunity_zones

## Overview
- **Table**: `silver.opportunity_zones`
- **Purpose**: Standardized Opportunity Zone designation surface with full tract coverage plus county and CBSA rollups.
- **KPI applicability**: tract-level designation joins and higher-level share-of-tracts summaries for investor-lens analysis.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id`.
- **Primary key candidate**: (`geo_level`, `geo_id`)
- **Observed geo coverage**: `tract`, `county`, `cbsa`

## Columns

| Column | Type | Definition |
| --- | --- | --- |
| `geo_level` | `VARCHAR` | Geographic level for the row (`tract`, `county`, or `cbsa`). |
| `geo_id` | `VARCHAR` | Geographic identifier for the row. Tract rows use 11-digit tract GEOIDs, county rows use 5-digit county FIPS, and CBSA rows use 5-digit CBSA codes. |
| `geo_name` | `VARCHAR` | Geographic display name for the row. |
| `is_opportunity_zone` | `BOOLEAN` | Binary Opportunity Zone designation flag for tract rows. Null for county and CBSA rollup rows. |
| `oz_tract_count` | `INTEGER` | Number of designated Opportunity Zone tracts in the geography. For tract rows, this is `1` when the tract is designated and `0` otherwise. |
| `total_tract_count` | `INTEGER` | Number of tracts represented by the geography row. Tract rows always equal `1`. |
| `pct_oz_tracts` | `DOUBLE` | Share of tracts in the geography that are designated Opportunity Zones. |

## Data Quality Notes
- Silver uses `silver.xwalk_tract_county` as the tract backbone, so non-designated tracts are represented explicitly with `FALSE` rather than being absent.
- County and CBSA rollups inherit the current tract crosswalk coverage, which means a small number of source designations can remain unmatched when the source tract vintage differs from the current backbone.
- County rollups include every tract in the tract backbone. CBSA rollups include only tracts whose counties map to a CBSA in `silver.xwalk_cbsa_county`.

## Lineage
1. `foundations/etl/staging/get_opportunity_zones.R` downloads the official CDFI Fund designated tract list and writes `staging.opportunity_zones`.
2. `foundations/etl/silver/opportunity_zones_silver.R` applies the designation flag to the tract backbone, derives county and CBSA counts and shares, and writes `silver.opportunity_zones`.

## Known Gaps / To-Dos
- Opportunity Zone designations are static in the current contract, so this table does not include a `year` column.
- Puerto Rico and other tract-vintage edge cases are not forced into the current tract backbone; they should be tracked as join exceptions in run QA.
