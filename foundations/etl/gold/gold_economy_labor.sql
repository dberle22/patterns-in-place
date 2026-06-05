-- This script creates Gold Labor KPIs
	-- We use ACS as our Base and LAUS for unemployment figures

create or replace table patterns_in_place.gold.economics_labor_wide as 

with acs_base as ( 
select lower(geo_level) as geo_level,
	geo_id,
	geo_name,
	year, 
	pop_total,
	age_15_17 + age_18_24 + age_25_34 + age_35_44 + age_45_54 + age_55_64 + age_65_74 + age_85p as working_age_pop
	-- This needs to be updated to remove 15 year olds in the future
from patterns_in_place.silver.age_kpi 
),

laus as (
select lower(geo_level) as geo_level,
	geo_id,
	geo_name,
	period,
	labor_force,
	employed,
	unemployed,
	unemployment_rate_percent 
from patterns_in_place.silver.bls_laus_wide
),

growthes as (
select base.geo_level,
	base.geo_id,
	base.geo_name,
	base.year, 
	base.pop_total,
	working_age_pop,
	labor_force,
	labor_force / working_age_pop as lfpr,
	
	LAG((labor_force / working_age_pop), 1) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS lfpr_lag1,
	LAG((labor_force / working_age_pop), 5) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS lfpr_lag5,
	LAG((labor_force / working_age_pop), 10) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS lfpr_lag10,
	employed,
	employed / pop_total as jobs_to_pop_ratio,
	LAG((employed / pop_total), 1) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS jobs_to_pop_lag1,
	LAG((employed / pop_total), 5) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS jobs_to_pop_lag5,
	LAG((employed / pop_total), 10) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS jobs_to_pop_lag10,
	unemployed,
	unemployment_rate_percent / 100 as pct_unemployment_rate,
	LAG((unemployment_rate_percent / 100), 1) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS unemployment_rate_lag1

from acs_base base  
left join laus
	on base.geo_id = laus.geo_id
	and base.year = laus.period
	and lower(base.geo_level) = lower(laus.geo_level)
)

select geo_level,
	geo_id,
	geo_name,
	year, 
	pop_total,
	working_age_pop,
	labor_force,
	lfpr,
	CASE 
   	WHEN lfpr_lag5 > 0 THEN
        (lfpr - lfpr_lag5) / lfpr_lag5 
    ELSE NULL
	END AS lfpr_growth_5yr,
	CASE 
   	WHEN lfpr_lag5 > 0 THEN
        POWER(lfpr * 1.0 / lfpr_lag5, 1.0 / 5.0) - 1
    ELSE NULL
	END AS lfpr_cagr_5yr,
	employed,
	jobs_to_pop_ratio,
	unemployed,
	pct_unemployment_rate,
	pct_unemployment_rate - unemployment_rate_lag1 as unemployment_rate_change_1yr
from growthes
