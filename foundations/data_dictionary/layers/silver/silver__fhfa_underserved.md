# Data Dictionary: silver.fhfa_underserved

## Overview
- **Table**: `silver.fhfa_underserved`
- **Purpose**: Standardized current-year FHFA underserved designation surface with tract booleans plus county and CBSA rollups.
- **KPI applicability**: tract-level designation joins and higher-level share-of-tracts summaries for investor-lens and housing-opportunity analysis.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
- **Observed geo coverage**: `tract`, `county`, `cbsa`

## Columns

| Column | Type | Definition |
| --- | --- | --- |
| `geo_level` | `VARCHAR` | Geographic level for the row (`tract`, `county`, or `cbsa`). |
| `geo_id` | `VARCHAR` | Geographic identifier for the row. Tract rows use 11-digit tract GEOIDs, county rows use 5-digit county FIPS, and CBSA rows use 5-digit CBSA codes. |
| `geo_name` | `VARCHAR` | Geographic display name for the row. |
| `year` | `INTEGER` | FHFA underserved release year represented by the row. |
| `is_underserved` | `BOOLEAN` | Combined underserved designation flag for tract rows. True when the tract qualifies as a low-income area, minority tract, or designated disaster area. Null for county and CBSA rollup rows. |
| `is_low_income_area` | `BOOLEAN` | FHFA low-income-area designation flag for tract rows. Null for county and CBSA rollup rows. |
| `is_minority_area` | `BOOLEAN` | FHFA minority-tract designation flag for tract rows. Null for county and CBSA rollup rows. |
| `is_disaster_area` | `BOOLEAN` | FHFA designated-disaster-area flag for tract rows. Null for county and CBSA rollup rows. |
| `underserved_tract_count` | `INTEGER` | Number of tracts in the geography that qualify for the combined underserved designation. For tract rows, this is `1` when the tract is underserved and `0` otherwise. |
| `total_tract_count` | `INTEGER` | Number of tracts represented by the geography row. Tract rows always equal `1`. |
| `pct_underserved_tracts` | `DOUBLE` | Share of tracts in the geography that qualify for the combined underserved designation. |

## Data Quality Notes
- Silver uses `silver.xwalk_tract_county` as the tract backbone, so non-designated tracts are represented explicitly with `FALSE` rather than being absent.
- `is_underserved` is the combined tract flag used for county and CBSA rollups. It is derived as `TRUE` when any of `is_low_income_area`, `is_minority_area`, or `is_disaster_area` is true.
- County rollups include every tract in the tract backbone. CBSA rollups include only tracts whose counties map to a CBSA in `silver.xwalk_cbsa_county`.
- FHFA’s source file can contain split-tract special cases; the first-pass contract collapses them to a single tract record so the tract backbone remains one row per tract GEOID.

## Lineage
1. `foundations/etl/staging/get_fhfa_underserved.R` resolves the latest yearly FHFA ZIP, parses the fixed-width tract file, and writes `staging.fhfa_underserved`.
2. `foundations/etl/silver/fhfa_underserved_silver.R` applies the tract flags to the tract backbone, derives county and CBSA counts and shares, and writes `silver.fhfa_underserved`.

## Known Gaps / To-Dos
- The current contract uses only the latest available yearly release. Multi-year backfill can be added later if needed.
- Puerto Rico and other source geographies outside the current tract backbone are counted as join exceptions rather than forced into the Silver surface.
