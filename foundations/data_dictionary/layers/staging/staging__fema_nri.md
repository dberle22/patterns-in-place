# Data Dictionary: staging FEMA National Risk Index

## Overview
- Schema: `staging`
- Family: `FEMA National Risk Index`
- Contract scope: source-family staging contract for the county and tract FEMA NRI releases produced by [`foundations/etl/staging/get_fema_nri.R`](../../../etl/staging/get_fema_nri.R)
- Documentation rule: both geography slices are covered by this one family contract because FEMA ships the same hazard matrix at parallel county and tract grains

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| County-equivalent release | `fema_nri` | One row per county-equivalent geography from `NRI_Table_Counties.csv`, including counties, parishes, municipios, boroughs, planning regions, and other county-equivalent types |
| Tract release | `fema_nri_tract` | One row per tract from `NRI_Table_CensusTracts.csv`, with county-equivalent helper fields retained alongside tract identifiers |

## Contract Summary
- This family has two geometry variants with the same overall FEMA hazard matrix.
- `staging.fema_nri` grain: one row per `stcofips`
- `staging.fema_nri_tract` grain: one row per `tractfips`
- Current initial scope: FEMA NRI release `v120` / `December 2025`
- Current landed shape:
  - `staging.fema_nri`: `3,232` rows, `467` columns
  - `staging.fema_nri_tract`: `85,154` rows, `469` columns
- Both staging tables intentionally keep the full cleaned FEMA field inventory so Silver can choose a compact analytical subset later without re-ingesting the provider files

## Shared Columns
- Source-native geography metadata:
  - `nri_id`
  - `state`
  - `stateabbrv`
  - `statefips`
  - `county`
  - `countytype`
  - `countyfips`
  - `stcofips`
- Staging helper metadata:
  - `nri_ver`
  - `nri_release_year`
  - `nri_geo_level`
- Shared exposure / composite risk columns:
  - `population`
  - `buildvalue`
  - `agrivalue`
  - `area`
  - `risk_*`
  - `eal_*`
  - `alr_*`
  - `sovi_*`
  - `resl_*`
  - `crf_value`
- Source-faithful hazard matrix:
  - all cleaned FEMA hazard prefix families (`avln_*`, `cfld_*`, `cwav_*`, `drgt_*`, `erqk_*`, `hail_*`, `hwav_*`, `hrcn_*`, `istm_*`, `ifld_*`, `lnds_*`, `ltng_*`, `swnd_*`, `trnd_*`, `tsun_*`, `vlcn_*`, `wfir_*`, `wntw_*`) are retained in staging for both geography slices

## Tract-Only Columns
- `tract`
- `tractfips`

The tract release includes these direct tract identifiers; the county-equivalent release does not include tract columns in the CSV header even though the shared FEMA data dictionary lists them.

## Lineage
- [`foundations/etl/staging/get_fema_nri.R`](../../../etl/staging/get_fema_nri.R) downloads both FEMA ZIP bundles, extracts the packaged CSV + metadata sidecars, cleans the column names, pads the published geography identifiers, validates county and tract key uniqueness, and writes `staging.fema_nri` plus `staging.fema_nri_tract`.
- The provider-level source notes and keep/drop guidance live in [`../../sources/source__fema.md`](../../sources/source__fema.md).

## Data Quality Notes
- Treat `stcofips` as the canonical county-equivalent helper key in staging. It must always be a zero-padded 5-digit code after ingest.
- Treat `tractfips` as the canonical tract helper key in tract staging. It must always be a zero-padded 11-digit tract code after ingest.
- `nri_id` is a source-native QA field rather than the canonical geography key:
  - county rows should satisfy `nri_id = C + stcofips`
  - tract rows should satisfy `nri_id = T + tractfips`
- `countytype` should be preserved exactly as published. It is descriptive metadata for county-equivalent rows, not a filter condition.
- The tract table is intentionally staged even though the first Silver model remains county-first. Tract compatibility with the current Foundations tract backbone is a Silver concern, not a staging concern.

## Known Gaps / To-Dos
- `staging.fema_nri_tract` is staged-only for now. Silver should not include tract rows until the county-first modeled contract is stable and the tract geography backbone is explicitly audited.
- The packaged `NRIDataDictionary.csv` and `NRI_HazardInfo.csv` are useful sidecars for future automated field mapping and should remain cached with the raw downloads.
