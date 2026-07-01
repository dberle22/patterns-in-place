-- Population & Demographics Gold Base
-- This table contains a series of demographic KPIs, built mainly from ACS
-- The KPIs are organized into the following subcategories: Population Size & Growth, Age Structure, Race & Diversity, Education, Household & Living Patterns
-- This table is sourced from ACS Silver layer tables

create or replace table patterns_in_place.gold.population_demographics as 
-- Select Population and Age based KPIs
WITH pop as (
SELECT geo_level,
	geo_id,
	geo_name,
	year,
	pop_total,
	LAG(pop_total, 1) OVER (PARTITION BY geo_level, geo_id ORDER BY year) AS pop_lag1,
	LAG(pop_total, 3) OVER (PARTITION BY geo_level, geo_id ORDER BY year) AS pop_lag3,
	LAG(pop_total, 5) OVER (PARTITION BY geo_level, geo_id ORDER BY year) AS pop_lag5,
	LAG(pop_total, 10) OVER (PARTITION BY geo_level, geo_id ORDER BY year) AS pop_lag10,
	CASE 
   	WHEN pop_lag1 > 0 THEN
        (pop_total - pop_lag1) / pop_lag1 
    ELSE NULL
	END AS pop_growth_1yr,
	CASE 
   	WHEN pop_lag3 > 0 THEN
        (pop_total - pop_lag3) / pop_lag3
    ELSE NULL
	END AS pop_growth_3yr,
	CASE 
   	WHEN pop_lag5 > 0 THEN
        (pop_total - pop_lag5) / pop_lag5
    ELSE NULL
	END AS pop_growth_5yr,
	CASE 
   	WHEN pop_lag10 > 0 THEN
        (pop_total - pop_lag10) / pop_lag10
    ELSE NULL
	END AS pop_growth_10yr,
	CASE 
   	WHEN pop_lag3 > 0 THEN
        POWER(pop_total * 1.0 / pop_lag3, 1.0 / 5.0) - 1
    ELSE NULL
	END AS pop_cagr_3yr,
	CASE 
   	WHEN pop_lag5 > 0 THEN
        POWER(pop_total * 1.0 / pop_lag5, 1.0 / 5.0) - 1
    ELSE NULL
	END AS pop_cagr_5yr,
	CASE 
    WHEN pop_lag10 > 0 THEN
        POWER(pop_total * 1.0 / pop_lag5, 1.0 / 10.0) - 1
    ELSE NULL
	END AS pop_cagr_10yr,
	median_age,
	(age_0_4 + age_5_14 + age_15_17) / pop_total AS pct_age_under_18,
	(age_18_24 + age_25_34 + age_35_44 + age_45_54 + age_55_64) / pop_total AS pct_age_18_64,
	(age_65_74 + age_75_84 + age_85p) / pop_total AS pct_age_over_64,
	(age_0_4 + age_5_14 + age_15_17 + age_65_74 + age_75_84 + age_85p) / (age_25_34 + age_35_44 + age_45_54) AS dependents_per_worker,
	youth_dependency,
	old_age_dependency,
	(age_0_4 + age_5_14) / (age_65_74 + age_75_84 + age_85p) AS aging_index
FROM patterns_in_place.silver.age_kpi 
),

-- Select Race based KPIs
race as (
SELECT geo_level,
	geo_id,
	geo_name,
	year,
	pct_white_nh,
	pct_black_nh,
	pct_aian_nh,
	pct_asian_nh,
	pct_nhpi_nh ,
	pct_other_nh,
	pct_two_plus_nh,
	pct_hispanic,
	diversity_index
FROM patterns_in_place.silver.race_kpi 
),

-- Select Education based KPIs
education as (
SELECT geo_level,
	geo_id,
	geo_name,
	year,
	pct_lt_hs_25p + pct_hs_ged_25p as pct_hs_or_less,
	pct_ba_25p as pct_ba,
	pct_ba_25p + pct_ma_plus_25p as pct_ba_plus,
	LAG(pct_ba_25p + pct_ma_plus_25p, 3) OVER (PARTITION BY geo_level, geo_id ORDER BY year) AS pct_ba_plus_lag3,
	LAG(pct_ba_25p + pct_ma_plus_25p, 5) OVER (PARTITION BY geo_level, geo_id ORDER BY year) AS pct_ba_plus_lag5,
	pct_ma_plus_25p as pct_grad_plus
FROM patterns_in_place.silver.education_kpi 
)

-- Final Select
select p.geo_level,
	p.geo_id,
	p.geo_name,
	p.year,
	p.pop_total,
	pop_growth_1yr,
	pop_growth_3yr,
	pop_growth_5yr,
	pop_growth_10yr,
	pop_cagr_3yr,
	pop_cagr_5yr,
	pop_cagr_10yr,
	median_age,
	pct_age_under_18,
	pct_age_18_64,
	pct_age_over_64,
	dependents_per_worker,
	youth_dependency,
	old_age_dependency,
	aging_index,
	pct_white_nh,
	pct_black_nh,
	pct_aian_nh,
	pct_asian_nh,
	pct_nhpi_nh ,
	pct_other_nh,
	pct_two_plus_nh,
	pct_hispanic,
	diversity_index,
	pct_hs_or_less,
	pct_ba,
	pct_ba_plus,
	CASE
		WHEN pct_ba_plus_lag3 IS NOT NULL
			AND NOT isnan(pct_ba_plus)
			AND NOT isnan(pct_ba_plus_lag3)
			THEN pct_ba_plus - pct_ba_plus_lag3
		ELSE NULL
	END AS pct_ba_plus_change_3yr,
	CASE
		WHEN pct_ba_plus_lag5 IS NOT NULL
			AND NOT isnan(pct_ba_plus)
			AND NOT isnan(pct_ba_plus_lag5)
			THEN pct_ba_plus - pct_ba_plus_lag5
		ELSE NULL
	END AS pct_ba_plus_change_5yr,
	pct_grad_plus
from pop p 
left join race r 
	on p.geo_level = r.geo_level 
	and p.geo_id = r.geo_id 
	and p.year = r.year
left join education e 
	on p.geo_level = e.geo_level 
	and p.geo_id = e.geo_id 
	and p.year = e.year
