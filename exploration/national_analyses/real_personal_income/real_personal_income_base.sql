-- This script is used to build the base to analyze real personal income by CBSA
-- We will get personal income from BEA CAINC1 and RPP from MARPP
with county_pop as (
select geo_level,
	geo_id, 
	pop_total
from metro_deep_dive.silver.age_kpi 
where geo_level = 'county'
and year = '2023'
),

county_mapping as (	
select cbsa.cbsa_code, 
	cbsa.cbsa_name,
	cbsa.cbsa_type,
	cbsa.county_name,
	cbsa.county_geoid,
	pop.pop_total,
	cbsa.state_name,
	cbsa.state_fips,
	st.census_region,
	st.census_division,
	row_number() over(partition by cbsa.cbsa_code order by pop.pop_total desc) as county_pop_rank
from metro_deep_dive.silver.xwalk_cbsa_county cbsa
left join metro_deep_dive.silver.xwalk_state_region st 
	on cbsa.state_fips = st.state_fips
left join county_pop pop 
	on cbsa.county_geoid = pop.geo_id
),

cbsa_metadata as (
select cbsa_code,
	cbsa_name,
	cbsa_type,
	state_name as primary_state,
	state_fips,
	census_region,
	census_division
from county_mapping
where county_pop_rank = 1
),

income as (
select cainc.geo_level,
	cainc.geo_id,
	cainc.geo_name,
	xw.cbsa_type,
	xw.state_fips,
	xw.primary_state,
	xw.census_region,
	xw.census_division,
	period,
	population,
	pi_total,
	pi_per_capita 
from metro_deep_dive.silver.bea_regional_cainc1_wide cainc
left join cbsa_metadata xw 
	on cainc.geo_id = xw.cbsa_code
where cainc.geo_level = 'cbsa'
),

-- Real Personal Income is already computed, we have RPP for all items and goods
-- We would need to bring more data to silver if we want to break it down another way
cbsa_rpp as (
select geo_level,
	geo_id,
	geo_name,
	period,
	rpp_real_pc_income,
	rpp_all_items,
	rpp_goods
from metro_deep_dive.silver.bea_regional_marpp_wide 
where geo_level = 'cbsa'
),

state_rpp as (
select geo_level,
	LEFT(geo_id, 2) as state_fips, -- We need to only take the first two digits
	geo_name, 
	period,
	rpp_real_pc_income,
	rpp_all_items,
	rpp_goods
from metro_deep_dive.silver.bea_regional_marpp_wide 
where geo_level = 'state'
),

-- Join CAINC1 and MARPP data
kpi_base as (
select inc.geo_level,
	inc.geo_id,
	inc.geo_name,
	inc.cbsa_type,
	inc.state_fips,
	inc.primary_state,
	inc.census_region,
	inc.census_division,
	inc.period,
	inc.population,
	inc.pi_total,
	inc.pi_per_capita,
	-- cbsa.rpp_real_pc_income as cbsa_real_pc_income, -- This looks wrong for some reason
	cbsa.rpp_all_items as cbsa_rpp_all_items,
	inc.pi_per_capita / (cbsa.rpp_all_items / 100) as cbsa_real_pc_income,
	cbsa.rpp_goods as cbsa_rpp_goods,
	-- state.rpp_real_pc_income as state_real_pc_income,
	state.rpp_all_items as state_rpp_all_items,
	inc.pi_per_capita / (state.rpp_all_items / 100) as state_real_pc_income,
	state.rpp_goods as state_rpp_goods,
	coalesce(cbsa_real_pc_income, state_real_pc_income) as real_pc_income,
	coalesce(cbsa.rpp_all_items, state.rpp_all_items) as rpp_all_items_coalesce
from income inc 
left join cbsa_rpp cbsa 
	on inc.geo_id = cbsa.geo_id 
	and inc.period = cbsa.period
left join state_rpp state 
	on inc.state_fips = state.state_fips 
	and inc.period = state.period
)

select geo_level,
	geo_id,
	period,
	geo_name,
	cbsa_type,
	state_fips,
	primary_state,
	census_region,
	census_division,
	population,
	pi_per_capita as nominal_pc_income,
	real_pc_income,
	(real_pc_income - pi_per_capita) / pi_per_capita as pc_real_change,
	rpp_all_items_coalesce as rpp_all_items,
	rank() over(partition by cbsa_type, period order by rpp_all_items_coalesce) as lowest_rpp_rank,
	rank() over(partition by cbsa_type, period order by pi_per_capita desc) as nominal_pc_income_rank,
	rank() over(partition by cbsa_type, period order by real_pc_income desc) as real_pc_income_rank,
	(rank() over(partition by cbsa_type, period order by real_pc_income desc)) - 
	(rank() over(partition by cbsa_type, period order by pi_per_capita desc)) as pc_real_rank_change
from kpi_base
order by pi_per_capita desc
