# Data Dictionary: gold.social_infra_wide

## Overview
- **Table**: `gold.social_infra_wide`
- **Purpose**: Narrow annual social infrastructure mart for household structure, health insurance coverage, and household internet access headline metrics.
- **Row count**: 1,471,832
- **KPI applicability**: Gold output table built from recurring ACS-derived Silver panels.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
  - Live uniqueness check on June 9, 2026: rows=1,471,832; distinct PK=1,471,832; duplicates=0
- **Time coverage**: `year` min=2015, max=2024
- **Geo coverage**: 9 geo levels; 165,557 distinct `geo_id`

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **Household structure**: `hh_total`, `single_households`, `pct_hh_single_person`
- **Insurance coverage**: `ins_total`, `ins_insured`, `ins_uninsured`, `pct_health_insured`, `pct_health_uninsured`
- **Broadband access**: `internet_total_hh`, `internet_broadband_subscription`, `internet_cellular_only`, `internet_no_access`, `pct_broadband_subscription`, `pct_cellular_only`, `pct_no_internet_access`

## Data Quality Notes
- This table uses `silver.social_infra_kpi` as the row spine, so the full mart spans `2015–2024` even though broadband does not begin until `2017`.
- Broadband fields are null for the pre-2017 rows by design. In the current snapshot, broadband is populated for the large majority of `2017+` rows, with the remaining `17,432` null rows concentrated in `tract`, `zcta`, and `place`.
- The broadband metrics come from the dedicated `silver.broadband_kpi` family rather than the older commented-out `acs_social_infra` broadband stub.
- ACS broadband question wording changed in `2019`, so breakpoint-sensitive analysis should treat pre-2019 and post-2019 values with caution even though the headline series is still useful.
- Single-parent household metrics are intentionally not included yet because the needed `B11003` fields are not currently landed in `staging.acs_social_infra_*`.

## Lineage
1. `foundations/etl/silver/acs_social_infra_silver.R` builds `silver.social_infra_kpi` from `staging.acs_social_infra_*`.
2. `foundations/etl/silver/acs_broadband_silver.R` builds `silver.broadband_kpi` from the dedicated ACS broadband staging family.
3. `foundations/etl/gold/gold_social_infra_wide.sql` joins those two recurring panels and materializes `gold.social_infra_wide`.

## Known Gaps / To-Dos
- Add `pct_family_single_parent` after `B11003` is staged into the social infrastructure family or promoted through a separate household-structure path.
- Decide later whether limited-English access metrics belong here or remain only in `gold.population_demographics`.
