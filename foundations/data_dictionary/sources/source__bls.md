# Source Spec: BLS

## 1. Overview

- Source: U.S. Bureau of Labor Statistics
- Current Foundations coverage: `LAUS` and `QCEW`
- Primary dependency: public BLS downloadable files plus local raw-data and DuckDB paths
- Documentation goal: this file is the provider-level spec for how Foundations ingests, stages, and models BLS labor-market datasets today

## 2. Coverage Matrix

| Topic group | Staging family contracts | Silver outputs | Gold outputs |
| --- | --- | --- | --- |
| LAUS | [../layers/staging/staging__bls_laus.md](../layers/staging/staging__bls_laus.md) | `silver.bls_laus_wide` | `gold.economics_labor_wide` |
| QCEW | [../layers/staging/staging__bls_qcew.md](../layers/staging/staging__bls_qcew.md) | `silver.bls_qcew` | `gold.economics_industry_wide` |

## 3. Source Contract

- Provider: U.S. Bureau of Labor Statistics
- Common local environment wiring:
  - `DATA` for cached raw files
  - `DB_PATH` for DuckDB materialization
- Common ingest pattern: download year-specific BLS artifacts to the raw cache, then normalize them into staging tables

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- [../../etl/staging/get_bls_laus.R](../../etl/staging/get_bls_laus.R)
- [../../etl/staging/get_bls_qcew.R](../../etl/staging/get_bls_qcew.R)

| Topic group | Retrieval interface | Source files / subject area | Staging ingest entrypoint |
| --- | --- | --- | --- |
| LAUS | direct file download | county-level labor force, employment, unemployment, and unemployment rate workbooks | [../../etl/staging/get_bls_laus.R](../../etl/staging/get_bls_laus.R) |
| QCEW | direct file download | annual NAICS-based QCEW `annual_singlefile` ZIP files, with titles backfilled from reference metadata and small code lookups | [../../etl/staging/get_bls_qcew.R](../../etl/staging/get_bls_qcew.R) |

## 4. Staging Shape

### LAUS

- One county landing table
- One normalized row per county-year observation

### QCEW

- Two geography-replica landing tables:
  - `staging.bls_qcew_county`
  - `staging.bls_qcew_state`
- One normalized row per `geo_id + period + own_code + industry_code + agglvl_code + size_code + qtr`
- Current staging strategy is intentionally source-faithful for annual state and county rows:
  - keep all published industry members from the annual singlefile
  - keep all published ownership and size slices present in the annual files
  - keep `lq_*` and `oty_*` fields for later analytical use
  - keep raw county rows such as `999` unknown county codes in staging, even if they do not roll cleanly into downstream geography products

| Topic group | Staging family | Coverage shape |
| --- | --- | --- |
| LAUS | `staging__bls_laus` | county-only landing table materialized as `staging.bls_laus_county` |
| QCEW | `staging__bls_qcew` | state and county annual landing tables materialized as `staging.bls_qcew_state` and `staging.bls_qcew_county` |

## 5. Staging To Silver

### LAUS handoff
1. Read the county staging table.
2. Normalize county rows into the shared Silver geography contract.
3. Join crosswalks to add CBSA and state rollups.
4. Aggregate labor-force counts upward for CBSA and state.
5. Recompute unemployment rate after aggregation.

### QCEW handoff
1. Read the county staging table as the canonical fine-grain geography feed.
2. Materialize the governed QCEW industry mapping as `silver.bls_qcew_industry_map`.
3. Join that map to distinguish plain NAICS codes from BLS aggregate supersectors and choose the canonical analytical subset for the long Silver table.
4. Roll county rows up to CBSA using `silver.xwalk_cbsa_county`.
5. Roll county rows up to state using `silver.xwalk_county_state` when state totals need to be recomputed from county inputs for consistency.

| Topic group | Silver handoff | Special path |
| --- | --- | --- |
| LAUS | `staging__bls_laus` -> `silver.bls_laus_wide` | CBSA and state rows are derived from county rows using `silver.xwalk_cbsa_county` and `silver.xwalk_county_state` |
| QCEW | `staging__bls_qcew` -> `silver.bls_qcew` | CBSA rows are intentionally derived from counties rather than relying on published metro QCEW extracts |

## 6. Transformation Notes

| Topic group | Silver-table role | Derivation logic |
| --- | --- | --- |
| LAUS | standardized geography-year labor-market table | county rows pass through directly; CBSA and state rows sum `labor_force`, `employed`, and `unemployed`, then recompute `unemployment_rate_percent` as `unemployed / labor_force * 100` |
| QCEW | curated geography-year-industry wages and employment table | county rows are the base grain; `silver.bls_qcew` keeps the `10` total-covered headline row plus private-sector canonical industries, then adds `92 Public administration` back in from the government sector slices before rolling the curated subset to CBSA and state |

Additional QCEW transform notes:
- The annual singlefile preserves the full annual metric payload in one CSV per year, which is materially faster to ingest than iterating through thousands of per-industry members.
- Because singlefile excludes the human-readable title columns, the staging script backfills `industry_title`, `own_title`, `agglvl_title`, `size_title`, and geography titles from the QCEW mapping asset plus small lookup tables.
- The managed Silver mapping table is `silver.bls_qcew_industry_map`, materialized from the maintained CSV seed.
- The industry mapping seed lives at [../../etl/reference/bls_qcew_industry_map.csv](../../etl/reference/bls_qcew_industry_map.csv).
- The mapping is currently generated across the full `2010–2024` annual archive range by [../../etl/reference/build_bls_qcew_industry_map.R](../../etl/reference/build_bls_qcew_industry_map.R).

## 6b. Silver To Gold

### QCEW Gold handoff
1. Read `silver.bls_qcew` as the curated annual QCEW long table.
2. Align QCEW industries to the broader Gold industry families already used by ACS and BEA.
3. Keep `10` total-covered headline metrics as the all-ownership QCEW summary.
4. Keep private-sector industry detail for the canonical broad industry families.
5. Keep `92 Public administration` as a government-sector exception in the Gold mart.
6. Left join the aggregated QCEW family metrics into `gold.economics_industry_wide`.

Gold placement note:
- QCEW lands in `gold.economics_industry_wide`, not `gold.economics_labor_wide`, because the source is primarily an industry-structure and wage dataset rather than a labor-force and unemployment dataset.
- That Gold mart is intentionally narrowed to `county`, `cbsa`, and `state` so the output stays focused on the geography levels where ACS, QCEW, and BEA can be interpreted together.

## 7. Data Quality Expectations

| Topic group | Non-boilerplate checks worth preserving |
| --- | --- |
| LAUS | verify uniqueness at `geo_level + geo_id + period`; watch the small null population already present in the Silver contract; confirm aggregated CBSA and state unemployment rates are recomputed from summed counts rather than averaged from percentages |
| QCEW | verify uniqueness at `geo_level + geo_id + period + own_code + industry_code + agglvl_code + size_code + qtr`; confirm the staged industry-code universe matches the published ZIP member inventory; confirm both state and county rows are retained; watch row growth closely before expanding the year range |

## 8. Operational Notes

- Staging entrypoints:
  - [../../etl/staging/get_bls_laus.R](../../etl/staging/get_bls_laus.R)
  - [../../etl/staging/get_bls_qcew.R](../../etl/staging/get_bls_qcew.R)
- Silver model entrypoints:
  - [../../etl/silver/bls_laus_silver.R](../../etl/silver/bls_laus_silver.R)
  - [../../etl/silver/bls_qcew_silver.R](../../etl/silver/bls_qcew_silver.R)
- Current documentation pattern:
  - staging remains family-contract based
  - Silver remains table-contract based
  - this file sits above both as the provider-level source spec

## 9. Current QCEW Availability Notes

As of **June 4, 2026**:
- BLS downloadable QCEW files show `2025` quarterly data as available.
- The annual QCEW download slots are still `N/A` for `2025`, because annual averages are only published once a full year is available in that annual file series.
- The latest annual file available for this ingest path is therefore `2024`.

This is why the annual QCEW staging logic currently stops at `2024` for full-history annual ingestion, even though more recent quarterly QCEW data already exist.

## 10. Known Gaps

- The current QCEW mapping asset is heuristic for BLS aggregate component lists; the high-level supersector components are strong, but we should still treat some of the broader aggregate relationships as confirmation-worthy before using them for exact decomposition logic.
- `silver.bls_qcew` is intentionally curated rather than exhaustive; if we later need a broader ownership-aware analytical view, it should be introduced as a separate Silver table instead of widening the current contract.

## 11. Source References

Official BLS references used for the current QCEW strategy:
- https://www.bls.gov/cew/downloadable-data-files.htm
- https://www.bls.gov/cew/about-data/downloadable-file-layouts/annual/naics-based-annual-layout.htm
- https://www.bls.gov/cew/classifications/industry/industry-titles.htm
- https://www.bls.gov/qcew/
