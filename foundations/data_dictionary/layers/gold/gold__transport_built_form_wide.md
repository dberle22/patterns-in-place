# Data Dictionary: gold.transport_built_form_wide

## Overview
- **Table**: `gold.transport_built_form_wide`
- **Purpose**: Transport behavior and vehicle access mart with tract-derived built form density where tract geometry support exists.
- **Row count**: 1,891,571
- **KPI applicability**: Gold output table with inherited ACS transport metrics and derived density measures.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
  - Live uniqueness check on April 10, 2026: rows=1,020,930; distinct PK=1,020,930; duplicates=0
- **Time coverage**: `year` min=2012, max=2024
- **Geo coverage**: 9 geo levels; 115,976 distinct `geo_id`

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **Commute counts**: `commute_*`
- **Commute mode shares**: `pct_commute_drive_alone`, `pct_commute_carpool`, `pct_commute_transit`, `pct_commute_walk`, `pct_commute_wfh`, `pct_low_car_commute`
- **Vehicle access**: `veh_total_hh`, `veh_0` to `veh_4_plus`, `pct_hh_0_vehicles` to `pct_hh_4p_vehicles`
- **Travel time**: `total_travel_time`, `mean_travel_time`
- **Built form density**: `density_population`, `land_area_sqmi`, `gross_density_sqmi`, `pop_weighted_density_sqmi`

## Data Quality Notes
- Live query checks on 2026-06-08 confirm the intended `geo_level + geo_id + year` grain with zero duplicate keys.
- `pct_commute_wfh` is nearly complete, with only 70 null rows in the current snapshot.
- `gross_density_sqmi` is null in 897,909 rows because density is only computed where tract geometry support exists and where the mart can safely aggregate that geometry-driven input.
- Non-null density rows are concentrated in supported geography types:
  - `tract`: 116,621
  - `county`: 4,788
  - `cbsa`: 1,560
  - `state`: 52
- `zcta`, `place`, `division`, `region`, and `us` currently carry transport metrics but not density outputs.

## Lineage
1. **Primary build script**: [scripts/etl/gold/gold_transport_built_form_wide.sql]
2. **Primary upstreams**:
   - `silver.transport_kpi`
   - `silver.xwalk_tract_county`
   - `silver.xwalk_county_state`
   - `silver.xwalk_cbsa_county`
   - `geo.tracts_all_us`

## Known Gaps / To-Dos
- Density coverage is limited by current tract geometry support and tract-to-parent aggregation coverage.
- EPA Smart Location Database enrichment now lives in the companion `gold.transport_built_form_sld` baseline table rather than this recurring ACS transport panel.
- State density only lands for supported states in the current geometry footprint.
- If national tract geometry support expands, reprofile density completeness and update this dictionary entry.
