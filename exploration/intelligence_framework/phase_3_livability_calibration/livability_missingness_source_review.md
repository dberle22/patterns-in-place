# Livability Missingness Source Review

This note audits every Livability Phase 3 KPI that still has missing CBSA values in the `401`-CBSA universe. The goal is to separate:

1. source-native coverage limits
2. rollup / geography-contract issues
3. cases where median imputation is probably fine versus cases we may want to fix upstream first

Reference artifacts:

- KPI frame: [livability_phase3_kpi_frame.parquet](outputs/livability_phase3_kpi_frame.parquet)
- completeness table: [livability_phase3_metric_completeness.csv](outputs/livability_phase3_metric_completeness.csv)
- missing-CBSA long file: [livability_phase3_missing_cbsas_long.csv](outputs/livability_phase3_missing_cbsas_long.csv)

## Summary

| KPI family | KPIs with missingness | Source | CBSA method | Main missingness pattern |
| --- | --- | --- | --- | --- |
| CHR health | `premature_death_rate`, `preventable_hospital_stay_rate`, `drug_overdose_death_rate`, `firearm_fatality_rate`, `mental_health_provider_ratio`, `motor_vehicle_crash_rate`, `pct_uninsured_adults` | County Health Rankings analytic county panel | County-to-CBSA population-weighted rollup | Puerto Rico missing entirely; two CT metrics null inside otherwise present CT CBSA rows |
| USDA Food Access | `pct_population_low_income_low_access_1_10` | USDA Food Access Research Atlas tract table (`2019`) | Tract -> county via tract prefix -> CBSA via county crosswalk | PR absent; CT CBSA rollup appears blocked by legacy-vs-current county GEOID mismatch |
| EPA Smart Location Database | `walkability_index`, `jobs_access_45min_transit` | EPA SLD block-group table (`2021`) | Block group -> county weighted aggregation -> CBSA via county crosswalk | Only CT metros missing; county rows exist, but CBSA rollup is absent |
| ACS transport built form | `pop_weighted_density_sqmi` | recurring ACS transport mart with tract-derived density | promoted in Gold from tract-derived density support | PR-only missing; aligns with tract geometry support gap |
| EPA AQI | `aqi_unhealthy_days` | source-published annual CBSA AQI file | source-native CBSA rows | partial monitor coverage, mostly smaller metros across many states |
| FEMA NRI joined into Gold environment | `fema_risk_score` | FEMA county-equivalent NRI, joined onto AQI backbone in Gold | county-equivalent -> CBSA weighted mean in Silver, then AQI-backed Gold join | all AQI gaps inherited, plus 12 extra AQI/FEMA intersection gaps |

## 1. CHR Health Metrics

Affected KPIs:

- `premature_death_rate`
- `preventable_hospital_stay_rate`
- `drug_overdose_death_rate`
- `firearm_fatality_rate`
- `mental_health_provider_ratio`
- `motor_vehicle_crash_rate`
- `pct_uninsured_adults`

Source and lineage:

- source doc: [source__chr.md](../../../foundations/data_dictionary/sources/source__chr.md)
- silver table doc: [silver__chr_health_outcomes.md](../../../foundations/data_dictionary/layers/silver/silver__chr_health_outcomes.md)
- silver build: [chr_silver.R](../../../foundations/etl/silver/chr_silver.R)
- gold table doc: [gold__health_wide.md](../../../foundations/data_dictionary/layers/gold/gold__health_wide.md)

CBSA method:

- CHR is county-native, not CBSA-native.
- Silver builds `silver.chr_health_outcomes` from the curated county panel in `staging.chr_health_rankings_history`.
- CBSA rows are derived by joining counties to `silver.xwalk_cbsa_county`.
- Most KPIs use total ACS population weights from `silver.age_kpi`.
- Only `reading_score_index` and `math_score_index` switch to school-age weights.

Relevant code:

- county standardization: [chr_silver.R](../../../foundations/etl/silver/chr_silver.R)
- CBSA rollup: [chr_silver.R](../../../foundations/etl/silver/chr_silver.R)

Observed missingness patterns:

- `5` Puerto Rico CBSAs are missing the whole PR-sensitive cluster:
  - `10380` Aguadilla, PR
  - `11640` Arecibo, PR
  - `32420` Mayagüez, PR
  - `38660` Ponce, PR
  - `41980` San Juan-Bayamón-Caguas, PR
- Those same `5` metros are missing:
  - `drug_overdose_death_rate`
  - `firearm_fatality_rate`
  - `mental_health_provider_ratio`
  - `motor_vehicle_crash_rate`
  - `pct_uninsured_adults`
- Silver currently has `0` Puerto Rico county geographies in `silver.chr_health_outcomes`, so this is a source-coverage / staging-contract issue rather than a CBSA aggregation issue.
- `premature_death_rate` and `preventable_hospital_stay_rate` are missing for `11` CBSAs:
  - the `5` Puerto Rico metros above
  - plus `6` Connecticut metros:
    - `14860` Bridgeport-Stamford-Danbury, CT
    - `25540` Hartford-West Hartford-East Hartford, CT
    - `35300` New Haven, CT
    - `35980` Norwich-New London-Willimantic, CT
    - `45860` Torrington, CT
    - `47930` Waterbury-Shelton, CT
- Important nuance: those `6` Connecticut CBSA rows do exist in `silver.chr_health_outcomes`, and other CHR KPIs like `drug_overdose_death_rate` are populated there. So this is not a missing-CBSA-row problem for CT; it is metric-specific nulls inside otherwise valid CHR CBSA rows.

Interpretation:

- Puerto Rico should be treated as an upstream coverage gap for CHR in the current build.
- Connecticut looks like a narrower metric-level source null pattern for specific CHR measures, not a geography join failure.

## 2. USDA Food Access

Affected KPI:

- `pct_population_low_income_low_access_1_10`

Source and lineage:

- source doc: [source__usda_food_atlas.md](../../../foundations/data_dictionary/sources/source__usda_food_atlas.md)
- silver table doc: [silver__usda_food_atlas.md](../../../foundations/data_dictionary/layers/silver/silver__usda_food_atlas.md)
- silver build: [usda_food_atlas_silver.R](../../../foundations/etl/silver/usda_food_atlas_silver.R)
- gold table doc: [gold__food_access_wide.md](../../../foundations/data_dictionary/layers/gold/gold__food_access_wide.md)

CBSA method:

- USDA is tract-native and single-vintage (`2019`).
- Silver keeps tract rows source-faithful.
- County rows are derived directly from the first `5` digits of `tract_geoid`.
- CBSA rows are derived from county rows through `silver.xwalk_cbsa_county`.
- Population burden shares are recomputed from summed numerator and denominator counts.

Relevant code:

- tract standardization: [usda_food_atlas_silver.R](../../../foundations/etl/silver/usda_food_atlas_silver.R)
- county rollup: [usda_food_atlas_silver.R](../../../foundations/etl/silver/usda_food_atlas_silver.R)
- CBSA rollup: [usda_food_atlas_silver.R](../../../foundations/etl/silver/usda_food_atlas_silver.R)

Observed missingness patterns:

- Missing for the same `11` metros as the CHR `11`-metro set:
  - `6` Connecticut metros
  - `5` Puerto Rico metros
- Silver has no Puerto Rico county rows in `silver.usda_food_atlas`, so the PR gap looks source-native in the current build.
- Silver does keep the `8` legacy Connecticut county GEOIDs via manual lookup, but there are no Connecticut CBSA rows in `silver.usda_food_atlas`.

Interpretation:

- Puerto Rico is an upstream source coverage gap in the current USDA table.
- Connecticut looks like a geography-contract mismatch:
  - USDA county rows are using legacy CT county GEOIDs like `09001`
  - `silver.xwalk_cbsa_county` now uses current CT planning-region-style GEOIDs like `09110`, `09120`, etc.
- That means the CT county rows exist, but the county-to-CBSA join likely never lands for CT in the USDA rollup.
- This is an inference from the observed row pattern plus the current crosswalk contents, but it is a strong one.

## 3. EPA Smart Location Database

Affected KPIs:

- `walkability_index`
- `jobs_access_45min_transit`

Source and lineage:

- source doc: [source__epa_smart_location.md](../../../foundations/data_dictionary/sources/source__epa_smart_location.md)
- silver table doc: [silver__epa_sld.md](../../../foundations/data_dictionary/layers/silver/silver__epa_sld.md)
- silver build: [epa_sld_silver.R](../../../foundations/etl/silver/epa_sld_silver.R)

CBSA method:

- Source is block-group-native and single-vintage (`2021`).
- Silver first aggregates block groups to counties using metric-specific weighting.
- `walkability_index` and `jobs_access_45min_transit` use population-weighted means.
- CBSA rows are then derived from the county base through `silver.xwalk_cbsa_county`.

Relevant code:

- weighted metric aggregation helper: [epa_sld_silver.R](../../../foundations/etl/silver/epa_sld_silver.R)
- county base: [epa_sld_silver.R](../../../foundations/etl/silver/epa_sld_silver.R)
- CBSA rollup: [epa_sld_silver.R](../../../foundations/etl/silver/epa_sld_silver.R)

Observed missingness patterns:

- Missing only for `6` Connecticut metros:
  - `14860` Bridgeport-Stamford-Danbury, CT
  - `25540` Hartford-West Hartford-East Hartford, CT
  - `35300` New Haven, CT
  - `35980` Norwich-New London-Willimantic, CT
  - `45860` Torrington, CT
  - `47930` Waterbury-Shelton, CT
- Silver does contain Connecticut county rows and Puerto Rico county rows.
- Silver does not contain Connecticut CBSA rows for these metros.

Interpretation:

- This does not look like a source coverage problem for CT at county grain.
- It looks like the same legacy-CT-county to current-CT-crosswalk mismatch seen in USDA:
  - SLD county rows preserve legacy CT county GEOIDs
  - the CBSA crosswalk now maps current CT GEOIDs
  - the CBSA join therefore fails for CT
- `jobs_access_45min_transit` also has a general GTFS-coverage caution in the source, but that is not the main issue here because `walkability_index` and `jobs_access_45min_transit` fail together and the CT CBSA rows are absent entirely.

## 4. ACS Transport Built Form Density

Affected KPI:

- `pop_weighted_density_sqmi`

Source and lineage:

- metric contract: [metric_catalog.yml](../../../foundations/semantic_layer/metric_catalog.yml)
- gold table doc: [gold__transport_built_form_wide.md](../../../foundations/data_dictionary/layers/gold/gold__transport_built_form_wide.md)

CBSA method:

- This KPI is already promoted in `gold.transport_built_form_wide`.
- The density fields are tract-derived and only materialize where tract geometry support exists.
- `pop_weighted_density_sqmi` is a population-weighted tract density aggregated to the parent geography.

Observed missingness patterns:

- Missing only for the `5` Puerto Rico metros:
  - `10380` Aguadilla, PR
  - `11640` Arecibo, PR
  - `32420` Mayagüez, PR
  - `38660` Ponce, PR
  - `41980` San Juan-Bayamón-Caguas, PR

Interpretation:

- This looks like a geometry-support gap rather than a metric-source gap.
- The data dictionary already notes that density only lands where tract geometry support exists.
- The PR-only missingness is consistent with the current tract geometry footprint not supporting these metro rollups yet.

## 5. EPA AQI

Affected KPI:

- `aqi_unhealthy_days`

Source and lineage:

- source doc: [source__epa.md](../../../foundations/data_dictionary/sources/source__epa.md)
- silver table doc: [silver__epa_aqi.md](../../../foundations/data_dictionary/layers/silver/silver__epa_aqi.md)
- silver build: [epa_aqi_silver.R](../../../foundations/etl/silver/epa_aqi_silver.R)
- gold table doc: [gold__environment_wide.md](../../../foundations/data_dictionary/layers/gold/gold__environment_wide.md)

CBSA method:

- County rows require name normalization to map EPA county strings to canonical county GEOIDs.
- CBSA rows do not require aggregation.
- Silver uses the source-published CBSA codes directly.

Relevant code:

- county normalization: [epa_aqi_silver.R](../../../foundations/etl/silver/epa_aqi_silver.R)
- CBSA direct use: [epa_aqi_silver.R](../../../foundations/etl/silver/epa_aqi_silver.R)

Observed missingness patterns:

- Missing for `56` CBSAs across `26` state / territory suffixes.
- Universe median CBSA population is `245,242`.
- AQI-missing metro median population is about `148k`, so the missing set skews smaller.
- This is clearly not just a tiny-metro issue, though. Large missing examples include:
  - `17410` Cleveland, OH
  - `19430` Dayton-Kettering-Beavercreek, OH
  - `28880` Kiryas Joel-Poughkeepsie-Newburgh, NY
  - `47930` Waterbury-Shelton, CT

Interpretation:

- This is source-native partial coverage, not a Foundations rollup bug.
- The EPA source docs explicitly say AQI county and CBSA coverage is incomplete by design because the annual files only include areas with sufficient monitoring-based summaries.

## 6. FEMA NRI In The Gold Environment Table

Affected KPI:

- `fema_risk_score`

Source and lineage:

- silver table doc: [silver__fema_nri.md](../../../foundations/data_dictionary/layers/silver/silver__fema_nri.md)
- silver build: [fema_nri_silver.R](../../../foundations/etl/silver/fema_nri_silver.R)
- gold table doc: [gold__environment_wide.md](../../../foundations/data_dictionary/layers/gold/gold__environment_wide.md)

CBSA method:

- FEMA source is county-equivalent-native.
- Silver derives CBSA rows from county-equivalent rows using population-weighted means.
- Gold does **not** expose every FEMA CBSA row directly.
- Instead, `gold.environment_wide` keeps AQI as the backbone and only attaches FEMA where the `2025` AQI row and FEMA row intersect on `geo_level + geo_id + year`.

Relevant code and docs:

- silver CBSA rollup: [fema_nri_silver.R](../../../foundations/etl/silver/fema_nri_silver.R)
- AQI-backed Gold note: [gold__environment_wide.md](../../../foundations/data_dictionary/layers/gold/gold__environment_wide.md)

Observed missingness patterns:

- Missing for `68` CBSAs across `30` state / territory suffixes.
- All `56` AQI-missing CBSAs are also missing `fema_risk_score`.
- There are `12` additional FEMA-missing CBSAs beyond the AQI missing set:
  - `11180` Ames, IA
  - `19260` Danville, VA
  - `20020` Dothan, AL
  - `22520` Florence-Muscle Shoals, AL
  - `27860` Jonesboro, AR
  - `32420` Mayagüez, PR
  - `33780` Monroe, MI
  - `34900` Napa, CA
  - `38660` Ponce, PR
  - `40080` Richmond-Berea, KY
  - `40700` Roseburg, OR
  - `41980` San Juan-Bayamón-Caguas, PR
- Missing-set median population is again about `148k`, below the universe median.

Interpretation:

- The Livability missingness for `fema_risk_score` is only partly a FEMA-source problem.
- Most of it is inherited from the AQI-backed Gold table design.
- If we want broader FEMA coverage for Phase 3, the clean fix is likely in `gold.environment_wide`, not in the Silver FEMA rollup.

## Recommended Pre-Imputation Read

Before median imputation:

1. Treat AQI and FEMA as expected coverage-limited metrics unless we want to redesign `gold.environment_wide`.
2. Treat Puerto Rico gaps in CHR, USDA, and tract-density as real upstream coverage gaps in the current build.
3. Treat Connecticut gaps in USDA and SLD as likely fixable geography-contract issues, not true source absence.
4. Treat the two CT CHR metric gaps (`premature_death_rate`, `preventable_hospital_stay_rate`) as a separate CHR source-null problem inside otherwise valid CBSA rows.

If we want to reduce avoidable imputation before modeling, the most promising upstream fixes are:

1. Connecticut CBSA rollups in `silver.usda_food_atlas`
2. Connecticut CBSA rollups in `silver.epa_sld`
3. possibly broader FEMA exposure in `gold.environment_wide` if we do not want AQI-backbone-limited coverage
