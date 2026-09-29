-- Metro-level harmonized tract totals for every supported comparison horizon.
SELECT *
FROM mart_explanation_q3.metro_growth_ledger
WHERE cbsa_code = ?
ORDER BY horizon_years;
