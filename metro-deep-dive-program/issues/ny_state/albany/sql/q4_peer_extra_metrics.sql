-- Extra raw metrics for the peer profile (Q4g), from the Intelligence marts' raw (unscored) columns,
-- long and shaped like q4_metro_scorecard.sql so the two stack. Metros only (2023 delineation).
-- Raw values, not the flipped or standardized model inputs (R32).
WITH metros AS (
  SELECT geo_id, geo_name, state_fips = '36' AS is_ny_metro FROM gold.dim_geo WHERE geo_level = 'cbsa' AND is_metro
),
character AS (
  UNPIVOT (
    SELECT cbsa_code, pop_weighted_density_sqmi, pct_struct_multifam, social_associations_per_10k,
           civic_organizations_per_1000, diversity_index
    FROM mart_intelligence.intelligence_character
  ) ON pop_weighted_density_sqmi, pct_struct_multifam, social_associations_per_10k, civic_organizations_per_1000, diversity_index
  INTO NAME metric_id VALUE value
),
livability AS (
  UNPIVOT (
    SELECT cbsa_code, pct_hh_0_vehicles, pct_commute_wfh, walkability_index, vacancy_rate,
           permits_per_1000_housing_units, premature_death_rate, pct_rent_burden_30plus
    FROM mart_intelligence.intelligence_livability
  ) ON pct_hh_0_vehicles, pct_commute_wfh, walkability_index, vacancy_rate, permits_per_1000_housing_units,
       premature_death_rate, pct_rent_burden_30plus
  INTO NAME metric_id VALUE value
)
SELECT 'cbsa' AS geo_level, m.geo_id, m.geo_name, m.is_ny_metro, x.metric_id,
       CASE WHEN x.metric_id = 'premature_death_rate' THEN 2025 ELSE 2024 END AS year, x.value
FROM (SELECT * FROM character UNION ALL SELECT * FROM livability) AS x
JOIN metros AS m ON m.geo_id = x.cbsa_code
ORDER BY x.metric_id, m.geo_id
