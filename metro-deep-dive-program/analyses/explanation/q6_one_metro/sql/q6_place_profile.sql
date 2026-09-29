-- Direct ACS Place measures remain separate from population-weighted
-- allocation of tract WAC workplace jobs.
WITH membership AS (
  SELECT place_geoid, target_geo_id AS cbsa_code, membership_status,
         quality_flag, target_share_in_place, is_primary_cbsa
  FROM mart_geography.place_to_cbsa_membership
  WHERE weight_basis = 'population' AND target_geo_id = '__CBSA_CODE__'
), allocated_jobs AS (
  SELECT allocation.target_geo_id AS place_geoid,
         SUM(wac.jobs_total * allocation.weight) AS allocated_workplace_jobs,
         MAX(allocation.quality_flag) AS allocation_quality_flag
  FROM silver.lehd_lodes_wac AS wac
  JOIN silver.xwalk_allocation AS allocation
    ON allocation.source_geo_id = wac.geo_id
  WHERE wac.year = 2023
    AND allocation.source_geo_level = 'tract'
    AND allocation.target_geo_level = 'place'
    AND allocation.weight_basis = 'population'
  GROUP BY 1
), metro_population AS (
  SELECT geo_id AS cbsa_code, geo_name AS cbsa_name, pop_total AS cbsa_population
  FROM gold.population_demographics
  WHERE lower(geo_level) = 'cbsa' AND year = 2024
)
SELECT membership.cbsa_code, metro_population.cbsa_name, membership.place_geoid,
       place.geo_name AS place_name, place.pop_total AS direct_population,
       housing.median_hh_income AS direct_median_hh_income,
       housing.hu_total AS direct_housing_units,
       jobs.allocated_workplace_jobs, jobs.allocation_quality_flag,
       membership.membership_status,
       membership.quality_flag AS membership_quality_flag,
       membership.target_share_in_place AS cbsa_share_of_place_population,
       membership.is_primary_cbsa,
       place.pop_total / NULLIF(metro_population.cbsa_population, 0) AS metro_population_share,
       '2023_TRACT_WAC_ALLOCATED_TO_PLACE_BY_2020_POPULATION' AS workplace_jobs_provenance,
       'DIRECT_2024_ACS_PLACE_NOT_METRO_ADDITIVE' AS direct_metrics_provenance
FROM membership
JOIN gold.population_demographics AS place
  ON place.geo_id = membership.place_geoid
 AND lower(place.geo_level) = 'place' AND place.year = 2024
LEFT JOIN gold.housing_core_wide AS housing
  ON housing.geo_id = membership.place_geoid
 AND lower(housing.geo_level) = 'place' AND housing.year = 2024
LEFT JOIN allocated_jobs AS jobs USING (place_geoid)
JOIN metro_population USING (cbsa_code)
ORDER BY direct_population DESC, place_name;
