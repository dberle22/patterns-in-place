-- Join Q2's published versioned proximity surface to Q1's direct 2024 tract
-- outcomes. This reader preserves the 2023 WAC / 2024 ACS timing difference.
select
    proximity.center_version,
    proximity.center_count,
    proximity.has_center_candidate,
    proximity.nearest_center_tract_geoid,
    proximity.distance_to_nearest_center_miles,
    centers.cbsa_code,
    centers.cbsa_name,
    centers.tract_geoid,
    centers.jobs_total,
    centers.workers_total,
    centers.market_job_share,
    centers.jobs_to_workers_ratio,
    centers.is_strict_core_seed,
    centers.is_recommended_center,
    centers.is_no_share_sensitivity,
    centers.center_role,
    centers.recommended_cluster_id,
    outcomes.year as housing_year,
    outcomes.pop_total,
    outcomes.hu_total as housing_units,
    outcomes.annualized_median_rent,
    outcomes.median_home_value,
    outcomes.median_hh_income,
    outcomes.median_rent_to_all_hh_income_proxy,
    outcomes.pct_rent_burden_30plus,
    geography.geom_wkb
from mart_explanation_q2.job_center_proximity_v0 proximity
join mart_explanation_q2.job_center_candidates_v0 centers
  on proximity.cbsa_code = centers.cbsa_code
 and proximity.tract_geoid = centers.tract_geoid
join mart_explanation_q1.supply_demand_base outcomes
  on centers.tract_geoid = outcomes.geo_id
 and centers.cbsa_code = outcomes.cbsa_code
join geo.tracts_all_us geography
  on centers.tract_geoid = geography.tract_geoid
where proximity.cbsa_code = '__CBSA_CODE__'
  and outcomes.geo_level = 'tract'
  and outcomes.year = 2024
order by proximity.center_version, centers.tract_geoid;
