-- Raw KPI surface for a selected CBSA.
-- These are organized by frame and theme group so Act 1 can load the full
-- candidate set and choose what it needs later.

SELECT
  c.cbsa_code,
  c.cbsa_name,
  'character' AS frame_id,
  m.theme_group,
  m.metric_id,
  m.metric_label,
  m.metric_value,
  m.source_year
FROM mart_intelligence.intelligence_character AS c
CROSS JOIN LATERAL (
  VALUES
    ('demographics', 'pop_total', 'Population', c.pop_total, c.spine_year),
    ('demographics', 'diversity_index', 'Diversity index', c.diversity_index, c.diversity_index_source_year),
    ('demographics', 'pct_black_nh', 'Black non-Hispanic share', c.pct_black_nh, c.pct_black_nh_source_year),
    ('demographics', 'pct_asian_nh', 'Asian non-Hispanic share', c.pct_asian_nh, c.pct_asian_nh_source_year),
    ('demographics', 'pct_hispanic', 'Hispanic share', c.pct_hispanic, c.pct_hispanic_source_year),
    ('demographics', 'pct_age_over_64', 'Age 65+ share', c.pct_age_over_64, c.pct_age_over_64_source_year),
    ('demographics', 'pct_ba_plus', 'Adults with BA+', c.pct_ba_plus, c.pct_ba_plus_source_year),
    ('demographics', 'pct_foreign_born', 'Foreign-born share', c.pct_foreign_born, c.pct_foreign_born_source_year),
    ('demographics', 'pop_weighted_density_sqmi', 'Population-weighted density', c.pop_weighted_density_sqmi, c.pop_weighted_density_sqmi_source_year),
    ('social_fabric', 'friending_bias', 'Friending bias', c.friending_bias, c.friending_bias_source_year),
    ('social_fabric', 'civic_engagement_volunteering_rate', 'Volunteering rate', c.civic_engagement_volunteering_rate, c.civic_engagement_volunteering_rate_source_year),
    ('social_fabric', 'civic_organizations_per_1000', 'Civic organizations per 1,000', c.civic_organizations_per_1000, c.civic_organizations_per_1000_source_year),
    ('social_fabric', 'nonprofits_per_100k', 'Nonprofits per 100k', c.nonprofits_per_100k, c.nonprofits_per_100k_source_year),
    ('social_fabric', 'irs_net_migration_rate', 'IRS net migration rate', c.irs_net_migration_rate, c.irs_net_migration_rate_source_year),
    ('social_fabric', 'pct_moved_diff_st', 'Moved from different state share', c.pct_moved_diff_st, c.pct_moved_diff_st_source_year),
    ('social_fabric', 'pct_moved_abroad', 'Moved from abroad share', c.pct_moved_abroad, c.pct_moved_abroad_source_year),
    ('social_fabric', 'social_associations_per_10k', 'Social associations per 10k', c.social_associations_per_10k, c.social_associations_per_10k_source_year),
    ('social_fabric', 'pct_struct_multifam', 'Multifamily housing share', c.pct_struct_multifam, c.pct_struct_multifam_source_year)
) AS m(theme_group, metric_id, metric_label, metric_value, source_year)
WHERE c.cbsa_code = '__CBSA_CODE__'

UNION ALL

SELECT
  l.cbsa_code,
  l.cbsa_name,
  'livability' AS frame_id,
  m.theme_group,
  m.metric_id,
  m.metric_label,
  m.metric_value,
  m.source_year
FROM mart_intelligence.intelligence_livability AS l
CROSS JOIN LATERAL (
  VALUES
    ('affordability', 'value_to_income', 'Value-to-income ratio', l.value_to_income, l.affordability_year),
    ('affordability', 'pct_rent_burden_30plus', 'Rent-burdened renter share', l.pct_rent_burden_30plus, l.housing_year),
    ('affordability', 'pov_rate', 'Poverty rate', l.pov_rate, l.income_year),
    ('affordability', 'permits_per_1000_housing_units', 'Permits per 1,000 housing units', l.permits_per_1000_housing_units, l.housing_year),
    ('affordability', 'permits_share_units_5_plus', 'Large multifamily permit share', l.permits_share_units_5_plus, l.housing_year),
    ('affordability', 'pct_struct_mobile', 'Mobile home share', l.pct_struct_mobile, l.housing_year),
    ('affordability', 'pct_struct_small_mf', 'Small multifamily share', l.pct_struct_small_mf, l.housing_year),
    ('affordability', 'pct_struct_mid_mf', 'Mid-size multifamily share', l.pct_struct_mid_mf, l.housing_year),
    ('health_and_safety', 'premature_death_rate', 'Premature death rate', l.premature_death_rate, l.health_year),
    ('health_and_safety', 'mental_health_provider_ratio', 'Mental health provider ratio', l.mental_health_provider_ratio, l.health_year),
    ('health_and_safety', 'drug_overdose_death_rate', 'Drug overdose death rate', l.drug_overdose_death_rate, l.health_year),
    ('health_and_safety', 'pct_uninsured_adults', 'Uninsured adult share', l.pct_uninsured_adults, l.health_year),
    ('health_and_safety', 'preventable_hospital_stay_rate', 'Preventable hospital stay rate', l.preventable_hospital_stay_rate, l.health_year),
    ('health_and_safety', 'firearm_fatality_rate', 'Firearm fatality rate', l.firearm_fatality_rate, l.health_year),
    ('health_and_safety', 'motor_vehicle_crash_rate', 'Motor vehicle crash rate', l.motor_vehicle_crash_rate, l.health_year),
    ('access_and_infrastructure', 'pct_commute_walk', 'Walk commute share', l.pct_commute_walk, l.transport_year),
    ('access_and_infrastructure', 'pct_commute_wfh', 'Work-from-home commute share', l.pct_commute_wfh, l.transport_year),
    ('access_and_infrastructure', 'vacancy_rate', 'Vacancy rate', l.vacancy_rate, l.housing_year),
    ('access_and_infrastructure', 'pct_hh_0_vehicles', 'Zero-vehicle household share', l.pct_hh_0_vehicles, l.transport_year),
    ('access_and_infrastructure', 'pct_no_internet_access', 'No internet access share', l.pct_no_internet_access, l.transport_year),
    ('access_and_infrastructure', 'walkability_index', 'Walkability index', l.walkability_index, l.social_infra_year),
    ('access_and_infrastructure', 'jobs_access_45min_transit', 'Jobs accessible within 45 minutes transit', l.jobs_access_45min_transit, l.social_infra_year),
    ('access_and_infrastructure', 'pct_population_low_income_low_access_1_10', 'Low-income low-access population share', l.pct_population_low_income_low_access_1_10, l.food_access_year),
    ('access_and_infrastructure', 'pop_weighted_density_sqmi', 'Population-weighted density', l.pop_weighted_density_sqmi, l.transport_year),
    ('physical_environment', 'aqi_median', 'Median AQI', l.aqi_median, l.environment_year),
    ('physical_environment', 'fema_risk_score', 'FEMA risk score', l.fema_risk_score, l.environment_year)
) AS m(theme_group, metric_id, metric_label, metric_value, source_year)
WHERE l.cbsa_code = '__CBSA_CODE__'

UNION ALL

SELECT
  o.cbsa_code,
  o.cbsa_name,
  'opportunity' AS frame_id,
  m.theme_group,
  m.metric_id,
  m.metric_label,
  m.metric_value,
  m.source_year
FROM mart_intelligence.intelligence_opportunity AS o
CROSS JOIN LATERAL (
  VALUES
    ('market_opportunity', 'zori_annual_avg_yoy_pct', 'Annual average ZORI YoY', o.zori_annual_avg_yoy_pct, o.zori_annual_avg_yoy_pct_source_year),
    ('business_and_industry', 'bfs_business_application_rate_per_1000_establishments', 'Business application rate per 1,000 establishments', o.bfs_business_application_rate_per_1000_establishments, o.bfs_business_application_rate_per_1000_establishments_source_year),
    ('business_and_industry', 'cbp_estabs_per_1000_residents', 'Establishments per 1,000 residents', o.cbp_estabs_per_1000_residents, o.cbp_estabs_per_1000_residents_source_year),
    ('business_and_industry', 'productivity_growth_5yr', 'Productivity growth 5-year', o.productivity_growth_5yr, o.productivity_growth_5yr_source_year),
    ('business_and_industry', 'pct_ba_plus_change_5yr', 'BA+ share change 5-year', o.pct_ba_plus_change_5yr, o.pct_ba_plus_change_5yr_source_year),
    ('business_and_industry', 'industry_concentration_hhi', 'Industry concentration HHI', o.industry_concentration_hhi, o.industry_concentration_hhi_source_year),
    ('business_and_industry', 'lq_information', 'Information LQ', o.lq_information, o.lq_information_source_year),
    ('business_and_industry', 'lq_manufacturing', 'Manufacturing LQ', o.lq_manufacturing, o.lq_manufacturing_source_year),
    ('business_and_industry', 'lq_professional', 'Professional services LQ', o.lq_professional, o.lq_professional_source_year),
    ('market_opportunity', 'hpi_5yr_pct', 'Home price index 5-year change', o.hpi_5yr_pct, o.hpi_5yr_pct_source_year),
    ('market_opportunity', 'hpi_yoy_pct', 'Home price index YoY change', o.hpi_yoy_pct, o.hpi_yoy_pct_source_year),
    ('market_opportunity', 'irs_net_agi', 'IRS net AGI flow', o.irs_net_agi, o.irs_net_agi_source_year),
    ('market_opportunity', 'irs_net_migration_rate', 'IRS net migration rate', o.irs_net_migration_rate, o.irs_net_migration_rate_source_year),
    ('market_opportunity', 'permits_share_units_5_plus', 'Large multifamily permit share', o.permits_share_units_5_plus, o.permits_share_units_5_plus_source_year),
    ('market_opportunity', 'pop_growth_5yr', 'Population growth 5-year', o.pop_growth_5yr, o.pop_growth_5yr_source_year),
    ('resident_opportunity', 'income_pc_growth_5yr', 'Per-capita income growth 5-year', o.income_pc_growth_5yr, o.income_pc_growth_5yr_source_year),
    ('resident_opportunity', 'lfpr', 'Labor force participation rate', o.lfpr, o.lfpr_source_year),
    ('resident_opportunity', 'pct_unemployment_rate', 'Unemployment rate', o.pct_unemployment_rate, o.pct_unemployment_rate_source_year),
    ('resident_opportunity', 'pov_rate_change_5yr', 'Poverty rate change 5-year', o.pov_rate_change_5yr, o.pov_rate_change_5yr_source_year),
    ('resident_opportunity', 'qcew_private_avg_wkly_wage', 'Private average weekly wage', o.qcew_private_avg_wkly_wage, o.qcew_private_avg_wkly_wage_source_year),
    ('resident_opportunity', 'economic_connectedness', 'Economic connectedness', o.economic_connectedness, o.economic_connectedness_source_year),
    ('business_and_industry', 'pct_real_gdp_information', 'Information GDP share', o.pct_real_gdp_information, o.pct_real_gdp_information_source_year),
    ('market_opportunity', 'permits_per_1000_housing_units', 'Permits per 1,000 housing units', o.permits_per_1000_housing_units, o.permits_per_1000_housing_units_source_year)
) AS m(theme_group, metric_id, metric_label, metric_value, source_year)
WHERE o.cbsa_code = '__CBSA_CODE__'

ORDER BY frame_id, theme_group, metric_id;
