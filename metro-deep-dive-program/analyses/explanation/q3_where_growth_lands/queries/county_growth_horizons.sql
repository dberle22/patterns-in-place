-- County lens for the selected metro and comparison horizon.
SELECT *
FROM mart_explanation_q3.county_growth_horizons
WHERE cbsa_code = ?
  AND horizon_years = ?;
