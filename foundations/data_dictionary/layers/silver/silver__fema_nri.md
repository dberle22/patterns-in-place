# Data Dictionary: silver.fema_nri

## Overview
- **Table**: `silver.fema_nri`
- **Purpose**: Standardized FEMA National Risk Index table at county-equivalent and derived CBSA grain for the compact analytical climate-and-hazard risk contract.
- **Row count**: 4,167
- **Time coverage**: 2025 only

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
- **Observed geo coverage**:
  - `county`: 3,232 rows
  - `cbsa`: 935 rows
- **Key QA**: live duplicate check on `geo_level + geo_id + year` returned zero duplicates.

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **Composite FEMA metrics**: `risk_score`, `eal_score`, `alr_national_pctile`, `alr_vra_national_pctile`, `social_vulnerability_score`, `community_resilience_score`
- **Hazard risk scores**: one `*_risk_score` column for each FEMA hazard family
- **Hazard expected annual loss scores**: one `*_expected_annual_loss_score` column for each FEMA hazard family
- **Hazard annualized frequencies**: one `*_annualized_frequency` column for each FEMA hazard family

## Data Quality Notes
- County rows preserve FEMA's county-equivalent release rather than filtering to literal `County` records.
  - Parishes, municipios, boroughs, planning regions, census areas, and other county-equivalent designations stay in the Silver contract.
- County `geo_id` uses staged `stcofips` after zero-padding and validation in staging.
  - `nri_id` remains a source-native QA field rather than the canonical geography key.
- County display names come from `silver.xwalk_county_state` where possible and fall back to FEMA `county + countytype` naming when the crosswalk does not supply a normalized long name.
- CBSA rows are derived from county-equivalent staging rows using `silver.xwalk_cbsa_county`.
  - The first-pass rollup uses staged `population` as the weight for all promoted FEMA score and frequency fields.
- This Silver table intentionally keeps a compact analytical subset rather than the full FEMA hazard matrix.
  - The much wider exposure, loss-component, and raw helper fields remain in staging only.
- The tract FEMA release is staged in `staging.fema_nri_tract` but is not yet promoted into Silver.

## Hazard Prefix Reference
- `avalanche` = `AVLN`
- `coastal_flooding` = `CFLD`
- `cold_wave` = `CWAV`
- `drought` = `DRGT`
- `earthquake` = `ERQK`
- `hail` = `HAIL`
- `heat_wave` = `HWAV`
- `hurricane` = `HRCN`
- `ice_storm` = `ISTM`
- `inland_flooding` = `IFLD`
- `landslide` = `LNDS`
- `lightning` = `LTNG`
- `strong_wind` = `SWND`
- `tornado` = `TRND`
- `tsunami` = `TSUN`
- `volcanic_activity` = `VLCN`
- `wildfire` = `WFIR`
- `winter_weather` = `WNTW`

## Lineage
1. `foundations/etl/staging/get_fema_nri.R` downloads the FEMA county-equivalent and tract NRI ZIP bundles, preserves the full source-faithful hazard matrices in staging, pads and validates the helper geography keys, and writes `staging.fema_nri` plus `staging.fema_nri_tract`.
2. `foundations/etl/silver/fema_nri_silver.R` keeps the county-equivalent FEMA release at county grain, assigns canonical display names where possible, selects the approved composite and hazard metrics, derives CBSA rows with population-weighted averages, and writes `silver.fema_nri`.

## Known Gaps / To-Dos
- Tract rows are staged but intentionally deferred from the Silver contract until we explicitly decide how they should interact with the current tract backbone and downstream environment marts.
- FEMA is currently a single-release `2025` surface rather than a longitudinal historical series, so downstream joins only populate for `year = 2025`.
- The first-pass CBSA rollup uses population-weighted means for all promoted FEMA fields. If we later decide some hazard metrics should aggregate differently, that should be introduced as a documented method change rather than silently replacing the current contract.
