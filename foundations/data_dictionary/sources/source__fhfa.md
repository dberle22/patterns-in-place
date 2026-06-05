# Source Spec: FHFA (House Price Index)

## 1. Overview

- Source: Federal Housing Finance Agency (FHFA)
- Program: House Price Index (HPI)
- Access pattern: public annual-workbook bulk downloads — no API, no key required
- Primary dependency: public FHFA data portal files plus local raw-data and DuckDB paths
- Scope in Foundations: FHFA HPI will provide the primary home-price-appreciation signal for the platform. Current staging coverage includes U.S., state, CBSA, county, ZIP5, and tract annual developmental index files so we can choose the right downstream Silver subset deliberately. FHFA is the standard repeat-sales methodology reference and is more methodologically consistent across markets than Zillow's hedonic approach.
- Documentation goal: this file is the provider-level spec for FHFA as it will be represented in Foundations.

---

## 2. Coverage Matrix

| Topic group | Staging family contracts | Silver outputs |
| --- | --- | --- |
| HPI — U.S. | [../layers/staging/staging__fhfa_hpi.md](../layers/staging/staging__fhfa_hpi.md) | [../layers/silver/silver__fhfa_hpi.md](../layers/silver/silver__fhfa_hpi.md) |
| HPI — State | [../layers/staging/staging__fhfa_hpi.md](../layers/staging/staging__fhfa_hpi.md) | [../layers/silver/silver__fhfa_hpi.md](../layers/silver/silver__fhfa_hpi.md) |
| HPI — CBSA | [../layers/staging/staging__fhfa_hpi.md](../layers/staging/staging__fhfa_hpi.md) | [../layers/silver/silver__fhfa_hpi.md](../layers/silver/silver__fhfa_hpi.md) |
| HPI — County | [../layers/staging/staging__fhfa_hpi.md](../layers/staging/staging__fhfa_hpi.md) | [../layers/silver/silver__fhfa_hpi.md](../layers/silver/silver__fhfa_hpi.md) |
| HPI — ZIP5 | [../layers/staging/staging__fhfa_hpi.md](../layers/staging/staging__fhfa_hpi.md) | [../layers/silver/silver__fhfa_hpi.md](../layers/silver/silver__fhfa_hpi.md) |
| HPI — Tract | [../layers/staging/staging__fhfa_hpi.md](../layers/staging/staging__fhfa_hpi.md) | staged only for now |

These staged geography slices now feed a single unified Silver table at the `geo_level + geo_id + year` grain for the approved first-pass geography set.

---

## 3. Source Contract

- Provider: Federal Housing Finance Agency
- Data portal: `https://www.fhfa.gov/data/hpi/datasets`
- Retrieval interface: direct flat-file downloads, no authentication required
- Common request pattern: one annual source file per geography is downloaded and cached locally before being parsed into staging tables
- Common geography pattern:
  - annual national workbook — developmental annual HPI for the United States
  - annual state workbook — developmental annual HPI for states
  - annual CBSA workbook — developmental annual HPI for CBSA and non-CBSA residual rows, identified by FHFA code (`place_id`) and name (`place_name`)
  - annual county workbook — developmental annual HPI for counties, identified by 5-digit county FIPS (`place_id`) and county name (`place_name`)
  - annual ZIP5 workbook — developmental annual HPI for five-digit ZIP codes
  - annual tract CSV — developmental annual HPI for census tracts
- Common time pattern: annual observations; Silver standardizes the staged annual rows directly rather than averaging quarterly observations

**Index choice rationale:**
Use the FHFA annual developmental index files directly because they already publish annual appreciation metrics at the exact geographies we want to evaluate for staging. This avoids rebuilding annual metrics from quarterly files and keeps Track 3 aligned with FHFA's annual-data landing page.

**CBSA code alignment:**
FHFA uses OMB CBSA codes as `place_id`. These should align to `silver.xwalk_cbsa_county.cbsa_code` and `geo.cbsas.cbsa_code`, but the match must be verified during staging — FHFA may lag behind the most recent OMB delineation update.

**File structure (shared annual pattern):**

| Column | Description |
| --- | --- |
| `hpi_flavor` | Index flavor label (currently `all-transactions`) |
| `frequency` | Temporal frequency (`annual`) |
| `level` | Geography type label |
| `place_name` | Geography display name |
| `place_id` | FHFA code or county FIPS |
| `yr` | Calendar year of observation |
| `annual_change_pct` | Published FHFA annual appreciation rate |
| `hpi` | Published annual HPI level |
| `hpi_1990_base` | HPI rebased so 1990 = 100 |
| `hpi_2000_base` | HPI rebased so 2000 = 100 |

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- [../../etl/staging/get_fhfa.R](../../etl/staging/get_fhfa.R)

| Topic group | Source files | Staging ingest entrypoint |
| --- | --- | --- |
| HPI — U.S. | annual national workbook | [../../etl/staging/get_fhfa.R](../../etl/staging/get_fhfa.R) |
| HPI — State | annual state workbook | [../../etl/staging/get_fhfa.R](../../etl/staging/get_fhfa.R) |
| HPI — CBSA | annual CBSA workbook | [../../etl/staging/get_fhfa.R](../../etl/staging/get_fhfa.R) |
| HPI — County | annual county workbook | [../../etl/staging/get_fhfa.R](../../etl/staging/get_fhfa.R) |
| HPI — ZIP5 | annual ZIP5 workbook | [../../etl/staging/get_fhfa.R](../../etl/staging/get_fhfa.R) |
| HPI — Tract | annual tract CSV | [../../etl/staging/get_fhfa.R](../../etl/staging/get_fhfa.R) |

---

## 4. Staging Shape

Common FHFA staging pattern:
- one staging table per geography level (`staging.fhfa_hpi_us`, `staging.fhfa_hpi_state`, `staging.fhfa_hpi_cbsa`, `staging.fhfa_hpi_county`, `staging.fhfa_hpi_zip5`, `staging.fhfa_hpi_tract`)
- source is already annual-format; no quarterly rollup or pivot required
- each row carries `yr`, `place_id`, `place_name`, `annual_change_pct`, and published HPI base variants

**`staging.fhfa_hpi_us`**

| Column | Type | Description |
| --- | --- | --- |
| `hpi_flavor` | VARCHAR | Index flavor label (`all-transactions`) |
| `frequency` | VARCHAR | Always `annual` |
| `level` | VARCHAR | Geography type label |
| `place_name` | VARCHAR | Always `United States` |
| `place_id` | VARCHAR | Fixed national key (`US`) |
| `yr` | INTEGER | Calendar year |
| `annual_change_pct` | DOUBLE | Published annual appreciation rate |
| `hpi` | DOUBLE | Annual HPI level |
| `hpi_1990_base` | DOUBLE | HPI rebased to 1990 = 100 |
| `hpi_2000_base` | DOUBLE | HPI rebased to 2000 = 100 |

**`staging.fhfa_hpi_state`**

| Column | Type | Description |
| --- | --- | --- |
| `hpi_flavor` | VARCHAR | Index flavor label (`all-transactions`) |
| `frequency` | VARCHAR | Always `annual` |
| `level` | VARCHAR | Geography type label |
| `state_name` | VARCHAR | State name from source workbook |
| `state_abbr` | VARCHAR | Two-letter state abbreviation |
| `state_fips` | VARCHAR | Two-digit state FIPS |
| `place_name` | VARCHAR | State display name |
| `place_id` | VARCHAR | Two-digit state FIPS |
| `yr` | INTEGER | Calendar year |
| `annual_change_pct` | DOUBLE | Published annual appreciation rate |
| `hpi` | DOUBLE | Annual HPI level |
| `hpi_1990_base` | DOUBLE | HPI rebased to 1990 = 100 |
| `hpi_2000_base` | DOUBLE | HPI rebased to 2000 = 100 |

**`staging.fhfa_hpi_cbsa`**

| Column | Type | Description |
| --- | --- | --- |
| `hpi_flavor` | VARCHAR | Index flavor label (`all-transactions`) |
| `frequency` | VARCHAR | Always `annual` |
| `level` | VARCHAR | Geography type label |
| `place_name` | VARCHAR | CBSA display name |
| `place_id` | VARCHAR | FHFA CBSA code |
| `yr` | INTEGER | Calendar year |
| `annual_change_pct` | DOUBLE | Published annual appreciation rate |
| `hpi` | DOUBLE | Annual HPI level |
| `hpi_1990_base` | DOUBLE | HPI rebased to 1990 = 100 |
| `hpi_2000_base` | DOUBLE | HPI rebased to 2000 = 100 |

**`staging.fhfa_hpi_county`**

| Column | Type | Description |
| --- | --- | --- |
| `hpi_flavor` | VARCHAR | Index flavor label (`all-transactions`) |
| `frequency` | VARCHAR | Always `annual` |
| `level` | VARCHAR | Geography type label |
| `state_abbr` | VARCHAR | Two-letter state abbreviation from the source workbook |
| `place_name` | VARCHAR | County display name |
| `place_id` | VARCHAR | 5-digit county FIPS |
| `yr` | INTEGER | Calendar year |
| `annual_change_pct` | DOUBLE | Published annual appreciation rate |
| `hpi` | DOUBLE | Annual HPI level |
| `hpi_1990_base` | DOUBLE | HPI rebased to 1990 = 100 |
| `hpi_2000_base` | DOUBLE | HPI rebased to 2000 = 100 |

**`staging.fhfa_hpi_zip5`**

| Column | Type | Description |
| --- | --- | --- |
| `hpi_flavor` | VARCHAR | Index flavor label (`all-transactions`) |
| `frequency` | VARCHAR | Always `annual` |
| `level` | VARCHAR | Geography type label |
| `place_name` | VARCHAR | ZIP code display label, currently the ZIP itself |
| `place_id` | VARCHAR | 5-digit ZIP code |
| `yr` | INTEGER | Calendar year |
| `annual_change_pct` | DOUBLE | Published annual appreciation rate |
| `hpi` | DOUBLE | Annual HPI level |
| `hpi_1990_base` | DOUBLE | HPI rebased to 1990 = 100 |
| `hpi_2000_base` | DOUBLE | HPI rebased to 2000 = 100 |

**`staging.fhfa_hpi_tract`**

| Column | Type | Description |
| --- | --- | --- |
| `hpi_flavor` | VARCHAR | Index flavor label (`all-transactions`) |
| `frequency` | VARCHAR | Always `annual` |
| `level` | VARCHAR | Geography type label |
| `state_abbr` | VARCHAR | Two-letter state abbreviation from source file |
| `place_name` | VARCHAR | Census tract GEOID display label, currently the tract GEOID itself |
| `place_id` | VARCHAR | 11-digit census tract GEOID |
| `yr` | INTEGER | Calendar year |
| `annual_change_pct` | DOUBLE | Published annual appreciation rate |
| `hpi` | DOUBLE | Annual HPI level |
| `hpi_1990_base` | DOUBLE | HPI rebased to 1990 = 100 |
| `hpi_2000_base` | DOUBLE | HPI rebased to 2000 = 100 |

---

## 5. Staging To Silver

FHFA handoff pattern:
1. Download and cache one annual source file per selected geography.
2. Parse the published annual rows directly into staging tables.
3. Decide which staged geographies should flow into the first-pass unified Silver table.
4. Compute YoY, 5-year, and 10-year appreciation in Silver from the staged annual HPI level.
5. Use the direct published geography files rather than deriving these rows from other FHFA slices.

| Topic group | Silver handoff | Special path |
| --- | --- | --- |
| HPI — U.S. | modeled into `silver.fhfa_hpi` at `us` geo_level | direct from staging with fixed national key |
| HPI — State | modeled into `silver.fhfa_hpi` at `state` geo_level | direct from staging; `place_id` is two-digit state FIPS |
| HPI — CBSA | modeled into `silver.fhfa_hpi` at `cbsa` geo_level | direct from staging; join `place_id` → `cbsa_code` for canonical naming and exclude non-CBSA residual rows from the first-pass Silver contract |
| HPI — County | modeled into `silver.fhfa_hpi` at `county` geo_level | direct from staging; `place_id` is already a 5-digit FIPS |
| HPI — ZIP5 | modeled into `silver.fhfa_hpi` at `zcta` proxy grain | direct from staging because the current Foundations decision allows ZIP5 to proxy for ZCTA |
| HPI — Tract | staged only for now | retained in staging for future expansion; not included in the first-pass Silver contract |

---

## 6. Transformation Notes

### Silver annual metrics

The annual workbooks already publish one HPI level per geography-year. Silver should take the staged `hpi` column as `hpi_level` and compute longer-horizon appreciation rates from those annual levels.

| Metric | Derivation |
| --- | --- |
| `hpi_level` | Published annual `hpi` value from the FHFA workbook; Silver does not use the rebased `1990` or `2000` helper columns as its canonical level |
| `hpi_yoy_pct` | `(hpi_level - lag1_hpi) / lag1_hpi` |
| `hpi_5yr_pct` | `(hpi_level - lag5_hpi) / lag5_hpi` |
| `hpi_10yr_pct` | `(hpi_level - lag10_hpi) / lag10_hpi` |

### CBSA code join

FHFA `place_id` should match `cbsa_code` in `silver.xwalk_cbsa_county`. Join quality must be verified on first ingest — the FHFA CBSA list may include delineations from older OMB vintages that do not appear in the current crosswalk, or may be missing metros added in recent OMB updates.

### County experimental coverage

The annual county file is marked experimental by FHFA. Counties with thin transaction volumes can still show null or unstable values. Silver should retain all county rows but flag thin-coverage or unstable counties in the data quality notes rather than dropping them.

---

## 7. Data Quality Expectations

| Check | What to verify |
| --- | --- |
| CBSA code join rate | Fraction of FHFA `place_id` values that match `silver.xwalk_cbsa_county.cbsa_code`; any unmatched CBSAs should be logged |
| U.S. key consistency | Verify the national staging slice always uses `place_id = 'US'` |
| State FIPS completeness | Verify `place_id` is a 2-digit FIPS for all state rows |
| County FIPS completeness | Verify `place_id` is a 5-digit FIPS for all county rows |
| ZIP5 completeness | Verify `place_id` is a 5-digit ZIP for all ZIP5 rows |
| Tract GEOID completeness | Verify `place_id` is an 11-digit tract GEOID for all tract rows |
| Annual continuity | Confirm that staged series have expected annual continuity across long time ranges for each included geography |
| Appreciation direction | Spot-check YoY appreciation against known market trends for major metros |
| Null rate by geo level | Document the share of county rows with null `hpi_level` due to thin transaction volume |

---

## 8. Gold Placement

FHFA HPI lands in `gold.housing_market_wide` alongside the existing Zillow ZHVI and ZORI series. This is the market-pricing Gold table — it is intentionally separate from `gold.housing_core_wide` (structural supply, regulatory rents) and `gold.affordability_wide` (affordability burden ratios).

**Gold enrichment columns in `gold.housing_market_wide`:**

| Column | Description |
| --- | --- |
| `hpi_level` | FHFA annual HPI index level |
| `hpi_yoy_pct` | Year-over-year HPI appreciation |
| `hpi_5yr_pct` | 5-year cumulative HPI appreciation |
| `hpi_10yr_pct` | 10-year cumulative HPI appreciation |

The existing Zillow columns remain unchanged. FHFA now enriches CBSA, county, and ZCTA rows wherever the Zillow market surface already includes the same geography-year.

---

## 9. Operational Notes

- Staging entrypoint: [../../etl/staging/get_fhfa.R](../../etl/staging/get_fhfa.R)
- Required local environment wiring: `DATA` for cached FHFA workbooks and `DB_PATH` for DuckDB materialization
- Annual workbook URLs should be verified against `https://www.fhfa.gov/data/hpi/datasets?tab=annual-data` before each pipeline run — FHFA does not version URLs but has occasionally changed file names between releases

---

## 10. Related Sources

**FHFA Underserved Areas** is a separate FHFA data product published under the Housing Goals program (`https://www.fhfa.gov/data/underserved-areas`). It designates census tracts as "underserved" based on low income, minority populations, and disaster-area status — completely independent of the HPI price-index program documented in this spec. Although it comes from the same agency, it has a different schema, different cadence, and a different Gold destination (`gold.dim_policy_designations`). Staging, Silver, and source spec for FHFA Underserved Areas live in Track 5 alongside Opportunity Zones. See `source__opportunity_zones.md` for that source spec.

---

## 11. Architecture Decisions

**Decision date:** 2026-06-04

### Index choice
Use the annual developmental HPI files directly at each geography we want to stage. They already provide annual geography-level HPI and appreciation values at the exact grains needed for Track 3 staging.

### Silver contract
A single unified `silver.fhfa_hpi` table at annual grain remains the target, one row per `geo_level + geo_id + year`. The first-pass Silver contract now includes `us`, `state`, `cbsa`, `county`, and ZIP5-as-`zcta` rows. Tract remains staged-only for now so we can add it later without re-ingesting FHFA.

### Gold placement
FHFA HPI extends `gold.housing_market_wide` with four new appreciation columns (`hpi_level`, `hpi_yoy_pct`, `hpi_5yr_pct`, `hpi_10yr_pct`). This table was intentionally designed at Zillow Gold time to accept FHFA as its next source addition.

### ZCTA exclusion
FHFA does publish annual ZIP-level HPI, and the current staging scope now includes ZIP5. Because the approved Silver scope treats ZIP5 as a ZCTA proxy, FHFA can now enrich the ZCTA rows in `gold.housing_market_wide` wherever the Zillow market surface already includes the same geography-year.

### ZIP to ZCTA proxy decision
If FHFA ZIP-level HPI is added later, use the FHFA five-digit ZIP annual file and treat ZIP codes as an acceptable proxy for ZCTAs in Foundations rather than building a separate USPS-to-ZCTA reconciliation layer for the first pass. This is a pragmatic modeling choice rather than a claim of exact geographic equivalence.
