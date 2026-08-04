WITH state_rows AS (
    SELECT
        i.*,
        CAST(g.division_id AS VARCHAR) AS division_id,
        g.division_name
    FROM patterns_in_place.gold.economics_industry_wide i
    LEFT JOIN patterns_in_place.gold.dim_geo g
      ON g.geo_level = i.geo_level
     AND g.geo_id = i.geo_id
    WHERE i.geo_level = 'state'
),
us_rollup AS (
    SELECT
        'us' AS benchmark_scope,
        'us' AS benchmark_geo_id,
        'United States' AS benchmark_geo_name,
        year,
        SUM(qcew_private_emp_ag_mining) AS qcew_private_emp_ag_mining,
        SUM(qcew_private_emp_construction) AS qcew_private_emp_construction,
        SUM(qcew_private_emp_manufacturing) AS qcew_private_emp_manufacturing,
        SUM(qcew_private_emp_wholesale) AS qcew_private_emp_wholesale,
        SUM(qcew_private_emp_retail) AS qcew_private_emp_retail,
        SUM(qcew_private_emp_transport_util) AS qcew_private_emp_transport_util,
        SUM(qcew_private_emp_information) AS qcew_private_emp_information,
        SUM(qcew_private_emp_finance_real) AS qcew_private_emp_finance_real,
        SUM(qcew_private_emp_professional) AS qcew_private_emp_professional,
        SUM(qcew_private_emp_educ_health) AS qcew_private_emp_educ_health,
        SUM(qcew_private_emp_arts_accomm_food) AS qcew_private_emp_arts_accomm_food,
        SUM(qcew_private_emp_other_services) AS qcew_private_emp_other_services,
        SUM(real_gdp_natural_resources) AS real_gdp_natural_resources,
        SUM(real_gdp_manufacturing) AS real_gdp_manufacturing,
        SUM(real_gdp_construction) AS real_gdp_construction,
        SUM(real_gdp_trade) AS real_gdp_trade,
        SUM(real_gdp_transportation) AS real_gdp_transportation,
        SUM(real_gdp_information) AS real_gdp_information,
        SUM(real_gdp_fire) AS real_gdp_fire,
        SUM(real_gdp_professional) AS real_gdp_professional,
        SUM(real_gdp_edu_health) AS real_gdp_edu_health,
        SUM(real_gdp_leisure) AS real_gdp_leisure,
        SUM(real_gdp_gov) AS real_gdp_gov
    FROM state_rows
    GROUP BY year
),
division_rollup AS (
    SELECT
        'division' AS benchmark_scope,
        'division:' || COALESCE(CAST(? AS VARCHAR), 'unknown') AS benchmark_geo_id,
        COALESCE(MAX(division_name), 'Division benchmark') AS benchmark_geo_name,
        year,
        SUM(qcew_private_emp_ag_mining) AS qcew_private_emp_ag_mining,
        SUM(qcew_private_emp_construction) AS qcew_private_emp_construction,
        SUM(qcew_private_emp_manufacturing) AS qcew_private_emp_manufacturing,
        SUM(qcew_private_emp_wholesale) AS qcew_private_emp_wholesale,
        SUM(qcew_private_emp_retail) AS qcew_private_emp_retail,
        SUM(qcew_private_emp_transport_util) AS qcew_private_emp_transport_util,
        SUM(qcew_private_emp_information) AS qcew_private_emp_information,
        SUM(qcew_private_emp_finance_real) AS qcew_private_emp_finance_real,
        SUM(qcew_private_emp_professional) AS qcew_private_emp_professional,
        SUM(qcew_private_emp_educ_health) AS qcew_private_emp_educ_health,
        SUM(qcew_private_emp_arts_accomm_food) AS qcew_private_emp_arts_accomm_food,
        SUM(qcew_private_emp_other_services) AS qcew_private_emp_other_services,
        SUM(real_gdp_natural_resources) AS real_gdp_natural_resources,
        SUM(real_gdp_manufacturing) AS real_gdp_manufacturing,
        SUM(real_gdp_construction) AS real_gdp_construction,
        SUM(real_gdp_trade) AS real_gdp_trade,
        SUM(real_gdp_transportation) AS real_gdp_transportation,
        SUM(real_gdp_information) AS real_gdp_information,
        SUM(real_gdp_fire) AS real_gdp_fire,
        SUM(real_gdp_professional) AS real_gdp_professional,
        SUM(real_gdp_edu_health) AS real_gdp_edu_health,
        SUM(real_gdp_leisure) AS real_gdp_leisure,
        SUM(real_gdp_gov) AS real_gdp_gov
    FROM state_rows
    WHERE CAST(? AS VARCHAR) IS NOT NULL
      AND division_id = CAST(? AS VARCHAR)
    GROUP BY year
)
SELECT *
FROM us_rollup
UNION ALL
SELECT *
FROM division_rollup
ORDER BY year, benchmark_scope;
