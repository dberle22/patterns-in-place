-- This script creates Gold Income KPIs

-- BEA/BLS is at the State, CBSA, County level - We can roll up to Division, Region, US (In Silver)
-- We will use ACS Pop as our denom
-- We need to get CPI for Real Income

create or replace table patterns_in_place.gold.economics_income_wide as 
-- Let's start with a base from ACS
	-- Total Pop, Median Income, Per Capita Income, Poverty Rate, Gini Index, Household Incomes
with acs_base as ( 
select lower(geo_level) as geo_level,
	geo_id,
	geo_name,
	year, 
	pop_total
from patterns_in_place.silver.age_kpi 
),

acs_income as (
select lower(geo_level) as geo_level,
	geo_id,
	geo_name,
	year, 
	median_hh_income,
	per_capita_income,
	pov_rate,
	LAG(pov_rate, 1) OVER (PARTITION BY lower(geo_level), geo_id, geo_name ORDER BY year) AS pov_rate_lag1,
	LAG(pov_rate, 5) OVER (PARTITION BY lower(geo_level), geo_id, geo_name ORDER BY year) AS pov_rate_lag5,
	gini_index,
	pct_hh_lt25k,
	pct_hh_25k_50k,
	pct_hh_50k_100k,
	pct_hh_100k_plus
from patterns_in_place.silver.income_kpi 
),



-- Income is sourced from CAINC from BEA, CAINC1 is high level and CAINC4 is more detailed
-- We will use CAINC1 and ACS for Median Income
-- We will use CAINC4 to get Wage as a % of Earnings

cainc1 as (
select cainc1.geo_level,
	cainc1.geo_id,
	cainc1.geo_name,
	cainc1.period,
	cainc1.population,
	base.pop_total,
	ABS(cainc1.population - base.pop_total) / base.pop_total AS pop_diff_pct,
	pi_total,
	LAG(pi_total, 1) OVER (PARTITION BY cainc1.geo_level, cainc1.geo_id, cainc1.geo_name ORDER BY year) AS pi_total_lag1,
	LAG(pi_total, 5) OVER (PARTITION BY cainc1.geo_level, cainc1.geo_id, cainc1.geo_name ORDER BY year) AS pi_total_lag5,
	LAG(pi_total, 10) OVER (PARTITION BY cainc1.geo_level, cainc1.geo_id, cainc1.geo_name ORDER BY year) AS pi_total_lag10,
	pi_total / base.pop_total as calc_income_pc,
	LAG(calc_income_pc, 1) OVER (PARTITION BY cainc1.geo_level, cainc1.geo_id, cainc1.geo_name ORDER BY year) AS pi_pc_lag1,
	LAG(calc_income_pc, 5) OVER (PARTITION BY cainc1.geo_level, cainc1.geo_id, cainc1.geo_name ORDER BY year) AS pi_pc_lag5,
	LAG(calc_income_pc, 10) OVER (PARTITION BY cainc1.geo_level, cainc1.geo_id, cainc1.geo_name ORDER BY year) AS pi_pc_lag10,
	pi_per_capita
from patterns_in_place.silver.bea_regional_cainc1_wide cainc1
inner join acs_base base 
	on cainc1.geo_id = base.geo_id
	and cainc1.period = base.year
	and lower(cainc1.geo_level) = lower(base.geo_level)
),

cainc4 as (
select geo_level,
	geo_id,
	geo_name,
	period,
	pi_wages_salary
from patterns_in_place.silver.bea_regional_cainc4_wide
)


select base.geo_level,
	base.geo_id,
	base.geo_name,
	base.year, 
	base.pop_total,
	median_hh_income,
	per_capita_income as acs_income_pc,
	pov_rate,
	CASE
		WHEN pov_rate_lag1 IS NOT NULL
			AND NOT isnan(pov_rate)
			AND NOT isnan(pov_rate_lag1)
			THEN pov_rate - pov_rate_lag1
		ELSE NULL
	END AS pov_rate_change_1yr,
	CASE
		WHEN pov_rate_lag5 IS NOT NULL
			AND NOT isnan(pov_rate)
			AND NOT isnan(pov_rate_lag5)
			THEN pov_rate - pov_rate_lag5
		ELSE NULL
	END AS pov_rate_change_5yr,
	gini_index,
	pi_total,
	calc_income_pc,
	CASE 
   	WHEN pi_pc_lag1 > 0 THEN
        (calc_income_pc - pi_pc_lag1) / pi_pc_lag1 
    ELSE NULL
	END AS income_pc_growth_1yr,
	CASE 
   	WHEN pi_pc_lag5 > 0 THEN
        (calc_income_pc - pi_pc_lag5) / pi_pc_lag5 
    ELSE NULL
	END AS income_pc_growth_5yr,
	CASE 
   	WHEN pi_pc_lag5 > 0 THEN
        POWER(calc_income_pc * 1.0 / pi_pc_lag5, 1.0 / 5.0) - 1
    ELSE NULL
	END AS income_pc_cagr_5yr,
	CASE 
   	WHEN pi_pc_lag10 > 0 THEN
        (calc_income_pc - pi_pc_lag10) / pi_pc_lag10
    ELSE NULL
	END AS income_pc_growth_10yr,
	CASE 
   	WHEN pi_pc_lag10 > 0 THEN
        POWER(calc_income_pc * 1.0 / pi_pc_lag10, 1.0 / 10) - 1
    ELSE NULL
	END AS income_pc_cagr_10yr,
	pi_wages_salary,
	pi_wages_salary / pi_total as pi_wage_share
from acs_base base 
left join acs_income inc 
	on base.geo_id = inc.geo_id
	and base.year = inc.year
	and lower(base.geo_level) = lower(inc.geo_level)
left join cainc1 
	on base.geo_id = cainc1.geo_id
	and base.year = cainc1.period
	and lower(base.geo_level) = lower(cainc1.geo_level)
left join cainc4
	on base.geo_id = cainc4.geo_id
	and base.year = cainc4.period
	and lower(base.geo_level) = lower(cainc4.geo_level)
-- where lower(base.geo_level) in ('state', 'cbsa', 'county')
-- Still need to add in RPP


-- Seems like PR, Hawaii, and Virginia are missing for some reason
