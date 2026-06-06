-- Build: property_explorer_gold.fct_nta_features
--
-- Source contract:
--   property_explorer_gold.fct_tract_features must already exist.
--   property_explorer_gold.dim_tract_to_nta must already exist.
--
-- Business logic:
--   1. Join tract features to the authoritative tract-to-NTA mapping.
--   2. Use an inner join so only mapped tracts contribute to NTA summaries.
--   3. Carry forward NTA-native context fields (`borough`, `tract_count`) so
--      downstream neighborhood views are not forced to reconstruct them.
--   4. Aggregate numeric tract metrics with median(), matching the current
--      Python pipeline implementation.
--   4. Crime is deferred for the MVP, but the nullable column is retained.

CREATE OR REPLACE TABLE property_explorer_gold.fct_nta_features AS
WITH mapped_tract_features AS (
    SELECT
        mapping.nta_id,
        mapping.nta_name,
        mapping.borough,
        tract_features.tract_id,
        CASE
            WHEN isnan(CAST(tract_features.median_income AS DOUBLE)) THEN NULL
            ELSE CAST(tract_features.median_income AS DOUBLE)
        END AS median_income,
        CASE
            WHEN isnan(CAST(tract_features.median_rent AS DOUBLE)) THEN NULL
            ELSE CAST(tract_features.median_rent AS DOUBLE)
        END AS median_rent,
        CASE
            WHEN isnan(CAST(tract_features.median_home_value AS DOUBLE)) THEN NULL
            ELSE CAST(tract_features.median_home_value AS DOUBLE)
        END AS median_home_value,
        CASE
            WHEN isnan(CAST(tract_features.pct_bachelors_plus AS DOUBLE)) THEN NULL
            ELSE CAST(tract_features.pct_bachelors_plus AS DOUBLE)
        END AS pct_bachelors_plus,
        CASE
            WHEN isnan(CAST(tract_features.median_age AS DOUBLE)) THEN NULL
            ELSE CAST(tract_features.median_age AS DOUBLE)
        END AS median_age,
        CASE
            WHEN isnan(CAST(tract_features.crime_rate_proxy AS DOUBLE)) THEN NULL
            ELSE CAST(tract_features.crime_rate_proxy AS DOUBLE)
        END AS crime_rate_proxy
    FROM property_explorer_gold.fct_tract_features AS tract_features
    INNER JOIN (
        SELECT DISTINCT
            tract_id,
            nta_id,
            nta_name,
            borough
        FROM property_explorer_gold.dim_tract_to_nta
    ) AS mapping
        ON tract_features.tract_id = mapping.tract_id
)
SELECT
    CAST(nta_id AS VARCHAR) AS nta_id,
    CAST(nta_name AS VARCHAR) AS nta_name,
    string_agg(DISTINCT CAST(borough AS VARCHAR), ' / ' ORDER BY CAST(borough AS VARCHAR)) AS borough,
    COUNT(DISTINCT tract_id) AS tract_count,
    median(median_income) AS median_income,
    median(median_rent) AS median_rent,
    median(median_home_value) AS median_home_value,
    median(pct_bachelors_plus) AS pct_bachelors_plus,
    median(median_age) AS median_age,
    median(crime_rate_proxy) AS crime_rate_proxy
FROM mapped_tract_features
GROUP BY
    nta_id,
    nta_name;
