-- First-pass Act 1 fingerprint surface.
-- This is a curated join across frame tables, not a locked fingerprint mart.

SELECT
  c.cbsa_code,
  c.cbsa_name,
  c.pop_total,

  cf.character_percentile_rank,
  cf.livability_percentile_rank,
  cf.opportunity_percentile_rank,
  cf.cross_frame_percentile_rank,

  c.topic_score_population_density,
  c.topic_score_educational_attainment,
  c.topic_score_social_capital,
  c.subject_score_demographics,
  c.subject_score_social_fabric,

  l.topic_score_price_pressure,
  l.topic_score_housing_burden,
  l.topic_score_health_outcomes,
  l.topic_score_walkability_baseline,
  l.subject_score_affordability,
  l.subject_score_health_and_safety,
  l.subject_score_access_and_infrastructure,
  l.subject_score_physical_environment,

  o.topic_score_income_growth,
  o.topic_score_population_growth,
  o.topic_score_wage_levels,
  o.topic_score_business_formation,
  o.subject_score_resident_opportunity,
  o.subject_score_market_opportunity,
  o.subject_score_business_and_industry_opportunity,

  c.pct_ba_plus,
  c.pct_foreign_born,
  c.pop_weighted_density_sqmi,
  l.value_to_income,
  l.pct_rent_burden_30plus,
  l.walkability_index,
  l.aqi_median,
  o.pop_growth_5yr,
  o.income_pc_growth_5yr,
  o.qcew_private_avg_wkly_wage,
  o.hpi_5yr_pct
FROM mart_intelligence.intelligence_character AS c
JOIN mart_intelligence.intelligence_livability AS l
  ON c.cbsa_code = l.cbsa_code
JOIN mart_intelligence.intelligence_opportunity AS o
  ON c.cbsa_code = o.cbsa_code
JOIN mart_intelligence.intelligence_cross_frame AS cf
  ON c.cbsa_code = cf.cbsa_code
WHERE c.cbsa_code = '40060';
