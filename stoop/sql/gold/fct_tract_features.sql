-- Build: property_explorer_gold.fct_tract_features
--
-- Source contract:
--   Attach the local Metro Deep Dive database before running this script:
--     ATTACH '<metro_deep_dive.duckdb path>' AS metro_deep_dive (READ_ONLY);
--
-- Current configured local source path is documented in config/data_sources.yaml
-- as sources.metro_deep_dive_tract_features.source_database_path.
--
-- Business logic:
--   1. Prefer the latest target-county rows from
--      metro_deep_dive.rof_features.tract_features.
--   2. Fill tract IDs absent from rof_features with
--      metro_deep_dive.foundation.tract_features when available.
--   3. Fill any remaining tract IDs from the latest tract year in
--      metro_deep_dive.gold.housing_core_wide joined to
--      metro_deep_dive.gold.population_demographics.
--   4. If no source row exists for a mapped tract, create a null-valued feature
--      row from property_explorer_gold.dim_tract_to_nta.
--   5. Crime is deferred for the MVP, so crime_rate_proxy remains null.
--   6. The current target counties are Brooklyn (36047) and Manhattan (36061).

CREATE OR REPLACE TABLE property_explorer_gold.fct_tract_features AS
WITH target_counties AS (
    SELECT county_geoid
    FROM (
        VALUES
            ('36047'),
            ('36061')
    ) AS counties(county_geoid)
),
latest_rof_tract_year AS (
    SELECT MAX(year) AS year
    FROM metro_deep_dive.rof_features.tract_features
    WHERE county_geoid IN (SELECT county_geoid FROM target_counties)
),
rof_features AS (
    SELECT
        r.tract_geoid AS tract_id,
        r.median_hh_income AS median_income,
        r.median_gross_rent AS median_rent,
        r.median_home_value,
        p.pct_ba_plus AS pct_bachelors_plus,
        p.median_age,
        CAST(NULL AS DOUBLE) AS crime_rate_proxy
    FROM metro_deep_dive.rof_features.tract_features AS r
    INNER JOIN latest_rof_tract_year AS latest
        ON r.year = latest.year
    LEFT JOIN metro_deep_dive.gold.population_demographics AS p
        ON p.geo_level = 'tract'
       AND r.tract_geoid = p.geo_id
       AND r.year = p.year
    WHERE r.county_geoid IN (SELECT county_geoid FROM target_counties)
),
latest_foundation_tract_year AS (
    SELECT MAX(year) AS year
    FROM metro_deep_dive.foundation.tract_features
    WHERE county_geoid IN (SELECT county_geoid FROM target_counties)
),
foundation_features AS (
    SELECT
        f.tract_geoid AS tract_id,
        f.median_hh_income AS median_income,
        f.median_gross_rent AS median_rent,
        f.median_home_value,
        p.pct_ba_plus AS pct_bachelors_plus,
        p.median_age,
        CAST(NULL AS DOUBLE) AS crime_rate_proxy
    FROM metro_deep_dive.foundation.tract_features AS f
    INNER JOIN latest_foundation_tract_year AS latest
        ON f.year = latest.year
    LEFT JOIN metro_deep_dive.gold.population_demographics AS p
        ON p.geo_level = 'tract'
       AND f.tract_geoid = p.geo_id
       AND f.year = p.year
    WHERE f.county_geoid IN (SELECT county_geoid FROM target_counties)
),
latest_gold_tract_year AS (
    SELECT MAX(year) AS year
    FROM metro_deep_dive.gold.housing_core_wide
    WHERE geo_level = 'tract'
),
gold_features AS (
    SELECT
        h.geo_id AS tract_id,
        h.median_hh_income AS median_income,
        h.median_gross_rent AS median_rent,
        h.median_home_value,
        p.pct_ba_plus AS pct_bachelors_plus,
        p.median_age,
        CAST(NULL AS DOUBLE) AS crime_rate_proxy
    FROM metro_deep_dive.gold.housing_core_wide AS h
    INNER JOIN latest_gold_tract_year AS latest
        ON h.year = latest.year
    LEFT JOIN metro_deep_dive.gold.population_demographics AS p
        ON h.geo_level = p.geo_level
       AND h.geo_id = p.geo_id
       AND h.year = p.year
    WHERE h.geo_level = 'tract'
      AND EXISTS (
          SELECT 1
          FROM target_counties AS counties
          WHERE starts_with(h.geo_id, counties.county_geoid)
      )
),
selected_features AS (
    SELECT *
    FROM rof_features

    UNION ALL

    SELECT *
    FROM foundation_features
    WHERE NOT EXISTS (
        SELECT 1
        FROM rof_features
        WHERE rof_features.tract_id = foundation_features.tract_id
    )

    UNION ALL

    SELECT *
    FROM gold_features
    WHERE NOT EXISTS (
        SELECT 1
        FROM rof_features
        WHERE rof_features.tract_id = gold_features.tract_id
    )
      AND NOT EXISTS (
          SELECT 1
          FROM foundation_features
          WHERE foundation_features.tract_id = gold_features.tract_id
      )
),
mapping_fallback_features AS (
    SELECT DISTINCT
        mapping.tract_id,
        CAST(NULL AS DOUBLE) AS median_income,
        CAST(NULL AS DOUBLE) AS median_rent,
        CAST(NULL AS DOUBLE) AS median_home_value,
        CAST(NULL AS DOUBLE) AS pct_bachelors_plus,
        CAST(NULL AS DOUBLE) AS median_age,
        CAST(NULL AS DOUBLE) AS crime_rate_proxy
    FROM property_explorer_gold.dim_tract_to_nta AS mapping
    WHERE EXISTS (
        SELECT 1
        FROM target_counties AS counties
        WHERE starts_with(mapping.tract_id, counties.county_geoid)
    )
),
features_with_fallback AS (
    SELECT *
    FROM selected_features

    UNION ALL

    SELECT *
    FROM mapping_fallback_features
    WHERE NOT EXISTS (
        SELECT 1
        FROM selected_features
        WHERE selected_features.tract_id = mapping_fallback_features.tract_id
    )
)
SELECT
    CAST(tract_id AS VARCHAR) AS tract_id,
    CASE
        WHEN isnan(CAST(median_income AS DOUBLE)) THEN NULL
        ELSE CAST(median_income AS DOUBLE)
    END AS median_income,
    CASE
        WHEN isnan(CAST(median_rent AS DOUBLE)) THEN NULL
        ELSE CAST(median_rent AS DOUBLE)
    END AS median_rent,
    CASE
        WHEN isnan(CAST(median_home_value AS DOUBLE)) THEN NULL
        ELSE CAST(median_home_value AS DOUBLE)
    END AS median_home_value,
    CASE
        WHEN isnan(CAST(pct_bachelors_plus AS DOUBLE)) THEN NULL
        ELSE CAST(pct_bachelors_plus AS DOUBLE)
    END AS pct_bachelors_plus,
    CASE
        WHEN isnan(CAST(median_age AS DOUBLE)) THEN NULL
        ELSE CAST(median_age AS DOUBLE)
    END AS median_age,
    CASE
        WHEN isnan(CAST(crime_rate_proxy AS DOUBLE)) THEN NULL
        ELSE CAST(crime_rate_proxy AS DOUBLE)
    END AS crime_rate_proxy
FROM features_with_fallback;
