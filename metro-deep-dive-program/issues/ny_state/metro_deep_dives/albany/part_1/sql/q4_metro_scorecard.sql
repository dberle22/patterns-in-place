-- Q4 scorecard: one row per geography x metric for every US metro (2023 delineation),
-- New York State and the US. Each metric reads its own latest complete year
-- (ACS 2020-24 5-year = 2024; BEA = 2023; Zillow/FHFA = 2025; LODES = 2023; IRS = 2022).
-- Python ranks the metros; NY and US are reference rows (null where the source has no row).
-- NY counties come along so Python can build an Upstate aggregate from them.
WITH geos AS (
  SELECT 'cbsa' AS geo_level, geo_id, geo_name, state_fips = '36' AS is_ny_metro
  FROM gold.dim_geo
  WHERE geo_level = 'cbsa' AND is_metro
  UNION ALL
  SELECT 'county', geo_id, geo_name, NULL
  FROM gold.dim_geo
  WHERE geo_level = 'county' AND state_fips = '36'
  UNION ALL SELECT 'state', '36', 'New York State', NULL
  UNION ALL SELECT 'us', '1', 'US', NULL
),
pop AS (
  UNPIVOT (
    SELECT lower(geo_level) AS geo_level, geo_id, 2024 AS year,
      pop_total, pop_growth_10yr, pct_ba_plus, median_age, pct_age_over_64,
      1 - pct_white_nh AS pct_nonwhite
    FROM gold.population_demographics WHERE year = 2024
  ) ON pop_total, pop_growth_10yr, pct_ba_plus, median_age, pct_age_over_64, pct_nonwhite
  INTO NAME metric_id VALUE value
),
pop_base AS (
  -- The base of the 10-year growth (ACS 2010-14), so county sums give an exact Upstate growth rate.
  SELECT lower(geo_level) AS geo_level, geo_id, 2014 AS year, 'pop_total_2014' AS metric_id, pop_total AS value
  FROM gold.population_demographics WHERE year = 2014
),
income_acs AS (
  UNPIVOT (
    SELECT lower(geo_level) AS geo_level, geo_id, 2024 AS year, median_hh_income, pov_rate
    FROM gold.economics_income_wide WHERE year = 2024
  ) ON median_hh_income, pov_rate INTO NAME metric_id VALUE value
),
income_bea AS (
  UNPIVOT (
    SELECT lower(geo_level) AS geo_level, geo_id, 2023 AS year, calc_income_pc, income_pc_growth_10yr
    FROM gold.economics_income_wide WHERE year = 2023
  ) ON calc_income_pc, income_pc_growth_10yr INTO NAME metric_id VALUE value
),
real_income AS (
  UNPIVOT (
    SELECT lower(geo_level) AS geo_level, geo_id, 2023 AS year, rpp_real_pc_income, rpp_all_items
    FROM gold.affordability_wide WHERE year = 2023
  ) ON rpp_real_pc_income, rpp_all_items INTO NAME metric_id VALUE value
),
gdp_level AS (
  UNPIVOT (
    SELECT lower(geo_level) AS geo_level, geo_id, 2023 AS year, nominal_gdp_total, nominal_gdp_pc
    FROM gold.economics_gdp_wide WHERE year = 2023
  ) ON nominal_gdp_total, nominal_gdp_pc INTO NAME metric_id VALUE value
),
gdp_growth AS (
  UNPIVOT (
    SELECT lower(geo_level) AS geo_level, geo_id, 2024 AS year, real_gdp_cagr_5yr
    FROM gold.economics_gdp_wide WHERE year = 2024
  ) ON real_gdp_cagr_5yr INTO NAME metric_id VALUE value
),
housing AS (
  UNPIVOT (
    SELECT lower(geo_level) AS geo_level, geo_id, 2024 AS year,
      median_home_value, median_gross_rent, value_to_income, owner_occ_rate
    FROM gold.housing_core_wide WHERE year = 2024
  ) ON median_home_value, median_gross_rent, value_to_income, owner_occ_rate
  INTO NAME metric_id VALUE value
),
market AS (
  UNPIVOT (
    SELECT lower(geo_level) AS geo_level, geo_id, 2025 AS year, zhvi_annual_avg, hpi_5yr_pct
    FROM gold.housing_market_wide WHERE year = 2025
  ) ON zhvi_annual_avg, hpi_5yr_pct INTO NAME metric_id VALUE value
),
labor AS (
  UNPIVOT (
    SELECT lower(geo_level) AS geo_level, geo_id, 2024 AS year, pct_unemployment_rate, lfpr
    FROM gold.economics_labor_wide WHERE year = 2024
  ) ON pct_unemployment_rate, lfpr INTO NAME metric_id VALUE value
),
jobs AS (
  -- LODES WAC: jobs_all_total is all jobs (JT00); jobs_total is private only (JT02), per R34.
  UNPIVOT (
    SELECT lower(geo_level) AS geo_level, geo_id, 2023 AS year,
      jobs_all_total,
      jobs_total AS jobs_private_total,
      1 - jobs_total / nullif(jobs_all_total, 0) AS public_job_share,
      pct_jobs_ind_health_care_social_assistance AS private_health_share,
      pct_jobs_ind_educational_services AS private_education_share
    FROM gold.economics_lodes_wide WHERE year = 2023
  ) ON jobs_all_total, jobs_private_total, public_job_share, private_health_share, private_education_share
  INTO NAME metric_id VALUE value
),
migration_acs AS (
  UNPIVOT (
    SELECT lower(geo_level) AS geo_level, geo_id, 2024 AS year, pct_foreign_born, pct_moved_diff_st
    FROM gold.migration_wide WHERE year = 2024
  ) ON pct_foreign_born, pct_moved_diff_st INTO NAME metric_id VALUE value
),
migration_irs AS (
  UNPIVOT (
    -- Net households per resident, positive = net gain (IRS direction fixed 2026-10-26;
    -- foundations/etl/IRS_MIGRATION_DIRECTION_FIX_SPEC.md).
    SELECT lower(geo_level) AS geo_level, geo_id, 2022 AS year, irs_net_migration_rate
    FROM gold.migration_wide WHERE year = 2022
  ) ON irs_net_migration_rate INTO NAME metric_id VALUE value
),
metrics AS (
  SELECT * FROM pop
  UNION ALL SELECT * FROM pop_base
  UNION ALL SELECT * FROM income_acs
  UNION ALL SELECT * FROM income_bea
  UNION ALL SELECT * FROM real_income
  UNION ALL SELECT * FROM gdp_level
  UNION ALL SELECT * FROM gdp_growth
  UNION ALL SELECT * FROM housing
  UNION ALL SELECT * FROM market
  UNION ALL SELECT * FROM labor
  UNION ALL SELECT * FROM jobs
  UNION ALL SELECT * FROM migration_acs
  UNION ALL SELECT * FROM migration_irs
)
SELECT g.geo_level, g.geo_id, g.geo_name, g.is_ny_metro, m.metric_id, m.year, m.value
FROM geos AS g
JOIN metrics AS m USING (geo_level, geo_id)
ORDER BY m.metric_id, g.geo_level, g.geo_id
