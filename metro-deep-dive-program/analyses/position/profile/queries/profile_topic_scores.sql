-- Topic and subject score surface for a selected CBSA.
-- This is the main Act 1 interpretation layer: all currently useful scored
-- dimensions, organized by frame and theme group.

SELECT
  c.cbsa_code,
  c.cbsa_name,
  'character' AS frame_id,
  m.theme_group,
  m.metric_id,
  m.metric_label,
  m.metric_value,
  m.metric_type
FROM mart_intelligence.intelligence_character AS c
CROSS JOIN LATERAL (
  VALUES
    ('demographics', 'topic_score_race_and_ethnicity', 'Race and ethnicity', c.topic_score_race_and_ethnicity, 'topic_score'),
    ('demographics', 'topic_score_age_structure', 'Age structure', c.topic_score_age_structure, 'topic_score'),
    ('demographics', 'topic_score_educational_attainment', 'Educational attainment', c.topic_score_educational_attainment, 'topic_score'),
    ('demographics', 'topic_score_nativity_and_citizenship', 'Nativity and citizenship', c.topic_score_nativity_and_citizenship, 'topic_score'),
    ('demographics', 'topic_score_population_density', 'Population density', c.topic_score_population_density, 'topic_score'),
    ('social_fabric', 'topic_score_social_capital', 'Social capital', c.topic_score_social_capital, 'topic_score'),
    ('social_fabric', 'topic_score_nonprofits_and_civic_orgs', 'Nonprofits and civic organizations', c.topic_score_nonprofits_and_civic_orgs, 'topic_score'),
    ('social_fabric', 'topic_score_residential_stability', 'Residential stability', c.topic_score_residential_stability, 'topic_score'),
    ('social_fabric', 'topic_score_social_associations', 'Social associations', c.topic_score_social_associations, 'topic_score'),
    ('social_fabric', 'topic_score_built_form', 'Built form', c.topic_score_built_form, 'topic_score'),
    ('demographics', 'subject_score_demographics', 'Demographics subject', c.subject_score_demographics, 'subject_score'),
    ('social_fabric', 'subject_score_social_fabric', 'Social fabric subject', c.subject_score_social_fabric, 'subject_score')
) AS m(theme_group, metric_id, metric_label, metric_value, metric_type)
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
  m.metric_type
FROM mart_intelligence.intelligence_livability AS l
CROSS JOIN LATERAL (
  VALUES
    ('affordability', 'topic_score_price_pressure', 'Price pressure', l.topic_score_price_pressure, 'topic_score'),
    ('affordability', 'topic_score_housing_burden', 'Housing burden', l.topic_score_housing_burden, 'topic_score'),
    ('affordability', 'topic_score_poverty_context', 'Poverty context', l.topic_score_poverty_context, 'topic_score'),
    ('affordability', 'topic_score_housing_supply', 'Housing supply', l.topic_score_housing_supply, 'topic_score'),
    ('affordability', 'topic_score_housing_structure_mix', 'Housing structure mix', l.topic_score_housing_structure_mix, 'topic_score'),
    ('health_and_safety', 'topic_score_health_outcomes', 'Health outcomes', l.topic_score_health_outcomes, 'topic_score'),
    ('health_and_safety', 'topic_score_health_behavior_and_access', 'Health behavior and access', l.topic_score_health_behavior_and_access, 'topic_score'),
    ('health_and_safety', 'topic_score_violence_and_injury', 'Violence and injury', l.topic_score_violence_and_injury, 'topic_score'),
    ('access_and_infrastructure', 'topic_score_commute_and_mode', 'Commute and mode', l.topic_score_commute_and_mode, 'topic_score'),
    ('access_and_infrastructure', 'topic_score_vehicle_access', 'Vehicle access', l.topic_score_vehicle_access, 'topic_score'),
    ('access_and_infrastructure', 'topic_score_housing_slack', 'Housing slack', l.topic_score_housing_slack, 'topic_score'),
    ('access_and_infrastructure', 'topic_score_digital_access', 'Digital access', l.topic_score_digital_access, 'topic_score'),
    ('access_and_infrastructure', 'topic_score_walkability_baseline', 'Walkability baseline', l.topic_score_walkability_baseline, 'topic_score'),
    ('access_and_infrastructure', 'topic_score_food_access_baseline', 'Food access baseline', l.topic_score_food_access_baseline, 'topic_score'),
    ('access_and_infrastructure', 'topic_score_built_form_proxy', 'Built form proxy', l.topic_score_built_form_proxy, 'topic_score'),
    ('physical_environment', 'topic_score_air_pollution', 'Air pollution', l.topic_score_air_pollution, 'topic_score'),
    ('physical_environment', 'topic_score_climate_hazard_risk', 'Climate hazard risk', l.topic_score_climate_hazard_risk, 'topic_score'),
    ('affordability', 'subject_score_affordability', 'Affordability subject', l.subject_score_affordability, 'subject_score'),
    ('health_and_safety', 'subject_score_health_and_safety', 'Health and safety subject', l.subject_score_health_and_safety, 'subject_score'),
    ('access_and_infrastructure', 'subject_score_access_and_infrastructure', 'Access and infrastructure subject', l.subject_score_access_and_infrastructure, 'subject_score'),
    ('physical_environment', 'subject_score_physical_environment', 'Physical environment subject', l.subject_score_physical_environment, 'subject_score')
) AS m(theme_group, metric_id, metric_label, metric_value, metric_type)
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
  m.metric_type
FROM mart_intelligence.intelligence_opportunity AS o
CROSS JOIN LATERAL (
  VALUES
    ('resident_opportunity', 'topic_score_income_growth', 'Income growth', o.topic_score_income_growth, 'topic_score'),
    ('resident_opportunity', 'topic_score_wage_levels', 'Wage levels', o.topic_score_wage_levels, 'topic_score'),
    ('resident_opportunity', 'topic_score_labor_market_tightness', 'Labor market tightness', o.topic_score_labor_market_tightness, 'topic_score'),
    ('resident_opportunity', 'topic_score_poverty_and_inclusion', 'Poverty and inclusion', o.topic_score_poverty_and_inclusion, 'topic_score'),
    ('resident_opportunity', 'topic_score_intergenerational_mobility_proxy', 'Intergenerational mobility proxy', o.topic_score_intergenerational_mobility_proxy, 'topic_score'),
    ('market_opportunity', 'topic_score_home_price_appreciation', 'Home price appreciation', o.topic_score_home_price_appreciation, 'topic_score'),
    ('market_opportunity', 'topic_score_rent_growth', 'Rent growth', o.topic_score_rent_growth, 'topic_score'),
    ('market_opportunity', 'topic_score_population_growth', 'Population growth', o.topic_score_population_growth, 'topic_score'),
    ('market_opportunity', 'topic_score_migration_and_wealth_flows', 'Migration and wealth flows', o.topic_score_migration_and_wealth_flows, 'topic_score'),
    ('market_opportunity', 'topic_score_permit_activity', 'Permit activity', o.topic_score_permit_activity, 'topic_score'),
    ('business_and_industry', 'topic_score_gdp_growth', 'GDP growth', o.topic_score_gdp_growth, 'topic_score'),
    ('business_and_industry', 'topic_score_industry_concentration', 'Industry concentration', o.topic_score_industry_concentration, 'topic_score'),
    ('business_and_industry', 'topic_score_human_capital_momentum', 'Human capital momentum', o.topic_score_human_capital_momentum, 'topic_score'),
    ('business_and_industry', 'topic_score_business_formation', 'Business formation', o.topic_score_business_formation, 'topic_score'),
    ('business_and_industry', 'topic_score_establishment_density', 'Establishment density', o.topic_score_establishment_density, 'topic_score'),
    ('business_and_industry', 'topic_score_lq_specialization', 'Location quotient specialization', o.topic_score_lq_specialization, 'topic_score'),
    ('business_and_industry', 'topic_score_sector_gdp_mix', 'Sector GDP mix', o.topic_score_sector_gdp_mix, 'topic_score'),
    ('resident_opportunity', 'subject_score_resident_opportunity', 'Resident opportunity subject', o.subject_score_resident_opportunity, 'subject_score'),
    ('market_opportunity', 'subject_score_market_opportunity', 'Market opportunity subject', o.subject_score_market_opportunity, 'subject_score'),
    ('business_and_industry', 'subject_score_business_and_industry_opportunity', 'Business and industry subject', o.subject_score_business_and_industry_opportunity, 'subject_score')
) AS m(theme_group, metric_id, metric_label, metric_value, metric_type)
WHERE o.cbsa_code = '__CBSA_CODE__'

ORDER BY frame_id, theme_group, metric_type, metric_id;
