-- Economics KPIs
-- Income: BEA + ACS
-- GDP
-- Labor
-- Industry Structure

-- BEA/BLS is at the State, CBSA, County level - We can roll up to Division, Region, US (In Silver)

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
),

-- For GDP we need to select the correct variables
	-- We're missing some Vars in Silver that we should check
cagdp2 as (
select geo_level,
	geo_id,
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
select geo_level,
	geo_id,
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
)

-- Create high level economy metrics, using ACS as our base
	-- ACS Base, ACS Income,
	-- BEA Income, GDP
	-- BLS Employment
select base.geo_level,
	base.geo_id,
	base.geo_name,
	base.year, 
	base.pop_total,
	median_hh_income,
	per_capita_income as acs_income_pc,
	pov_rate,
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
   	WHEN pi_pc_lag10 > 0 THEN
        (calc_income_pc - pi_pc_lag10) / pi_pc_lag10
    ELSE NULL
	END AS income_pc_growth_10yr,
	pi_wages_salary,
	pi_wages_salary / pi_total as pi_wage_share,
	cagdp2.gdp_total,
	cagdp2.gdp_total / base.pop_total as gdp_per_capita,
	cagdp9.real_gdp_total,
	cagdp9.real_gdp_total / base.pop_total as real_gdp_per_capita,
	labor_force,
	employed,
	unemployed,
	unemployment_rate_percent
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
left join cagdp2
	on base.geo_id = cagdp2.geo_id
	and base.year = cagdp2.period
	and lower(base.geo_level) = lower(cagdp2.geo_level)
left join cagdp9
	on base.geo_id = cagdp9.geo_id
	and base.year = cagdp9.period
	and lower(base.geo_level) = lower(cagdp2.geo_level)
left join laus
	on base.geo_id = laus.geo_id
	and base.year = laus.period
	and lower(base.geo_level) = lower(laus.geo_level)
where base.geo_level = 'county'


-- Main Questions
	-- BEA: Do we use ACS or BEA Population to calculate Per Capita - Use ACS as Base, calculate the diff between ACS and BEA as a check
	-- MARPP: We need to create mappings to use State to backfill for Counties and CBSAs without RPP
		-- Let's create a Gold table that has these updated RPPs for Counties and CBSAs with the backfills from State
	-- MARPP: Do we use the Price Deflator for Real Incomes? 
		-- The suggestion is to use RPP All Items, then ingest CPI
	-- What year is Real GDP pegged at?
		-- BEA uses 2017 Chained Dollars - we should keep as is
	-- For Labor Force Participation we need the working age population, how do we define? 18-64? 16-64?
		-- Use 16+, we will need to refactor our Silver Layer to 16-17 separate from 15-17
	-- Do we have States or Counties missing from any of our tables?

-- Join Income to MARPP to get Real Income
	-- MARPP is only at CBSA and State
	-- For County, we should first mapp on CBSA, then go to CBSA
select inc.geo_level,
	inc.geo_id,
	inc.geo_name,
	inc.period,
	inc.population,
	inc.pi_total,
	inc.pi_per_capita,
	rpp.rpp_real_personal_income,
	rpp.rpp_real_pc_income,
	rpp.rpp_all_items,
	rpp.rpp_price_deflator
from patterns_in_place.silver.bea_regional_cainc1_wide inc
left join patterns_in_place.silver.bea_regional_marpp_wide rpp 
	on inc.geo_id = rpp.geo_id 
	and inc.period = rpp.period
where inc.geo_level = 'cbsa'


-- We need to deep dive into RPP Consumption
-- Use RPP Price Deflator to get Real Personal Income
-- We need to create our County level RPPs, if a CBSA doesn't have RPP we will use the state values

select distinct geo_level
from patterns_in_place.silver.bea_regional_marpp_wide