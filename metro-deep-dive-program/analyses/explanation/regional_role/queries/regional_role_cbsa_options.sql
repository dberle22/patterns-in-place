-- Metropolitan CBSA selector backed by the governed current dimension.
SELECT geo_id AS cbsa_code,
       CONCAT(geo_name, ' (', geo_id, ')') AS display_name
FROM gold.dim_geo
WHERE geo_level = 'cbsa' AND is_metro = TRUE
ORDER BY geo_name;
