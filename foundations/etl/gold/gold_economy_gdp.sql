-- This script creates Gold GDP KPIs
	-- GDP PC, GDP Real PC, GDP Growth, Productivity

create or replace table patterns_in_place.gold.economics_gdp_wide as 

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
	gini_index,
	pct_hh_lt25k,
	pct_hh_25k_50k,
	pct_hh_50k_100k,
	pct_hh_100k_plus
from patterns_in_place.silver.income_kpi 
),

-- For GDP we need to select the correct variables
	-- We're missing some Vars in Silver that we should check
cagdp2 as (
select lower(geo_level) as geo_level,
	case
		when lower(geo_level) = 'state'
			and length(geo_id) = 5
			and substr(geo_id, 3, 3) = '000'
			then substr(geo_id, 1, 2)
		else geo_id
	end as geo_id,
	geo_name,
	period, 
	gdp_total,
	gdp_private,
	gdp_private / gdp_total as pct_gdp_private,
	gdp_gov_enterprises,
	gdp_gov_enterprises / gdp_total as pct_gdp_gov,
	gdp_natural_resources_all, -- Ag and Mining
	gdp_natural_resources_all / gdp_total as pct_gdp_natural_resources_all,
	gdp_utilities,
	gdp_utilities / gdp_total as pct_gdp_utilities,
	gdp_transportation,
	gdp_transportation / gdp_total as pct_gdp_transportation,
	gdp_trade_all, -- Retail and Wholesale trade
	gdp_trade_all / gdp_total as pct_gdp_trade_all,
	gdp_manufacturing_all, 
	gdp_manufacturing_all / gdp_total as pct_gdp_manufacturing_all,
	gdp_construction,
	gdp_construction / gdp_total as pct_gdp_construction,
	gdp_information,
	gdp_information / gdp_total as pct_gdp_information,
	gdp_finance_insurance + gdp_real_estate as gdp_fire, -- Finance, Insurance, Real Estate
	(gdp_finance_insurance + gdp_real_estate) / gdp_total as pct_gdp_fire,
	gdp_professional_scientific + gdp_professional_management + gdp_professional_admin_support as 
	gdp_professional_all, -- Science, Management, Admin Support
	(gdp_professional_scientific + gdp_professional_management + gdp_professional_admin_support) / gdp_total as 
	pct_gdp_professional_all,
	gdp_education_all as gdp_edu_health, -- Education and Health
	gdp_education_all / gdp_total as pct_gdp_edu_health,
	-- gdp_health,
	gdp_arts_entertainment + gdp_accomodation_food as
	gdp_tourism, -- Art, Entertainment, Accomidations, Food
	(gdp_arts_entertainment + gdp_accomodation_food) / gdp_total as pct_gdp_tourism,
	gdp_other,
	gdp_other / gdp_total as pct_gdp_total
from patterns_in_place.silver.bea_regional_cagdp2_wide
),

-- Real GDP
cagdp9 as (
select lower(geo_level) as geo_level,
	case
		when lower(geo_level) = 'state'
			and length(geo_id) = 5
			and substr(geo_id, 3, 3) = '000'
			then substr(geo_id, 1, 2)
		else geo_id
	end as geo_id,
	geo_name,
	period, 
	real_gdp_total,
	real_gdp_private,
	real_gdp_private / real_gdp_total as pct_real_gdp_private,
	real_gdp_gov_enterprises,
	real_gdp_gov_enterprises / real_gdp_total as pct_real_gdp_gov,
	real_gdp_natural_resources_all, -- Ag and Mining
	real_gdp_natural_resources_all / real_gdp_total as pct_real_gdp_natural_resources_all,
	real_gdp_utilities,
	real_gdp_utilities / real_gdp_total as pct_real_gdp_utilities,
	real_gdp_transportation,
	real_gdp_transportation / real_gdp_total as pct_real_gdp_transportation,
	real_gdp_trade_all, -- Retail and Wholesale trade
	real_gdp_trade_all / real_gdp_total as pct_real_gdp_trade_all,
	real_gdp_manufacturing_all, 
	real_gdp_manufacturing_all / real_gdp_total as pct_real_gdp_manufacturing_all,
	real_gdp_construction,
	real_gdp_construction / real_gdp_total as pct_real_gdp_construction,
	real_gdp_information,
	real_gdp_information / real_gdp_total as pct_real_gdp_information,
	real_gdp_finance_insurance + real_gdp_real_estate as real_gdp_fire, -- Finance, Insurance, Real Estate
	(real_gdp_finance_insurance + real_gdp_real_estate) / real_gdp_total as pct_real_gdp_fire,
	real_gdp_professional_scientific + real_gdp_professional_management + real_gdp_professional_admin_support as 
	real_gdp_professional_all, -- Science, Management, Admin Support
	(real_gdp_professional_scientific + real_gdp_professional_management + real_gdp_professional_admin_support) / real_gdp_total as 
	pct_real_gdp_professional_all,
	real_gdp_education_all as real_gdp_edu_health, -- Education and Health
	real_gdp_education_all / real_gdp_total as pct_real_gdp_edu_health,
	-- gdp_health,
	real_gdp_arts_entertainment + real_gdp_accomodation_food as
	real_gdp_tourism, -- Art, Entertainment, Accomidations, Food
	(real_gdp_arts_entertainment + real_gdp_accomodation_food) / real_gdp_total as pct_real_gdp_tourism,
	real_gdp_other,
	real_gdp_other / real_gdp_total as pct_real_gdp_total
from patterns_in_place.silver.bea_regional_cagdp9_wide
),

-- Get Employment from LAUS
laus as (
select geo_level,
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
	cagdp2.gdp_total as nominal_gdp_total,
	LAG(cagdp2.gdp_total, 1) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS gdp_total_lag1,
	LAG(cagdp2.gdp_total, 5) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS gdp_total_lag5,
	LAG(cagdp2.gdp_total, 10) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS gdp_total_lag10,
	cagdp2.gdp_total / base.pop_total as nominal_gdp_pc,
	LAG((cagdp2.gdp_total / base.pop_total), 1) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS nominal_gdp_pc_lag1,
	LAG((cagdp2.gdp_total / base.pop_total), 5) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS nominal_gdp_pc_lag5,
	LAG((cagdp2.gdp_total / base.pop_total), 10) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS nominal_gdp_pc_lag10,
	cagdp9.real_gdp_total,
	LAG(cagdp9.real_gdp_total, 1) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS real_gdp_total_lag1,
	LAG(cagdp9.real_gdp_total, 5) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS real_gdp_total_lag5,
	LAG(cagdp9.real_gdp_total, 10) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS real_gdp_total_lag10,
	cagdp9.real_gdp_total / base.pop_total as real_gdp_pc,
	LAG( (cagdp9.real_gdp_total / base.pop_total), 1) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS real_gdp_pc_lag1,
	LAG((cagdp9.real_gdp_total / base.pop_total), 5) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS real_gdp_pc_lag5,
	LAG((cagdp9.real_gdp_total / base.pop_total), 10) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS real_gdp_pc_lag10,
	laus.employed,
	cagdp9.real_gdp_total / laus.employed as productivity_index,
	LAG( (cagdp9.real_gdp_total / laus.employed), 1) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS productivity_lag1,
	LAG((cagdp9.real_gdp_total / laus.employed), 5) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS productivity_lag5,
	LAG((cagdp9.real_gdp_total / laus.employed), 10) OVER (PARTITION BY base.geo_level, base.geo_id, base.geo_name ORDER BY year) AS productivity_lag10,
	
from acs_base base 
left join cagdp2
	on base.geo_id = cagdp2.geo_id
	and base.year = cagdp2.period
	and lower(base.geo_level) = lower(cagdp2.geo_level)
left join cagdp9
	on base.geo_id = cagdp9.geo_id
	and base.year = cagdp9.period
	and lower(base.geo_level) = lower(cagdp9.geo_level)
left join laus
	on base.geo_id = laus.geo_id
	and base.year = laus.period
	and lower(base.geo_level) = lower(laus.geo_level)

)

-- Perform our final select and calculate new rates
select geo_level,
	geo_id,
	geo_name,
	year, 
	pop_total,
	
	-- Nominal GDP
	nominal_gdp_total,
	CASE 
   	WHEN gdp_total_lag5 > 0 THEN
        (nominal_gdp_total - gdp_total_lag5) / gdp_total_lag5 
    ELSE NULL
	END AS nominal_gdp_growth_5yr,
	CASE 
   	WHEN gdp_total_lag5 > 0 THEN
        POWER(nominal_gdp_total * 1.0 / gdp_total_lag5, 1.0 / 5.0) - 1
    ELSE NULL
	END AS nominal_gdp_cagr_5yr,
	nominal_gdp_pc,
	CASE 
   	WHEN nominal_gdp_pc_lag5 > 0 THEN
        (nominal_gdp_pc - nominal_gdp_pc_lag5) / nominal_gdp_pc_lag5 
    ELSE NULL
	END AS nominal_gdp_pc_growth_5yr,
	CASE 
   	WHEN nominal_gdp_pc_lag5 > 0 THEN
        POWER(nominal_gdp_pc * 1.0 / nominal_gdp_pc_lag5, 1.0 / 5.0) - 1
    ELSE NULL
	END AS nominal_gdp_pc_cagr_5yr,
	
	-- Real GDP
	real_gdp_total,
	CASE 
   	WHEN real_gdp_total_lag5 > 0 THEN
        (real_gdp_total - real_gdp_total_lag5) / real_gdp_total_lag5 
    ELSE NULL
	END AS real_gdp_growth_5yr,
	CASE 
   	WHEN real_gdp_total_lag5 > 0 THEN
        POWER(real_gdp_total * 1.0 / real_gdp_total_lag5, 1.0 / 5.0) - 1
    ELSE NULL
	END AS real_gdp_cagr_5yr,
	
	real_gdp_pc,
	CASE 
   	WHEN real_gdp_pc_lag5 > 0 THEN
        (real_gdp_pc - real_gdp_pc_lag5) / real_gdp_pc_lag5 
    ELSE NULL
	END AS real_gdp_pc_growth_5yr,
	CASE 
   	WHEN real_gdp_pc_lag5 > 0 THEN
        POWER(real_gdp_pc * 1.0 / real_gdp_pc_lag5, 1.0 / 5.0) - 1
    ELSE NULL
	END AS real_gdp_pc_cagr_5yr,
	
	employed,
	productivity_index,
	CASE 
   	WHEN productivity_lag5 > 0 THEN
        (productivity_index - productivity_lag5) / productivity_lag5 
    ELSE NULL
	END AS productivity_growth_5yr,
	CASE 
   	WHEN productivity_lag5 > 0 THEN
        POWER(productivity_index * 1.0 / productivity_lag5, 1.0 / 5.0) - 1
    ELSE NULL
	END AS productivity_cagr_5yr
	
from growthes
