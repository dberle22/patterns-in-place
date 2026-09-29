-- Market selector: restrict labels to metros materialized in the Q3 mart.
SELECT
  ledger.cbsa_code,
  cbsas.cbsa_name
FROM (
  SELECT DISTINCT cbsa_code
  FROM mart_explanation_q3.metro_growth_ledger
) AS ledger
JOIN geo.cbsas AS cbsas USING (cbsa_code)
ORDER BY cbsas.cbsa_name;
