-- This script creates Gold Labor KPIs
	-- We use ACS as our Base and LAUS for unemployment figures.
	-- LEHD QWI now adds private labor-market dynamics and workforce composition
	-- on the same county / CBSA / state geography surface.
	-- Tract and ZCTA rows fall back to ACS labor metrics because LAUS does not
	-- publish those finer geographies.

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
where lower(geo_level) in ('county', 'cbsa', 'state', 'tract', 'zcta')
),

acs_labor as (
select
	lower(geo_level) as geo_level,
	geo_id,
	geo_name,
	year,
	pop_16plus,
	in_labor_force,
	employed,
	unemployed,
	unemp_rate
from patterns_in_place.silver.labor_kpi
where lower(geo_level) in ('tract', 'zcta')
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

qwi_total as (
select
	lower(geo_level) as geo_level,
	geo_id,
	geo_name,
	year,
	employment as qwi_private_emp,
	hires as qwi_private_hires,
	separations as qwi_private_separations,
	replacements as qwi_private_replacements,
	payroll as qwi_private_payroll,
	avg_earnings as qwi_private_avg_earnings,
	new_hire_avg_earnings as qwi_private_new_hire_avg_earnings,
	separation_avg_earnings as qwi_private_separation_avg_earnings,
	hire_rate as qwi_private_hire_rate,
	separation_rate as qwi_private_separation_rate,
	replacement_rate as qwi_private_replacement_rate
from patterns_in_place.silver.lehd_qwi
where lower(geo_level) in ('county', 'cbsa', 'state')
	and industry_code = '00'
	and demo_family = 'age'
	and demo_code = 'A00'
),

qwi_age as (
select
	lower(geo_level) as geo_level,
	geo_id,
	year,
	max(case when demo_code = 'A00' then employment end) as qwi_age_emp_total,
	max(case when demo_code = 'A01' then employment end) as qwi_emp_age_14_18,
	max(case when demo_code = 'A02' then employment end) as qwi_emp_age_19_21,
	max(case when demo_code = 'A03' then employment end) as qwi_emp_age_22_24,
	max(case when demo_code = 'A04' then employment end) as qwi_emp_age_25_34,
	max(case when demo_code = 'A05' then employment end) as qwi_emp_age_35_44,
	max(case when demo_code = 'A06' then employment end) as qwi_emp_age_45_54,
	max(case when demo_code = 'A07' then employment end) as qwi_emp_age_55_64,
	max(case when demo_code = 'A08' then employment end) as qwi_emp_age_65_99
from patterns_in_place.silver.lehd_qwi
where lower(geo_level) in ('county', 'cbsa', 'state')
	and industry_code = '00'
	and demo_family = 'age'
group by 1, 2, 3
),

qwi_education as (
select
	lower(geo_level) as geo_level,
	geo_id,
	year,
	sum(case when demo_code in ('E1', 'E2', 'E3', 'E4') then employment else 0 end) as qwi_edu_emp_known_total,
	max(case when demo_code = 'E1' then employment end) as qwi_emp_edu_less_than_hs,
	max(case when demo_code = 'E2' then employment end) as qwi_emp_edu_hs,
	max(case when demo_code = 'E3' then employment end) as qwi_emp_edu_some_college,
	max(case when demo_code = 'E4' then employment end) as qwi_emp_edu_bachelors_plus,
	max(case when demo_code = 'E5' then employment end) as qwi_emp_edu_not_available
from patterns_in_place.silver.lehd_qwi
where lower(geo_level) in ('county', 'cbsa', 'state')
	and industry_code = '00'
	and demo_family = 'education'
group by 1, 2, 3
),

labor_surface as (
select
	base.geo_level,
	base.geo_id,
	base.geo_name,
	base.year,
	base.pop_total,
	case
		when base.geo_level in ('tract', 'zcta') and acs_labor.pop_16plus is not null
			then acs_labor.pop_16plus
		else base.working_age_pop
	end as working_age_pop,
	case
		when base.geo_level in ('tract', 'zcta') then acs_labor.in_labor_force
		else laus.labor_force
	end as labor_force,
	case
		when base.geo_level in ('tract', 'zcta') then acs_labor.employed
		else laus.employed
	end as employed,
	case
		when base.geo_level in ('tract', 'zcta') then acs_labor.unemployed
		else laus.unemployed
	end as unemployed,
	case
		when base.geo_level in ('tract', 'zcta') then acs_labor.unemp_rate
		else laus.unemployment_rate_percent / 100
	end as pct_unemployment_rate,
	qwi.qwi_private_emp,
	qwi.qwi_private_hires,
	qwi.qwi_private_separations,
	qwi.qwi_private_replacements,
	qwi.qwi_private_payroll,
	qwi.qwi_private_avg_earnings,
	qwi.qwi_private_new_hire_avg_earnings,
	qwi.qwi_private_separation_avg_earnings,
	qwi.qwi_private_hire_rate,
	qwi.qwi_private_separation_rate,
	qwi.qwi_private_replacement_rate,
	qwi_age.qwi_age_emp_total,
	qwi_age.qwi_emp_age_14_18,
	qwi_age.qwi_emp_age_19_21,
	qwi_age.qwi_emp_age_22_24,
	qwi_age.qwi_emp_age_25_34,
	qwi_age.qwi_emp_age_35_44,
	qwi_age.qwi_emp_age_45_54,
	qwi_age.qwi_emp_age_55_64,
	qwi_age.qwi_emp_age_65_99,
	qwi_education.qwi_edu_emp_known_total,
	qwi_education.qwi_emp_edu_less_than_hs,
	qwi_education.qwi_emp_edu_hs,
	qwi_education.qwi_emp_edu_some_college,
	qwi_education.qwi_emp_edu_bachelors_plus,
	qwi_education.qwi_emp_edu_not_available
from acs_base base
left join acs_labor
	on base.geo_id = acs_labor.geo_id
	and base.year = acs_labor.year
	and lower(base.geo_level) = lower(acs_labor.geo_level)
left join laus
	on base.geo_id = laus.geo_id
	and base.year = laus.period
	and lower(base.geo_level) = lower(laus.geo_level)
left join qwi_total qwi
	on base.geo_id = qwi.geo_id
	and base.year = qwi.year
	and lower(base.geo_level) = lower(qwi.geo_level)
left join qwi_age
	on base.geo_id = qwi_age.geo_id
	and base.year = qwi_age.year
	and lower(base.geo_level) = lower(qwi_age.geo_level)
left join qwi_education
	on base.geo_id = qwi_education.geo_id
	and base.year = qwi_education.year
	and lower(base.geo_level) = lower(qwi_education.geo_level)
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
	
	LAG((labor_force / working_age_pop), 1) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY base.year) AS lfpr_lag1,
	LAG((labor_force / working_age_pop), 5) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY base.year) AS lfpr_lag5,
	LAG((labor_force / working_age_pop), 10) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY base.year) AS lfpr_lag10,
	employed,
	employed / pop_total as jobs_to_pop_ratio,
	LAG((employed / pop_total), 1) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY base.year) AS jobs_to_pop_lag1,
	LAG((employed / pop_total), 5) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY base.year) AS jobs_to_pop_lag5,
	LAG((employed / pop_total), 10) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY base.year) AS jobs_to_pop_lag10,
	unemployed,
	pct_unemployment_rate,
	LAG(pct_unemployment_rate, 1) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY base.year) AS unemployment_rate_lag1,
	qwi_private_emp,
	qwi_private_hires,
	qwi_private_separations,
	qwi_private_replacements,
	qwi_private_payroll,
	qwi_private_avg_earnings,
	qwi_private_new_hire_avg_earnings,
	qwi_private_separation_avg_earnings,
	qwi_private_hire_rate,
	qwi_private_separation_rate,
	qwi_private_replacement_rate,
	qwi_age_emp_total,
	qwi_emp_age_14_18,
	qwi_emp_age_19_21,
	qwi_emp_age_22_24,
	qwi_emp_age_25_34,
	qwi_emp_age_35_44,
	qwi_emp_age_45_54,
	qwi_emp_age_55_64,
	qwi_emp_age_65_99,
	qwi_edu_emp_known_total,
	qwi_emp_edu_less_than_hs,
	qwi_emp_edu_hs,
	qwi_emp_edu_some_college,
	qwi_emp_edu_bachelors_plus,
	qwi_emp_edu_not_available

from labor_surface base
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
	pct_unemployment_rate - unemployment_rate_lag1 as unemployment_rate_change_1yr,
	qwi_private_emp,
	qwi_private_hires,
	qwi_private_separations,
	qwi_private_replacements,
	qwi_private_payroll,
	qwi_private_avg_earnings,
	qwi_private_new_hire_avg_earnings,
	qwi_private_separation_avg_earnings,
	qwi_private_hire_rate,
	qwi_private_separation_rate,
	qwi_private_replacement_rate,
	qwi_emp_age_14_18 / nullif(qwi_age_emp_total, 0) as qwi_pct_emp_age_14_18,
	qwi_emp_age_19_21 / nullif(qwi_age_emp_total, 0) as qwi_pct_emp_age_19_21,
	qwi_emp_age_22_24 / nullif(qwi_age_emp_total, 0) as qwi_pct_emp_age_22_24,
	qwi_emp_age_25_34 / nullif(qwi_age_emp_total, 0) as qwi_pct_emp_age_25_34,
	qwi_emp_age_35_44 / nullif(qwi_age_emp_total, 0) as qwi_pct_emp_age_35_44,
	qwi_emp_age_45_54 / nullif(qwi_age_emp_total, 0) as qwi_pct_emp_age_45_54,
	qwi_emp_age_55_64 / nullif(qwi_age_emp_total, 0) as qwi_pct_emp_age_55_64,
	qwi_emp_age_65_99 / nullif(qwi_age_emp_total, 0) as qwi_pct_emp_age_65_99,
	qwi_emp_edu_less_than_hs / nullif(qwi_edu_emp_known_total, 0) as qwi_pct_emp_edu_less_than_hs,
	qwi_emp_edu_hs / nullif(qwi_edu_emp_known_total, 0) as qwi_pct_emp_edu_hs,
	qwi_emp_edu_some_college / nullif(qwi_edu_emp_known_total, 0) as qwi_pct_emp_edu_some_college,
	qwi_emp_edu_bachelors_plus / nullif(qwi_edu_emp_known_total, 0) as qwi_pct_emp_edu_bachelors_plus,
	qwi_emp_edu_not_available / nullif(qwi_private_emp, 0) as qwi_pct_emp_edu_not_available
from growthes
