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

## Track 6 — New Source: EPA EJScreen (Environmental Justice)

**Priority: Medium — AQI first as simpler precursor; EJScreen is the full target**

AQI (annual county CSV) is a straightforward first pass that unblocks the `gold.environment_wide` table. EJScreen (block-group → tract aggregate) adds the pollution-burden and proximity indicators the arch doc identifies for the Climate & Environmental Risk topic. Both land in the same Gold table.

- [ ] **6.1** Research & spec: verify annual AQI county CSV download URL and column names; review EJScreen block-group CSV structure and indicator list; document crosswalk approach for EPA name → FIPS; write `foundations/data_dictionary/sources/source__epa.md` covering both AQI and EJScreen; update `SOURCES.md`
- [ ] **6.2** Write `foundations/etl/staging/get_epa_aqi.R` — download `annual_aqi_by_county_<year>.zip` for relevant years, parse to `staging.epa_aqi`; retain state/county name strings for crosswalk
- [ ] **6.3** Write staging contract: `layers/staging/staging__epa_aqi.md`
- [ ] **6.4** Write `foundations/etl/silver/epa_aqi_silver.R` — apply state+county name → FIPS crosswalk, standardize to county/CBSA grain with `aqi_median`, `aqi_days_unhealthy`, `pm25_days` columns; produce `silver.epa_aqi`
- [ ] **6.5** Write Silver YAML + Markdown: `layers/silver/silver__epa_aqi.yml` + `.md`
- [ ] **6.6** Write `foundations/etl/gold/gold_environment_wide.sql` — new Gold table at county/CBSA grain with EPA AQI columns; designed as extension point for FEMA NRI (Track 7) and EJScreen columns
- [ ] **6.7** Write Gold data dictionary: `layers/gold/gold__environment_wide.yml` + `.md`
- [ ] **6.8** Add EPA AQI row to `source_topic_checklist.md` (Ingested — AQI only)
- [ ] **6.9** Add EPA to `create_DB.R` / `pipeline_manifest.yml`
- [ ] **6.10** Write `foundations/etl/staging/get_ejscreen.R` — download EPA EJScreen block-group CSV, parse to `staging.ejscreen`; retain block-group FIPS for tract aggregation
- [ ] **6.11** Write staging contract: `layers/staging/staging__ejscreen.md`
- [ ] **6.12** Write `foundations/etl/silver/ejscreen_silver.R` — aggregate block groups → tract and county/CBSA grain; retain `pm25`, `ozone`, `diesel_pm`, `superfund_proximity`, `wastewater_discharge`, `pollution_burden_score`; produce `silver.ejscreen`
- [ ] **6.13** Write Silver YAML + Markdown: `layers/silver/silver__ejscreen.yml` + `.md`
- [ ] **6.14** Update `gold/gold_environment_wide.sql` to add EJScreen columns alongside AQI
- [ ] **6.15** Update Gold data dictionary for EJScreen columns
- [ ] **6.16** Add EJScreen row to `source_topic_checklist.md` (Ingested)

---

## Track 7 — New Source: FEMA (National Risk Index)

**Priority: Medium — NRI first; defer NFIP and disaster declarations**

- [ ] **7.1** Research & spec: read `notes/.../Sources/FEMA.md`, verify NRI county CSV download URL, confirm `STCOFIPS`, `RISK_SCORE`, `EAL_SCORE`, individual hazard score columns, document in source spec and `SOURCES.md`
- [ ] **7.2** Write `foundations/etl/staging/get_fema_nri.R` — download NRI county CSV, produce `staging.fema_nri`
- [ ] **7.3** Write staging contract: `layers/staging/staging__fema_nri.md`
- [ ] **7.4** Write `foundations/etl/silver/fema_nri_silver.R` — standardize to county/CBSA grain, retain `risk_score`, `eal_score`, and individual hazard scores; produce `silver.fema_nri`
- [ ] **7.5** Write Silver YAML + Markdown: `layers/silver/silver__fema_nri.yml` + `.md`
- [ ] **7.6** Update `gold/gold_environment_wide.sql` to add FEMA NRI risk columns alongside EPA AQI (or create environment Gold table here if EPA track not yet done)
- [ ] **7.7** Update Gold data dictionary for FEMA columns
- [ ] **7.8** Add FEMA row to `source_topic_checklist.md` (Ingested — NRI only)
- [ ] **7.9** Add FEMA to `create_DB.R` / `pipeline_manifest.yml`

---

## Track 8 — FBI UCR / NIBRS (Crime) — Skipped

**Decision: Skip.** The ICPSR county-level UCR files require a non-standard FIPS crosswalk and have significant voluntary reporting gaps that make county-grain comparisons unreliable. CHR already covers homicide, firearm fatalities, and motor vehicle crash deaths from CDC WONDER death records, which have better county-level completeness than UCR. City open-data portals (per-market incident data) are the preferred path for crime signal in deep-dive markets.

_No ETL work planned for this track._

---

## Track 9 — New Source: EPA Smart Location Database (Transportation)

**Priority: Medium — add later once ACS transport topic is stable**

The EPA Smart Location Database (SLD) provides 90+ built-environment indicators at block-group grain (2021 vintage): transit accessibility scores, intersection density, land use mix, employment accessibility by auto and transit, and walkability. It is the primary source for the Transportation topic beyond ACS commute metrics. Aggregate block groups → tract and county/CBSA for grain consistency with the rest of Foundations.

- [ ] **9.1** Research & spec: verify EPA SLD download URL and geodatabase/CSV format, confirm `GEOID10` block-group identifier, select the ~15 highest-signal indicators for Foundations (transit accessibility, intersection density, land use mix, walkability index, employment density); write `foundations/data_dictionary/sources/source__epa_sld.md`; update `SOURCES.md`
- [ ] **9.2** Write `foundations/etl/staging/get_epa_sld.R` — download EPA SLD national block-group file, parse selected indicator columns to `staging.epa_sld`; retain block-group GEOID for tract aggregation
- [ ] **9.3** Write staging contract: `layers/staging/staging__epa_sld.md`
- [ ] **9.4** Write `foundations/etl/silver/epa_sld_silver.R` — aggregate block groups → tract and county/CBSA grain using population-weighted means where appropriate; produce `silver.epa_sld` with `transit_access_score`, `intersection_density`, `land_use_mix`, `walkability_index`, `employment_density` and companions
- [ ] **9.5** Write Silver YAML + Markdown: `layers/silver/silver__epa_sld.yml` + `.md`
- [ ] **9.6** Update `gold/gold_transport_built_form_wide.sql` to add SLD indicators alongside existing ACS commute columns; the Gold table is already the home for this topic
- [ ] **9.7** Update Gold data dictionary `layers/gold/gold__transport_built_form_wide.yml` + `.md` for SLD columns
- [ ] **9.8** Add EPA SLD row to `source_topic_checklist.md` (Ingested)
- [ ] **9.9** Add EPA SLD to `create_DB.R` / `pipeline_manifest.yml`

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

Three ACS tables not yet in the pipeline: B28002 (broadband subscription), B18101 (disability by age/sex), B16001 (language spoken at home). All three follow the established ACS silver pattern and can be added incrementally to existing silver scripts or as a new combined `acs_social_context` step. They feed into `gold.population_demographics` or a new Quality of Life gold extension.

- [ ] **11.1** Research & spec: confirm current ACS variable IDs for B28002, B18101, B16001; decide whether these extend `acs_social_infra_silver.R` or live in a new script; document decision
- [ ] **11.2** Extend or write the appropriate staging `get_acs_*.R` script to pull the three new table sets across the standard geo grains (tract → US)
- [ ] **11.3** Extend or write the silver script to produce `social_infra_base`/`social_infra_kpi` additions or new `silver.social_context_base` / `silver.social_context_kpi`
- [ ] **11.4** Update or write Silver YAML + Markdown for affected tables
- [ ] **11.5** Decide which Gold table receives these fields (`gold.population_demographics` extension vs. new `gold.quality_of_life_wide`); document decision
- [ ] **11.6** Update the appropriate Gold SQL and data dictionary
- [ ] **11.7** Add ACS broadband/disability/language to `source_topic_checklist.md` (Ingested)
- [ ] **11.8** Update `pipeline_manifest.yml` with any new steps

---

## Track 12 — CBP + BFS (Business Formation)

**Priority: Medium — run together, both straightforward Census downloads**

County Business Patterns (CBP) provides establishment count, employment, and payroll by NAICS at county grain. Business Formation Statistics (BFS) provides new business applications and startup activity at county/state grain. Both are Census products with no API key required, and both extend the Economics topic alongside BLS QCEW.

- [ ] **12.1** Research & spec: confirm CBP annual ZIP download URL and column layout; confirm BFS CSV download URL; document NAICS crosswalk approach for CBP → industry rollup families consistent with QCEW; write `foundations/data_dictionary/sources/source__cbp.md` and `source__bfs.md`; update `SOURCES.md`
- [ ] **12.2** Write `foundations/etl/staging/get_cbp.R` — download CBP county annual ZIP, parse to `staging.cbp_county`; retain NAICS code, establishment size classes, employment, payroll
- [ ] **12.3** Write `foundations/etl/staging/get_bfs.R` — download BFS county/state CSV, parse to `staging.bfs`; retain application type, NAICS sector, year
- [ ] **12.4** Write staging contracts: `layers/staging/staging__cbp.md`, `staging__bfs.md`
- [ ] **12.5** Write `foundations/etl/silver/cbp_silver.R` — standardize to county/CBSA grain, curate NAICS rollup to major sectors consistent with QCEW families; produce `silver.cbp`
- [ ] **12.6** Write `foundations/etl/silver/bfs_silver.R` — standardize to county/CBSA grain, produce `silver.bfs` with `total_applications`, `high_propensity_applications`, `business_formation_rate`
- [ ] **12.7** Write Silver YAML + Markdown: `silver__cbp.yml` + `.md`, `silver__bfs.yml` + `.md`
- [ ] **12.8** Update `gold/gold_economy_industry.sql` (or write `gold_economy_business_wide.sql`) to add CBP establishment density and BFS formation rate columns; document Gold placement decision
- [ ] **12.9** Update Gold data dictionary for new columns
- [ ] **12.10** Add CBP and BFS rows to `source_topic_checklist.md` (Ingested)
- [ ] **12.11** Add CBP and BFS to `pipeline_manifest.yml`

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

## Track 14 — JEC Social Capital Index

**Priority: Low — add later, low complexity, strong editorial angle**

The Joint Economic Committee Social Capital Project publishes a county-level index covering civic engagement, social trust, family structure, and associational density. Single CSV download, county grain, no API required. Extends the Quality of Life topic.

- [ ] **14.1** Research & spec: confirm JEC Social Capital CSV download URL and column layout; verify county FIPS identifier; document the four sub-index dimensions in `foundations/data_dictionary/sources/source__jec_social_capital.md`; update `SOURCES.md`
- [ ] **14.2** Write `foundations/etl/staging/get_jec_social_capital.R` — download CSV, parse to `staging.jec_social_capital`
- [ ] **14.3** Write staging contract: `layers/staging/staging__jec_social_capital.md`
- [ ] **14.4** Write `foundations/etl/silver/jec_social_capital_silver.R` — standardize county FIPS, derive CBSA rollup rows (population-weighted), produce `silver.jec_social_capital` with `social_capital_index`, `family_unity_index`, `community_health_index`, `institutional_health_index`, `collective_efficacy_index`
- [ ] **14.5** Write Silver YAML + Markdown: `layers/silver/silver__jec_social_capital.yml` + `.md`
- [ ] **14.6** Decide Gold placement: extend `gold.health_wide` (given civic/social scope) or new `gold.quality_of_life_wide`; document decision
- [ ] **14.7** Update or write the appropriate Gold SQL and data dictionary
- [ ] **14.8** Add JEC Social Capital row to `source_topic_checklist.md` (Ingested)
- [ ] **14.9** Add JEC to `pipeline_manifest.yml`

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

## Track 18 — Final Integration and Documentation Sync

These tasks close out the plan after all tracks above are complete.

- [ ] **18.1** Update `source_topic_checklist.md` — verify all status fields are accurate; move any remaining Planned rows with evidence of partial work to Partial
- [ ] **18.2** Update `foundations/data_dictionary/sources/checklist.md` — add new source entries for all tracks: FHFA, CHR, OZ, EPA AQI, EPA EJScreen, EPA SLD, FEMA NRI, IPEDS, ACS expansions, CBP, BFS, HMDA, JEC Social Capital, NCES CCD, HIFLD, IMLS, USDA farmers markets, Overture, OSM, Transitland
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
4. **Tracks 6–7** (EPA EJScreen/AQI, FEMA NRI) — Climate & Environmental Risk; run in parallel, both feed `gold.environment_wide`
5. **Track 9** (EPA Smart Location Database) — Transportation; extends `gold.transport_built_form_wide`
6. **Track 10** (IPEDS) — Postsecondary education; can run in parallel with 6–9
7. **Track 11** (ACS broadband/disability/language) — next ACS ingestion cycle; extends existing silver scripts
8. **Tracks 12–13** (CBP/BFS, HMDA) — Economics and Housing extensions; run in parallel
9. **Track 14** (JEC Social Capital) — Quality of Life; lowest priority among Places tracks, run last
10. **Track 8** (FBI UCR) — Skipped

**Points/Parcels/Polygons layer (after Stoop migration):**
11. **Track 15** (NCES CCD) — Depends on Track 16 schema decisions; national-once, can proceed once schema is finalized
12. **Track 16** (Points layer schema + national-once sources: IPEDS points, HIFLD, IMLS, USDA) — blocks Track 17; do not start until Stoop migration is complete
13. **Track 17** (per-market framework: Overture, OSM, Transitland, parks, neighborhood boundaries) — depends on Track 16 and first deep-dive market selection

**Close-out:**
14. **Track 18** (integration sync) — after all source tracks complete
