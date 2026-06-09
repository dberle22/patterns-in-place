# Core Data Platform Completion Plan

This plan covers everything needed to bring the `patterns_in_place` data platform to a fully complete state. It picks up after ETL Migration Phases 1 and 2 are done (staging seeded, silver/gold built against `patterns_in_place.duckdb`).

Scope:
- Close all gaps in currently ingested/partial sources
- Resolve shared-field definition gaps in the data dictionary
- Ingest all high-and-medium-priority planned sources (FHFA, CHR, OZ, EPA EJScreen/AQI, EPA Smart Location Database, FEMA NRI, IPEDS, ACS expansions, CBP/BFS, HMDA, JEC Social Capital)
- Full Silver/Gold coverage and data dictionary entries for every source
- Foundation for the Points/Parcels/Polygons spatial layer (national once sources + framework for per-market)

Out of scope (deferred): NOAA, Walk Score, automated DQ pipeline, product-specific sources (Google Maps, OSM, Local Tax Records graduating to Foundations). Points layer per-market and deep-dive sources (Overture POIs, OSM, transit GTFS, school attendance zones, city crime incidents) are tracked in Tracks 16–17 but depend on the Stoop migration completing first.

---

## Track 1 — Close Existing Gaps

_Track 1.1 (ETL Phase 3 ingestion audit) is complete — source documentation lives in `foundations/data_dictionary/sources/` which already covers all existing staging scripts._

### 1.2 Open Architecture Decisions
Each item needs a written decision before implementation begins.

- [x] **1.2.1** **IRS Migration Silver/Gold** — Decide canonical Silver contract: full OD flow table (`staging.irs_*` → `silver.irs_migration_flows`) vs. county summary table vs. both. Document decision in `foundations/data_dictionary/sources/IRS Migration.md` and update source spec.
- [x] **1.2.2** **Zillow Silver/Gold** — Decide: does Zillow land in `gold.housing_core_wide` alongside BPS/HUD, or a dedicated `gold.housing_market_wide`? Document decision.
- [x] **1.2.3** **HUD CHAS Silver** — Decide: model CHAS into a documented Silver table (`silver.hud_chas_*`) or keep as staging-only supporting source. Document decision.
- [x] **1.2.4** **BLS QCEW expansion** — Decide: stay LAUS-only or expand to QCEW (industry employment/wages). Document decision. Note: `get_bls_qcew.R` already exists in staging.

### 1.3 IRS Migration — Complete Silver and Gold
_Depends on decision 1.2.1_

- Completed 2026-06-03:
  rewrote `foundations/etl/silver/irs_migration_silver.R` to materialize `silver.irs_migration_flows` and `silver.irs_migration_summary`, deduped repeated staged county flows, and documented both Silver outputs.

- [x] **1.3.1** Write or update `silver/irs_migration_silver.R` to produce the agreed Silver contract (OD flows and/or county summary)
- [x] **1.3.2** Write or update Silver YAML + Markdown data dictionary: `layers/silver/silver__irs_migration_flows.yml` + `.md`
- [x] **1.3.2a** Write companion Silver YAML + Markdown data dictionary for `layers/silver/silver__irs_migration_summary.yml` + `.md`
- [x] **1.3.3** Update `gold/gold_migration_wide.sql` to incorporate IRS flows if the decision calls for Gold inclusion
- [x] **1.3.4** Update Gold data dictionary `layers/gold/gold__migration_wide.yml` + `.md` for any new columns
- [x] **1.3.5** Update `source_topic_checklist.md` IRS row from Partial → Ingested

### 1.4 Zillow — Complete Silver and Gold
_Depends on decision 1.2.2_

- Completed 2026-06-03:
  wrote `foundations/etl/silver/zillow_silver.R` to materialize monthly `silver.zillow_zhvi` and `silver.zillow_zori` for county, ZCTA, and housing-unit-weighted CBSA rows; documented both Silver outputs and intentionally left city/state staging out of the current Silver contract.
  Added `foundations/etl/gold/gold_housing_market_wide.sql` plus Gold dictionary artifacts for an annual Zillow market mart using yearly averages and December reference values.

- [x] **1.4.1** Write `silver/zillow_silver.R` producing `silver.zillow_zhvi` and `silver.zillow_zori` (long-format, CBSA/county/zip grain matching BEA pattern)
- [x] **1.4.2** Write Silver YAML + Markdown: `layers/silver/silver__zillow_zhvi.yml` + `.md`, `silver__zillow_zori.yml` + `.md`
- [x] **1.4.3** Update the appropriate Gold SQL (housing_core or new housing_market) to include ZHVI/ZORI columns
- [x] **1.4.4** Update Gold data dictionary for any new columns
- [x] **1.4.4a** After Gold is ready, review the Zillow city and state staging slices and decide whether they are clean enough to extend the Silver contract beyond county/ZCTA/CBSA
- [x] **1.4.5** Update `source_topic_checklist.md` Zillow row from Partial → Ingested

### 1.5 HUD CHAS — Silver Model
_Depends on decision 1.2.3_

- Completed 2026-06-03:
  wrote `foundations/etl/silver/hud_chas_silver.R` to materialize `silver.hud_chas_burden` for county and place geographies, then extended it with a derived CBSA rollup built from summed county CHAS household counts.
  Added Silver dictionary artifacts documenting that CHAS now lives as a segmented burden table with direct >30% and >50% burden rates rather than as a staging-only supporting source.
  Extended `foundations/etl/gold/gold_affordability_wide.sql` and its Gold dictionary artifacts so 2021 CBSA, county, and place rows now expose the approved CHAS burden metrics alongside the existing rent benchmarks.

- [x] **1.5.1** If decision = model into Silver: write `silver/hud_chas_silver.R` producing `silver.hud_chas_burden` (county/place grain, cost-burden rate and renter/owner breakdowns)
- [x] **1.5.2** Write Silver YAML + Markdown: `layers/silver/silver__hud_chas_burden.yml` + `.md`
- [x] **1.5.3** Update `gold/gold_affordability_wide.sql` to pull CHAS burden columns alongside FMR
- [x] **1.5.4** Update Gold data dictionary `layers/gold/gold__affordability_wide.yml` + `.md`
- [x] **1.5.5** Update `source_topic_checklist.md` HUD row (CHAS note from "staged only" → modeled)

### 1.6 BLS QCEW Expansion
_Depends on decision 1.2.4_

- Completed 2026-06-03:
  added the prerequisite QCEW staging work that Track 1.6 turned out to need in practice, replacing the exploratory `get_bls_qcew.R` stub with a real annual county ingest and documenting the new `staging.bls_qcew_county` family contract.
  Wrote `foundations/etl/silver/bls_qcew_silver.R` plus the initial Silver YAML/Markdown contract for `silver.bls_qcew`, using a long table at `geo_level + geo_id + period + industry_code` and deriving CBSA/state rows from county staging.

- Completed 2026-06-04:
  widened the QCEW staging strategy to keep source-faithful annual `state` and `county` rows rather than a curated county-only subset, preserving ownership, size, `lq_*`, and `oty_*` fields.
  Added a reproducible QCEW industry mapping seed at `foundations/etl/reference/bls_qcew_industry_map.csv`, generated from the published annual archive, and updated the BLS source spec to document the annual-file availability boundary that currently stops annual ingestion at `2024`.
  Switched the staging ingest to the annual QCEW singlefile download for performance, then completed the full `2010–2024` staging backfill:
  `staging.bls_qcew_county` now holds `43,342,060` rows and `staging.bls_qcew_state` holds `2,073,926` rows, with the industry mapping expanded to `2,660` published codes across the full annual range.
  Materialized `silver.bls_qcew_industry_map` as a managed Silver reference table and rebuilt `silver.bls_qcew` as a curated subset that keeps the `10` total-covered headline row plus private-sector canonical industry rows, then rolls that subset from counties to CBSA and state.
  Extended `foundations/etl/gold/gold_economy_industry.sql` so `gold.economics_industry_wide` now carries aligned QCEW total-covered, private-sector, and Public Administration metrics alongside the existing ACS and BEA industry families, and refreshed the Gold/BLS documentation to describe the live table.

- [x] **1.6.0** Write or update `staging/get_bls_qcew.R` to materialize `staging.bls_qcew_county` from annual BLS QCEW industry ZIP files
- [x] **1.6.0a** Write staging data dictionary contract: `layers/staging/staging__bls_qcew.md`
- [x] **1.6.0b** Add a reproducible QCEW industry mapping asset for downstream Silver curation
- [x] **1.6.0c** Update `sources/source__bls.md` to reflect QCEW staging, mapping, and annual-file availability
- [x] **1.6.1** If decision = expand: write `silver/bls_qcew_silver.R` (county/CBSA grain, industry employment + wages, parallel pattern to LAUS)
- [x] **1.6.2** Write Silver YAML + Markdown: `layers/silver/silver__bls_qcew.yml` + `.md`
- [x] **1.6.3** Update `gold/gold_economy_labor.sql` or `gold_economy_industry.sql` to include QCEW columns
- [x] **1.6.4** Update Gold data dictionary for new columns
- [x] **1.6.5** Update `source_topic_checklist.md` BLS row to reflect expanded coverage

---

## Track 2 — Data Dictionary Shared Field Definitions

One-time pass to resolve the ~15 shared fields that appear unresolved across 10+ Silver tables (from the definition audit: 506/1029 unresolved, concentrated in shared fields).

Completed 2026-06-02:
- Added `docs/governance/shared_field_definitions.md` for the Track 2 canonical shared-field contract.
- Verified all targeted shared fields across current Silver YAMLs and fixed the two remaining unresolved placeholders (`code` in `silver__bea_regional_marpp_long.yml`, `source` in `silver__kpi_dictionary.yml`).
- Updated `docs/governance/definition_audit.md` to show zero unresolved records for the Track 2 shared-field set.

- [x] **2.1** Write canonical definitions for the shared fields: `geo_id`, `geo_level`, `geo_name`, `period`, `table`, `line_desc_clean`, `source`, `metric_key`, `code` — document them in `foundations/data_dictionary/docs/governance/shared_field_definitions.md`
- [x] **2.2** Apply canonical `geo_id`, `geo_level`, `geo_name` definitions across all Silver YAML files where these fields currently lack a description
- [x] **2.3** Apply canonical `period` definition across all Silver YAML files
- [x] **2.4** Apply canonical `source`, `metric_key`, `code`, `table`, `line_desc_clean` definitions across all Silver YAML files
- [x] **2.5** Re-run definition audit (or manually check) and confirm unresolved count is zero for the targeted shared fields; update `docs/governance/definition_audit.md`

---

## Track 3 — New Source: FHFA (House Price Index)

**Priority: High**

- Completed 2026-06-04:
  wrote `foundations/data_dictionary/sources/source__fhfa.md` documenting the annual FHFA CBSA and county file contract, index choice rationale, staging shape, Silver annual-metric logic, CBSA code join risk, and Gold placement decision (extends `gold.housing_market_wide`).
  Recorded the follow-on ZIP geography decision as well: if FHFA ZIP-level HPI is added later, we will treat five-digit ZIPs as an acceptable proxy for ZCTAs in Foundations.

- Completed 2026-06-04:
  wrote `foundations/etl/staging/get_fhfa.R` to cache FHFA annual HPI workbooks under the raw data directory, normalize the annual CBSA and county extracts into source-faithful staging tables, and validate the staged annual key contract before writing to DuckDB.

- Completed 2026-06-04:
  expanded `foundations/etl/staging/get_fhfa.R` to also stage FHFA annual U.S., state, ZIP5, and tract files, so the staging layer now covers the broader geography set we expect to evaluate for Silver inclusion.

- Completed 2026-06-04:
  wrote `foundations/data_dictionary/layers/staging/staging__fhfa_hpi.md` and ran the FHFA staging refresh into DuckDB.
  Landed row counts:
  `staging.fhfa_hpi_us` = `51`,
  `staging.fhfa_hpi_state` = `2,601`,
  `staging.fhfa_hpi_cbsa` = `43,401`,
  `staging.fhfa_hpi_county` = `105,195`,
  `staging.fhfa_hpi_zip5` = `670,165`,
  `staging.fhfa_hpi_tract` = `2,069,265`.

- Completed 2026-06-04:
  wrote `foundations/etl/silver/fhfa_hpi_silver.R` and materialized `silver.fhfa_hpi` with first-pass geography coverage of `us`, `state`, `cbsa`, `county`, and ZIP5-as-`zcta`.
  The Silver table uses FHFA's canonical `hpi` column as `hpi_level` rather than either rebased helper series (`hpi_1990_base` or `hpi_2000_base`), excludes the non-CBSA residual rows from the CBSA annual file, and leaves tract staged-only for now.
  Landed Silver row counts:
  `us` = `51`,
  `state` = `2,601`,
  `cbsa` = `41,392`,
  `county` = `105,195`,
  `zcta` = `670,165`,
  total `silver.fhfa_hpi` rows = `819,404`.

- Completed 2026-06-04:
  wrote `foundations/data_dictionary/layers/silver/silver__fhfa_hpi.yml` and `.md` from the live landed Silver table profile.
  Updated `foundations/etl/gold/gold_housing_market_wide.sql` plus the Gold YAML / Markdown so FHFA now enriches the market mart with `hpi_level`, `hpi_yoy_pct`, `hpi_5yr_pct`, and `hpi_10yr_pct`.
  Also updated `source_topic_checklist.md`, `pipeline_manifest.yml`, and `create_DB.R` so the FHFA Silver step and the market-housing build path are now part of the documented pipeline sequence.
  Re-ran `gold.housing_market_wide` successfully after the temporary DuckDB lock cleared. The refreshed Gold mart still has `289,585` rows at the same Zillow market surface, and FHFA now fills `9,141` CBSA rows, `27,217` county rows, and `173,374` ZCTA rows through the approved ZIP5 proxy.

- [x] **3.1** Research & spec: read `notes/.../Sources/FHFA.md`, confirm current annual download URLs and workbook structure for the CBSA and county files, document in `foundations/etl/staging/SOURCES.md` and write `foundations/data_dictionary/sources/source__fhfa.md` source spec
- [x] **3.2** Write `foundations/etl/staging/get_fhfa.R` — download the FHFA annual U.S., state, CBSA, county, ZIP5, and tract HPI files, parse to tidy staging tables, and use `DB_PATH` from `.Renviron`
- [x] **3.3** Write staging data dictionary contract: `layers/staging/staging__fhfa_hpi.md`, using the actual landed FHFA staging columns from `get_fhfa.R`
- [x] **3.4** Write `foundations/etl/silver/fhfa_hpi_silver.R` — standardize annual FHFA staging rows, join CBSA `place_id` → `cbsa_code`, and materialize unified `silver.fhfa_hpi` with columns `geo_level`, `geo_id`, `geo_name`, `year`, `hpi_level`, `hpi_yoy_pct`, `hpi_5yr_pct`, `hpi_10yr_pct`
  First-pass scope decision:
  include `us`, `state`, `cbsa`, `county`, and ZIP5-as-`zcta`;
  keep tract staged-only for now even though it is available upstream and in staging.
- [x] **3.5** Write Silver YAML + Markdown: `layers/silver/silver__fhfa_hpi.yml` + `.md`
- [x] **3.6** Update `gold/gold_housing_market_wide.sql` to left-join `silver.fhfa_hpi` and add `hpi_level`, `hpi_yoy_pct`, `hpi_5yr_pct`, `hpi_10yr_pct` columns (Zillow columns unchanged; ZCTA rows can now populate via the approved ZIP5 proxy)
- [x] **3.7** Update Gold data dictionary `layers/gold/gold__housing_market_wide.yml` + `.md` for the four new FHFA columns
- [x] **3.8** Add FHFA row to `source_topic_checklist.md` (Ingested)
- [x] **3.9** Add FHFA to `create_DB.R` / `pipeline_manifest.yml` in correct sequence order (silver after `geo_crosswalks` + seeded FHFA staging; gold after FHFA Silver + Zillow market Silver)

---

## Track 4 — New Source: CHR (County Health Rankings)

**Priority: High**

- Completed 2026-06-04:
  reviewed the 2025 CHR analytic CSV (2,388 columns, ~3,200 county rows) and the Trends CSV (15 measures, long-format back to ~1997).
  Wrote `foundations/data_dictionary/sources/source__chr.md` documenting every CHR measure with an include/staging-only decision and rationale.
  Key decisions: 22 Silver columns across health outcomes, behaviors, clinical care, social/economic, physical environment, safety, and education, made up of 20 raw-value measures plus the 2 provider-ratio helper fields that CHR publishes for primary care and mental health access; single-year 2025 snapshot (Trends CSV deferred — only 3 of the 22 measures have Trends coverage); Gold table named `gold.health_wide` (broader than `health_outcomes_wide` given safety + education + environment scope); physical environment columns flagged as lagged vs. direct EPA/FEMA sources; CHR safety metrics sourced from CDC WONDER death records (more complete than FBI UCR at county grain for fatal violence).

- [x] **4.1** Research & spec: review `notes/.../Sources/CHR.md`, download and inspect 2025 analytic CSV and Trends CSV column layouts, document full measure inventory with include/staging-only decisions in `foundations/data_dictionary/sources/source__chr.md`
- Completed 2026-06-04:
  wrote `foundations/etl/staging/get_chr.R` to resolve the live 2025 analytic CSV link from the official CHR documentation page, cache the file under the raw data directory, normalize the county identifiers, validate uniqueness at `fips5 + release_year`, and materialize the full wide `staging.chr_health_rankings` contract with source-faithful measure provenance columns intact.
  Added `foundations/data_dictionary/layers/staging/staging__chr_health_rankings.md` documenting the wide annual county staging contract, provenance column families, clustered-county quality note, and the expectation that Silver will prune measures and derive CBSA rows downstream.
  After the first live refresh, aligned the staging contract to the actual 2025 file shape: preserved the national and state summary rows in staging, dropped one repeated embedded header row before validation, and confirmed landed staging volume at `3,204` rows (`3,152` county rows plus `52` national/state summary rows).

- [x] **4.2** Write `foundations/etl/staging/get_chr.R` — download 2025 analytic CSV, parse all columns to `staging.chr_health_rankings` with snake_cased names; preserve raw values, numerators, denominators, CI bounds, and quality flags; use `DB_PATH` from `.Renviron`
- [x] **4.3** Write staging data dictionary contract: `layers/staging/staging__chr_health_rankings.md`
- Completed 2026-06-04:
  wrote `foundations/etl/silver/chr_silver.R` to standardize the approved 22-measure CHR contract at county grain, filter out the staged national/state summary rows, and derive CBSA rows from counties using `silver.xwalk_cbsa_county` plus ACS `silver.age_kpi` weights.
  Used total population weights for the general rates and ratios, and school-age population weights for reading and math. The landed Silver table now has `3,152` county rows and `925` derived CBSA rows for `2025`.
  Wrote `foundations/data_dictionary/layers/silver/silver__chr_health_outcomes.yml` and `.md` from the landed Silver table profile, documenting the approved 22-measure contract, the provider-ratio exception, and the live null-pattern caveats.
  Added `foundations/etl/gold/gold_health_wide.sql` plus Gold YAML / Markdown artifacts for the first-pass CHR health mart at county + CBSA grain.
  Updated `source_topic_checklist.md`, `pipeline_manifest.yml`, and `create_DB.R` so CHR is now treated as an ingested source and its Silver + Gold steps are part of the documented build order.

- [x] **4.4** Write `foundations/etl/silver/chr_silver.R` — select the 22 approved measures (20 raw-value measures plus the 2 provider-ratio helper fields), standardize to `geo_level='county'`, `geo_id=fips5`, `year=release_year` grain, derive CBSA rows via population-weighted county rollup using `silver.xwalk_cbsa_county`; produce `silver.chr_health_outcomes`
- [x] **4.5** Write Silver YAML + Markdown: `layers/silver/silver__chr_health_outcomes.yml` + `.md`
- [x] **4.6** Write `foundations/etl/gold/gold_health_wide.sql` — new Gold table at county + CBSA grain with all 22 Silver columns; note `air_pollution_pm25` and `adverse_climate_events` as lagged holdovers pending Tracks 6 and 7
- [x] **4.7** Write Gold data dictionary: `layers/gold/gold__health_wide.yml` + `.md`
- [x] **4.8** Add CHR row to `source_topic_checklist.md` (Ingested)
- [x] **4.9** Add CHR to `create_DB.R` / `pipeline_manifest.yml` in correct sequence order

---

## Track 5 — New Sources: Opportunity Zones + FHFA Underserved Areas

**Priority: High, low effort**

Decisions recorded 2026-06-04:
- **Source**: Use the HUD CDFI Fund designation CSV as the canonical OZ source (`https://www.cdfifund.gov/opportunity-zones`). It is the Treasury-certified allowlist (~8,764 designated tracts), downloads as a single CSV with an 11-digit `geoid`, requires no API key, and has not changed since the 2018 designation. Census TIGER (shapefile, heavyweight) and the HUD map portal are alternatives but not preferred.
- **FHFA Underserved Areas**: Included in this track alongside OZ. Both are tract-level policy designation flags and both land in the same Gold destination. Source spec cross-referenced in `source__fhfa.md`. ETL and Silver live here, not in Track 3.
- **Silver grain**: Full tract coverage (~85K rows, `is_opportunity_zone = TRUE/FALSE`) rather than an allowlist-only slice. This enables clean inner-joins downstream and supports county/CBSA rollup metrics (`oz_tract_count`, `pct_oz_tracts`). The Silver table has no `year` dimension since OZ designations are static.
- **FHFA Underserved year scope**: Current year only for the first pass. Extend to multi-year backfill if an analytical need is identified later.
- **Gold destination**: New table `gold.dim_policy_designations` — a policy-designation dimension at `geo_level + geo_id + year` grain. OZ rows carry no `year` (static); FHFA Underserved rows carry the designation year. This table is explicitly NOT `gold.dim_geo` (geography identity) and NOT a housing fact table (metric mart). It is the canonical join target for investor-lens analytics and is designed as an extension point for future designations (Census Distressed Communities, HUD Choice Neighborhoods, USDA Rural, etc.).
- **Tract vintage mismatch note**: The CDFI Fund file now uses 2020 tract vintages; our crosswalk uses 2023 TIGER. The join should be very clean with only minor edge cases from boundary changes. Document in source spec and flag unmatched tracts during staging validation.

- [x] **5.1** Research & spec: confirm download source, document decisions above, write `foundations/data_dictionary/sources/source__opportunity_zones.md` covering both OZ and FHFA Underserved; add cross-reference note in `source__fhfa.md`
- [x] **5.2a** Write `foundations/etl/staging/get_opportunity_zones.R` — download CDFI Fund OZ CSV, zero-pad `geoid` to 11 digits, validate uniqueness at `tract_geoid`, produce `staging.opportunity_zones`
- [x] **5.2b** Write `foundations/etl/staging/get_fhfa_underserved.R` — download FHFA Underserved Areas CSV (current year only), normalize tract identifier, produce `staging.fhfa_underserved` with `tract_geoid`, `year`, `is_underserved`, `is_low_income_area`, `is_minority_area`, `is_disaster_area`
- [x] **5.3a** Write staging contract: `layers/staging/staging__opportunity_zones.md`
- [x] **5.3b** Write staging contract: `layers/staging/staging__fhfa_underserved.md`
- [x] **5.4a** Write `foundations/etl/silver/opportunity_zones_silver.R` — produce `silver.opportunity_zones` at full tract coverage (`is_opportunity_zone = TRUE/FALSE`), derive county and CBSA rollup rows with `oz_tract_count`, `total_tract_count`, `pct_oz_tracts` via `silver.xwalk_tract_county` + `silver.xwalk_cbsa_county`
- [x] **5.4b** Write `foundations/etl/silver/fhfa_underserved_silver.R` — standardize tract FIPS, derive county and CBSA rollup rows (share of underserved tracts), produce `silver.fhfa_underserved`
- [x] **5.5a** Write Silver YAML + Markdown: `layers/silver/silver__opportunity_zones.yml` + `.md`
- [x] **5.5b** Write Silver YAML + Markdown: `layers/silver/silver__fhfa_underserved.yml` + `.md`
- [x] **5.6** Write `foundations/etl/gold/gold_policy_designations.sql` — new `gold.dim_policy_designations` at `geo_level + geo_id + year` grain; join OZ and FHFA Underserved Silver tables; include `oz_tract_count`, `pct_oz_tracts`, `underserved_tract_count`, `pct_underserved_tracts` at county/CBSA rollup rows
- [x] **5.7** Write Gold data dictionary: `layers/gold/gold__dim_policy_designations.yml` + `.md`
- [x] **5.8** Add OZ and FHFA Underserved rows to `source_topic_checklist.md` (Ingested)
- [x] **5.9** Add both staging scripts + both Silver scripts + Gold policy designations to `create_DB.R` / `pipeline_manifest.yml` in correct sequence (after geo crosswalks, before any Gold table that joins to designations)

### Track 5 completion note

- Added the missing provider spec `foundations/data_dictionary/sources/source__opportunity_zones.md` because `source__fhfa.md` already referenced it and the file was not yet present.

---

## Track 6 — New Source: EPA AQI & EJScreen (Environmental Justice)

**Priority: Medium — AQI first as simpler precursor; EJScreen is the full target**

AQI (annual county CSV) is a straightforward first pass that unblocks the `gold.environment_wide` table. EJScreen adds the pollution-burden and proximity indicators the arch doc identifies for the Climate & Environmental Risk topic. The archived Harvard Dataverse snapshot includes both block-group and tract CSVs for 2024, so the recommended first-pass ingest is tract-first rather than block-group-first; block groups can remain a later expansion if we need finer geography. Both land in the same Gold table.

- [x] **6.1** Research & spec: verified live AQI county + CBSA annual ZIP URLs and 2025 column names; documented county name → FIPS crosswalk approach; wrote `foundations/data_dictionary/sources/source__epa.md` with AQI-first scope plus archival EJScreen notes; updated `SOURCES.md`
- [x] **6.2** Write `foundations/etl/staging/get_epa_aqi.R` — downloads 2016–2025 `annual_aqi_by_county_<year>.zip` and `annual_aqi_by_cbsa_<year>.zip`, row-binds each geography family, normalizes to the unified `staging.epa_aqi` contract, validates annual AQI bucket totals, and loads the combined county + CBSA table
- [x] **6.3** Write staging contract: `layers/staging/staging__epa_aqi.md`
- [x] **6.4** Write `foundations/etl/silver/epa_aqi_silver.R` — reads county and CBSA staging slices separately, normalizes county `geo_id` via state+county name crosswalk and CBSA `geo_id` via source `cbsa_code`, row-binds the approved AQI metric set, and writes `silver.epa_aqi`
- [x] **6.5** Write Silver YAML + Markdown: `layers/silver/silver__epa_aqi.yml` + `.md`
- [x] **6.6** Write `foundations/etl/gold/gold_environment_wide.sql` — new Gold table at county/CBSA grain with EPA AQI columns; designed as extension point for FEMA NRI (Track 7) and EJScreen columns
- [x] **6.7** Write Gold data dictionary: `layers/gold/gold__environment_wide.yml` + `.md`
- [x] **6.8** Add EPA AQI row to `source_topic_checklist.md` (Ingested — AQI only)
- [x] **6.9** Add EPA to `create_DB.R` / `pipeline_manifest.yml`
- [x] **6.10** Write `foundations/etl/staging/get_ejscreen.R` — download archived Harvard Dataverse EJScreen tract CSV (preferred first pass), clean the column names, validate the tract key, and parse to `staging.ejscreen`
- [x] **6.11** Write staging contract: `layers/staging/staging__ejscreen.md`
- [x] **6.12** Write `foundations/etl/silver/ejscreen_silver.R` — audit archived tract GEOIDs against `silver.xwalk_tract_county` and `gold.dim_geo`, keep the agreed core tract-level indicators, exclude unsupported Puerto Rico / territorial rows plus unresolved tract IDs, and produce `silver.ejscreen`
- [x] **6.13** Write Silver YAML + Markdown: `layers/silver/silver__ejscreen.yml` + `.md`
- Track 6 EJScreen tract-first summary: archived 2024 staging landed `86,082` tract rows; first-pass Silver materialized `84,121` canonical tract rows after excluding `1,667` Puerto Rico / territorial archive rows outside the current geo backbone and `294` additional unmatched supported-state tracts.
- [x] **6.14** Update `gold/gold_environment_wide.sql` to add EJScreen columns alongside AQI using tract-to-county / tract-to-CBSA population-weighted rollups
- [x] **6.15** Update Gold data dictionary for EJScreen columns
- [x] **6.16** Add EJScreen row to `source_topic_checklist.md` (Ingested)

Track 6 reusables for the next source waves:
- Stage first, and keep staging source-faithful even when the source is awkward or archival. That gave us one reliable place to inspect EJScreen before modeling anything.
- Treat canonical geography validation as a dedicated Silver concern. The tract audit against `xwalk` / `dim_geo` prevented us from silently shipping stale or unsupported archive rows.
- Separate unsupported-geography exclusions from true data-quality failures. Puerto Rico and territorial misses were a backbone-coverage issue, not proof that the archive was unusable.
- Prefer the simplest trustworthy geography path. AQI was fastest when we used native county and CBSA files; EJScreen was safest when we started from tract instead of block group.
- Document exclusion policy and weighting rules in the contracts as soon as they become real. That turned the EJScreen tract rollup into a reusable pattern for future small-area archive sources.

---

## Track 7 — New Source: FEMA (National Risk Index)

**Priority: Medium — NRI first; defer NFIP and disaster declarations**

- Completed 2026-06-08:
  verified the live FEMA NRI county and tract ZIP URLs for release `v120`, inspected the packaged `NRIDataDictionary.csv` and `NRI_HazardInfo.csv`, confirmed the county geography behavior (`NRI_ID = C + county GEOID`, `STCOFIPS` as the real county FIPS needing zero-padding), and wrote `foundations/data_dictionary/sources/source__fema.md` plus the corresponding `SOURCES.md` entry.
  Documented the first-pass column-selection strategy: keep the county geography backbone, composite risk/loss/vulnerability/resilience metrics, and a compact 7-field hazard family for all 18 FEMA hazard prefixes; defer the much wider exposure/component-loss fields and keep tract as a documented follow-on.

- [x] **7.1** Research & spec: read `notes/.../Sources/FEMA.md`, verify NRI county CSV download URL, confirm `STCOFIPS`, `RISK_SCORE`, `EAL_SCORE`, individual hazard score columns, document in source spec and `SOURCES.md`
- Completed 2026-06-08:
  wrote `foundations/etl/staging/get_fema_nri.R` to cache both the county and tract ZIPs under the raw FEMA directory, extract the bundled CSV + sidecar metadata files, preserve both full source-faithful hazard matrices, normalize the county-equivalent and tract FIPS backbone fields, validate `NRI_ID = C + STCOFIPS` for county plus `NRI_ID = T + TRACTFIPS` for tract, and materialize both `staging.fema_nri` and `staging.fema_nri_tract`.
  Live staging load succeeded with `3,232` county-equivalent rows and `467` columns in `staging.fema_nri`, plus `85,154` tract rows and `469` columns in `staging.fema_nri_tract`; parse-problem checks returned zero rows for both files.

- [x] **7.2** Write `foundations/etl/staging/get_fema_nri.R` — download NRI county CSV, produce `staging.fema_nri`
- Completed 2026-06-08:
  wrote `foundations/data_dictionary/layers/staging/staging__fema_nri.md` as the family staging contract for both `staging.fema_nri` and `staging.fema_nri_tract`, documenting the county-equivalent vs tract grains, the shared hazard matrix, and the live landed shapes.

- [x] **7.3** Write staging contract: `layers/staging/staging__fema_nri.md`
- Completed 2026-06-08:
  wrote `foundations/etl/silver/fema_nri_silver.R` to standardize the county-equivalent FEMA staging rows into a compact county + derived CBSA analytical table, keeping the selected composite scores plus, for each of the 18 hazards, risk score, expected annual loss score, and annualized frequency.
  County rows keep all `3,232` staged county-equivalent observations; CBSA rows are derived with `silver.xwalk_cbsa_county` using staged population as the first-pass weight. The landed Silver table has `4,167` rows total (`3,232` county + `935` cbsa) and `64` columns.

- [x] **7.4** Write `foundations/etl/silver/fema_nri_silver.R` — standardize to county/CBSA grain, retain `risk_score`, `eal_score`, and individual hazard scores; produce `silver.fema_nri`
- Completed 2026-06-08:
  wrote `foundations/data_dictionary/layers/silver/silver__fema_nri.yml` and `.md` from the landed county + CBSA Silver profile, documenting the compact FEMA contract, county-equivalent coverage, hazard families, and the tract-staged-only boundary.

- [x] **7.5** Write Silver YAML + Markdown: `layers/silver/silver__fema_nri.yml` + `.md`
- Completed 2026-06-08:
  extended `foundations/etl/gold/gold_environment_wide.sql` so the AQI backbone now carries the approved FEMA slice from `silver.fema_nri`: composite FEMA risk/loss/vulnerability/resilience metrics plus 18 hazard-specific FEMA risk scores, all joined at `geo_level + geo_id + year`.
  Rebuilt `gold.environment_wide` successfully after the transient DuckDB lock cleared. The refreshed Gold mart remains `15,145` rows and now has `59` columns, with FEMA fields populated for `2025` overlap rows (`959` county, `478` cbsa).

- [x] **7.6** Update `gold/gold_environment_wide.sql` to add FEMA NRI risk columns alongside EPA AQI (or create environment Gold table here if EPA track not yet done)
- Completed 2026-06-08:
  refreshed the Gold YAML / Markdown dictionary artifacts for `gold.environment_wide` to describe the live FEMA join behavior, the 2025-only non-null window, and the compact FEMA column group promoted into Gold.

- [x] **7.7** Update Gold data dictionary for FEMA columns
- Completed 2026-06-08:
  updated `foundations/data_dictionary/sources/source_topic_checklist.md` so FEMA is now marked Ingested for the NRI scope, with current staging / Silver / Gold coverage and the remaining NFIP / disaster-declaration gap called out explicitly.

- [x] **7.8** Add FEMA row to `source_topic_checklist.md` (Ingested — NRI only)
- Completed 2026-06-08:
  added FEMA staging and Silver steps to `foundations/etl/pipeline_manifest.yml` and added the corresponding script calls to `foundations/etl/create_DB.R`, keeping the source in the documented build path after geo crosswalks and before Gold environment assembly.

- [x] **7.9** Add FEMA to `create_DB.R` / `pipeline_manifest.yml`

---

## Track 8 — FBI UCR / NIBRS (Crime) — Skipped

**Decision: Skip.** The ICPSR county-level UCR files require a non-standard FIPS crosswalk and have significant voluntary reporting gaps that make county-grain comparisons unreliable. CHR already covers homicide, firearm fatalities, and motor vehicle crash deaths from CDC WONDER death records, which have better county-level completeness than UCR. City open-data portals (per-market incident data) are the preferred path for crime signal in deep-dive markets.

_No ETL work planned for this track._

---

## Track 9 — New Source: EPA Smart Location Database (Transportation)

**Priority: Medium — add later once ACS transport topic is stable**

The EPA Smart Location Database (SLD) provides 90+ built-environment indicators at block-group grain (2021 vintage): transit accessibility scores, intersection density, land use mix, employment accessibility by auto and transit, and walkability. It is the primary source for the Transportation topic beyond ACS commute metrics. Aggregate block groups → tract and county/CBSA for grain consistency with the rest of Foundations.

- [x] **9.1** Research & spec: verified EPA Smart Location Mapping bulk download and ArcGIS REST service, confirmed `GEOID10` as the first-pass block-group identifier with `GEOID20` retained for QA, selected a compact ~15-field keep list for Foundations, wrote `foundations/data_dictionary/sources/source__epa_smart_location.md`, and updated `SOURCES.md`
- [x] **9.2** Write `foundations/etl/staging/get_epa_sld.R` — downloads the direct EPA SLD CSV (`EPA_SmartLocationDatabase_V3_Jan_2021_Final.csv`), normalizes the approved compact indicator set into `staging.epa_sld`, reconstructs canonical 12-digit block-group GEOIDs from `STATEFP + COUNTYFP + TRACTCE + BLKGRPCE` because the delivered `GEOID10` / `GEOID20` fields are scientific-notation strings, and lands `220,740` rows in staging
- [x] **9.3** Write staging contract: `layers/staging/staging__epa_sld.md` documenting the direct CSV path, reconstructed block-group GEOIDs, retained `TotEmp` helper, and current landed shape of `220,740` rows and `31` columns
- [x] **9.4** Write `foundations/etl/silver/epa_sld_silver.R` — aggregated block groups → county grain for the first-pass modeled contract using summed numerators / denominators where exact recomputation is possible and documented weighted means elsewhere; landed `silver.epa_sld` with county `2021` coverage, kept the 8 legacy Connecticut county GEOIDs through an explicit manual fallback so the SLD rows align with 2021 ACS county transport geography, excluded Alaska `02261`, and documented tract-level recovery as a future follow-on
- [x] **9.5** Write Silver YAML + Markdown: `layers/silver/silver__epa_sld.yml` + `.md` documenting the county-only first pass, the metric-specific aggregation rules, and the deferred tract fix
- [x] **9.6** Gold placement decision and SQL: kept the recurring ACS transport panel clean by removing SLD from `gold.transport_built_form_wide` and instead created a dedicated county-only baseline table `gold.transport_built_form_sld` promoted directly from `silver.epa_sld`
- [x] **9.7** Update Gold data dictionary artifacts: refreshed `gold__transport_built_form_wide.yml` + `.md` to remove SLD enrichment and added `gold__transport_built_form_sld.yml` + `.md` documenting the separate county-only 2021 baseline mart
- [x] **9.8** Add EPA SLD row to `source_topic_checklist.md` (Ingested)
- [x] **9.9** Add EPA SLD to `create_DB.R` / `pipeline_manifest.yml`

Track 9 lessons learned:
- The direct EPA CSV is good enough for staging and county modeling, but not trustworthy enough for tract-first canonical modeling because the delivered `GEOID10` / `GEOID20` keys are scientific-notation strings and a meaningful tract share still needs a 2010/2020 bridge.
- `TotEmp` is worth retaining in staging because it lets us recompute employment density exactly instead of carrying a weighted average of density fields.
- Connecticut needs explicit geography handling. For 2021, the right operational choice was to keep the legacy county GEOIDs so SLD aligns with the ACS county transport contract already in use.
- SLD behaves like a baseline context layer, not a recurring annual panel. Keeping it in a dedicated Gold table is clearer than mixing sparse 2021-only source fields into the broader multi-year ACS transport mart.

---

## Track 10 — New Source: IPEDS (Postsecondary Education)

**Priority: Medium**

- [ ] **10.1** Research & spec: read `notes/.../Sources/IPEDS.md`, confirm current year file names (`HD<year>.zip`, `EFIA<year>.zip`, `C<year>_A.zip`), verify `FIPS`+`COUNTYCD` geocoding path, write `foundations/data_dictionary/sources/source__ipeds.md` source spec and update `SOURCES.md`
- [ ] **10.2** Write `foundations/etl/staging/get_ipeds.R` — download and unzip three IPEDS files, join on `UNITID`, produce `staging.ipeds_institutions` (characteristics, enrollment, completions joined)
- [ ] **10.3** Write staging contract: `layers/staging/staging__ipeds_institutions.md`
- [ ] **10.4** Write `foundations/etl/silver/ipeds_silver.R` — geocode to county via `FIPS`+`COUNTYCD`, aggregate to county/CBSA grain with `institution_count`, `total_enrollment`, `degrees_granted`, `rd_expenditures`; produce `silver.ipeds_county`
- [ ] **10.5** Write Silver YAML + Markdown: `layers/silver/silver__ipeds_county.yml` + `.md`
- [ ] **10.6** Decide whether IPEDS Gold lands in `gold_population_demographics` (college presence as character signal) or a new `gold_education_postsecondary_wide` table; document decision
- [ ] **10.7** Update or write the appropriate Gold SQL and data dictionary
- [ ] **10.8** Add IPEDS row to `source_topic_checklist.md` (Ingested)
- [ ] **10.9** Add IPEDS to `create_DB.R` / `pipeline_manifest.yml`

---

## Track 11 — ACS Expansions (Broadband, Disability, Language)

**Priority: Medium — add to next ACS ingestion cycle**

Three ACS tables not yet in the pipeline: B28002 (broadband subscription), B18101 (disability by age/sex), B16001 (language spoken at home). We are treating them as three separate ACS topic families rather than widening `acs_social_infra`, so each topic gets its own staging and Silver contract. They feed into `gold.population_demographics` or a new Quality of Life gold extension.

Completed 2026-06-08:
confirmed the current ACS 5-year variable IDs for B28002, B18101, and B16001 using the 2024 `tidycensus` variable catalog.
Decided to model Track 11 as three separate ACS family ingests instead of extending `acs_social_infra`.
Added `foundations/etl/staging/get_acs_broadband.R`, `get_acs_disability.R`, and `get_acs_language.R` following the existing geography-replica staging pattern.
Broadband staging uses `2017–2024` because B28002 is not present in the ACS 5-year catalog before 2017. Disability keeps the standard `2012–2024` ACS family range, while language uses `2016–2024` because `B16001_120` through `B16001_128` are not present in the ACS 5-year catalog before 2016.

Completed 2026-06-09:
wrote `foundations/etl/silver/acs_broadband_silver.R`, `acs_disability_silver.R`, and `acs_language_silver.R`, each following the existing ACS base-plus-KPI pattern with county-to-CBSA rebasing through `silver.xwalk_cbsa_county`.
Materialized six new Silver tables:
`silver.broadband_base`, `silver.broadband_kpi`, `silver.disability_base`, `silver.disability_kpi`, `silver.language_base`, and `silver.language_kpi`.
Landed KPI table coverage:
`silver.broadband_kpi` spans `2017–2024` with `1,191,904` rows,
`silver.disability_kpi` spans `2012–2024` with `1,891,571` rows,
and `silver.language_kpi` spans `2016–2024` with `1,331,868` rows.
Generated the companion Silver data dictionary artifacts for all six tables under `foundations/data_dictionary/layers/silver/`.
Decided Gold placement: disability and language stay on the `gold.population_demographics` path, while broadband lands in a new `gold.social_infra_wide` mart alongside household structure and insurance coverage.
Built `foundations/etl/gold/gold_social_infra_wide.sql` and materialized `gold.social_infra_wide` with `1,471,832` rows at the `2015–2024` `geo_level + geo_id + year` grain, using `silver.social_infra_kpi` as the row spine and joining broadband for `2017+`.

- [x] **11.1** Research & spec: confirm current ACS variable IDs for B28002, B18101, B16001; decide whether these extend `acs_social_infra_silver.R` or live in a new script; document decision
- [x] **11.2** Extend or write the appropriate staging `get_acs_*.R` script to pull the three new table sets across the standard geo grains (tract → US)
- [x] **11.3** Extend or write the silver script to produce `social_infra_base`/`social_infra_kpi` additions or new `silver.social_context_base` / `silver.social_context_kpi`
- [x] **11.4** Update or write Silver YAML + Markdown for affected tables
- [x] **11.5** Decide which Gold table receives these fields (`gold.population_demographics` extension vs. new `gold.quality_of_life_wide`); document decision
- [ ] **11.6** Update the appropriate Gold SQL and data dictionary
- [ ] **11.7** Add ACS broadband/disability/language to `source_topic_checklist.md` (Ingested)
- [ ] **11.8** Update `pipeline_manifest.yml` with any new steps

---

## Track 12 — CBP + BFS (Business Formation)

**Priority: Medium — run together, both straightforward Census downloads**

County Business Patterns (CBP) provides establishment count, employment, and payroll by NAICS at county grain. Business Formation Statistics (BFS) provides new business applications and startup activity at county/state grain. Both are Census products with no API key required, and both extend the Economics topic alongside BLS QCEW.

Completed 2026-06-09:
verified the live CBP `2023` annual geography file inventory and exact download URLs, then downloaded the county ZIP locally and confirmed the archive contains a quoted comma-delimited `cbp23co.txt` with the expected county columns.
Documented a county-first CBP ingest strategy in `foundations/data_dictionary/sources/source__cbp.md`, including why ZIP totals and ZIP industry detail should stay out of the first pass and how CBP NAICS rows should roll into the same broad industry families already used in `gold.economics_industry_wide`.
verified that the BFS county source is an annual XLSX workbook rather than a CSV, inspected the live workbook header and county data dictionary, and documented the narrow BA-only county contract in `foundations/data_dictionary/sources/source__bfs.md`.
Updated `foundations/etl/staging/SOURCES.md` plus the source-spec index/checklist to reflect the new Track 12 provider specs and the current ingestion assumptions.
Refined the implementation decision after spec review: CBP stays county-first until the ingest -> Silver -> Gold path is stable, then ZIP industry detail becomes the next geography expansion, but only for the most recent release year and in a separate ZIP staging / Silver surface; BFS Silver can retain monthly published series in a normalized table, but Gold will remain annual-only and will use CBP all-sector establishments as the preferred denominator for `business_application_rate_per_1000_establishments`.
Polled the live CBP geography files directly to lock the first-pass staging boundary: county `2023` is `1,100,961` rows and `23` columns, MSA is `576,818` rows and the same compact shape, state is `348,204` rows but a different `73`-column shape with `lfo`, ZIP totals is `34,954` rows, and ZIP detail is `2,974,116` rows.
Recorded the resulting staging decision: keep the full county payload in staging, but do not stage state / MSA / ZIP history yet because those are either derivable rollups, divergent raw shapes, or scale-heavy follow-ons. When we add ZIP, the approved first pass is latest-year ZIP industry detail only in a separate ZIP path.
Recorded the historical note more precisely as well: once the county-first path is stable for the current release, backfill county CBP for the approved first-pass annual range from `2010` forward; keep SIC-era `1997` and earlier as a separate future decision and leave the deeper `1998-2009` NAICS history as a later expansion if we want it.
Completed the county staging load and validated the landed shape in DuckDB: `staging.cbp_county` now contains `22,577,676` rows for `2010-2023`, spanning `3,209` counties and `2,249` distinct published NAICS codes.
Materialized `silver.cbp` from the landed county history after fixing the first rollup bug in the CBSA/state aggregation step. The live Silver table now has `1,053,398` rows: `789,399` county rows, `249,733` CBSA rows, and `14,266` state rows, all at `geo_level + geo_id + period + industry_code` grain across the curated 20-code broad-sector surface.
Wrote the first-pass CBP layer contracts at `layers/staging/staging__cbp.md`, `layers/silver/silver__cbp.md`, and `layers/silver/silver__cbp.yml`, using the landed table profile rather than draft estimates.
Extended `gold.economics_industry_wide` with the first-pass CBP establishment surface: total establishments, broad-family establishment counts and shares, and `cbp_estabs_per_1000_residents`, all sourced from `silver.cbp`.
Added a separate latest-year ZIP industry-detail staging script at `foundations/etl/staging/get_cbp_zip.R`, wired both county and ZIP CBP into `create_DB.R` and `pipeline_manifest.yml`, and successfully landed `staging.cbp_zip_detail` as a separate latest-year staging surface.
Documented the ZIP staging surface in `layers/staging/staging__cbp_zip_detail.md`; the current `2023` source artifact contains `2,974,116` ZIP-by-industry rows.

- [x] **12.1** Research & spec: confirm CBP annual ZIP download URL and column layout; confirm BFS annual county XLSX download URL and layout; document NAICS crosswalk approach for CBP → industry rollup families consistent with QCEW; write `foundations/data_dictionary/sources/source__cbp.md` and `source__bfs.md`; update `SOURCES.md`
- [x] **12.2** Write `foundations/etl/staging/get_cbp.R` — download CBP county annual ZIP, parse to `staging.cbp_county`; retain NAICS code, establishment size classes, employment, payroll
- [ ] **12.3** Write `foundations/etl/staging/get_bfs.R` — stage the annual county BFS workbook to `staging.bfs_county`; if we add the monthly BFS release files in the same pass, land them as `staging.bfs_monthly` so Silver can retain the richer monthly series without widening Gold
- [ ] **12.4** Write staging contracts: `layers/staging/staging__cbp.md`, `staging__bfs.md`
  ZIP note: after the county path is stable, add a separate latest-year ZIP industry-detail staging table and separate latest-year `silver.cbp_zip`; do not fold ZIP into the `2010+` county history path
- [x] **12.5** Write `foundations/etl/silver/cbp_silver.R` — standardize to county/CBSA/state grain, curate NAICS rollup to major sectors consistent with QCEW families; produce `silver.cbp`
- [ ] **12.6** Write `foundations/etl/silver/bfs_silver.R` — standardize BFS into one normalized Silver table that can retain monthly published series plus annual county / county-derived CBSA rows; compute annual `business_application_rate_per_1000_establishments` from CBP all-sector establishments for the annual county / CBSA / state surface
- [ ] **12.7** Write Silver YAML + Markdown: `silver__cbp.yml` + `.md`, `silver__bfs.yml` + `.md`; document that monthly BFS is Silver-only and Gold is annual-only
- [x] **12.8** Update `gold/gold_economy_industry.sql` (or write `gold_economy_business_wide.sql`) to add CBP establishment density and annual BFS business-application metrics only; document Gold placement decision
- [x] **12.9** Update Gold data dictionary for new columns
- [ ] **12.10** Add CBP and BFS rows to `source_topic_checklist.md` (Ingested)
- [ ] **12.11** Add CBP and BFS to `pipeline_manifest.yml`
- [ ] **12.12** After the first stable current-release county CBP pipeline lands, backfill historical annual county CBP files for the approved first-pass range (`2010+`) and document the approved year range for ongoing refreshes; keep SIC-era `1997` and earlier as a separate follow-on decision

---

## Track 13 — HMDA (Mortgage Lending)

**Priority: Medium — FHFA is now stable, unblocking this track**

HMDA (via CFPB) provides mortgage originations, denial rates, and lending equity metrics at census tract grain. This is the primary source for the lending-access dimension of the Housing topic. The tract-level grain makes it a natural complement to FHFA HPI and ACS housing metrics.

- [ ] **13.1** Research & spec: confirm CFPB HMDA flat-file download URL and column layout for the most recent year; identify the ~10 key fields (loan purpose, action taken, denial reason, applicant race, loan amount, tract FIPS); document in `foundations/data_dictionary/sources/source__hmda.md`; update `SOURCES.md`
- [ ] **13.2** Write `foundations/etl/staging/get_hmda.R` — download HMDA institution/loan-level flat file for target year(s), filter to home-purchase and refinance originations, produce `staging.hmda`; this file is large — document row count and filtering decisions in the staging contract
- [ ] **13.3** Write staging contract: `layers/staging/staging__hmda.md`; note that staging retains loan-level rows (one row per application) before Silver aggregation
- [ ] **13.4** Write `foundations/etl/silver/hmda_silver.R` — aggregate loan-level staging to tract/county/CBSA grain; compute `origination_rate`, `denial_rate`, `median_loan_amount`, `minority_applicant_denial_gap`; produce `silver.hmda`
- [ ] **13.5** Write Silver YAML + Markdown: `layers/silver/silver__hmda.yml` + `.md`
- [ ] **13.6** Decide whether HMDA Gold extends `gold.housing_core_wide` or `gold.housing_market_wide`, or lands in a new `gold.housing_lending_wide`; document decision (lending equity metrics may warrant their own table)
- [ ] **13.7** Update or write the appropriate Gold SQL and data dictionary
- [ ] **13.8** Add HMDA row to `source_topic_checklist.md` (Ingested)
- [ ] **13.9** Add HMDA to `pipeline_manifest.yml`

---

## Track 14 — Opportunity Insights (Social Capital Atlas + Opportunity Atlas)

**Priority: High — preferred social capital source; also delivers intergenerational mobility**

_Replaces the originally planned JEC Social Capital track. JEC's index uses 2018 data and is a single composite; Opportunity Insights publishes more recent data with decomposed sub-indices (economic connectedness, cohesion, civic engagement) and a separate Opportunity Atlas with intergenerational mobility estimates. Both datasets are county-grain CSV downloads from the same source, making this a single ingestion pipeline that delivers two high-value metric map items: Social Capital (Character / Social Fabric) and Intergenerational Mobility (Opportunity / Resident Opportunity)._

_JEC Social Capital remains available as a future cross-reference if the sub-index decomposition proves analytically useful, but it is not the primary ingestion target._

- [ ] **14.1** Research & spec: confirm Opportunity Insights Social Capital Atlas download URL and column layout (economic connectedness, cohesion, civic engagement sub-indices at county grain); confirm Opportunity Atlas download URL and column layout (upward mobility, income rank by parent income percentile at county grain); document both in `foundations/data_dictionary/sources/source__opportunity_insights.md`; update `SOURCES.md`
- [ ] **14.2** Write `foundations/etl/staging/get_opportunity_insights.R` — download Social Capital Atlas CSV and Opportunity Atlas CSV, parse to `staging.opportunity_insights_social_capital` and `staging.opportunity_insights_opportunity_atlas`
- [ ] **14.3** Write staging contracts: `layers/staging/staging__opportunity_insights_social_capital.md`, `staging__opportunity_insights_opportunity_atlas.md`
- [ ] **14.4** Write `foundations/etl/silver/opportunity_insights_silver.R` — standardize county FIPS for both tables, derive CBSA rollup rows (population-weighted); produce `silver.opportunity_insights_social_capital` with `economic_connectedness`, `cohesion_index`, `civic_engagement_index` and `silver.opportunity_insights_opportunity_atlas` with `p25_household_income`, `p75_household_income`, `upward_mobility_rate` (probability of reaching top quintile from bottom quintile)
- [ ] **14.5** Write Silver YAML + Markdown: `layers/silver/silver__opportunity_insights_social_capital.yml` + `.md`, `silver__opportunity_insights_opportunity_atlas.yml` + `.md`
- [ ] **14.6** Decide Gold placement: Social Capital sub-indices extend `gold.health_wide` or land in a new `gold.social_fabric_wide`; Opportunity Atlas metrics extend `gold.economics_income_wide` or same new table; document decision
- [ ] **14.7** Update or write the appropriate Gold SQL and data dictionary
- [ ] **14.8** Add Opportunity Insights rows to `source_topic_checklist.md` (Ingested)
- [ ] **14.9** Add Opportunity Insights to `pipeline_manifest.yml`

---

## Track 15 — NCES CCD (K–12 Schools, Points Layer)

**Priority: Medium — national-once ingest; prerequisite for per-market school aggregations**

NCES Common Core of Data provides lat/lon, enrollment, Title I status, grade span, and locale code for every U.S. public school. This is the primary K–12 source for the Points layer (`dim_point_of_interest`) and the upstream source for county/CBSA school-density aggregations that flow into the Places layer. Ingest once nationally; no per-market parameterization needed.

_Depends on: basic Points layer schema decisions (surrogate `point_id`, `point_source_mapping`) being made before this track runs. Those decisions are part of Track 16._

- [ ] **15.1** Research & spec: confirm NCES CCD annual ZIP download URL and column layout (`NCESSCH`, lat/lon, `MEMBER` enrollment, `TITLEI_STATUS`, `GSLO`/`GSHI`, `LOCALE`); write `foundations/data_dictionary/sources/source__nces_ccd.md`; update `SOURCES.md`
- [ ] **15.2** Write `foundations/etl/staging/get_nces_ccd.R` — download most recent CCD school-level file, parse to `staging.nces_ccd`; retain `NCESSCH` as source ID, lat/lon, key attributes
- [ ] **15.3** Write staging contract: `layers/staging/staging__nces_ccd.md`
- [ ] **15.4** Write `foundations/etl/silver/nces_ccd_silver.R` — assign surrogate `point_id`, write to `dim_point_of_interest` (category = `education / k12_school`) and `point_source_mapping` (source = `nces`, source_id = `NCESSCH`); pass through native lat/lon; enrich with county/CBSA from spatial join (or crosswalk via `xwalk_tract_county` if geometry not yet available)
- [ ] **15.5** Write Silver YAML + Markdown for the CCD contribution to `dim_point_of_interest` and `point_source_mapping`
- [ ] **15.6** Aggregate school-level Points to county/CBSA grain: `school_count`, `title1_share`, `avg_enrollment`, `locale_urban_share`; write aggregation SQL or dbt model that feeds `gold.population_demographics` or a new `gold.education_k12_wide`
- [ ] **15.7** Write Gold data dictionary for new K–12 aggregation columns
- [ ] **15.8** Add NCES CCD row to `source_topic_checklist.md` (Ingested)
- [ ] **15.9** Add NCES CCD to `pipeline_manifest.yml`

---

## Track 16 — Points Layer Foundation (Schema + National-Once Sources)

**Priority: Depends on Stoop migration — do not start until Stoop has migrated its POI data**

This track establishes the core Points layer schema (`dim_point_of_interest`, `point_source_mapping`) and ingests the national-once sources that don't require per-market parameterization. The per-market and deep-dive sources (Overture POIs, OSM, transit GTFS, school attendance zones) are Track 17.

_Depends on: Stoop migration completing. The surrogate `point_id` scheme and deduplication logic need to be finalized against Stoop's existing data before new sources are added._

- [ ] **16.1** Architecture decision: finalize `dim_point_of_interest` schema (surrogate `point_id` generation, `category/subcategory/detail` taxonomy driven by `config/poi_categories.yaml`, geography link columns `nta_id`, `tract_id`, `county_fips`); finalize `point_source_mapping` schema; document in `foundations/data_dictionary/docs/data_platform_architecture.md` and write table-level data dictionary stubs
- [ ] **16.2** Write `foundations/etl/gold/gold_dim_point_of_interest.sql` (or equivalent R script) — create the managed Gold tables `gold.dim_point_of_interest` and `gold.point_source_mapping` with the approved schema
- [ ] **16.3** Write Gold data dictionary: `layers/gold/gold__dim_point_of_interest.yml` + `.md`, `gold__point_source_mapping.yml` + `.md`
- [ ] **16.4** IPEDS (colleges/universities) — write `get_ipeds_points.R`, silver script, and `dim_point_of_interest` contribution (source = `ipeds`, source_id = `UNITID`; category = `education / college`); coordinate with Track 10 which handles the county-grain IPEDS aggregations for Places
- [ ] **16.5** HIFLD (hospitals) — write `get_hifld_hospitals.R`, silver script, and `dim_point_of_interest` contribution (source = `hifld`, source_id = CMS Certification Number; category = `health / hospital`)
- [ ] **16.6** IMLS (public libraries) — write `get_imls.R`, silver script, and `dim_point_of_interest` contribution (source = `imls`; category = `civic / library`)
- [ ] **16.7** USDA Farmers Markets — write `get_usda_farmers_markets.R`, silver script, and `dim_point_of_interest` contribution (source = `usda_fmd`; category = `food / farmers_market`)
- [ ] **16.8** Write staging and Silver data dictionary contracts for each national-once source (IPEDS points, HIFLD, IMLS, USDA farmers markets)
- [ ] **16.9** Write `fct_geo_aggregations` stub SQL — point-in-polygon counts by category per NTA/tract, to be populated as Points sources are added; document the aggregation pattern
- [ ] **16.10** Add all national-once Points sources to `source_topic_checklist.md` (Ingested) and `pipeline_manifest.yml`

---

## Track 17 — Points Layer: Per-Market Framework

**Priority: Depends on Track 16 + first market deep-dive selection**

Per-market and deep-dive Points sources. The ingestion framework is built once parameterized by bounding box or metro area code; it is triggered per market on first deep-dive. This track covers the framework design; actual per-market runs happen at product time.

_Depends on: Track 16 (Points layer schema), Stoop migration, and a first target market being selected for deep-dive._

- [ ] **17.1** Architecture decision: confirm bounding-box parameterization approach for Overture and OSM Overpass queries; document market-onboarding checklist (neighborhood boundary source, transit agency GTFS feed ID, city open data portal for crime/parks)
- [ ] **17.2** Overture Places framework — write `get_overture_places.R` parameterized by bounding box; map Overture categories → `poi_categories.yaml`; produce `staging.overture_places_{market}`; write silver deduplication logic against existing `dim_point_of_interest` rows
- [ ] **17.3** OSM via Overpass framework — write `get_osm_pois.R` parameterized by bounding box; extract amenity/shop/leisure nodes; produce `staging.osm_pois_{market}`; silver deduplication against Overture and existing rows
- [ ] **17.4** Transit stops (Transitland) — write `get_transitland_stops.R` parameterized by bounding box or GTFS feed ID; produce `staging.transit_stops_{market}`; silver contribution to `dim_point_of_interest` (source = `gtfs:{agency_id}`, source_id = `stop_id`; category = `transportation / transit_stop`)
- [ ] **17.5** Park boundaries (Overture baseline) — write `get_overture_parks.R`; produce `staging.overture_parks_{market}`; silver contribution to `dim_polygon` (category = `parks`)
- [ ] **17.6** Neighborhood boundaries — write `get_neighborhood_boundaries.R` parameterized by market; produce `staging.neighborhood_boundaries_{market}`; silver contribution to `dim_polygon` as the primary NTA/neighborhood aggregation unit
- [ ] **17.7** Write staging and Silver data dictionary contract templates for per-market sources (one template per source type, to be instantiated per market)
- [ ] **17.8** Write `fct_geo_aggregations` production SQL — POI counts and density per NTA/tract by category, park area per NTA, transit stop density; feeds `gold.transport_built_form_wide` and future neighborhood-level gold tables
- [ ] **17.9** Document per-market onboarding checklist in `foundations/data_dictionary/docs/data_platform_architecture.md` (neighborhood boundary source, GTFS feed ID, city open data portals, editorial list sourcing)

---

## Track 19 — Existing Table Updates (CHR Extension + Derived Gold Columns)

**Priority: High — no new ingestion pipelines; closes open items in existing gold tables**

_This track covers updates to already-ingested sources and derived column additions that don't require new staging scripts. All items here are small ETL changes to existing scripts or SQL files._

### 19.1 CHR Silver Contract Extension (Health Behavior Fields)

Three CHR fields are present in the `staging.chr_health_rankings` download but were excluded from the original 22-measure Silver contract in `chr_silver.R`. Adding them requires updating `measure_columns` in the silver script and rebuilding `gold.health_wide`.

- [ ] **19.1.1** Add `physical_inactivity`, `adult_obesity`, and `poor_mental_health_days` to `measure_columns` in `foundations/etl/silver/chr_silver.R`
- [ ] **19.1.2** Re-run `chr_silver.R` to rebuild `silver.chr_health_outcomes` with the three new columns
- [ ] **19.1.3** Re-run `gold_health_wide.sql` to promote the three new columns to `gold.health_wide`
- [ ] **19.1.4** Update `foundations/data_dictionary/layers/silver/silver__chr_health_outcomes.md` + `.yml` to document the three new fields
- [ ] **19.1.5** Update `foundations/data_dictionary/layers/gold/gold__health_wide.md` + `.yml` for the three new columns

### 19.2 CHR Trends File (Health Time Series)

The current CHR Silver contract is a single-year 2025 snapshot. CHR publishes a separate Trends CSV with 15 measures going back to ~1997. Without this, no health metric supports trend analysis. This is the most analytically significant gap in the current health data.

- [ ] **19.2.1** Research & spec: download and inspect the CHR Trends CSV; document which of our 22+ Silver measures have Trends coverage and the available year range; note any column name differences from the analytic CSV
- [ ] **19.2.2** Extend `foundations/etl/staging/get_chr.R` to also download and stage the Trends CSV as `staging.chr_health_trends`
- [ ] **19.2.3** Extend `foundations/etl/silver/chr_silver.R` to process `staging.chr_health_trends` into a long-format `silver.chr_health_trends` at `geo_level + geo_id + year + measure` grain with CBSA rollup rows
- [ ] **19.2.4** Decide Gold placement: extend `gold.health_wide` with a multi-year panel (breaking the current single-year grain) or create a separate `gold.health_trends_long`; document decision
- [ ] **19.2.5** Update or write the appropriate Gold SQL and data dictionary artifacts
- [ ] **19.2.6** Update `silver__chr_health_outcomes.md` to note that multi-year coverage now exists via the companion trends table

### 19.3 Social Infra Silver Promotion (Household Structure)

ACS household structure promotion can now move forward for single-person households, but the current `acs_social_infra` staging family does not yet land the `B11003` single-parent fields even though the earlier plan assumed it did.

- [x] **19.3.1** Confirm current staged coverage: `B11001` household-alone fields are present in `staging.acs_social_infra_*`, while `B11003` single-parent fields are not currently landed
- [x] **19.3.2** Add `pct_hh_single_person` KPI derivation to `foundations/etl/silver/acs_social_infra_silver.R`
- [ ] **19.3.2b** Add `pct_family_single_parent` KPI derivation after `B11003` is staged
- [x] **19.3.3** Rebuild `silver.social_infra_kpi` with the promoted single-person household column
- [x] **19.3.4** Decide Gold placement: land household structure in the new `gold.social_infra_wide` table
- [x] **19.3.5** Update silver and gold data dictionary artifacts for the promoted single-person household column

### 19.4 Broadband Promotion (ACS B28002)

ACS broadband variables (B28002) are commented out in `get_acs_social_infra.R` with a note that historical coverage is incomplete. The data exists from ~2016 onward with consistent enough methodology to be useful.

Completed 2026-06-09 via the dedicated Track 11 broadband family:
`silver.broadband_kpi` now provides the recurring broadband panel, and `gold.social_infra_wide` consumes that family directly instead of backfilling the older `acs_social_infra` staging path.

- [x] **19.4.1** Deprecated / superseded: do not backfill B28002 into `acs_social_infra`; use the dedicated broadband staging family from Track 11 instead
- [x] **19.4.2** Deprecated / superseded: no re-run needed for `staging.acs_social_infra_*` because broadband now lands through `staging.acs_broadband_*`
- [x] **19.4.3** Deprecated / superseded: do not derive broadband KPIs inside `silver.social_infra_kpi`; use `silver.broadband_kpi`
- [x] **19.4.4** Deprecated / superseded: no rebuild needed for `silver.social_infra_kpi` because broadband is modeled in its own Silver contract
- [x] **19.4.5** Extend the appropriate Gold table (same destination decision as 19.3.4)
- [x] **19.4.6** Update data dictionary artifacts; note 2016+ coverage start and 2019 question-wording change in the definition

### 19.5 Derived Gold Columns (Poverty Trend, LQ, Attainment Trend)

Three metric map items are derivable from existing gold time series — no new ingestion, just new computed columns in gold ETL scripts.

- [ ] **19.5.1** Add `pov_rate_change_1yr` and `pov_rate_change_5yr` to `foundations/etl/gold/gold_economy_income.sql` (derived from the `pov_rate` time series already in `gold.economics_income_wide`); update gold data dictionary
- [ ] **19.5.2** Add `pct_ba_plus_change_5yr` to `foundations/etl/gold/gold_population_wide.sql` (derived from `pct_ba_plus` time series in `gold.population_demographics`); update gold data dictionary
- [ ] **19.5.3** Add location quotient columns (`lq_professional`, `lq_manufacturing`, `lq_information`, etc.) to `foundations/etl/gold/gold_economy_industry.sql` — derived as `pct_qcew_private_emp_* / national_pct_qcew_private_emp_*` joining the `geo_level = 'us'` row; update gold data dictionary

---

## Track 20 — USDA Food Access Research Atlas

**Priority: Medium — feeds Livability / Access & Infrastructure**

The USDA Economic Research Service Food Access Research Atlas provides tract-level food desert designation, threshold-based low-access measures, and low-income + low-access population counts. Published approximately every 5 years (most recent 2019). Candidate Gold destination is a dedicated access-oriented mart rather than the recurring ACS transport panel.

- [x] **20.1** Research & spec: confirmed ERS download and ArcGIS REST service for the current `2019` Food Access Research Atlas, verified tract `GEOID10` and key fields including `LILATracts_1And10`, `lapop1`, and `LA1and10`, documented the first-pass keep list in `foundations/data_dictionary/sources/source__usda_food_atlas.md`, and updated `SOURCES.md`
- [x] **20.2** Write `foundations/etl/staging/get_usda_food_atlas.R` — downloaded the current USDA workbook, kept the approved compact tract field set, validated `tract_geoid`, and materialized `staging.usda_food_atlas` with `72,531` rows and `37` columns
- [x] **20.3** Write staging contract: `layers/staging/staging__usda_food_atlas.md`; documented the 2019 vintage, tract-native workbook path, and the live landed staging shape
- [x] **20.4** Write `foundations/etl/silver/usda_food_atlas_silver.R` — kept tract rows source-native, derived county GEOIDs directly from tract prefixes, rolled counties to CBSAs through `silver.xwalk_cbsa_county`, and materialized `silver.usda_food_atlas` with `72,531` tract rows, `3,141` county rows, and `918` CBSA rows
- [x] **20.5** Write Silver YAML + Markdown: `layers/silver/silver__usda_food_atlas.yml` + `.md`
- [x] **20.6** Gold placement decision: followed the Track 9 lesson and kept this source out of the recurring ACS transport panel by creating a dedicated baseline mart `gold.food_access_wide`
- [x] **20.7** Update or write the appropriate Gold SQL and data dictionary: added `gold/gold_food_access_wide.sql` plus `gold__food_access_wide.yml` + `.md`
- [x] **20.8** Add USDA Food Atlas to `source_topic_checklist.md` (Ingested)
- [x] **20.9** Add USDA Food Atlas to `pipeline_manifest.yml` and `create_DB.R`

Track 20 lessons learned:
- The workbook path is the right operational ingest surface. It already publishes the tract table cleanly enough that we do not need to lean on the ArcGIS service except for schema QA.
- The Atlas is tract-native and based on 2010 tracts, but we can still get stable county rollups without a tract-backbone rescue step by deriving county GEOIDs directly from the tract key prefix.
- The county geography edge case matches Track 9: keep the 8 legacy Connecticut county GEOIDs explicitly for alignment with the current county contract, and exclude Alaska county-equivalent `02261` from the first-pass county / CBSA rollups.
- Like EPA SLD, this behaves better as a specialty baseline mart than as a sparse enrichment inside a broader recurring Gold panel.

---

## Track 21 — Social Fabric Sources (MIT Election Lab + IRS Business Master File)

**Priority: Medium — two lightweight ingestions bundled; both feed Character / Social Fabric**

Two small standalone ingestions with no shared dependencies, bundled into one track for efficiency. MIT Election Lab provides county-level midterm election turnout normalized to voting-age population. IRS Business Master File provides nonprofit organization counts by county, used to compute nonprofits per 100K residents as a proxy for organized civic life.

### 21.1 MIT Election Lab (Voting Rates)

- [ ] **21.1.1** Research & spec: confirm MIT Election Lab county-level returns download URL and column layout; verify county FIPS identifier, election year, total votes cast, and VAP denominator source (CVAP from Census); document in `foundations/data_dictionary/sources/source__mit_election_lab.md`
- [ ] **21.1.2** Write `foundations/etl/staging/get_mit_election_lab.R` — download county returns for midterm election years (2010, 2014, 2018, 2022), parse to `staging.mit_election_lab`; retain county FIPS, year, total votes, office type filter (House or Governor as midterm proxy)
- [ ] **21.1.3** Write staging contract: `layers/staging/staging__mit_election_lab.md`; note that VAP denominator comes from Census CVAP, not raw population
- [ ] **21.1.4** Write `foundations/etl/silver/mit_election_lab_silver.R` — standardize county FIPS, compute `voter_turnout_rate` as total votes ÷ CVAP (join to ACS working-age population as proxy if CVAP not yet ingested), derive CBSA rollup rows (population-weighted); produce `silver.mit_election_lab`
- [ ] **21.1.5** Write Silver YAML + Markdown: `layers/silver/silver__mit_election_lab.yml` + `.md`

### 21.2 IRS Business Master File (Nonprofits per 100K)

- [ ] **21.2.1** Research & spec: confirm IRS BMF extract download URL (IRS publishes monthly; confirm most recent annual snapshot); verify county FIPS derivation from zip code (requires zip-to-county crosswalk); identify relevant NTEE codes for non-religious nonprofits; document in `foundations/data_dictionary/sources/source__irs_bmf.md`
- [ ] **21.2.2** Write `foundations/etl/staging/get_irs_bmf.R` — download IRS BMF CSV, filter to active organizations, parse to `staging.irs_bmf`; retain EIN, zip code, NTEE code, ruling year
- [ ] **21.2.3** Write staging contract: `layers/staging/staging__irs_bmf.md`; note zip-to-county crosswalk dependency and NTEE exclusion logic for religious organizations
- [ ] **21.2.4** Write `foundations/etl/silver/irs_bmf_silver.R` — crosswalk zip → county via HUD USPS crosswalk or Census zip-county relationship file, aggregate to county and CBSA grain, compute `nonprofits_per_100k`; produce `silver.irs_bmf`
- [ ] **21.2.5** Write Silver YAML + Markdown: `layers/silver/silver__irs_bmf.yml` + `.md`

### 21.3 Gold Promotion (Both Sources)

- [ ] **21.3.1** Decide Gold placement for both: extend `gold.health_wide` (social context group) or new `gold.social_fabric_wide` alongside Opportunity Insights (Track 14); document decision — consistent placement with Track 14 and Track 19.3 decisions
- [ ] **21.3.2** Update or write the appropriate Gold SQL to include `voter_turnout_rate` (midterm) and `nonprofits_per_100k`
- [ ] **21.3.3** Update Gold data dictionary for both new columns
- [ ] **21.3.4** Add MIT Election Lab and IRS BMF to `source_topic_checklist.md` (Ingested)
- [ ] **21.3.5** Add both to `pipeline_manifest.yml`

---

## Track 22 — Stanford SEDA (K–12 Learning Rates)

**Priority: Low — future ingestion; crosswalk complexity warrants separate track**

The Stanford Education Data Archive (SEDA) provides district-level standardized test score averages and learning rate estimates (growth per grade level) derived from state assessment data. It is more analytically useful than CHR's test score indices because it measures learning rates rather than proficiency levels, and it covers a longer time series (approximately 2009–2018). The primary challenge is crosswalking school districts to counties and CBSAs, since districts do not nest cleanly into counties.

_Depends on: Track 15 (NCES CCD) completing first, since CCD provides the district-to-county relationship file needed for the crosswalk._

- [ ] **22.1** Research & spec: confirm Stanford SEDA download URL and most recent release year; review available measures (mean test scores, learning rates, trend estimates); confirm district NCES ID as the join key; document crosswalk approach (NCES district → county via NCES geographic relationship files) in `foundations/data_dictionary/sources/source__stanford_seda.md`; update `SOURCES.md`
- [ ] **22.2** Write `foundations/etl/staging/get_stanford_seda.R` — download SEDA district-level CSV, parse to `staging.stanford_seda`; retain NCES district ID, grade-level mean scores, learning rate estimates, year range
- [ ] **22.3** Write staging contract: `layers/staging/staging__stanford_seda.md`; document coverage years and note that learning rates are more reliable than single-year score averages
- [ ] **22.4** Write `foundations/etl/silver/stanford_seda_silver.R` — join NCES district ID to county via NCES geographic relationship file (enrollment-weighted where multiple counties share a district); aggregate to county and CBSA grain; produce `silver.stanford_seda` with `avg_learning_rate`, `avg_test_score_grade3`, `avg_test_score_grade8`, `score_trend_5yr`
- [ ] **22.5** Write Silver YAML + Markdown: `layers/silver/silver__stanford_seda.yml` + `.md`; document district-to-county crosswalk methodology and enrollment-weighting approach
- [ ] **22.6** Decide Gold placement: extend `gold.health_wide` (education group alongside CHR graduation and test scores) or new `gold.education_k12_wide`; document decision — coordinate with Track 15 (NCES CCD) Gold placement decision
- [ ] **22.7** Update or write the appropriate Gold SQL and data dictionary
- [ ] **22.8** Add Stanford SEDA to `source_topic_checklist.md` (Ingested)
- [ ] **22.9** Add Stanford SEDA to `pipeline_manifest.yml`

---

## Track 18 — Final Integration and Documentation Sync

These tasks close out the plan after all tracks above are complete.

- [ ] **18.1** Update `source_topic_checklist.md` — verify all status fields are accurate; move any remaining Planned rows with evidence of partial work to Partial
- [ ] **18.2** Update `foundations/data_dictionary/sources/checklist.md` — add new source entries for all tracks: FHFA, CHR, OZ, EPA AQI, EPA EJScreen, EPA SLD, FEMA NRI, IPEDS, ACS expansions, CBP, BFS, HMDA, Opportunity Insights (Social Capital Atlas + Opportunity Atlas), USDA Food Atlas, MIT Election Lab, IRS BMF, Stanford SEDA, NCES CCD, HIFLD, IMLS, USDA farmers markets, Overture, OSM, Transitland
- [ ] **18.3** Update `foundations/data_dictionary/README.md` — add new Gold themes (health, environment, transportation built form, postsecondary education, lending, social capital, policy designations, points layer) to the main themes table
- [ ] **18.4** Update `foundations/etl/pipeline_manifest.yml` — verify all new scripts are present with correct `depends_on` entries and `enabled: true`
- [ ] **18.5** Update `foundations/etl/create_DB.R` — confirm new staging/silver/gold scripts are sourced in correct sequence order
- [ ] **18.6** Update `ETL_MIGRATION_PLAN.md` — add a note marking the plan as closed

---

## Sequence Summary

Recommended execution order:

**Places layer (already complete or in progress):**
1. **Track 2** (shared field definitions) — complete
2. **Tracks 1.2–1.6** (decisions + IRS, Zillow, HUD CHAS, BLS) — complete
3. **Tracks 3–5** (FHFA, CHR, OZ + FHFA Underserved) — complete

**Places layer (remaining):**
4. **Track 19** (existing table updates: CHR extension, CHR trends, social infra promotion, broadband, derived gold columns) — no new ingestion; highest-value/lowest-effort work; run first among remaining tracks
5. **Tracks 6–7** (EPA EJScreen/AQI, FEMA NRI) — Climate & Environmental Risk; run in parallel, both feed `gold.environment_wide`
6. **Track 9** (EPA Smart Location Database) — Transportation baseline; now lands in dedicated `gold.transport_built_form_sld`; run alongside Track 20
7. **Track 20** (USDA Food Access Research Atlas) — Access & Infrastructure; can run in parallel with Track 9
8. **Track 10** (IPEDS) — Postsecondary education; can run in parallel with 6–9
9. **Track 11** (ACS broadband/disability/language) — next ACS ingestion cycle; extends existing silver scripts; coordinate broadband with Track 19.4
10. **Tracks 12–13** (CBP/BFS, HMDA) — Economics and Housing extensions; run in parallel
11. **Track 14** (Opportunity Insights — Social Capital Atlas + Opportunity Atlas) — Social Fabric and Resident Opportunity; high priority, can run in parallel with Tracks 6–13
12. **Track 21** (MIT Election Lab + IRS BMF) — Social Fabric; lightweight, run in parallel with any other track
13. **Track 22** (Stanford SEDA) — Education; depends on Track 15 (NCES CCD) for the district-county crosswalk
14. **Track 8** (FBI UCR) — Skipped

**Points/Parcels/Polygons layer (after Stoop migration):**
11. **Track 15** (NCES CCD) — Depends on Track 16 schema decisions; national-once, can proceed once schema is finalized
12. **Track 16** (Points layer schema + national-once sources: IPEDS points, HIFLD, IMLS, USDA) — blocks Track 17; do not start until Stoop migration is complete
13. **Track 17** (per-market framework: Overture, OSM, Transitland, parks, neighborhood boundaries) — depends on Track 16 and first deep-dive market selection

**Close-out:**
14. **Track 18** (integration sync) — after all source tracks complete
