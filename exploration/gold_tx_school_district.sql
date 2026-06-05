-- Create Texas Unified School District Gold Data
-- This is made of metadata from TEA, Economic Disadvantage from TEA, Title 1 from DOE, and ACS
-- TEA and Title 1 has already been normalized

create or replace table patterns_in_place.gold.tx_isd_metrics as 
-- Create our base of ISDs
	-- We have 1,020 ISDs
with isd_base as (
select county_number,
	county_name,
	esc_region_served,
	district_number,
	nces_district_id,
	district_name,
	district_city,
	district_zip,
	district_type,
	year,
	district_enrollment_as_of_oct_2024 as enrollment,
	number_of_schools,
	avg_school_enrollment,
	allocations as title_1_allocations,
	round(allocations / district_enrollment_as_of_oct_2024, 2) as allocations_per_student,
	not_economically_disadvantaged_percent,
	economically_disadvantaged_percent 
from patterns_in_place.silver.tx_tea_district_metrics 
where district_type = 'INDEPENDENT'
),

-- Build ACS metrics for latest year
acs_metrics as (
select geo_level,
	geo_id,
	geo_name,
	year,
	population,
	LAG(population, 5) OVER (PARTITION BY geo_level, geo_id, geo_name ORDER BY year) AS population_lag5,
	(population - LAG(population, 5) OVER (PARTITION BY geo_level, geo_id, geo_name ORDER BY year)) / 
	LAG(population, 5) OVER (PARTITION BY geo_level, geo_id, geo_name ORDER BY year) as population_growth_5yr,
	median_age,
	median_income,
	child_poverty_rate,
	edu_no_higher_ed as no_higher_ed_share,
	households_w_children_share,
	hispanic_any_share,
	1 - racial_diversity_index as diversity_index -- Higher is more diverse
from patterns_in_place.silver.acs_tx_school_metrics
),

-- Joining NCES District ID to Geo ID - This works


joined_table as (
select isd.district_name,
	isd.county_number,
	isd.county_name,
	isd.esc_region_served,
	isd.district_city,
	isd.district_zip,
	isd.district_type,
	isd.nces_district_id,
	isd.district_number,
	isd.enrollment,
	percent_rank() over(order by isd.enrollment) as enrollment_pct_rank,
	isd.number_of_schools,
	isd.avg_school_enrollment,
	isd.title_1_allocations,
	isd.allocations_per_student,
	percent_rank() over(order by isd.allocations_per_student) as student_allocation_pct_rank,
	isd.economically_disadvantaged_percent,
--	acs.geo_name,
--	acs.year as acs_year,
	acs.population,
	acs.population_growth_5yr,
	acs.median_age,
	acs.median_income,
	acs.child_poverty_rate,
	percent_rank() over(order by acs.child_poverty_rate) as child_poverty_pct_rank, -- Higher Poverty is better
	acs.no_higher_ed_share,
	acs.households_w_children_share,
	acs.hispanic_any_share,
	acs.diversity_index
from isd_base isd 
left join acs_metrics acs 
	on isd.nces_district_id = acs.geo_id
where acs.year = '2023'
), 

	-- Check which of our metrics have NULLs, we will need separate CTEs to calculate them
	-- Econ Disadvantage & Pop Growth
--select count(district_name) as total_records, 
--count(enrollment) as enrollment_count,
--count(allocations_per_student) as allocation_count,
--count(economically_disadvantaged_percent) as econ_count,
--count(population_growth_5yr) as pop_growth_count,
--count(child_poverty_rate) as pov_rate_count
--from joined_table

econ_rank as (
select nces_district_id,
	economically_disadvantaged_percent,
	percent_rank() over(order by economically_disadvantaged_percent) as economic_disadvantaged_pct_rank
from joined_table 
where economically_disadvantaged_percent is not null
),

pop_growth_rank as (
select nces_district_id,
	population_growth_5yr,
	percent_rank() over(order by population_growth_5yr) as population_growth_pct_rank,
	NTILE(4) OVER (ORDER BY population_growth_5yr) AS pop_growth_quartile
from joined_table 
where population_growth_5yr is not null
)

select jt.district_name,
	county_number,
	county_name,
	esc_region_served,
	district_city,
	district_zip,
	district_type,
	jt.nces_district_id,
	district_number,
	enrollment,
	enrollment_pct_rank,
	number_of_schools,
	avg_school_enrollment,
	title_1_allocations,
	allocations_per_student,
	student_allocation_pct_rank,
	jt.economically_disadvantaged_percent / 100 as economically_disadvantaged_percent,
	economic_disadvantaged_pct_rank,
	population,
	jt.population_growth_5yr,
	population_growth_pct_rank,
	pop_growth_quartile,
	median_age,
	median_income,
	child_poverty_rate,
	child_poverty_pct_rank, -- Higher Poverty is better
	no_higher_ed_share,
	households_w_children_share,
	hispanic_any_share,
	diversity_index,
	(
  0.30 * COALESCE(enrollment_pct_rank, 0) +
  0.30 * COALESCE(student_allocation_pct_rank, 0) +
  0.20 * COALESCE(economic_disadvantaged_pct_rank, 0) +
  0.20 * COALESCE(child_poverty_pct_rank, 0)
) AS numerator,
(
  0.30 * (case when enrollment_pct_rank IS NOT NULL then 1 else 0 end) +
  0.30 * (case when student_allocation_pct_rank IS NOT NULL then 1 else 0 end) +
  0.20 * (case when economic_disadvantaged_pct_rank IS NOT NULL then 1 else 0 end) +
  0.20 * (case when child_poverty_pct_rank IS NOT NULL then 1 else 0 end)
) AS denom_weight,
CASE
    WHEN denom_weight = 0 THEN NULL
    ELSE 100 * numerator / denom_weight
  END AS lead_score,
  CASE 
  	WHEN pop_growth_quartile = 1 THEN lead_score - 5
  	WHEN pop_growth_quartile = 2 THEN lead_score
  	WHEN pop_growth_quartile = 3 THEN lead_score + 2
  	WHEN pop_growth_quartile = 4 THEN lead_score + 5
  	WHEN pop_growth_quartile IS NULL then lead_score
  	ELSE NULL
  END as lead_score_growth_boost,
  rank() over(order by lead_score desc) as lead_score_rank,
  rank() over(order by lead_score_growth_boost desc) as lead_score_growth_boost_rank
from joined_table jt  
left join econ_rank eco 
	on jt.nces_district_id = eco.nces_district_id
left join pop_growth_rank pop 
	on jt.nces_district_id = pop.nces_district_id;
	
	
select *
from patterns_in_place.gold.tx_isd_metrics 
where district_name = 'WYLIE ISD'
