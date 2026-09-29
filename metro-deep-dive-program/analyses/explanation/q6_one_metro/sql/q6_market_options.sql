-- Q6 only offers CBSAs with governed Census Place membership and 2024 ACS
-- context. The profile query remains market-specific and read-only.
SELECT DISTINCT membership.target_geo_id AS cbsa_code,
       cbsa.geo_name AS cbsa_name
FROM mart_geography.place_to_cbsa_membership AS membership
JOIN gold.population_demographics AS cbsa
  ON cbsa.geo_id = membership.target_geo_id
 AND lower(cbsa.geo_level) = 'cbsa'
 AND cbsa.year = 2024
WHERE membership.weight_basis = 'population'
ORDER BY cbsa_name, cbsa_code;
