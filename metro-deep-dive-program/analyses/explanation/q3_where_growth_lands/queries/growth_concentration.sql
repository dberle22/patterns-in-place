-- Cumulative contribution of positive-growth tracts for the selected horizon.
SELECT *
FROM mart_explanation_q3.growth_concentration
WHERE cbsa_code = ?
  AND horizon_years = ?;
