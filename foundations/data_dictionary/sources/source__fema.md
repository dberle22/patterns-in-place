# Source Spec: FEMA (National Risk Index)

## 1. Overview

- Source: Federal Emergency Management Agency
- Program family in scope: National Risk Index (NRI)
- Access pattern: public ZIP downloads from the FEMA OpenFEMA NRI release directory; no API key required
- Primary dependency: county and census-tract CSV bundles for NRI version `1.20.0` (`December 2025`)
- Scope in Foundations: full staging for both county and tract NRI releases; county-first for the initial modeled Silver implementation
- Documentation goal: define the first-pass NRI ingest path, the geography normalization rules, and the deliberately selected NRI columns to keep from the wide FEMA delivery

---

## 2. Coverage Matrix

| Topic group | Staging family contract | Silver outputs |
| --- | --- | --- |
| National Risk Index - county | planned: `../layers/staging/staging__fema_nri.md` | planned: `silver.fema_nri` |
| National Risk Index - census tract | planned: `../layers/staging/staging__fema_nri.md` | deferred after county Silver is stable |
| FEMA flood products / declarations | out of scope for this source spec | tracked separately |

The first implementation should stage both NRI geographies because FEMA packages the county and tract releases in parallel and the tract file is useful to preserve once downloaded. Silver should still start with county NRI because it lands directly at a Gold-friendly geography and already carries the composite and hazard-specific risk signals we need for `gold.environment_wide`.

---

## 3. Source Contract

- Provider: Federal Emergency Management Agency
- Landing page: `https://www.fema.gov/about/openfema/data-sets/national-risk-index-data`
- Verified county ZIP: `https://www.fema.gov/about/reports-and-data/openfema/nri/v120/NRI_Table_Counties.zip`
- Verified tract ZIP: `https://www.fema.gov/about/reports-and-data/openfema/nri/v120/NRI_Table_CensusTracts.zip`
- Retrieval interface: direct ZIP download, no authentication required
- Verified package contents in both ZIPs:
  - main CSV (`NRI_Table_Counties.csv` or `NRI_Table_CensusTracts.csv`)
  - `NRIDataDictionary.csv`
  - `NRI_HazardInfo.csv`
  - `NRI_metadata_December2025.pdf`
- Version observed in the verified data dictionary: `1.20.0`
- Version date observed in the verified data dictionary: `December 2025`

**Observed geography keys**

| Field | County file behavior | Tract file behavior | Foundations handling |
| --- | --- | --- | --- |
| `NRI_ID` | `C` + county GEOID, e.g. `C01001` | `T` + tract GEOID, e.g. `T01001020100` | Keep as source-native ID for QA only, not canonical `geo_id` |
| `COUNTYFIPS` | 3-digit county code within state | same | Keep for QA; not sufficient alone as canonical county key |
| `STCOFIPS` | county GEOID, but must be treated as zero-padded text | repeated on tract rows | Canonical county join key after `str_pad(..., 5, "left", "0")` |
| `TRACTFIPS` | not present in the county CSV header even though the shared data dictionary lists it | 11-digit tract GEOID | Canonical tract join key later if tract modeling is added |
| `STATEFIPS` | 2-digit state FIPS | same | Useful QA field only |

The key data-quality rule for staging is to cast geography identifiers as character immediately and preserve leading zeros. `STCOFIPS` is the county backbone field we should rely on, not `NRI_ID`.

**Observed county-equivalent coverage in the county file**

The verified county ZIP contains `3,232` rows and is not limited to rows where `COUNTYTYPE = County`. FEMA is using a county-equivalent layer:

| `COUNTYTYPE` | Rows | Notes |
| --- | --- | --- |
| `County` | 2,999 | Standard county rows |
| `Municipio` | 78 | Puerto Rico county-equivalents |
| `Parish` | 64 | Louisiana county-equivalents |
| `City` | 41 | Independent cities in states such as Virginia, Maryland, Missouri, and Nevada |
| `Borough` | 13 | Alaska county-equivalents |
| `Census Area` | 11 | Alaska county-equivalents |
| `Planning Region` | 9 | Connecticut county-equivalent planning regions |
| `Municipality` | 5 | Alaska / Northern Mariana Islands county-equivalents |
| `City and Borough` | 4 | Alaska county-equivalents |
| `District` | 3 | American Samoa county-equivalents |
| `Island` | 3 | U.S. Virgin Islands county-equivalents |
| blank | 2 | District of Columbia and Guam |

This is still a single county-equivalent geography grain. The staging layer should keep all rows and preserve `COUNTYTYPE` as a descriptive field rather than filtering to literal counties. Any decision to exclude territories or unsupported county-equivalents should happen later in Silver, where we can compare FEMA coverage against the current Foundations geography backbone.

**Hazard inventory verified from `NRI_HazardInfo.csv`**

The current FEMA release ships 18 hazard families with stable prefixes:

`AVLN` avalanche, `CFLD` coastal flooding, `CWAV` cold wave, `DRGT` drought, `ERQK` earthquake, `HAIL` hail, `HWAV` heat wave, `HRCN` hurricane, `ISTM` ice storm, `IFLD` inland flooding, `LNDS` landslide, `LTNG` lightning, `SWND` strong wind, `TRND` tornado, `TSUN` tsunami, `VLCN` volcanic activity, `WFIR` wildfire, `WNTW` winter weather.

Each hazard family repeats a wide set of component fields. For Foundations we do not need the entire exposure/loss decomposition in the first pass.

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- planned: `../../etl/staging/get_fema_nri.R`

---

## 4. Column Selection Approach

FEMA publishes more than 470 columns in the county and tract CSVs. That width is exactly why Foundations should separate the staging decision from the Silver decision.

The approved first-pass approach is:

1. Land the full county CSV in staging, source-faithfully, including the full hazard matrix.
2. Keep the county-equivalent geography fields exactly as FEMA publishes them.
3. Use Silver, not staging, to decide which hazard and composite fields are worth carrying into the modeled layer.
4. Stage the tract CSV too, but keep it out of the first modeled Silver build until the county contract is settled.

This gives us a future-proof raw landing without committing the full raw width to downstream modeled tables.

---

## 5. Preferred First-Pass Staging Contract

Recommended first-pass table:
- `staging.fema_nri`
- county rows only in the initial implementation
- source-faithful names retained with straightforward `janitor::clean_names()` normalization
- one row per county NRI record
- keep county-equivalents exactly as published; do not pre-filter `COUNTYTYPE`
- keep the full published county field inventory, not just the compact risk subset

The point of the staging table is to preserve the full county NRI release so we do not have to re-ingest FEMA later if we decide a currently-unused hazard component matters.

Companion tract staging table:
- `staging.fema_nri_tract`
- tract rows only
- same source-faithful column treatment as the county table
- one row per tract NRI record
- preserve the full tract hazard matrix, including the tract and county helper keys FEMA publishes

The tract table should be staged now for completeness, but it remains a staged-only asset until we explicitly decide how it fits the current tract backbone and downstream modeled contract.

**Core geography and backbone fields to validate explicitly**

| Output column | Source column | Why keep it |
| --- | --- | --- |
| `nri_id` | `NRI_ID` | Source-native identifier for QA and source traceability |
| `state_name` | `STATE` | Human-readable QA field |
| `state_abbrev` | `STATEABBRV` | Compact state QA field |
| `state_fips` | `STATEFIPS` | QA and debugging field |
| `county_name` | `COUNTY` | Human-readable county name |
| `county_type` | `COUNTYTYPE` | Distinguishes county-equivalent types |
| `county_fips_3` | `COUNTYFIPS` | Source-native county code within state |
| `stcofips` | `STCOFIPS` | Canonical county backbone after zero-padding to 5 digits |
| `population` | `POPULATION` | Weight for future county-to-CBSA rollups |
| `buildvalue` | `BUILDVALUE` | Exposure context for interpreting losses |
| `agrivalue` | `AGRIVALUE` | Agriculture exposure context |
| `area_sqmi` | `AREA` | Optional density/context denominator |
| `nri_version` | `NRI_VER` | Release provenance |

**Composite metrics that Silver is expected to use first**

| Output column | Source column | Why keep it |
| --- | --- | --- |
| `risk_value` | `RISK_VALUE` | FEMA composite risk value output |
| `risk_score` | `RISK_SCORE` | Main county risk ranking measure |
| `risk_rating` | `RISK_RATNG` | Human-readable FEMA bucket |
| `risk_state_pctile` | `RISK_SPCTL` | Within-state context for county comparisons |
| `eal_score` | `EAL_SCORE` | Main expected annual loss score |
| `eal_rating` | `EAL_RATNG` | Human-readable FEMA bucket |
| `eal_state_pctile` | `EAL_SPCTL` | Within-state loss context |
| `eal_value_total` | `EAL_VALT` | Expected annual loss total dollars / equivalence |
| `eal_value_building` | `EAL_VALB` | Building-loss component |
| `eal_value_population` | `EAL_VALP` | Population-loss component |
| `eal_value_population_equiv` | `EAL_VALPE` | FEMA population-equivalence component |
| `eal_value_agriculture` | `EAL_VALA` | Agriculture-loss component |
| `alr_value_building` | `ALR_VALB` | Building expected annual loss rate |
| `alr_value_population` | `ALR_VALP` | Population expected annual loss rate |
| `alr_value_agriculture` | `ALR_VALA` | Agriculture expected annual loss rate |
| `alr_national_pctile` | `ALR_NPCTL` | Cross-county normalized loss-rate context |
| `alr_vra_national_pctile` | `ALR_VRA_NPCTL` | FEMA adjusted loss-rate percentile that already incorporates vulnerability / resilience |
| `social_vulnerability_score` | `SOVI_SCORE` | Vulnerability lens needed for editorial interpretation |
| `social_vulnerability_rating` | `SOVI_RATNG` | Human-readable vulnerability bucket |
| `social_vulnerability_state_pctile` | `SOVI_SPCTL` | Within-state vulnerability context |
| `community_resilience_score` | `RESL_SCORE` | Resilience lens needed for editorial interpretation |
| `community_resilience_rating` | `RESL_RATNG` | Human-readable resilience bucket |
| `community_resilience_state_pctile` | `RESL_SPCTL` | Within-state resilience context |
| `community_resilience_value` | `RESL_VALUE` | Underlying FEMA resilience value |
| `community_risk_factor_value` | `CRF_VALUE` | Additional FEMA context used in the NRI framework |

**Hazard family interpretation**

For each verified hazard prefix (`AVLN`, `CFLD`, `CWAV`, `DRGT`, `ERQK`, `HAIL`, `HWAV`, `HRCN`, `ISTM`, `IFLD`, `LNDS`, `LTNG`, `SWND`, `TRND`, `TSUN`, `VLCN`, `WFIR`, `WNTW`), FEMA repeats a larger family of related fields. The common suffix groups mean:

| Output suffix | Source suffix | Why keep it |
| --- | --- | --- |
| `_events` | `_EVNTS` | Event count context where FEMA publishes it |
| `_annualized_frequency` | `_AFREQ` | Frequency / probability signal |
| `_exp_*` | `_EXP_AREA`, `_EXPB`, `_EXPP`, `_EXPPE`, `_EXPA`, `_EXPT` | Exposure measures for area, building value, population, population-equivalent, agriculture, and total exposed value |
| `_hlr_*` | `_HLRB`, `_HLRP`, `_HLRA`, `_HLRR` | Historic loss ratio components and rating |
| `_eal_*` | `_EALB`, `_EALP`, `_EALPE`, `_EALA`, `_EALT`, `_EALS`, `_EALR` | Expected annual loss components, score, and rating |
| `_alr_*` | `_ALRB`, `_ALRP`, `_ALRA`, `_ALR_NPCTL` | Annualized loss-rate components and national percentile |
| `_risk_*` | `_RISKV`, `_RISKS`, `_RISKR` | FEMA hazard risk value, score, and rating |

Example mapped columns:
- `hurricane_risk_score` <- `HRCN_RISKS`
- `wildfire_risk_score` <- `WFIR_RISKS`
- `coastal_flooding_expected_annual_loss_score` <- `CFLD_EALS`
- `tornado_annualized_frequency` <- `TRND_AFREQ`

Staging should keep all of these source-native hazard columns for the county file. Silver should then prune to the compact subset that is most useful downstream.

---

## 6. Preferred Silver Contract

Preferred first-pass Silver output:
- `silver.fema_nri`
- county plus derived CBSA rows
- one row per `geo_level + geo_id + year`

Recommended Silver columns:

| Silver column | Source basis | Notes |
| --- | --- | --- |
| `geo_level` | derived | `county` in direct rows; `cbsa` in rollups |
| `geo_id` | padded `STCOFIPS` or derived CBSA code | Canonical Foundations geography key |
| `geo_name` | county name or derived CBSA name | Standard display field |
| `year` | release year from `NRI_VER` package date | First-pass use `2025` for version `December 2025` |
| `risk_score` | `RISK_SCORE` | Core composite risk metric |
| `eal_score` | `EAL_SCORE` | Core composite expected annual loss metric |
| `alr_national_pctile` | `ALR_NPCTL` | Comparable loss-rate metric |
| `alr_vra_national_pctile` | `ALR_VRA_NPCTL` | FEMA adjusted risk context |
| `social_vulnerability_score` | `SOVI_SCORE` | Vulnerability context |
| `community_resilience_score` | `RESL_SCORE` | Resilience context |
| `<hazard>_risk_score` | `<PREFIX>_RISKS` | Keep for all 18 hazards |
| `<hazard>_expected_annual_loss_score` | `<PREFIX>_EALS` | Keep for all 18 hazards |
| `<hazard>_annualized_frequency` | `<PREFIX>_AFREQ` | Keep for all 18 hazards |
| optional: `<hazard>_expected_annual_loss_rate_pctile` | `<PREFIX>_ALR_NPCTL` | Keep if we want normalized hazard-level context beyond the raw score family |

County-to-CBSA rollups should use population-weighted averages for score-like fields unless the FEMA metadata or downstream QA suggests a better aggregation rule. If FEMA composite values prove non-additive in a way that makes weighting misleading, we should pause and document a county-only first pass rather than silently force a CBSA summary.

---

## 7. Tract Follow-On Decision

The tract ZIP is now part of the recommended staging scope and mirrors the county schema closely enough to reuse the same field-selection logic. It should still remain out of the first modeled build because:

- the tract CSV is much larger (~634 MB compressed)
- the county track already unlocks the planned Gold environment mart
- we should validate the county metric choices before carrying the same wide hazard family to tract scale
- tract staging will need an explicit compatibility audit against the current Foundations tract backbone before any modeled table is built

When tract is added later, `TRACTFIPS` should become the canonical tract key and `STCOFIPS` should remain the county rollup key.

---

## 8. Gold Placement

FEMA NRI should extend `gold.environment_wide` alongside EPA AQI. The first Gold pass should focus on:

- `risk_score`
- `eal_score`
- `social_vulnerability_score`
- `community_resilience_score`
- the highest-signal hazard-specific scores, starting with all 18 `<hazard>_risk_score` fields unless width pressure forces a narrower editorial subset

This keeps the Gold table aligned with the architecture doc's Climate & Environmental Risk topic while preserving a clean upgrade path to tract NRI, EJScreen, and later NOAA additions.

---

## 9. Implementation Notes

- Cast all FEMA geography identifiers to character immediately on read.
- Zero-pad `STCOFIPS` to 5 digits before any county join.
- Treat `NRI_ID` as a source QA field, not the canonical geography key.
- Keep the county and tract downloads version-locked to the same FEMA release when both are used.
- Validate one row per padded `STCOFIPS` in county staging.
- Validate the current county release against the observed `COUNTYTYPE` distribution so future FEMA vintages do not silently change the geography mix.
- Retain the packaged `NRIDataDictionary.csv` and `NRI_HazardInfo.csv` in raw storage or sidecar QA assets if practical; they are useful for future automated field mapping.
