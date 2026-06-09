# Source Spec: EPA (AQI + EJScreen)

## 1. Overview

- Source: U.S. Environmental Protection Agency
- Program families in scope: AirData / AQS annual AQI summaries and EJScreen environmental justice indicators
- Access pattern: public flat-file downloads — no API key required for the AQI bulk files; EJScreen now behaves like an archival snapshot source rather than a stable live EPA feed
- Primary dependency: EPA AirData annual ZIP files for county and CBSA AQI, plus an archived EJScreen snapshot if we decide to ingest block-group indicators later
- Scope in Foundations: EPA is the primary direct source for environmental quality metrics in the proposed Climate & Environmental Risk topic. The first-pass implementation should start with annual AQI because EPA publishes county and CBSA summaries directly. EJScreen remains the fuller long-term source for block-group pollution-burden and proximity indicators, but public EPA access was discontinued on February 5, 2025, so ingestion should be treated as archive-based and lower-confidence operationally.
- Documentation goal: this file is the provider-level spec for how Foundations should ingest EPA environmental data now, with AQI as the active path and EJScreen as a documented archival follow-on.

---

## 2. Coverage Matrix

| Topic group | Staging family contract | Silver outputs |
| --- | --- | --- |
| AQI — county annual summary | planned: `../layers/staging/staging__epa_aqi.md` | planned: `silver.epa_aqi` |
| AQI — CBSA annual summary | planned: `../layers/staging/staging__epa_aqi.md` | planned: `silver.epa_aqi` |
| EJScreen — block group and tract environmental indicators | planned: `../layers/staging/staging__ejscreen.md` | planned: `silver.ejscreen` |

AQI is the approved first implementation because EPA publishes county and CBSA files directly at the grain we already use in Gold. EJScreen is a second-phase archival ingest that adds tract- and county/CBSA-aggregated pollution-burden context.

---

## 3. Source Contract

- Provider: U.S. Environmental Protection Agency
- Primary AQI portal: `https://aqs.epa.gov/aqsweb/airdata/download_files.html`
- Retrieval interface: direct ZIP download, no authentication required
- AQI refresh cadence: EPA states these pre-generated AirData files are updated twice per year — once in June for the complete prior calendar year and once in December for summer-season refreshes
- Common time pattern: one annual summary file per year
- Common geography pattern:
  - county AQI: native county rows, but identified by `State` + `County` name strings rather than county FIPS
  - CBSA AQI: native CBSA rows identified by `CBSA` name and `CBSA Code`
  - EJScreen archive: both census block group and census tract CSVs are available in the Harvard Dataverse snapshot; tract is the preferred first-pass ingest for Foundations, with block group reserved for later finer-grain use if needed

**AQI files verified for 2025**

| File | Geography | Notes |
| --- | --- | --- |
| `annual_aqi_by_county_2025.zip` | County | One CSV inside the ZIP: `annual_aqi_by_county_2025.csv` |
| `annual_aqi_by_cbsa_2025.zip` | CBSA | One CSV inside the ZIP: `annual_aqi_by_cbsa_2025.csv` |

**AQI county header verified from the 2025 file**

| Column | Description |
| --- | --- |
| `State` | State name |
| `County` | County or county-equivalent display name |
| `Year` | Calendar year |
| `Days with AQI` | Number of days with AQI observations |
| `Good Days` | Days in AQI good category |
| `Moderate Days` | Days in AQI moderate category |
| `Unhealthy for Sensitive Groups Days` | AQI category count |
| `Unhealthy Days` | AQI category count |
| `Very Unhealthy Days` | AQI category count |
| `Hazardous Days` | AQI category count |
| `Max AQI` | Annual max AQI |
| `90th Percentile AQI` | Annual 90th percentile AQI |
| `Median AQI` | Annual median AQI |
| `Days CO` | Days where CO drove AQI |
| `Days NO2` | Days where NO2 drove AQI |
| `Days Ozone` | Days where ozone drove AQI |
| `Days PM2.5` | Days where PM2.5 drove AQI |
| `Days PM10` | Days where PM10 drove AQI |

**AQI CBSA header verified from the 2025 file**

The CBSA file uses the same metric columns as the county file, but replaces `State` and `County` with:

| Column | Description |
| --- | --- |
| `CBSA` | CBSA display name |
| `CBSA Code` | 5-digit CBSA code |

**EJScreen archival status**

- EPA public access to EJScreen was discontinued on February 5, 2025.
- A reconstructed public instance currently exists at `https://screening-tools.com/epa-ejscreen`.
- That site links to an underlying Harvard Dataverse archive for EPA EJScreen data and to EPA technical documentation for version `2.3`.
- Because the official EPA delivery path is no longer stable, Foundations should treat EJScreen as a pinned snapshot source once downloaded rather than as a routinely refreshed EPA endpoint.

**EJScreen archive files confirmed in Harvard Dataverse**

| File | Geography | Size |
| --- | --- | --- |
| `EJSCREEN_2024_BG_with_AS_CNMI_GU_VI.csv` | Block group | ~437 MB |
| `EJSCREEN_2024_BG_StatePct_with_AS_CNMI_GU_VI.csv` | Block group + state percentiles | ~428 MB |
| `EJScreen_2024_Tract_with_AS_CNMI_GU_VI.csv` | Tract | ~153 MB |
| `EJScreen_2024_Tract_StatePct_with_AS_CNMI_GU_VI.csv` | Tract + state percentiles | ~153 MB |

The tract archive is substantially smaller and already carries the indicator fields needed for Foundations, so it should be the default ingest target unless block-group coverage is specifically required.

**EJScreen indicator scope planned for Foundations**

The architecture doc only needs a focused subset for Climate & Environmental Risk. The high-signal indicators to target when archival access is validated are:

| Indicator family | Planned fields for Foundations |
| --- | --- |
| Air pollution | `pm25`, `ozone`, `diesel_pm` |
| Hazard proximity | `superfund_proximity`, `rmp_proximity` |
| Water / waste burden | `wastewater_discharge` |
| Composite burden | `pollution_burden_score` or nearest published EJScreen composite equivalent |

Broader EJScreen environmental indicators documented in archived EPA materials also include traffic proximity, air toxics cancer risk, respiratory hazard index, lead paint, hazardous waste proximity, and other supplemental layers. Those can remain out of scope for the first Foundations ingest unless the Gold topic needs them.

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- planned: `../../etl/staging/get_epa_aqi.R`
- planned: `../../etl/staging/get_ejscreen.R`

---

## 4. Staging Shape

### AQI

Preferred first-pass staging pattern:
- one unified staging table: `staging.epa_aqi`
- retain the published EPA column names or straightforward snake_case equivalents
- retain source-native geography columns so we can audit the name-to-FIPS crosswalk rather than hiding it upstream
- include a `geo_level` column with values `county` or `cbsa`

**`staging.epa_aqi`**

| Column | Type | Description |
| --- | --- | --- |
| `geo_level` | VARCHAR | `county` or `cbsa` based on source file |
| `state_name` | VARCHAR | County file only; null for CBSA rows |
| `county_name` | VARCHAR | County file only; null for CBSA rows |
| `cbsa_name` | VARCHAR | CBSA file only; null for county rows |
| `cbsa_code` | VARCHAR | CBSA file only; native EPA code |
| `year` | INTEGER | Calendar year |
| `days_with_aqi` | INTEGER | Days with AQI observations |
| `good_days` | INTEGER | Good AQI days |
| `moderate_days` | INTEGER | Moderate AQI days |
| `usg_days` | INTEGER | Unhealthy for Sensitive Groups days |
| `unhealthy_days` | INTEGER | Unhealthy days |
| `very_unhealthy_days` | INTEGER | Very unhealthy days |
| `hazardous_days` | INTEGER | Hazardous days |
| `max_aqi` | INTEGER | Annual max AQI |
| `aqi_p90` | DOUBLE | 90th percentile AQI |
| `aqi_median` | DOUBLE | Median AQI |
| `days_co` | INTEGER | CO-driven AQI days |
| `days_no2` | INTEGER | NO2-driven AQI days |
| `days_ozone` | INTEGER | Ozone-driven AQI days |
| `days_pm25` | INTEGER | PM2.5-driven AQI days |
| `days_pm10` | INTEGER | PM10-driven AQI days |

**Preferred first-pass AQI column contract**

These are the columns we should actively carry forward in the first implementation, even if staging initially lands the fuller published file.

| Output column | Source column | Why keep it |
| --- | --- | --- |
| `geo_level` | derived | Required to unify county and CBSA rows in one staging table |
| `state_name` | `State` | Needed for county name-to-FIPS crosswalk |
| `county_name` | `County` | Needed for county name-to-FIPS crosswalk |
| `cbsa_name` | `CBSA` | Native metro display name from EPA |
| `cbsa_code` | `CBSA Code` | Native metro identifier from EPA |
| `year` | `Year` | Standard time key |
| `days_with_aqi` | `Days with AQI` | Coverage / completeness check and useful context metric |
| `good_days` | `Good Days` | Core AQI quality bucket |
| `moderate_days` | `Moderate Days` | Core AQI quality bucket |
| `usg_days` | `Unhealthy for Sensitive Groups Days` | First meaningful stress bucket below fully unhealthy conditions |
| `unhealthy_days` | `Unhealthy Days` | Core adverse-air-quality metric |
| `very_unhealthy_days` | `Very Unhealthy Days` | Severe event metric |
| `hazardous_days` | `Hazardous Days` | Extreme event metric |
| `max_aqi` | `Max AQI` | Peak annual AQI signal |
| `aqi_p90` | `90th Percentile AQI` | High-end annual AQI signal |
| `aqi_median` | `Median AQI` | Typical annual AQI signal |
| `days_ozone` | `Days Ozone` | Pollutant attribution for ozone burden |
| `days_pm25` | `Days PM2.5` | Pollutant attribution for particulate burden |

Columns such as `days_co`, `days_no2`, and `days_pm10` can stay available in raw staging if convenient, but they are not required for the first modeled contract.

### EJScreen

Preferred later staging pattern:
- one tract-first staging table: `staging.ejscreen`
- retain the tract GEOID exactly as published
- preserve both raw indicator values and, if present in the archive, percentile fields for future use
- allow a future block-group mode only if downstream use cases require finer-than-tract geography

**`staging.ejscreen`** (planned)

| Column | Type | Description |
| --- | --- | --- |
| `tract_geoid` | VARCHAR | Census tract GEOID (`ID` in the tract archive) |
| `state_fips` | VARCHAR | Two-digit state FIPS |
| `county_fips` | VARCHAR | Five-digit county FIPS |
| `year` | INTEGER | Snapshot year / EJScreen vintage |
| `pm25` | DOUBLE | PM2.5 indicator |
| `ozone` | DOUBLE | Ozone indicator |
| `diesel_pm` | DOUBLE | Diesel particulate matter indicator |
| `superfund_proximity` | DOUBLE | Superfund proximity metric |
| `rmp_proximity` | DOUBLE | Risk Management Plan facility proximity metric |
| `wastewater_discharge` | DOUBLE | Wastewater discharge metric |
| `pollution_burden_score` | DOUBLE | Published burden composite if available |
| `<indicator>_pctile_state` | DOUBLE | Optional published state percentile fields |
| `<indicator>_pctile_us` | DOUBLE | Optional published national percentile fields |

**Preferred first-pass EJScreen tract column contract**

These are the tract fields we should deliberately keep for the first Foundations implementation.

| Output column | Source column | Why keep it |
| --- | --- | --- |
| `tract_geoid` | `ID` | Canonical tract GEOID and the main geography key |
| `state_name` | `STATE_NAME` | Helpful for QA and debugging joins |
| `state_abbrev` | `ST_ABBREV` | Compact state identifier for QA and downstream joins |
| `county_name` | `CNTY_NAME` | Human-readable county reference for QA |
| `region` | `REGION` | EPA region provenance field |
| `total_population` | `ACSTOTPOP` | Weight for county / CBSA aggregation |
| `pm25` | `PM25` | Core particulate pollution measure |
| `ozone` | `OZONE` | Core ozone burden measure |
| `diesel_pm` | `DSLPM` | Core diesel particulate burden measure |
| `air_toxics_rsei` | `RSEI_AIR` | Air toxics exposure proxy |
| `traffic_proximity` | `PTRAF` | Traffic exposure / proximity measure |
| `pre1960_housing` | `PRE1960` | Lead-paint-era housing stock proxy |
| `pct_pre1960_housing` | `PRE1960PCT` | Share version of the same housing-risk signal |
| `superfund_proximity` | `PNPL` | Superfund proximity measure |
| `rmp_proximity` | `PRMP` | Risk Management Plan facility proximity measure |
| `hazardous_waste_proximity` | `PTSDF` | Treatment, storage, and disposal facility proximity |
| `underground_storage_tanks` | `UST` | Underground storage tank burden / proximity signal |
| `wastewater_discharge` | `PWDIS` | Wastewater discharge burden measure |
| `no2` | `NO2` | Nitrogen dioxide burden measure |
| `drinking_water_noncompliance` | `DWATER` | Drinking water compliance burden measure |
| `pctile_pm25_us` | `P_PM25` | National percentile form of PM2.5 |
| `pctile_ozone_us` | `P_OZONE` | National percentile form of ozone |
| `pctile_diesel_pm_us` | `P_DSLPM` | National percentile form of diesel PM |
| `pctile_rsei_air_us` | `P_RSEI_AIR` | National percentile form of air toxics burden |
| `pctile_traffic_us` | `P_PTRAF` | National percentile form of traffic proximity |
| `pctile_superfund_us` | `P_PNPL` | National percentile form of Superfund proximity |
| `pctile_rmp_us` | `P_PRMP` | National percentile form of RMP proximity |
| `pctile_hazardous_waste_us` | `P_PTSDF` | National percentile form of hazardous waste proximity |
| `pctile_ust_us` | `P_UST` | National percentile form of underground storage tank burden |
| `pctile_wastewater_us` | `P_PWDIS` | National percentile form of wastewater discharge burden |
| `pctile_no2_us` | `P_NO2` | National percentile form of NO2 burden |
| `pctile_drinking_water_us` | `P_DWATER` | National percentile form of drinking water burden |
| `count_high_exposure_indicators` | `EXCEED_COUNT_80` | Count of indicators above the 80th percentile |
| `count_high_exposure_supplemental` | `EXCEED_COUNT_80_SUP` | Count of supplemental indicators above the 80th percentile |

Fields we should leave out of the first modeled contract:
- raw demographic composition fields such as `PEOPCOLOR`, `LOWINCOME`, `UNEMPLOYED`, and their percent forms
- percentile label text fields (`T_*`)
- bucketized / integerized helper fields (`B_*`)
- `D2_*` and `D5_*` derived distance-family measures unless we decide they add distinct value beyond the main published indicators
- geometry helper columns such as `Shape_Length` and `Shape_Area`

---

## 5. Staging To Silver

EPA AQI handoff pattern:
1. Download the annual county and CBSA ZIP files for the target years.
2. Parse the single CSV inside each ZIP into `staging.epa_aqi` with `geo_level` retained.
3. For county rows, resolve `state_name + county_name` to canonical 5-digit county FIPS using the Foundations county dimension / crosswalk tables.
4. For CBSA rows, take `cbsa_code` as the canonical `geo_id` after validating it against `silver.xwalk_cbsa_county`.
5. Standardize both geography levels into `silver.epa_aqi` with grain `geo_level + geo_id + year`.
6. Feed AQI fields into `gold.environment_wide`.

EJScreen handoff pattern:
1. Download and pin an archival national tract extract for a known version.
2. Parse the raw tract fields into `staging.ejscreen`.
3. Audit tract GEOIDs against `silver.xwalk_tract_county` and `gold.dim_geo` before writing any modeled output.
4. Materialize a tract-level `silver.ejscreen` table for canonical supported geographies only, while leaving Puerto Rico and territorial archive rows in staging until the geography backbone is expanded.
5. Add county / CBSA rollups only after the tract-first Silver layer is stable and its exclusion policy is documented.
6. Join the selected indicators into `gold.environment_wide` alongside AQI and FEMA NRI once the tract-first modeled layer is approved.

**Key modeling decision:** Because EPA already publishes native CBSA AQI files, Foundations should use those direct CBSA rows rather than deriving CBSA AQI from county rows. That keeps the Silver table aligned with the source program's own metropolitan summary.

---

## 6. Transformation Notes

### County name to FIPS crosswalk

The county AQI file does not publish county FIPS. Silver will need a deterministic crosswalk from EPA county strings to canonical county GEOIDs.

Recommended approach:
- normalize `state_name` and `county_name` to uppercase ASCII
- strip punctuation and common suffix noise where needed
- join against the canonical county dimension using normalized `state_name + county_name`
- maintain a small exception map for county-equivalent naming edge cases such as:
  - `St.` vs `Saint`
  - Louisiana parishes
  - Alaska borough / census area names
  - Virginia independent cities if they ever appear in EPA county-equivalent coverage

### AQI metric selection for Silver / Gold

The county and CBSA files contain more fields than Gold needs. The first-pass modeled subset should prioritize:

| Modeled field | Source column |
| --- | --- |
| `aqi_days` | `Days with AQI` |
| `aqi_good_days` | `Good Days` |
| `aqi_moderate_days` | `Moderate Days` |
| `aqi_usg_days` | `Unhealthy for Sensitive Groups Days` |
| `aqi_unhealthy_days` | `Unhealthy Days` |
| `aqi_max` | `Max AQI` |
| `aqi_p90` | `90th Percentile AQI` |
| `aqi_median` | `Median AQI` |
| `aqi_days_ozone` | `Days Ozone` |
| `aqi_days_pm25` | `Days PM2.5` |

`Days NO2`, `Days PM10`, and `Days CO` should stay in staging and may remain in Silver if we want pollutant-specific breakouts later.

### EJScreen aggregation note

EJScreen is a small-area screening product, so county and CBSA outputs are modeled aggregates rather than source-native summaries. Because the archive exposes a tract CSV directly, Foundations can start from tract and avoid an unnecessary first-pass block-group aggregation step. The tract-first pass also gives us a clean place to audit whether archived tract IDs still resolve to the current geography backbone before we roll anything up. County and CBSA values should still be created later with documented weighting logic and clear caveats that they are aggregates of screening indicators, not direct EPA county products.

---

## 7. Data Quality Expectations

- AQI county coverage is incomplete by design: only counties with sufficient monitoring-based AQI summaries appear in a given year. The 2025 county file contains `978` rows, not all U.S. counties.
- AQI CBSA coverage is also partial: the 2025 CBSA file contains `496` rows.
- In the AQI files, category-day columns should sum to `Days with AQI`.
- Pollutant-attribution day columns are useful diagnostics but do not necessarily sum neatly to the category buckets the same way a user might expect; validate against EPA documentation before enforcing any strict additive contract beyond what the source guarantees.
- CBSA code quality should be high because EPA publishes `CBSA Code`, but name strings may still differ slightly from canonical OMB naming.
- EJScreen archival data quality should be treated cautiously until the exact snapshot artifact is pinned and profiled. Version drift, missing documentation, or archive incompleteness are realistic risks now that the official EPA distribution path is gone.
- The archived tract file includes Puerto Rico and territorial rows beyond the current canonical Foundations tract backbone. A tract-first Silver contract can still proceed if supported-state match quality is strong, but those exclusions must be explicit.

---

## 8. Operational Notes

- AQI is the stable operational path for Track 6. It is public, structured, annual, and already available at county and CBSA grain.
- EPA publishes the AirData download page with year-specific links that appear stable and predictable: `annual_aqi_by_county_<year>.zip` and `annual_aqi_by_cbsa_<year>.zip`.
- The safest first production target is the most recently complete year available each June refresh, while allowing historical backfill from earlier annual ZIP files.
- EJScreen should not block AQI delivery. If the archival path proves awkward or incomplete, proceed with AQI-only ingestion and treat EJScreen as a separate follow-up milestone.
- Once an EJScreen archive is selected, cache it immutably and record the exact version and retrieval URL in the staging script because public availability is now governed by third-party preservation rather than EPA operations.

---

## 9. Known Gaps

- The AQI county file lacks county FIPS, so county geo standardization depends on a maintained name crosswalk.
- AQI does not provide tract-level coverage and is not a substitute for the block-group burden indicators that EJScreen adds.
- We have verified the live AQI file structure directly, but we have not yet pinned and profiled a specific EJScreen archive file inside the repo workflow.
- EJScreen public continuity is uncertain because the official EPA endpoint was removed; third-party reconstruction and archive mirrors may change without notice.
- The first Foundations Gold table should be designed so AQI can ship alone, with EJScreen and FEMA columns added incrementally later.
