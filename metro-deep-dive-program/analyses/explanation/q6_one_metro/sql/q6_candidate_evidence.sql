-- The reviewed Q2 component association is the largest population-weighted
-- allocation of a component's center-tract jobs. Map display geometry is not
-- part of this calculation.
WITH profile AS (
  SELECT * FROM (
    WITH membership AS (
      SELECT place_geoid, target_geo_id AS cbsa_code, membership_status,
             quality_flag, target_share_in_place, is_primary_cbsa
      FROM mart_geography.place_to_cbsa_membership
      WHERE weight_basis = 'population' AND target_geo_id = '__CBSA_CODE__'
    ), allocated_jobs AS (
      SELECT allocation.target_geo_id AS place_geoid,
             SUM(wac.jobs_total * allocation.weight) AS allocated_workplace_jobs
      FROM silver.lehd_lodes_wac AS wac JOIN silver.xwalk_allocation AS allocation
        ON allocation.source_geo_id = wac.geo_id
      WHERE wac.year = 2023 AND allocation.source_geo_level = 'tract'
        AND allocation.target_geo_level = 'place' AND allocation.weight_basis = 'population'
      GROUP BY 1
    ), metro AS (
      SELECT geo_id AS cbsa_code, pop_total AS cbsa_population
      FROM gold.population_demographics WHERE lower(geo_level)='cbsa' AND year=2024
    )
    SELECT membership.cbsa_code, membership.place_geoid, place.geo_name AS place_name,
           place.pop_total AS direct_population, housing.median_hh_income AS direct_median_hh_income,
           housing.hu_total AS direct_housing_units, jobs.allocated_workplace_jobs,
           membership.membership_status, membership.quality_flag AS membership_quality_flag,
           membership.target_share_in_place AS cbsa_share_of_place_population,
           membership.is_primary_cbsa,
           place.pop_total / NULLIF(metro.cbsa_population,0) AS metro_population_share
    FROM membership JOIN gold.population_demographics AS place
      ON place.geo_id=membership.place_geoid AND lower(place.geo_level)='place' AND place.year=2024
    LEFT JOIN gold.housing_core_wide AS housing
      ON housing.geo_id=membership.place_geoid AND lower(housing.geo_level)='place' AND housing.year=2024
    LEFT JOIN allocated_jobs AS jobs USING(place_geoid) JOIN metro USING(cbsa_code)
  )
), contribution AS (
  SELECT center.cbsa_code, center.recommended_cluster_id AS component_id,
         allocation.target_geo_id AS place_geoid,
         SUM(center.jobs_total * allocation.weight) AS allocated_component_jobs
  FROM mart_explanation_q2.job_center_candidates_v0 AS center
  JOIN silver.xwalk_allocation AS allocation ON allocation.source_geo_id=center.tract_geoid
  WHERE center.cbsa_code='__CBSA_CODE__' AND center.is_recommended_center
    AND allocation.source_geo_level='tract' AND allocation.target_geo_level='place'
    AND allocation.weight_basis='population'
  GROUP BY 1,2,3
), primary_component AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY cbsa_code, component_id ORDER BY allocated_component_jobs DESC, place_geoid) AS association_rank,
         SUM(allocated_component_jobs) OVER (PARTITION BY cbsa_code, component_id) AS component_allocated_jobs
  FROM contribution
), proximity AS (
  SELECT profile.cbsa_code, allocation.target_geo_id AS place_geoid, proximity.center_version,
         SUM(proximity.distance_to_nearest_center_miles * allocation.weight) / NULLIF(SUM(allocation.weight),0) AS distance_miles
  FROM profile JOIN silver.xwalk_allocation AS allocation ON allocation.target_geo_id=profile.place_geoid
  JOIN mart_explanation_q2.job_center_proximity_v0 AS proximity
    ON proximity.tract_geoid=allocation.source_geo_id AND proximity.cbsa_code=profile.cbsa_code
  WHERE allocation.source_geo_level='tract' AND allocation.target_geo_level='place' AND allocation.weight_basis='population'
  GROUP BY 1,2,3
), proximity_wide AS (
  SELECT cbsa_code, place_geoid,
         MAX(CASE WHEN center_version='recommended_core_one_hop' THEN distance_miles END) AS recommended_distance_miles,
         MAX(CASE WHEN center_version='strict_core' THEN distance_miles END) AS strict_distance_miles,
         MAX(CASE WHEN center_version='no_share_sensitivity' THEN distance_miles END) AS no_share_distance_miles
  FROM proximity GROUP BY 1,2
)
SELECT profile.*, component.component_id AS associated_q2_component,
       component.allocated_component_jobs,
       component.allocated_component_jobs / NULLIF(component.component_allocated_jobs,0) AS component_job_share_in_place,
       CASE WHEN component.component_id IS NULL THEN NULL ELSE 'largest_population_weighted_tract_allocation' END AS association_rule,
       proximity_wide.recommended_distance_miles, proximity_wide.strict_distance_miles,
       proximity_wide.no_share_distance_miles,
       profile.direct_population >= 5000 AND profile.metro_population_share >= .01 AS meets_initial_materiality,
       CASE WHEN component.component_id IS NULL THEN 'no_associated_reviewed_component'
            WHEN profile.direct_population >= 5000 AND profile.metro_population_share >= .01 THEN 'candidate_for_review'
            ELSE 'profile_only_below_initial_materiality' END AS candidate_status,
       '5000_residents_and_1pct_cbsa_population__initial_rule_pending_review' AS materiality_rule
FROM profile
LEFT JOIN primary_component AS component
  ON component.cbsa_code=profile.cbsa_code AND component.place_geoid=profile.place_geoid
 AND component.association_rank=1
LEFT JOIN proximity_wide
  ON proximity_wide.cbsa_code=profile.cbsa_code
 AND proximity_wide.place_geoid=profile.place_geoid
ORDER BY meets_initial_materiality DESC, direct_population DESC, place_name;
