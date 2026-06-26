-- App-serving CBSA mart for the Area Explorer surfaces.
-- This mart is intentionally narrower than gold and focuses on the KPI set
-- we actually want to expose in the explorer UI today.

create schema if not exists mart_area_explorer;

-- ---------------------------------------------------------------------------
-- CBSA profile-year row model
--
-- This table is the place-first read layer for the profile panel, selected-CBSA
-- context, and the internal Intelligence tab. Intelligence outputs are
-- snapshot-style fields repeated across each year row so the app can avoid
-- frame-specific joins at read time.
-- ---------------------------------------------------------------------------

create or replace table mart_area_explorer.cbsa_profile_year as
with cbsa_dim as (
    select
        geo_id as cbsa_code,
        geo_name as cbsa_name,
        display_name as cbsa_display_name,
        state_fips as state_fips_primary,
        state_name as state_name_primary,
        state_abbr as state_abbr_primary,
        division_id,
        division_name,
        region_id,
        region_name,
        primary_city_name,
        cbsa_type,
        cbsa_type_short,
        is_metro,
        is_micro,
        state_count,
        county_count
    from gold.dim_geo
    where geo_level = 'cbsa'
),
population as (
    select
        geo_id as cbsa_code,
        year,
        pop_total,
        pop_growth_5yr,
        median_age,
        diversity_index,
        pct_ba_plus
    from gold.population_demographics
    where lower(geo_level) = 'cbsa'
),
migration as (
    select
        geo_id as cbsa_code,
        year,
        pct_foreign_born,
        pct_non_citizen,
        irs_net_migration_rate
    from gold.migration_wide
    where lower(geo_level) = 'cbsa'
),
housing as (
    select
        geo_id as cbsa_code,
        year,
        rent_to_income,
        value_to_income,
        pct_rent_burden_30plus,
        permits_per_1000_housing_units,
        vacancy_rate
    from gold.housing_core_wide
    where lower(geo_level) = 'cbsa'
),
health as (
    select
        geo_id as cbsa_code,
        year,
        life_expectancy,
        premature_death_rate
    from gold.health_wide
    where lower(geo_level) = 'cbsa'
),
transport as (
    select
        geo_id as cbsa_code,
        year,
        pct_commute_transit,
        pct_hh_0_vehicles
    from gold.transport_built_form_wide
    where lower(geo_level) = 'cbsa'
),
social_infra as (
    select
        geo_id as cbsa_code,
        year,
        pct_no_internet_access
    from gold.social_infra_wide
    where lower(geo_level) = 'cbsa'
),
environment as (
    select
        geo_id as cbsa_code,
        year,
        unhealthy_days as aqi_unhealthy_days,
        fema_risk_score
    from gold.environment_wide
    where lower(geo_level) = 'cbsa'
),
income as (
    select
        geo_id as cbsa_code,
        year,
        median_hh_income,
        pov_rate,
        income_pc_growth_5yr
    from gold.economics_income_wide
    where lower(geo_level) = 'cbsa'
),
labor as (
    select
        geo_id as cbsa_code,
        year,
        lfpr,
        pct_unemployment_rate
    from gold.economics_labor_wide
    where lower(geo_level) = 'cbsa'
),
housing_market as (
    select
        geo_id as cbsa_code,
        year,
        hpi_5yr_pct,
        zori_annual_avg_yoy_pct
    from gold.housing_market_wide
    where lower(geo_level) = 'cbsa'
),
gdp as (
    select
        geo_id as cbsa_code,
        year,
        productivity_growth_5yr
    from gold.economics_gdp_wide
    where lower(geo_level) = 'cbsa'
),
industry as (
    select
        geo_id as cbsa_code,
        year,
        bfs_business_application_rate_per_1000_establishments,
        cbp_estabs_per_1000_residents,
        industry_concentration_hhi
    from gold.economics_industry_wide
    where lower(geo_level) = 'cbsa'
),
character_intelligence as (
    select
        cbsa_code,
        character_percentile_rank,
        character_cluster,
        demographics_score,
        social_fabric_score
    from mart_intelligence.intelligence_character
),
livability_intelligence as (
    select
        cbsa_code,
        livability_percentile_rank,
        livability_cluster,
        affordability_score,
        health_and_safety_score,
        access_and_infrastructure_score,
        physical_environment_score
    from mart_intelligence.intelligence_livability
),
opportunity_intelligence as (
    select
        cbsa_code,
        opportunity_percentile_rank,
        opportunity_cluster,
        resident_opportunity_score,
        market_opportunity_score,
        business_and_industry_score
    from mart_intelligence.intelligence_opportunity
),
cross_frame_intelligence as (
    select
        cbsa_code,
        cross_frame_percentile_rank,
        combined_cluster,
        peer_1_code,
        peer_1_name,
        peer_1_similarity,
        top10_peer_1_cbsa_code,
        top10_peer_2_cbsa_code,
        top10_peer_3_cbsa_code,
        top10_peer_4_cbsa_code,
        top10_peer_5_cbsa_code,
        top10_peer_6_cbsa_code,
        top10_peer_7_cbsa_code,
        top10_peer_8_cbsa_code,
        top10_peer_9_cbsa_code,
        top10_peer_10_cbsa_code,
        top10_peer_1_cbsa_name,
        top10_peer_2_cbsa_name,
        top10_peer_3_cbsa_name,
        top10_peer_4_cbsa_name,
        top10_peer_5_cbsa_name,
        top10_peer_6_cbsa_name,
        top10_peer_7_cbsa_name,
        top10_peer_8_cbsa_name,
        top10_peer_9_cbsa_name,
        top10_peer_10_cbsa_name,
        top10_peer_1_similarity,
        top10_peer_2_similarity,
        top10_peer_3_similarity,
        top10_peer_4_similarity,
        top10_peer_5_similarity,
        top10_peer_6_similarity,
        top10_peer_7_similarity,
        top10_peer_8_similarity,
        top10_peer_9_similarity,
        top10_peer_10_similarity
    from mart_intelligence.intelligence_cross_frame
)
select
    'cbsa' as geo_level,
    p.cbsa_code,
    d.cbsa_name,
    d.cbsa_display_name,
    p.year,
    d.state_fips_primary,
    d.state_name_primary,
    d.state_abbr_primary,
    d.division_id,
    d.division_name,
    d.region_id,
    d.region_name,
    d.primary_city_name,
    d.cbsa_type,
    d.cbsa_type_short,
    d.is_metro,
    d.is_micro,
    d.state_count,
    d.county_count,
    p.pop_total,
    p.pop_growth_5yr,
    p.median_age,
    p.diversity_index,
    p.pct_ba_plus,
    m.pct_foreign_born,
    m.pct_non_citizen,
    m.irs_net_migration_rate,
    h.rent_to_income,
    h.value_to_income,
    h.pct_rent_burden_30plus,
    h.permits_per_1000_housing_units,
    h.vacancy_rate,
    hw.life_expectancy,
    hw.premature_death_rate,
    t.pct_commute_transit,
    t.pct_hh_0_vehicles,
    si.pct_no_internet_access,
    e.aqi_unhealthy_days,
    e.fema_risk_score,
    i.median_hh_income,
    i.pov_rate,
    i.income_pc_growth_5yr,
    l.lfpr,
    l.pct_unemployment_rate,
    hm.hpi_5yr_pct,
    hm.zori_annual_avg_yoy_pct,
    g.productivity_growth_5yr,
    ind.bfs_business_application_rate_per_1000_establishments,
    ind.cbp_estabs_per_1000_residents,
    ind.industry_concentration_hhi,
    ci.character_percentile_rank,
    ci.character_cluster,
    ci.demographics_score,
    ci.social_fabric_score,
    li.livability_percentile_rank,
    li.livability_cluster,
    li.affordability_score,
    li.health_and_safety_score,
    li.access_and_infrastructure_score,
    li.physical_environment_score,
    oi.opportunity_percentile_rank,
    oi.opportunity_cluster,
    oi.resident_opportunity_score,
    oi.market_opportunity_score,
    oi.business_and_industry_score,
    x.cross_frame_percentile_rank,
    x.combined_cluster,
    x.peer_1_code,
    x.peer_1_name,
    x.peer_1_similarity,
    x.top10_peer_1_cbsa_code,
    x.top10_peer_2_cbsa_code,
    x.top10_peer_3_cbsa_code,
    x.top10_peer_4_cbsa_code,
    x.top10_peer_5_cbsa_code,
    x.top10_peer_6_cbsa_code,
    x.top10_peer_7_cbsa_code,
    x.top10_peer_8_cbsa_code,
    x.top10_peer_9_cbsa_code,
    x.top10_peer_10_cbsa_code,
    x.top10_peer_1_cbsa_name,
    x.top10_peer_2_cbsa_name,
    x.top10_peer_3_cbsa_name,
    x.top10_peer_4_cbsa_name,
    x.top10_peer_5_cbsa_name,
    x.top10_peer_6_cbsa_name,
    x.top10_peer_7_cbsa_name,
    x.top10_peer_8_cbsa_name,
    x.top10_peer_9_cbsa_name,
    x.top10_peer_10_cbsa_name,
    x.top10_peer_1_similarity,
    x.top10_peer_2_similarity,
    x.top10_peer_3_similarity,
    x.top10_peer_4_similarity,
    x.top10_peer_5_similarity,
    x.top10_peer_6_similarity,
    x.top10_peer_7_similarity,
    x.top10_peer_8_similarity,
    x.top10_peer_9_similarity,
    x.top10_peer_10_similarity
from population p
left join cbsa_dim d
    on p.cbsa_code = d.cbsa_code
left join migration m
    on p.cbsa_code = m.cbsa_code
   and p.year = m.year
left join housing h
    on p.cbsa_code = h.cbsa_code
   and p.year = h.year
left join health hw
    on p.cbsa_code = hw.cbsa_code
   and p.year = hw.year
left join transport t
    on p.cbsa_code = t.cbsa_code
   and p.year = t.year
left join social_infra si
    on p.cbsa_code = si.cbsa_code
   and p.year = si.year
left join environment e
    on p.cbsa_code = e.cbsa_code
   and p.year = e.year
left join income i
    on p.cbsa_code = i.cbsa_code
   and p.year = i.year
left join labor l
    on p.cbsa_code = l.cbsa_code
   and p.year = l.year
left join housing_market hm
    on p.cbsa_code = hm.cbsa_code
   and p.year = hm.year
left join gdp g
    on p.cbsa_code = g.cbsa_code
   and p.year = g.year
left join industry ind
    on p.cbsa_code = ind.cbsa_code
   and p.year = ind.year
left join character_intelligence ci
    on p.cbsa_code = ci.cbsa_code
left join livability_intelligence li
    on p.cbsa_code = li.cbsa_code
left join opportunity_intelligence oi
    on p.cbsa_code = oi.cbsa_code
left join cross_frame_intelligence x
    on p.cbsa_code = x.cbsa_code;

-- ---------------------------------------------------------------------------
-- CBSA metric-long row model
--
-- This table powers the metric-first explorer surfaces. It intentionally uses
-- raw-value percentile ranks rather than polarity-adjusted scores so the app
-- can describe where a place sits in the current distribution of the selected
-- KPI.
-- ---------------------------------------------------------------------------

create or replace table mart_area_explorer.cbsa_metric_long as
with metric_rows as (
    select
        cbsa_code,
        cbsa_name,
        year,
        state_fips_primary,
        state_name_primary,
        division_id,
        division_name,
        region_id,
        region_name,
        'character' as theme_id,
        'demographics' as subject_id,
        'population_size_and_growth' as topic_id,
        'pop_total' as metric_id,
        'Total Population' as metric_display_name,
        'population_demographics' as source_table,
        'pop_total' as source_column,
        'integer' as unit_format,
        pop_total as metric_value
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'character', 'demographics', 'population_size_and_growth', 'pop_growth_5yr', 'Population Growth (5 Year)',
        'population_demographics', 'pop_growth_5yr', 'percent', pop_growth_5yr
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'character', 'demographics', 'age_structure', 'median_age', 'Median Age',
        'population_demographics', 'median_age', 'number_1dp', median_age
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'character', 'demographics', 'race_and_ethnicity', 'diversity_index', 'Diversity Index',
        'population_demographics', 'diversity_index', 'index', diversity_index
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'character', 'demographics', 'educational_attainment', 'pct_ba_plus', 'Share With Bachelor''s Degree Or Higher',
        'population_demographics', 'pct_ba_plus', 'percent', pct_ba_plus
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'character', 'demographics', 'nativity_and_citizenship', 'pct_foreign_born', 'Foreign-Born Share',
        'migration_wide', 'pct_foreign_born', 'percent', pct_foreign_born
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'character', 'demographics', 'nativity_and_citizenship', 'pct_non_citizen', 'Non-Citizen Share',
        'migration_wide', 'pct_non_citizen', 'percent', pct_non_citizen
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'character', 'social_fabric', 'residential_stability', 'irs_net_migration_rate', 'IRS Net Migration Rate',
        'migration_wide', 'irs_net_migration_rate', 'percent', irs_net_migration_rate
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'livability', 'affordability', 'price_pressure', 'rent_to_income', 'Rent To Income Ratio',
        'housing_core_wide', 'rent_to_income', 'ratio', rent_to_income
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'livability', 'affordability', 'price_pressure', 'value_to_income', 'Home Value To Income Ratio',
        'housing_core_wide', 'value_to_income', 'ratio', value_to_income
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'livability', 'affordability', 'housing_burden', 'pct_rent_burden_30plus', 'Share Rent Burdened 30%+',
        'housing_core_wide', 'pct_rent_burden_30plus', 'percent', pct_rent_burden_30plus
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'livability', 'affordability', 'housing_supply', 'permits_per_1000_housing_units', 'Permits Per 1,000 Housing Units',
        'housing_core_wide', 'permits_per_1000_housing_units', 'ratio', permits_per_1000_housing_units
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'livability', 'affordability', 'housing_supply', 'vacancy_rate', 'Vacancy Rate',
        'housing_core_wide', 'vacancy_rate', 'percent', vacancy_rate
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'livability', 'health_and_safety', 'health_outcomes', 'life_expectancy', 'Life Expectancy',
        'health_wide', 'life_expectancy', 'number_1dp', life_expectancy
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'livability', 'health_and_safety', 'health_outcomes', 'premature_death_rate', 'Premature Death Rate',
        'health_wide', 'premature_death_rate', 'number_1dp', premature_death_rate
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'livability', 'access_and_infrastructure', 'commute_and_mode', 'pct_commute_transit', 'Transit Commute Share',
        'transport_built_form_wide', 'pct_commute_transit', 'percent', pct_commute_transit
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'livability', 'access_and_infrastructure', 'vehicle_access', 'pct_hh_0_vehicles', 'Households With No Vehicle',
        'transport_built_form_wide', 'pct_hh_0_vehicles', 'percent', pct_hh_0_vehicles
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'livability', 'access_and_infrastructure', 'digital_access', 'pct_no_internet_access', 'No Internet Access Share',
        'social_infra_wide', 'pct_no_internet_access', 'percent', pct_no_internet_access
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'livability', 'physical_environment', 'air_pollution', 'aqi_unhealthy_days', 'Unhealthy AQI Days',
        'environment_wide', 'unhealthy_days', 'integer', aqi_unhealthy_days
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'livability', 'physical_environment', 'climate_hazard_risk', 'fema_risk_score', 'FEMA Risk Score',
        'environment_wide', 'fema_risk_score', 'index', fema_risk_score
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'opportunity', 'resident_opportunity', 'wage_levels', 'median_hh_income', 'Median Household Income',
        'economics_income_wide', 'median_hh_income', 'currency', median_hh_income
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'opportunity', 'resident_opportunity', 'poverty_and_inclusion', 'pov_rate', 'Poverty Rate',
        'economics_income_wide', 'pov_rate', 'percent', pov_rate
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'opportunity', 'resident_opportunity', 'income_growth', 'income_pc_growth_5yr', 'Per Capita Income Growth (5 Year)',
        'economics_income_wide', 'income_pc_growth_5yr', 'percent', income_pc_growth_5yr
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'opportunity', 'resident_opportunity', 'labor_market_tightness', 'lfpr', 'Labor Force Participation Rate',
        'economics_labor_wide', 'lfpr', 'percent', lfpr
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'opportunity', 'resident_opportunity', 'labor_market_tightness', 'pct_unemployment_rate', 'Unemployment Rate',
        'economics_labor_wide', 'pct_unemployment_rate', 'percent', pct_unemployment_rate
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'opportunity', 'market_opportunity', 'home_price_appreciation', 'hpi_5yr_pct', 'Home Price Appreciation (5 Year)',
        'housing_market_wide', 'hpi_5yr_pct', 'percent', hpi_5yr_pct
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'opportunity', 'market_opportunity', 'rent_growth', 'zori_annual_avg_yoy_pct', 'Rent Growth (Annual Average YoY)',
        'housing_market_wide', 'zori_annual_avg_yoy_pct', 'percent', zori_annual_avg_yoy_pct
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'opportunity', 'business_and_industry_opportunity', 'gdp_growth', 'productivity_growth_5yr', 'Productivity Growth (5 Year)',
        'economics_gdp_wide', 'productivity_growth_5yr', 'percent', productivity_growth_5yr
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'opportunity', 'business_and_industry_opportunity', 'business_formation', 'bfs_business_application_rate_per_1000_establishments', 'Business Application Rate Per 1,000 Establishments',
        'economics_industry_wide', 'bfs_business_application_rate_per_1000_establishments', 'ratio', bfs_business_application_rate_per_1000_establishments
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'opportunity', 'business_and_industry_opportunity', 'establishment_density', 'cbp_estabs_per_1000_residents', 'Establishments Per 1,000 Residents',
        'economics_industry_wide', 'cbp_estabs_per_1000_residents', 'ratio', cbp_estabs_per_1000_residents
    from mart_area_explorer.cbsa_profile_year

    union all

    select cbsa_code, cbsa_name, year, state_fips_primary, state_name_primary, division_id, division_name, region_id, region_name,
        'opportunity', 'business_and_industry_opportunity', 'industry_concentration', 'industry_concentration_hhi', 'Industry Concentration HHI',
        'economics_industry_wide', 'industry_concentration_hhi', 'index', industry_concentration_hhi
    from mart_area_explorer.cbsa_profile_year
),
ranked as (
    select
        *,
        percent_rank() over (
            partition by metric_id, year
            order by metric_value
        ) * 100 as national_pct_rank,
        percent_rank() over (
            partition by metric_id, year, division_name
            order by metric_value
        ) * 100 as division_pct_rank
    from metric_rows
    where metric_value is not null
)
select *
from ranked;
