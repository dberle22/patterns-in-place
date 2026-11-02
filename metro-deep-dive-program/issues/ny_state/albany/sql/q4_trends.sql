-- Yearly series for the head-to-head (Q4h), 2012 on, for the CBSAs in __CBSA_CODES__:
-- ACS 5-year population (year = end year), BEA real GDP and employment, and BEA income per person.
SELECT 'cbsa' AS geo_level, geo_id, year, 'pop_total' AS metric_id, pop_total AS value
FROM gold.population_demographics WHERE lower(geo_level) = 'cbsa' AND geo_id IN (__CBSA_CODES__)
UNION ALL
SELECT 'cbsa', geo_id, year, 'real_gdp_total', real_gdp_total
FROM gold.economics_gdp_wide WHERE lower(geo_level) = 'cbsa' AND geo_id IN (__CBSA_CODES__)
UNION ALL
SELECT 'cbsa', geo_id, year, 'employed', employed
FROM gold.economics_gdp_wide WHERE lower(geo_level) = 'cbsa' AND geo_id IN (__CBSA_CODES__)
UNION ALL
SELECT 'cbsa', geo_id, year, 'calc_income_pc', calc_income_pc
FROM gold.economics_income_wide WHERE lower(geo_level) = 'cbsa' AND geo_id IN (__CBSA_CODES__)
ORDER BY metric_id, geo_id, year
