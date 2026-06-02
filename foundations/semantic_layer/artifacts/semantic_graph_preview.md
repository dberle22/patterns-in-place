# Semantic Graph Preview

## Summary

```json
{
  "node_count": 227,
  "edge_count": 1718,
  "node_kinds": {
    "table": 13,
    "subject_area": 32,
    "geo_level": 10,
    "metric": 97,
    "theme": 3,
    "template": 6,
    "question_type": 7,
    "chart_rule": 6,
    "chart_type": 8,
    "topic": 15,
    "score": 7,
    "question_pattern": 13,
    "point_set": 3,
    "source": 7
  },
  "edge_relations": {
    "in_subject_area": 129,
    "supports_geo_level": 85,
    "joins_to": 5,
    "rolls_up_to": 9,
    "from_table": 97,
    "tagged_to_theme": 138,
    "valid_for_geo_level": 873,
    "has_topic": 15,
    "has_score": 7,
    "uses_template": 9,
    "mapped_to_chart_rule": 6,
    "has_question_pattern": 13,
    "approved_chart": 7,
    "fallback_chart": 6,
    "uses_metric": 99,
    "score_input": 43,
    "score_valid_for_geo_level": 35,
    "question_for_theme": 21,
    "requires_metric": 28,
    "requires_table": 20,
    "question_valid_for_geo_level": 33,
    "defaults_to_template": 13,
    "defaults_to_chart_rule": 13,
    "spatially_joins_to": 7,
    "point_source": 7
  }
}
```

## Mermaid

```mermaid
flowchart LR
  subgraph Tables
    table_affordability_wide["affordability_wide"]
    table_benchmark_reference["benchmark_reference"]
    table_economics_gdp_wide["economics_gdp_wide"]
    table_economics_income_wide["economics_income_wide"]
    table_economics_industry_wide["economics_industry_wide"]
    table_economics_labor_wide["economics_labor_wide"]
    table_geography_catalog["geography_catalog"]
    table_housing_core_wide["housing_core_wide"]
    table_migration_wide["migration_wide"]
    table_points_catalog_stub["points_catalog_stub"]
    table_population_demographics["population_demographics"]
    table_transport_built_form_wide["transport_built_form_wide"]
    table_tx_isd_metrics["tx_isd_metrics"]
  end
  subgraph Metrics
    metric_acs_income_pc["acs_income_pc"]
    metric_acs_ind_total_emp["acs_ind_total_emp"]
    metric_acs_industry_concentration_hhi["acs_industry_concentration_hhi"]
    metric_aging_index["aging_index"]
    metric_annualized_median_rent["annualized_median_rent"]
    metric_calc_income_pc["calc_income_pc"]
    metric_density_population["density_population"]
    metric_dependents_per_worker["dependents_per_worker"]
    metric_diversity_index["diversity_index"]
    metric_employed["employed"]
    metric_fmr_2br["fmr_2br"]
    metric_fmr_gap_2br_vs_median_rent["fmr_gap_2br_vs_median_rent"]
    metric_gini_index["gini_index"]
    metric_gross_density_sqmi["gross_density_sqmi"]
    metric_hu_total["hu_total"]
    metric_income_pc_growth_10yr["income_pc_growth_10yr"]
    metric_income_pc_growth_1yr["income_pc_growth_1yr"]
    metric_income_pc_growth_5yr["income_pc_growth_5yr"]
    metric_industry_concentration_hhi["industry_concentration_hhi"]
    metric_irs_migration_churn["irs_migration_churn"]
    metric_irs_net_migration["irs_net_migration"]
    metric_irs_net_migration_rate["irs_net_migration_rate"]
    metric_jobs_to_pop_ratio["jobs_to_pop_ratio"]
    metric_labor_force["labor_force"]
    metric_lfpr["lfpr"]
    metric_lfpr_growth_5yr["lfpr_growth_5yr"]
    metric_mean_travel_time["mean_travel_time"]
    metric_median_age["median_age"]
    metric_median_gross_rent["median_gross_rent"]
    metric_median_hh_income["median_hh_income"]
    metric_median_home_value["median_home_value"]
    metric_migration_churn["migration_churn"]
    metric_mobility_rate["mobility_rate"]
    metric_nominal_gdp_growth_5yr["nominal_gdp_growth_5yr"]
    metric_nominal_gdp_pc["nominal_gdp_pc"]
    metric_nominal_gdp_total["nominal_gdp_total"]
    metric_owner_occ_rate["owner_occ_rate"]
    metric_pct_acs_ind_arts_accomm_food["pct_acs_ind_arts_accomm_food"]
    metric_pct_acs_ind_educ_health["pct_acs_ind_educ_health"]
    metric_pct_acs_ind_manufacturing["pct_acs_ind_manufacturing"]
    metric_pct_acs_ind_professional["pct_acs_ind_professional"]
    metric_pct_age_18_64["pct_age_18_64"]
    metric_pct_age_over_64["pct_age_over_64"]
    metric_pct_age_under_18["pct_age_under_18"]
    metric_pct_asian_nh["pct_asian_nh"]
    metric_pct_ba_plus["pct_ba_plus"]
    metric_pct_black_nh["pct_black_nh"]
    metric_pct_commute_drive_alone["pct_commute_drive_alone"]
    metric_pct_commute_transit["pct_commute_transit"]
    metric_pct_commute_walk["pct_commute_walk"]
    metric_pct_commute_wfh["pct_commute_wfh"]
    metric_pct_foreign_born["pct_foreign_born"]
    metric_pct_grad_plus["pct_grad_plus"]
    metric_pct_hh_0_vehicles["pct_hh_0_vehicles"]
    metric_pct_hispanic["pct_hispanic"]
    metric_pct_low_car_commute["pct_low_car_commute"]
    metric_pct_moved_abroad["pct_moved_abroad"]
    metric_pct_moved_diff_st["pct_moved_diff_st"]
    metric_pct_non_citizen["pct_non_citizen"]
    metric_pct_real_gdp_edu_health["pct_real_gdp_edu_health"]
    metric_pct_real_gdp_manufacturing["pct_real_gdp_manufacturing"]
    metric_pct_real_gdp_professional["pct_real_gdp_professional"]
    metric_pct_rent_burden_30plus["pct_rent_burden_30plus"]
    metric_pct_rent_burden_50plus["pct_rent_burden_50plus"]
    metric_pct_same_house["pct_same_house"]
    metric_pct_struct_multifam["pct_struct_multifam"]
    metric_pct_unemployment_rate["pct_unemployment_rate"]
    metric_pct_white_nh["pct_white_nh"]
    metric_permits_per_1000_housing_units["permits_per_1000_housing_units"]
    metric_permits_share_multifam_units["permits_share_multifam_units"]
    metric_pi_total["pi_total"]
    metric_pi_wage_share["pi_wage_share"]
    metric_pi_wages_salary["pi_wages_salary"]
    metric_pop_growth_10yr["pop_growth_10yr"]
    metric_pop_growth_1yr["pop_growth_1yr"]
    metric_pop_growth_5yr["pop_growth_5yr"]
    metric_pop_total["pop_total"]
    metric_pop_weighted_density_sqmi["pop_weighted_density_sqmi"]
    metric_pov_rate["pov_rate"]
    metric_productivity_growth_5yr["productivity_growth_5yr"]
    metric_productivity_index["productivity_index"]
    metric_real_gdp_growth_5yr["real_gdp_growth_5yr"]
    metric_real_gdp_pc["real_gdp_pc"]
    metric_real_gdp_total["real_gdp_total"]
    metric_rent50_2br["rent50_2br"]
    metric_rent50_gap_2br_vs_median_rent["rent50_gap_2br_vs_median_rent"]
    metric_rent_to_income["rent_to_income"]
    metric_rent_to_rpp_income["rent_to_rpp_income"]
    metric_renter_occ_rate["renter_occ_rate"]
    metric_rpp_all_items["rpp_all_items"]
    metric_rpp_price_deflator["rpp_price_deflator"]
    metric_rpp_real_pc_income["rpp_real_pc_income"]
    metric_unemployed["unemployed"]
    metric_vacancy_rate["vacancy_rate"]
    metric_value_to_income["value_to_income"]
    metric_value_to_rpp_income["value_to_rpp_income"]
    metric_working_age_pop["working_age_pop"]
  end
  subgraph Themes
    theme_character["character"]
    theme_livability["livability"]
    theme_opportunity["opportunity"]
  end
  subgraph Topics
    topic_affordability["Affordability"]
    topic_built_environment["Built Environment"]
    topic_built_form_context["Built Form Context"]
    topic_demographic_profile["Demographic Profile"]
    topic_economic_output["Economic Output"]
    topic_education_and_equity_context["Education And Equity Context"]
    topic_education_attainment["Education Attainment"]
    topic_growth_and_momentum["Growth And Momentum"]
    topic_housing_supply["Housing Supply"]
    topic_income_and_wages["Income And Wages"]
    topic_industry_mix["Industry Mix"]
    topic_labor_market["Labor Market"]
    topic_mobility["Mobility"]
    topic_race_ethnicity["Race And Ethnicity"]
    topic_rootedness_and_mobility["Rootedness And Mobility"]
  end
  subgraph Scores
    score_business_opportunity_score["Business Opportunity Score"]
    score_character_profile_archetype["Character Profile Archetype"]
    score_livability_affordability_subscore["Livability Affordability Subscore"]
    score_livability_mobility_subscore["Livability Mobility Subscore"]
    score_livability_score["Livability Score"]
    score_market_opportunity_score["Market Opportunity Score"]
    score_resident_opportunity_score["Resident Opportunity Score"]
  end
  subgraph Question Patterns
    question_pattern_character_profile_summary["character_profile_summary"]
    question_pattern_compare_selected_geographies["compare_selected_geographies"]
    question_pattern_diversity_ranking["diversity_ranking"]
    question_pattern_income_growth_ranking["income_growth_ranking"]
    question_pattern_metric_distribution_by_grain["metric_distribution_by_grain"]
    question_pattern_metros_highest_cost_burden["metros_highest_cost_burden"]
    question_pattern_metros_highest_rent_to_income["metros_highest_rent_to_income"]
    question_pattern_metros_income_trend["metros_income_trend"]
    question_pattern_metros_rent_trend["metros_rent_trend"]
    question_pattern_national_vacancy_trend["national_vacancy_trend"]
    question_pattern_population_growth_ranking["population_growth_ranking"]
    question_pattern_states_highest_household_income["states_highest_household_income"]
    question_pattern_target_vs_benchmark["target_vs_benchmark"]
  end
  subgraph Templates
    template_benchmark["benchmark"]
    template_compare_selected["compare_selected"]
    template_distribution["distribution"]
    template_growth["growth"]
    template_ranking["ranking"]
    template_trend["trend"]
  end
  subgraph Chart Rules
    chart_rule_benchmark_default["benchmark_default"]
    chart_rule_comparison_selected["comparison_selected"]
    chart_rule_correlation_default["correlation_default"]
    chart_rule_distribution_default["distribution_default"]
    chart_rule_ranking_default["ranking_default"]
    chart_rule_trend_default["trend_default"]
  end
  subgraph Chart Types
    chart_type_bar["bar"]
    chart_type_boxplot["boxplot"]
    chart_type_heatmap_table["heatmap_table"]
    chart_type_hexbin["hexbin"]
    chart_type_line["line"]
    chart_type_scatter["scatter"]
    chart_type_slopegraph["slopegraph"]
    chart_type_strength_strip["strength_strip"]
  end
  subgraph Geographies
    geo_level_cbsa["cbsa"]
    geo_level_county["county"]
    geo_level_division["division"]
    geo_level_place["place"]
    geo_level_region["region"]
    geo_level_state["state"]
    geo_level_tract["tract"]
    geo_level_tx_isd["Texas School District"]
    geo_level_us["us"]
    geo_level_zcta["zcta"]
  end
  subgraph Point Sets
    point_set_curated_poi["Curated POI"]
    point_set_parcels["Parcels"]
    point_set_public_poi["Public POI"]
  end
  subgraph Sources
    source_Google_Maps_or_equivalent["Google_Maps_or_equivalent"]
    source_OSM["OSM"]
    source_county_assessor["county_assessor"]
    source_manual_curation["manual_curation"]
    source_parcel_standardization_pipeline["parcel_standardization_pipeline"]
    source_partner_poi_pipeline["partner_poi_pipeline"]
    source_web_scrapes["web_scrapes"]
  end
  subgraph Subject Areas
    subject_area_affordability["affordability"]
    subject_area_benchmarks["benchmarks"]
    subject_area_built_form["built_form"]
    subject_area_character["character"]
    subject_area_demographics["demographics"]
    subject_area_economy["economy"]
    subject_area_education["education"]
    subject_area_employment["employment"]
    subject_area_gdp["gdp"]
    subject_area_gdp_growth["gdp_growth"]
    subject_area_housing["housing"]
    subject_area_housing_benchmark["housing_benchmark"]
    subject_area_housing_supply["housing_supply"]
    subject_area_income["income"]
    subject_area_income_growth["income_growth"]
    subject_area_income_structure["income_structure"]
    subject_area_industry["industry"]
    subject_area_industry_diversification["industry_diversification"]
    subject_area_inequality["inequality"]
    subject_area_labor["labor"]
    subject_area_livability["livability"]
    subject_area_migration["migration"]
    subject_area_mobility["mobility"]
    subject_area_nativity["nativity"]
    subject_area_opportunity["opportunity"]
    subject_area_planner_internal["planner_internal"]
    subject_area_population["population"]
    subject_area_poverty["poverty"]
    subject_area_productivity["productivity"]
    subject_area_race_ethnicity["race_ethnicity"]
    subject_area_texas_school_districts["texas_school_districts"]
    subject_area_transport["transport"]
  end
  subgraph Question Types
    question_type_benchmark["benchmark"]
    question_type_comparison["comparison"]
    question_type_correlation["correlation"]
    question_type_distribution["distribution"]
    question_type_ranking["ranking"]
    question_type_summary["summary"]
    question_type_trend["trend"]
  end
  chart_rule_benchmark_default -->|approved| chart_type_bar
  chart_rule_benchmark_default -->|fallback| chart_type_strength_strip
  chart_rule_comparison_selected -->|approved| chart_type_bar
  chart_rule_comparison_selected -->|approved| chart_type_slopegraph
  chart_rule_comparison_selected -->|fallback| chart_type_heatmap_table
  chart_rule_correlation_default -->|approved| chart_type_scatter
  chart_rule_correlation_default -->|fallback| chart_type_hexbin
  chart_rule_distribution_default -->|approved| chart_type_boxplot
  chart_rule_distribution_default -->|fallback| chart_type_heatmap_table
  chart_rule_ranking_default -->|approved| chart_type_bar
  chart_rule_ranking_default -->|fallback| chart_type_heatmap_table
  chart_rule_trend_default -->|approved| chart_type_line
  chart_rule_trend_default -->|fallback| chart_type_slopegraph
  geo_level_county -->|rolls up to| geo_level_cbsa
  geo_level_county -->|rolls up to| geo_level_state
  geo_level_division -->|rolls up to| geo_level_region
  geo_level_state -->|rolls up to| geo_level_division
  geo_level_state -->|rolls up to| geo_level_region
  geo_level_tract -->|rolls up to| geo_level_county
  geo_level_zcta -->|rolls up to| geo_level_cbsa
  geo_level_zcta -->|rolls up to| geo_level_county
  geo_level_zcta -->|rolls up to| geo_level_tract
  metric_acs_income_pc -->|from table| table_economics_income_wide
  metric_acs_income_pc -->|subject area| subject_area_income
  metric_acs_income_pc -->|tagged to| theme_livability
  metric_acs_income_pc -->|tagged to| theme_opportunity
  metric_acs_income_pc -->|valid for| geo_level_cbsa
  metric_acs_income_pc -->|valid for| geo_level_county
  metric_acs_income_pc -->|valid for| geo_level_division
  metric_acs_income_pc -->|valid for| geo_level_place
  metric_acs_income_pc -->|valid for| geo_level_region
  metric_acs_income_pc -->|valid for| geo_level_state
  metric_acs_income_pc -->|valid for| geo_level_tract
  metric_acs_income_pc -->|valid for| geo_level_us
  metric_acs_income_pc -->|valid for| geo_level_zcta
  metric_acs_ind_total_emp -->|from table| table_economics_industry_wide
  metric_acs_ind_total_emp -->|subject area| subject_area_industry
  metric_acs_ind_total_emp -->|tagged to| theme_opportunity
  metric_acs_ind_total_emp -->|valid for| geo_level_cbsa
  metric_acs_ind_total_emp -->|valid for| geo_level_county
  metric_acs_ind_total_emp -->|valid for| geo_level_division
  metric_acs_ind_total_emp -->|valid for| geo_level_place
  metric_acs_ind_total_emp -->|valid for| geo_level_region
  metric_acs_ind_total_emp -->|valid for| geo_level_state
  metric_acs_ind_total_emp -->|valid for| geo_level_tract
  metric_acs_ind_total_emp -->|valid for| geo_level_us
  metric_acs_ind_total_emp -->|valid for| geo_level_zcta
  metric_acs_industry_concentration_hhi -->|from table| table_economics_industry_wide
  metric_acs_industry_concentration_hhi -->|subject area| subject_area_industry_diversification
  metric_acs_industry_concentration_hhi -->|tagged to| theme_opportunity
  metric_acs_industry_concentration_hhi -->|valid for| geo_level_cbsa
  metric_acs_industry_concentration_hhi -->|valid for| geo_level_county
  metric_acs_industry_concentration_hhi -->|valid for| geo_level_division
  metric_acs_industry_concentration_hhi -->|valid for| geo_level_place
  metric_acs_industry_concentration_hhi -->|valid for| geo_level_region
  metric_acs_industry_concentration_hhi -->|valid for| geo_level_state
  metric_acs_industry_concentration_hhi -->|valid for| geo_level_tract
  metric_acs_industry_concentration_hhi -->|valid for| geo_level_us
  metric_acs_industry_concentration_hhi -->|valid for| geo_level_zcta
  metric_aging_index -->|from table| table_population_demographics
  metric_aging_index -->|subject area| subject_area_population
  metric_aging_index -->|tagged to| theme_character
  metric_aging_index -->|valid for| geo_level_cbsa
  metric_aging_index -->|valid for| geo_level_county
  metric_aging_index -->|valid for| geo_level_division
  metric_aging_index -->|valid for| geo_level_place
  metric_aging_index -->|valid for| geo_level_region
  metric_aging_index -->|valid for| geo_level_state
  metric_aging_index -->|valid for| geo_level_tract
  metric_aging_index -->|valid for| geo_level_us
  metric_aging_index -->|valid for| geo_level_zcta
  metric_annualized_median_rent -->|from table| table_housing_core_wide
  metric_annualized_median_rent -->|subject area| subject_area_housing
  metric_annualized_median_rent -->|tagged to| theme_livability
  metric_annualized_median_rent -->|valid for| geo_level_cbsa
  metric_annualized_median_rent -->|valid for| geo_level_county
  metric_annualized_median_rent -->|valid for| geo_level_division
  metric_annualized_median_rent -->|valid for| geo_level_place
  metric_annualized_median_rent -->|valid for| geo_level_region
  metric_annualized_median_rent -->|valid for| geo_level_state
  metric_annualized_median_rent -->|valid for| geo_level_tract
  metric_annualized_median_rent -->|valid for| geo_level_us
  metric_annualized_median_rent -->|valid for| geo_level_zcta
  metric_calc_income_pc -->|from table| table_economics_income_wide
  metric_calc_income_pc -->|subject area| subject_area_income
  metric_calc_income_pc -->|tagged to| theme_opportunity
  metric_calc_income_pc -->|valid for| geo_level_cbsa
  metric_calc_income_pc -->|valid for| geo_level_county
  metric_calc_income_pc -->|valid for| geo_level_division
  metric_calc_income_pc -->|valid for| geo_level_place
  metric_calc_income_pc -->|valid for| geo_level_region
  metric_calc_income_pc -->|valid for| geo_level_state
  metric_calc_income_pc -->|valid for| geo_level_tract
  metric_calc_income_pc -->|valid for| geo_level_us
  metric_calc_income_pc -->|valid for| geo_level_zcta
  metric_density_population -->|from table| table_transport_built_form_wide
  metric_density_population -->|subject area| subject_area_built_form
  metric_density_population -->|tagged to| theme_character
  metric_density_population -->|tagged to| theme_livability
  metric_density_population -->|valid for| geo_level_cbsa
  metric_density_population -->|valid for| geo_level_county
  metric_density_population -->|valid for| geo_level_division
  metric_density_population -->|valid for| geo_level_place
  metric_density_population -->|valid for| geo_level_region
  metric_density_population -->|valid for| geo_level_state
  metric_density_population -->|valid for| geo_level_tract
  metric_density_population -->|valid for| geo_level_us
  metric_density_population -->|valid for| geo_level_zcta
  metric_dependents_per_worker -->|from table| table_population_demographics
  metric_dependents_per_worker -->|subject area| subject_area_population
  metric_dependents_per_worker -->|tagged to| theme_character
  metric_dependents_per_worker -->|tagged to| theme_opportunity
  metric_dependents_per_worker -->|valid for| geo_level_cbsa
  metric_dependents_per_worker -->|valid for| geo_level_county
  metric_dependents_per_worker -->|valid for| geo_level_division
  metric_dependents_per_worker -->|valid for| geo_level_place
  metric_dependents_per_worker -->|valid for| geo_level_region
  metric_dependents_per_worker -->|valid for| geo_level_state
  metric_dependents_per_worker -->|valid for| geo_level_tract
  metric_dependents_per_worker -->|valid for| geo_level_us
  metric_dependents_per_worker -->|valid for| geo_level_zcta
  metric_diversity_index -->|from table| table_population_demographics
  metric_diversity_index -->|subject area| subject_area_race_ethnicity
  metric_diversity_index -->|tagged to| theme_character
  metric_diversity_index -->|valid for| geo_level_cbsa
  metric_diversity_index -->|valid for| geo_level_county
  metric_diversity_index -->|valid for| geo_level_division
  metric_diversity_index -->|valid for| geo_level_place
  metric_diversity_index -->|valid for| geo_level_region
  metric_diversity_index -->|valid for| geo_level_state
  metric_diversity_index -->|valid for| geo_level_tract
  metric_diversity_index -->|valid for| geo_level_us
  metric_diversity_index -->|valid for| geo_level_zcta
  metric_employed -->|from table| table_economics_labor_wide
  metric_employed -->|subject area| subject_area_labor
  metric_employed -->|tagged to| theme_opportunity
  metric_employed -->|valid for| geo_level_cbsa
  metric_employed -->|valid for| geo_level_county
  metric_employed -->|valid for| geo_level_division
  metric_employed -->|valid for| geo_level_place
  metric_employed -->|valid for| geo_level_region
  metric_employed -->|valid for| geo_level_state
  metric_employed -->|valid for| geo_level_tract
  metric_employed -->|valid for| geo_level_us
  metric_employed -->|valid for| geo_level_zcta
  metric_fmr_2br -->|from table| table_housing_core_wide
  metric_fmr_2br -->|subject area| subject_area_housing_benchmark
  metric_fmr_2br -->|tagged to| theme_livability
  metric_fmr_2br -->|valid for| geo_level_cbsa
  metric_fmr_2br -->|valid for| geo_level_county
  metric_fmr_2br -->|valid for| geo_level_division
  metric_fmr_2br -->|valid for| geo_level_place
  metric_fmr_2br -->|valid for| geo_level_region
  metric_fmr_2br -->|valid for| geo_level_state
  metric_fmr_2br -->|valid for| geo_level_tract
  metric_fmr_2br -->|valid for| geo_level_us
  metric_fmr_2br -->|valid for| geo_level_zcta
  metric_fmr_gap_2br_vs_median_rent -->|from table| table_housing_core_wide
  metric_fmr_gap_2br_vs_median_rent -->|subject area| subject_area_housing_benchmark
  metric_fmr_gap_2br_vs_median_rent -->|tagged to| theme_livability
  metric_fmr_gap_2br_vs_median_rent -->|tagged to| theme_opportunity
  metric_fmr_gap_2br_vs_median_rent -->|valid for| geo_level_cbsa
  metric_fmr_gap_2br_vs_median_rent -->|valid for| geo_level_county
  metric_fmr_gap_2br_vs_median_rent -->|valid for| geo_level_division
  metric_fmr_gap_2br_vs_median_rent -->|valid for| geo_level_place
  metric_fmr_gap_2br_vs_median_rent -->|valid for| geo_level_region
  metric_fmr_gap_2br_vs_median_rent -->|valid for| geo_level_state
  metric_fmr_gap_2br_vs_median_rent -->|valid for| geo_level_tract
  metric_fmr_gap_2br_vs_median_rent -->|valid for| geo_level_us
  metric_fmr_gap_2br_vs_median_rent -->|valid for| geo_level_zcta
  metric_gini_index -->|from table| table_economics_income_wide
  metric_gini_index -->|subject area| subject_area_inequality
  metric_gini_index -->|tagged to| theme_character
  metric_gini_index -->|tagged to| theme_livability
  metric_gini_index -->|tagged to| theme_opportunity
  metric_gini_index -->|valid for| geo_level_cbsa
  metric_gini_index -->|valid for| geo_level_county
  metric_gini_index -->|valid for| geo_level_division
  metric_gini_index -->|valid for| geo_level_place
  metric_gini_index -->|valid for| geo_level_region
  metric_gini_index -->|valid for| geo_level_state
  metric_gini_index -->|valid for| geo_level_tract
  metric_gini_index -->|valid for| geo_level_us
  metric_gini_index -->|valid for| geo_level_zcta
  metric_gross_density_sqmi -->|from table| table_transport_built_form_wide
  metric_gross_density_sqmi -->|subject area| subject_area_built_form
  metric_gross_density_sqmi -->|tagged to| theme_character
  metric_gross_density_sqmi -->|tagged to| theme_livability
  metric_gross_density_sqmi -->|valid for| geo_level_cbsa
  metric_gross_density_sqmi -->|valid for| geo_level_county
  metric_gross_density_sqmi -->|valid for| geo_level_division
  metric_gross_density_sqmi -->|valid for| geo_level_place
  metric_gross_density_sqmi -->|valid for| geo_level_region
  metric_gross_density_sqmi -->|valid for| geo_level_state
  metric_gross_density_sqmi -->|valid for| geo_level_tract
  metric_gross_density_sqmi -->|valid for| geo_level_us
  metric_gross_density_sqmi -->|valid for| geo_level_zcta
  metric_hu_total -->|from table| table_housing_core_wide
  metric_hu_total -->|subject area| subject_area_housing
  metric_hu_total -->|tagged to| theme_livability
  metric_hu_total -->|tagged to| theme_opportunity
  metric_hu_total -->|valid for| geo_level_cbsa
  metric_hu_total -->|valid for| geo_level_county
  metric_hu_total -->|valid for| geo_level_division
  metric_hu_total -->|valid for| geo_level_place
  metric_hu_total -->|valid for| geo_level_region
  metric_hu_total -->|valid for| geo_level_state
  metric_hu_total -->|valid for| geo_level_tract
  metric_hu_total -->|valid for| geo_level_us
  metric_hu_total -->|valid for| geo_level_zcta
  metric_income_pc_growth_10yr -->|from table| table_economics_income_wide
  metric_income_pc_growth_10yr -->|subject area| subject_area_income_growth
  metric_income_pc_growth_10yr -->|tagged to| theme_opportunity
  metric_income_pc_growth_10yr -->|valid for| geo_level_cbsa
  metric_income_pc_growth_10yr -->|valid for| geo_level_county
  metric_income_pc_growth_10yr -->|valid for| geo_level_division
  metric_income_pc_growth_10yr -->|valid for| geo_level_place
  metric_income_pc_growth_10yr -->|valid for| geo_level_region
  metric_income_pc_growth_10yr -->|valid for| geo_level_state
  metric_income_pc_growth_10yr -->|valid for| geo_level_tract
  metric_income_pc_growth_10yr -->|valid for| geo_level_us
  metric_income_pc_growth_10yr -->|valid for| geo_level_zcta
  metric_income_pc_growth_1yr -->|from table| table_economics_income_wide
  metric_income_pc_growth_1yr -->|subject area| subject_area_income_growth
  metric_income_pc_growth_1yr -->|tagged to| theme_opportunity
  metric_income_pc_growth_1yr -->|valid for| geo_level_cbsa
  metric_income_pc_growth_1yr -->|valid for| geo_level_county
  metric_income_pc_growth_1yr -->|valid for| geo_level_division
  metric_income_pc_growth_1yr -->|valid for| geo_level_place
  metric_income_pc_growth_1yr -->|valid for| geo_level_region
  metric_income_pc_growth_1yr -->|valid for| geo_level_state
  metric_income_pc_growth_1yr -->|valid for| geo_level_tract
  metric_income_pc_growth_1yr -->|valid for| geo_level_us
  metric_income_pc_growth_1yr -->|valid for| geo_level_zcta
  metric_income_pc_growth_5yr -->|from table| table_economics_income_wide
  metric_income_pc_growth_5yr -->|subject area| subject_area_income_growth
  metric_income_pc_growth_5yr -->|tagged to| theme_opportunity
  metric_income_pc_growth_5yr -->|valid for| geo_level_cbsa
  metric_income_pc_growth_5yr -->|valid for| geo_level_county
  metric_income_pc_growth_5yr -->|valid for| geo_level_division
  metric_income_pc_growth_5yr -->|valid for| geo_level_place
  metric_income_pc_growth_5yr -->|valid for| geo_level_region
  metric_income_pc_growth_5yr -->|valid for| geo_level_state
  metric_income_pc_growth_5yr -->|valid for| geo_level_tract
  metric_income_pc_growth_5yr -->|valid for| geo_level_us
  metric_income_pc_growth_5yr -->|valid for| geo_level_zcta
  metric_industry_concentration_hhi -->|from table| table_economics_industry_wide
  metric_industry_concentration_hhi -->|subject area| subject_area_industry_diversification
  metric_industry_concentration_hhi -->|tagged to| theme_opportunity
  metric_industry_concentration_hhi -->|valid for| geo_level_cbsa
  metric_industry_concentration_hhi -->|valid for| geo_level_county
  metric_industry_concentration_hhi -->|valid for| geo_level_division
  metric_industry_concentration_hhi -->|valid for| geo_level_place
  metric_industry_concentration_hhi -->|valid for| geo_level_region
  metric_industry_concentration_hhi -->|valid for| geo_level_state
  metric_industry_concentration_hhi -->|valid for| geo_level_tract
  metric_industry_concentration_hhi -->|valid for| geo_level_us
  metric_industry_concentration_hhi -->|valid for| geo_level_zcta
  metric_irs_migration_churn -->|from table| table_migration_wide
  metric_irs_migration_churn -->|subject area| subject_area_migration
  metric_irs_migration_churn -->|tagged to| theme_character
  metric_irs_migration_churn -->|valid for| geo_level_cbsa
  metric_irs_migration_churn -->|valid for| geo_level_county
  metric_irs_migration_churn -->|valid for| geo_level_division
  metric_irs_migration_churn -->|valid for| geo_level_place
  metric_irs_migration_churn -->|valid for| geo_level_region
  metric_irs_migration_churn -->|valid for| geo_level_state
  metric_irs_migration_churn -->|valid for| geo_level_tract
  metric_irs_migration_churn -->|valid for| geo_level_us
  metric_irs_migration_churn -->|valid for| geo_level_zcta
  metric_irs_net_migration -->|from table| table_migration_wide
  metric_irs_net_migration -->|subject area| subject_area_migration
  metric_irs_net_migration -->|tagged to| theme_character
  metric_irs_net_migration -->|tagged to| theme_opportunity
  metric_irs_net_migration -->|valid for| geo_level_cbsa
  metric_irs_net_migration -->|valid for| geo_level_county
  metric_irs_net_migration -->|valid for| geo_level_division
  metric_irs_net_migration -->|valid for| geo_level_place
  metric_irs_net_migration -->|valid for| geo_level_region
  metric_irs_net_migration -->|valid for| geo_level_state
  metric_irs_net_migration -->|valid for| geo_level_tract
  metric_irs_net_migration -->|valid for| geo_level_us
  metric_irs_net_migration -->|valid for| geo_level_zcta
  metric_irs_net_migration_rate -->|from table| table_migration_wide
  metric_irs_net_migration_rate -->|subject area| subject_area_migration
  metric_irs_net_migration_rate -->|tagged to| theme_character
  metric_irs_net_migration_rate -->|tagged to| theme_opportunity
  metric_irs_net_migration_rate -->|valid for| geo_level_cbsa
  metric_irs_net_migration_rate -->|valid for| geo_level_county
  metric_irs_net_migration_rate -->|valid for| geo_level_division
  metric_irs_net_migration_rate -->|valid for| geo_level_place
  metric_irs_net_migration_rate -->|valid for| geo_level_region
  metric_irs_net_migration_rate -->|valid for| geo_level_state
  metric_irs_net_migration_rate -->|valid for| geo_level_tract
  metric_irs_net_migration_rate -->|valid for| geo_level_us
  metric_irs_net_migration_rate -->|valid for| geo_level_zcta
  metric_jobs_to_pop_ratio -->|from table| table_economics_labor_wide
  metric_jobs_to_pop_ratio -->|subject area| subject_area_labor
  metric_jobs_to_pop_ratio -->|tagged to| theme_opportunity
  metric_jobs_to_pop_ratio -->|valid for| geo_level_cbsa
  metric_jobs_to_pop_ratio -->|valid for| geo_level_county
  metric_jobs_to_pop_ratio -->|valid for| geo_level_division
  metric_jobs_to_pop_ratio -->|valid for| geo_level_place
  metric_jobs_to_pop_ratio -->|valid for| geo_level_region
  metric_jobs_to_pop_ratio -->|valid for| geo_level_state
  metric_jobs_to_pop_ratio -->|valid for| geo_level_tract
  metric_jobs_to_pop_ratio -->|valid for| geo_level_us
  metric_jobs_to_pop_ratio -->|valid for| geo_level_zcta
  metric_labor_force -->|from table| table_economics_labor_wide
  metric_labor_force -->|subject area| subject_area_labor
  metric_labor_force -->|tagged to| theme_opportunity
  metric_labor_force -->|valid for| geo_level_cbsa
  metric_labor_force -->|valid for| geo_level_county
  metric_labor_force -->|valid for| geo_level_division
  metric_labor_force -->|valid for| geo_level_place
  metric_labor_force -->|valid for| geo_level_region
  metric_labor_force -->|valid for| geo_level_state
  metric_labor_force -->|valid for| geo_level_tract
  metric_labor_force -->|valid for| geo_level_us
  metric_labor_force -->|valid for| geo_level_zcta
  metric_lfpr -->|from table| table_economics_labor_wide
  metric_lfpr -->|subject area| subject_area_labor
  metric_lfpr -->|tagged to| theme_opportunity
  metric_lfpr -->|valid for| geo_level_cbsa
  metric_lfpr -->|valid for| geo_level_county
  metric_lfpr -->|valid for| geo_level_division
  metric_lfpr -->|valid for| geo_level_place
  metric_lfpr -->|valid for| geo_level_region
  metric_lfpr -->|valid for| geo_level_state
  metric_lfpr -->|valid for| geo_level_tract
  metric_lfpr -->|valid for| geo_level_us
  metric_lfpr -->|valid for| geo_level_zcta
  metric_lfpr_growth_5yr -->|from table| table_economics_labor_wide
  metric_lfpr_growth_5yr -->|subject area| subject_area_labor
  metric_lfpr_growth_5yr -->|tagged to| theme_opportunity
  metric_lfpr_growth_5yr -->|valid for| geo_level_cbsa
  metric_lfpr_growth_5yr -->|valid for| geo_level_county
  metric_lfpr_growth_5yr -->|valid for| geo_level_division
  metric_lfpr_growth_5yr -->|valid for| geo_level_place
  metric_lfpr_growth_5yr -->|valid for| geo_level_region
  metric_lfpr_growth_5yr -->|valid for| geo_level_state
  metric_lfpr_growth_5yr -->|valid for| geo_level_tract
  metric_lfpr_growth_5yr -->|valid for| geo_level_us
  metric_lfpr_growth_5yr -->|valid for| geo_level_zcta
  metric_mean_travel_time -->|from table| table_transport_built_form_wide
  metric_mean_travel_time -->|subject area| subject_area_transport
  metric_mean_travel_time -->|tagged to| theme_livability
  metric_mean_travel_time -->|valid for| geo_level_cbsa
  metric_mean_travel_time -->|valid for| geo_level_county
  metric_mean_travel_time -->|valid for| geo_level_division
  metric_mean_travel_time -->|valid for| geo_level_place
  metric_mean_travel_time -->|valid for| geo_level_region
  metric_mean_travel_time -->|valid for| geo_level_state
  metric_mean_travel_time -->|valid for| geo_level_tract
  metric_mean_travel_time -->|valid for| geo_level_us
  metric_mean_travel_time -->|valid for| geo_level_zcta
  metric_median_age -->|from table| table_population_demographics
  metric_median_age -->|subject area| subject_area_population
  metric_median_age -->|tagged to| theme_character
  metric_median_age -->|valid for| geo_level_cbsa
  metric_median_age -->|valid for| geo_level_county
  metric_median_age -->|valid for| geo_level_division
  metric_median_age -->|valid for| geo_level_place
  metric_median_age -->|valid for| geo_level_region
  metric_median_age -->|valid for| geo_level_state
  metric_median_age -->|valid for| geo_level_tract
  metric_median_age -->|valid for| geo_level_us
  metric_median_age -->|valid for| geo_level_zcta
  metric_median_gross_rent -->|from table| table_housing_core_wide
  metric_median_gross_rent -->|subject area| subject_area_housing
  metric_median_gross_rent -->|tagged to| theme_livability
  metric_median_gross_rent -->|valid for| geo_level_cbsa
  metric_median_gross_rent -->|valid for| geo_level_county
  metric_median_gross_rent -->|valid for| geo_level_division
  metric_median_gross_rent -->|valid for| geo_level_place
  metric_median_gross_rent -->|valid for| geo_level_region
  metric_median_gross_rent -->|valid for| geo_level_state
  metric_median_gross_rent -->|valid for| geo_level_tract
  metric_median_gross_rent -->|valid for| geo_level_us
  metric_median_gross_rent -->|valid for| geo_level_zcta
  metric_median_hh_income -->|from table| table_economics_income_wide
  metric_median_hh_income -->|subject area| subject_area_income
  metric_median_hh_income -->|tagged to| theme_character
  metric_median_hh_income -->|tagged to| theme_livability
  metric_median_hh_income -->|tagged to| theme_opportunity
  metric_median_hh_income -->|valid for| geo_level_cbsa
  metric_median_hh_income -->|valid for| geo_level_county
  metric_median_hh_income -->|valid for| geo_level_division
  metric_median_hh_income -->|valid for| geo_level_place
  metric_median_hh_income -->|valid for| geo_level_region
  metric_median_hh_income -->|valid for| geo_level_state
  metric_median_hh_income -->|valid for| geo_level_tract
  metric_median_hh_income -->|valid for| geo_level_us
  metric_median_hh_income -->|valid for| geo_level_zcta
  metric_median_home_value -->|from table| table_housing_core_wide
  metric_median_home_value -->|subject area| subject_area_housing
  metric_median_home_value -->|tagged to| theme_livability
  metric_median_home_value -->|tagged to| theme_opportunity
  metric_median_home_value -->|valid for| geo_level_cbsa
  metric_median_home_value -->|valid for| geo_level_county
  metric_median_home_value -->|valid for| geo_level_division
  metric_median_home_value -->|valid for| geo_level_place
  metric_median_home_value -->|valid for| geo_level_region
  metric_median_home_value -->|valid for| geo_level_state
  metric_median_home_value -->|valid for| geo_level_tract
  metric_median_home_value -->|valid for| geo_level_us
  metric_median_home_value -->|valid for| geo_level_zcta
  metric_migration_churn -->|from table| table_migration_wide
  metric_migration_churn -->|subject area| subject_area_migration
  metric_migration_churn -->|tagged to| theme_character
  metric_migration_churn -->|valid for| geo_level_cbsa
  metric_migration_churn -->|valid for| geo_level_county
  metric_migration_churn -->|valid for| geo_level_division
  metric_migration_churn -->|valid for| geo_level_place
  metric_migration_churn -->|valid for| geo_level_region
  metric_migration_churn -->|valid for| geo_level_state
  metric_migration_churn -->|valid for| geo_level_tract
  metric_migration_churn -->|valid for| geo_level_us
  metric_migration_churn -->|valid for| geo_level_zcta
  metric_mobility_rate -->|from table| table_migration_wide
  metric_mobility_rate -->|subject area| subject_area_migration
  metric_mobility_rate -->|tagged to| theme_character
  metric_mobility_rate -->|valid for| geo_level_cbsa
  metric_mobility_rate -->|valid for| geo_level_county
  metric_mobility_rate -->|valid for| geo_level_division
  metric_mobility_rate -->|valid for| geo_level_place
  metric_mobility_rate -->|valid for| geo_level_region
  metric_mobility_rate -->|valid for| geo_level_state
  metric_mobility_rate -->|valid for| geo_level_tract
  metric_mobility_rate -->|valid for| geo_level_us
  metric_mobility_rate -->|valid for| geo_level_zcta
  metric_nominal_gdp_growth_5yr -->|from table| table_economics_gdp_wide
  metric_nominal_gdp_growth_5yr -->|subject area| subject_area_gdp_growth
  metric_nominal_gdp_growth_5yr -->|tagged to| theme_opportunity
  metric_nominal_gdp_growth_5yr -->|valid for| geo_level_cbsa
  metric_nominal_gdp_growth_5yr -->|valid for| geo_level_county
  metric_nominal_gdp_growth_5yr -->|valid for| geo_level_division
  metric_nominal_gdp_growth_5yr -->|valid for| geo_level_place
  metric_nominal_gdp_growth_5yr -->|valid for| geo_level_region
  metric_nominal_gdp_growth_5yr -->|valid for| geo_level_state
  metric_nominal_gdp_growth_5yr -->|valid for| geo_level_tract
  metric_nominal_gdp_growth_5yr -->|valid for| geo_level_us
  metric_nominal_gdp_growth_5yr -->|valid for| geo_level_zcta
  metric_nominal_gdp_pc -->|from table| table_economics_gdp_wide
  metric_nominal_gdp_pc -->|subject area| subject_area_gdp
  metric_nominal_gdp_pc -->|tagged to| theme_opportunity
  metric_nominal_gdp_pc -->|valid for| geo_level_cbsa
  metric_nominal_gdp_pc -->|valid for| geo_level_county
  metric_nominal_gdp_pc -->|valid for| geo_level_division
  metric_nominal_gdp_pc -->|valid for| geo_level_place
  metric_nominal_gdp_pc -->|valid for| geo_level_region
  metric_nominal_gdp_pc -->|valid for| geo_level_state
  metric_nominal_gdp_pc -->|valid for| geo_level_tract
  metric_nominal_gdp_pc -->|valid for| geo_level_us
  metric_nominal_gdp_pc -->|valid for| geo_level_zcta
  metric_nominal_gdp_total -->|from table| table_economics_gdp_wide
  metric_nominal_gdp_total -->|subject area| subject_area_gdp
  metric_nominal_gdp_total -->|tagged to| theme_opportunity
  metric_nominal_gdp_total -->|valid for| geo_level_cbsa
  metric_nominal_gdp_total -->|valid for| geo_level_county
  metric_nominal_gdp_total -->|valid for| geo_level_division
  metric_nominal_gdp_total -->|valid for| geo_level_place
  metric_nominal_gdp_total -->|valid for| geo_level_region
  metric_nominal_gdp_total -->|valid for| geo_level_state
  metric_nominal_gdp_total -->|valid for| geo_level_tract
  metric_nominal_gdp_total -->|valid for| geo_level_us
  metric_nominal_gdp_total -->|valid for| geo_level_zcta
  metric_owner_occ_rate -->|from table| table_housing_core_wide
  metric_owner_occ_rate -->|subject area| subject_area_housing
  metric_owner_occ_rate -->|tagged to| theme_character
  metric_owner_occ_rate -->|tagged to| theme_livability
  metric_owner_occ_rate -->|valid for| geo_level_cbsa
  metric_owner_occ_rate -->|valid for| geo_level_county
  metric_owner_occ_rate -->|valid for| geo_level_division
  metric_owner_occ_rate -->|valid for| geo_level_place
  metric_owner_occ_rate -->|valid for| geo_level_region
  metric_owner_occ_rate -->|valid for| geo_level_state
  metric_owner_occ_rate -->|valid for| geo_level_tract
  metric_owner_occ_rate -->|valid for| geo_level_us
  metric_owner_occ_rate -->|valid for| geo_level_zcta
  metric_pct_acs_ind_arts_accomm_food -->|from table| table_economics_industry_wide
  metric_pct_acs_ind_arts_accomm_food -->|subject area| subject_area_industry
  metric_pct_acs_ind_arts_accomm_food -->|tagged to| theme_character
  metric_pct_acs_ind_arts_accomm_food -->|tagged to| theme_opportunity
  metric_pct_acs_ind_arts_accomm_food -->|valid for| geo_level_cbsa
  metric_pct_acs_ind_arts_accomm_food -->|valid for| geo_level_county
  metric_pct_acs_ind_arts_accomm_food -->|valid for| geo_level_division
  metric_pct_acs_ind_arts_accomm_food -->|valid for| geo_level_place
  metric_pct_acs_ind_arts_accomm_food -->|valid for| geo_level_region
  metric_pct_acs_ind_arts_accomm_food -->|valid for| geo_level_state
  metric_pct_acs_ind_arts_accomm_food -->|valid for| geo_level_tract
  metric_pct_acs_ind_arts_accomm_food -->|valid for| geo_level_us
  metric_pct_acs_ind_arts_accomm_food -->|valid for| geo_level_zcta
  metric_pct_acs_ind_educ_health -->|from table| table_economics_industry_wide
  metric_pct_acs_ind_educ_health -->|subject area| subject_area_industry
  metric_pct_acs_ind_educ_health -->|tagged to| theme_livability
  metric_pct_acs_ind_educ_health -->|tagged to| theme_opportunity
  metric_pct_acs_ind_educ_health -->|valid for| geo_level_cbsa
  metric_pct_acs_ind_educ_health -->|valid for| geo_level_county
  metric_pct_acs_ind_educ_health -->|valid for| geo_level_division
  metric_pct_acs_ind_educ_health -->|valid for| geo_level_place
  metric_pct_acs_ind_educ_health -->|valid for| geo_level_region
  metric_pct_acs_ind_educ_health -->|valid for| geo_level_state
  metric_pct_acs_ind_educ_health -->|valid for| geo_level_tract
  metric_pct_acs_ind_educ_health -->|valid for| geo_level_us
  metric_pct_acs_ind_educ_health -->|valid for| geo_level_zcta
  metric_pct_acs_ind_manufacturing -->|from table| table_economics_industry_wide
  metric_pct_acs_ind_manufacturing -->|subject area| subject_area_industry
  metric_pct_acs_ind_manufacturing -->|tagged to| theme_opportunity
  metric_pct_acs_ind_manufacturing -->|valid for| geo_level_cbsa
  metric_pct_acs_ind_manufacturing -->|valid for| geo_level_county
  metric_pct_acs_ind_manufacturing -->|valid for| geo_level_division
  metric_pct_acs_ind_manufacturing -->|valid for| geo_level_place
  metric_pct_acs_ind_manufacturing -->|valid for| geo_level_region
  metric_pct_acs_ind_manufacturing -->|valid for| geo_level_state
  metric_pct_acs_ind_manufacturing -->|valid for| geo_level_tract
  metric_pct_acs_ind_manufacturing -->|valid for| geo_level_us
  metric_pct_acs_ind_manufacturing -->|valid for| geo_level_zcta
  metric_pct_acs_ind_professional -->|from table| table_economics_industry_wide
  metric_pct_acs_ind_professional -->|subject area| subject_area_industry
  metric_pct_acs_ind_professional -->|tagged to| theme_opportunity
  metric_pct_acs_ind_professional -->|valid for| geo_level_cbsa
  metric_pct_acs_ind_professional -->|valid for| geo_level_county
  metric_pct_acs_ind_professional -->|valid for| geo_level_division
  metric_pct_acs_ind_professional -->|valid for| geo_level_place
  metric_pct_acs_ind_professional -->|valid for| geo_level_region
  metric_pct_acs_ind_professional -->|valid for| geo_level_state
  metric_pct_acs_ind_professional -->|valid for| geo_level_tract
  metric_pct_acs_ind_professional -->|valid for| geo_level_us
  metric_pct_acs_ind_professional -->|valid for| geo_level_zcta
  metric_pct_age_18_64 -->|from table| table_population_demographics
  metric_pct_age_18_64 -->|subject area| subject_area_population
  metric_pct_age_18_64 -->|tagged to| theme_character
  metric_pct_age_18_64 -->|tagged to| theme_opportunity
  metric_pct_age_18_64 -->|valid for| geo_level_cbsa
  metric_pct_age_18_64 -->|valid for| geo_level_county
  metric_pct_age_18_64 -->|valid for| geo_level_division
  metric_pct_age_18_64 -->|valid for| geo_level_place
  metric_pct_age_18_64 -->|valid for| geo_level_region
  metric_pct_age_18_64 -->|valid for| geo_level_state
  metric_pct_age_18_64 -->|valid for| geo_level_tract
  metric_pct_age_18_64 -->|valid for| geo_level_us
  metric_pct_age_18_64 -->|valid for| geo_level_zcta
  metric_pct_age_over_64 -->|from table| table_population_demographics
  metric_pct_age_over_64 -->|subject area| subject_area_population
  metric_pct_age_over_64 -->|tagged to| theme_character
  metric_pct_age_over_64 -->|valid for| geo_level_cbsa
  metric_pct_age_over_64 -->|valid for| geo_level_county
  metric_pct_age_over_64 -->|valid for| geo_level_division
  metric_pct_age_over_64 -->|valid for| geo_level_place
  metric_pct_age_over_64 -->|valid for| geo_level_region
  metric_pct_age_over_64 -->|valid for| geo_level_state
  metric_pct_age_over_64 -->|valid for| geo_level_tract
  metric_pct_age_over_64 -->|valid for| geo_level_us
  metric_pct_age_over_64 -->|valid for| geo_level_zcta
  metric_pct_age_under_18 -->|from table| table_population_demographics
  metric_pct_age_under_18 -->|subject area| subject_area_population
  metric_pct_age_under_18 -->|tagged to| theme_character
  metric_pct_age_under_18 -->|valid for| geo_level_cbsa
  metric_pct_age_under_18 -->|valid for| geo_level_county
  metric_pct_age_under_18 -->|valid for| geo_level_division
  metric_pct_age_under_18 -->|valid for| geo_level_place
  metric_pct_age_under_18 -->|valid for| geo_level_region
  metric_pct_age_under_18 -->|valid for| geo_level_state
  metric_pct_age_under_18 -->|valid for| geo_level_tract
  metric_pct_age_under_18 -->|valid for| geo_level_us
  metric_pct_age_under_18 -->|valid for| geo_level_zcta
  metric_pct_asian_nh -->|from table| table_population_demographics
  metric_pct_asian_nh -->|subject area| subject_area_race_ethnicity
  metric_pct_asian_nh -->|tagged to| theme_character
  metric_pct_asian_nh -->|valid for| geo_level_cbsa
  metric_pct_asian_nh -->|valid for| geo_level_county
  metric_pct_asian_nh -->|valid for| geo_level_division
  metric_pct_asian_nh -->|valid for| geo_level_place
  metric_pct_asian_nh -->|valid for| geo_level_region
  metric_pct_asian_nh -->|valid for| geo_level_state
  metric_pct_asian_nh -->|valid for| geo_level_tract
  metric_pct_asian_nh -->|valid for| geo_level_us
  metric_pct_asian_nh -->|valid for| geo_level_zcta
  metric_pct_ba_plus -->|from table| table_population_demographics
  metric_pct_ba_plus -->|subject area| subject_area_education
  metric_pct_ba_plus -->|tagged to| theme_character
  metric_pct_ba_plus -->|tagged to| theme_livability
  metric_pct_ba_plus -->|tagged to| theme_opportunity
  metric_pct_ba_plus -->|valid for| geo_level_cbsa
  metric_pct_ba_plus -->|valid for| geo_level_county
  metric_pct_ba_plus -->|valid for| geo_level_division
  metric_pct_ba_plus -->|valid for| geo_level_place
  metric_pct_ba_plus -->|valid for| geo_level_region
  metric_pct_ba_plus -->|valid for| geo_level_state
  metric_pct_ba_plus -->|valid for| geo_level_tract
  metric_pct_ba_plus -->|valid for| geo_level_us
  metric_pct_ba_plus -->|valid for| geo_level_zcta
  metric_pct_black_nh -->|from table| table_population_demographics
  metric_pct_black_nh -->|subject area| subject_area_race_ethnicity
  metric_pct_black_nh -->|tagged to| theme_character
  metric_pct_black_nh -->|valid for| geo_level_cbsa
  metric_pct_black_nh -->|valid for| geo_level_county
  metric_pct_black_nh -->|valid for| geo_level_division
  metric_pct_black_nh -->|valid for| geo_level_place
  metric_pct_black_nh -->|valid for| geo_level_region
  metric_pct_black_nh -->|valid for| geo_level_state
  metric_pct_black_nh -->|valid for| geo_level_tract
  metric_pct_black_nh -->|valid for| geo_level_us
  metric_pct_black_nh -->|valid for| geo_level_zcta
  metric_pct_commute_drive_alone -->|from table| table_transport_built_form_wide
  metric_pct_commute_drive_alone -->|subject area| subject_area_transport
  metric_pct_commute_drive_alone -->|tagged to| theme_livability
  metric_pct_commute_drive_alone -->|valid for| geo_level_cbsa
  metric_pct_commute_drive_alone -->|valid for| geo_level_county
  metric_pct_commute_drive_alone -->|valid for| geo_level_division
  metric_pct_commute_drive_alone -->|valid for| geo_level_place
  metric_pct_commute_drive_alone -->|valid for| geo_level_region
  metric_pct_commute_drive_alone -->|valid for| geo_level_state
  metric_pct_commute_drive_alone -->|valid for| geo_level_tract
  metric_pct_commute_drive_alone -->|valid for| geo_level_us
  metric_pct_commute_drive_alone -->|valid for| geo_level_zcta
  metric_pct_commute_transit -->|from table| table_transport_built_form_wide
  metric_pct_commute_transit -->|subject area| subject_area_transport
  metric_pct_commute_transit -->|tagged to| theme_livability
  metric_pct_commute_transit -->|valid for| geo_level_cbsa
  metric_pct_commute_transit -->|valid for| geo_level_county
  metric_pct_commute_transit -->|valid for| geo_level_division
  metric_pct_commute_transit -->|valid for| geo_level_place
  metric_pct_commute_transit -->|valid for| geo_level_region
  metric_pct_commute_transit -->|valid for| geo_level_state
  metric_pct_commute_transit -->|valid for| geo_level_tract
  metric_pct_commute_transit -->|valid for| geo_level_us
  metric_pct_commute_transit -->|valid for| geo_level_zcta
  metric_pct_commute_walk -->|from table| table_transport_built_form_wide
  metric_pct_commute_walk -->|subject area| subject_area_transport
  metric_pct_commute_walk -->|tagged to| theme_character
  metric_pct_commute_walk -->|tagged to| theme_livability
  metric_pct_commute_walk -->|valid for| geo_level_cbsa
  metric_pct_commute_walk -->|valid for| geo_level_county
  metric_pct_commute_walk -->|valid for| geo_level_division
  metric_pct_commute_walk -->|valid for| geo_level_place
  metric_pct_commute_walk -->|valid for| geo_level_region
  metric_pct_commute_walk -->|valid for| geo_level_state
  metric_pct_commute_walk -->|valid for| geo_level_tract
  metric_pct_commute_walk -->|valid for| geo_level_us
  metric_pct_commute_walk -->|valid for| geo_level_zcta
  metric_pct_commute_wfh -->|from table| table_transport_built_form_wide
  metric_pct_commute_wfh -->|subject area| subject_area_transport
  metric_pct_commute_wfh -->|tagged to| theme_livability
  metric_pct_commute_wfh -->|tagged to| theme_opportunity
  metric_pct_commute_wfh -->|valid for| geo_level_cbsa
  metric_pct_commute_wfh -->|valid for| geo_level_county
  metric_pct_commute_wfh -->|valid for| geo_level_division
  metric_pct_commute_wfh -->|valid for| geo_level_place
  metric_pct_commute_wfh -->|valid for| geo_level_region
  metric_pct_commute_wfh -->|valid for| geo_level_state
  metric_pct_commute_wfh -->|valid for| geo_level_tract
  metric_pct_commute_wfh -->|valid for| geo_level_us
  metric_pct_commute_wfh -->|valid for| geo_level_zcta
  metric_pct_foreign_born -->|from table| table_migration_wide
  metric_pct_foreign_born -->|subject area| subject_area_nativity
  metric_pct_foreign_born -->|tagged to| theme_character
  metric_pct_foreign_born -->|valid for| geo_level_cbsa
  metric_pct_foreign_born -->|valid for| geo_level_county
  metric_pct_foreign_born -->|valid for| geo_level_division
  metric_pct_foreign_born -->|valid for| geo_level_place
  metric_pct_foreign_born -->|valid for| geo_level_region
  metric_pct_foreign_born -->|valid for| geo_level_state
  metric_pct_foreign_born -->|valid for| geo_level_tract
  metric_pct_foreign_born -->|valid for| geo_level_us
  metric_pct_foreign_born -->|valid for| geo_level_zcta
  metric_pct_grad_plus -->|from table| table_population_demographics
  metric_pct_grad_plus -->|subject area| subject_area_education
  metric_pct_grad_plus -->|tagged to| theme_character
  metric_pct_grad_plus -->|tagged to| theme_opportunity
  metric_pct_grad_plus -->|valid for| geo_level_cbsa
  metric_pct_grad_plus -->|valid for| geo_level_county
  metric_pct_grad_plus -->|valid for| geo_level_division
  metric_pct_grad_plus -->|valid for| geo_level_place
  metric_pct_grad_plus -->|valid for| geo_level_region
  metric_pct_grad_plus -->|valid for| geo_level_state
  metric_pct_grad_plus -->|valid for| geo_level_tract
  metric_pct_grad_plus -->|valid for| geo_level_us
  metric_pct_grad_plus -->|valid for| geo_level_zcta
  metric_pct_hh_0_vehicles -->|from table| table_transport_built_form_wide
  metric_pct_hh_0_vehicles -->|subject area| subject_area_transport
  metric_pct_hh_0_vehicles -->|tagged to| theme_livability
  metric_pct_hh_0_vehicles -->|valid for| geo_level_cbsa
  metric_pct_hh_0_vehicles -->|valid for| geo_level_county
  metric_pct_hh_0_vehicles -->|valid for| geo_level_division
  metric_pct_hh_0_vehicles -->|valid for| geo_level_place
  metric_pct_hh_0_vehicles -->|valid for| geo_level_region
  metric_pct_hh_0_vehicles -->|valid for| geo_level_state
  metric_pct_hh_0_vehicles -->|valid for| geo_level_tract
  metric_pct_hh_0_vehicles -->|valid for| geo_level_us
  metric_pct_hh_0_vehicles -->|valid for| geo_level_zcta
  metric_pct_hispanic -->|from table| table_population_demographics
  metric_pct_hispanic -->|subject area| subject_area_race_ethnicity
  metric_pct_hispanic -->|tagged to| theme_character
  metric_pct_hispanic -->|valid for| geo_level_cbsa
  metric_pct_hispanic -->|valid for| geo_level_county
  metric_pct_hispanic -->|valid for| geo_level_division
  metric_pct_hispanic -->|valid for| geo_level_place
  metric_pct_hispanic -->|valid for| geo_level_region
  metric_pct_hispanic -->|valid for| geo_level_state
  metric_pct_hispanic -->|valid for| geo_level_tract
  metric_pct_hispanic -->|valid for| geo_level_us
  metric_pct_hispanic -->|valid for| geo_level_zcta
  metric_pct_low_car_commute -->|from table| table_transport_built_form_wide
  metric_pct_low_car_commute -->|subject area| subject_area_transport
  metric_pct_low_car_commute -->|tagged to| theme_livability
  metric_pct_low_car_commute -->|valid for| geo_level_cbsa
  metric_pct_low_car_commute -->|valid for| geo_level_county
  metric_pct_low_car_commute -->|valid for| geo_level_division
  metric_pct_low_car_commute -->|valid for| geo_level_place
  metric_pct_low_car_commute -->|valid for| geo_level_region
  metric_pct_low_car_commute -->|valid for| geo_level_state
  metric_pct_low_car_commute -->|valid for| geo_level_tract
  metric_pct_low_car_commute -->|valid for| geo_level_us
  metric_pct_low_car_commute -->|valid for| geo_level_zcta
  metric_pct_moved_abroad -->|from table| table_migration_wide
  metric_pct_moved_abroad -->|subject area| subject_area_migration
  metric_pct_moved_abroad -->|tagged to| theme_character
  metric_pct_moved_abroad -->|valid for| geo_level_cbsa
  metric_pct_moved_abroad -->|valid for| geo_level_county
  metric_pct_moved_abroad -->|valid for| geo_level_division
  metric_pct_moved_abroad -->|valid for| geo_level_place
  metric_pct_moved_abroad -->|valid for| geo_level_region
  metric_pct_moved_abroad -->|valid for| geo_level_state
  metric_pct_moved_abroad -->|valid for| geo_level_tract
  metric_pct_moved_abroad -->|valid for| geo_level_us
  metric_pct_moved_abroad -->|valid for| geo_level_zcta
  metric_pct_moved_diff_st -->|from table| table_migration_wide
  metric_pct_moved_diff_st -->|subject area| subject_area_migration
  metric_pct_moved_diff_st -->|tagged to| theme_character
  metric_pct_moved_diff_st -->|tagged to| theme_opportunity
  metric_pct_moved_diff_st -->|valid for| geo_level_cbsa
  metric_pct_moved_diff_st -->|valid for| geo_level_county
  metric_pct_moved_diff_st -->|valid for| geo_level_division
  metric_pct_moved_diff_st -->|valid for| geo_level_place
  metric_pct_moved_diff_st -->|valid for| geo_level_region
  metric_pct_moved_diff_st -->|valid for| geo_level_state
  metric_pct_moved_diff_st -->|valid for| geo_level_tract
  metric_pct_moved_diff_st -->|valid for| geo_level_us
  metric_pct_moved_diff_st -->|valid for| geo_level_zcta
  metric_pct_non_citizen -->|from table| table_migration_wide
  metric_pct_non_citizen -->|subject area| subject_area_nativity
  metric_pct_non_citizen -->|tagged to| theme_character
  metric_pct_non_citizen -->|valid for| geo_level_cbsa
  metric_pct_non_citizen -->|valid for| geo_level_county
  metric_pct_non_citizen -->|valid for| geo_level_division
  metric_pct_non_citizen -->|valid for| geo_level_place
  metric_pct_non_citizen -->|valid for| geo_level_region
  metric_pct_non_citizen -->|valid for| geo_level_state
  metric_pct_non_citizen -->|valid for| geo_level_tract
  metric_pct_non_citizen -->|valid for| geo_level_us
  metric_pct_non_citizen -->|valid for| geo_level_zcta
  metric_pct_real_gdp_edu_health -->|from table| table_economics_industry_wide
  metric_pct_real_gdp_edu_health -->|subject area| subject_area_industry
  metric_pct_real_gdp_edu_health -->|tagged to| theme_livability
  metric_pct_real_gdp_edu_health -->|tagged to| theme_opportunity
  metric_pct_real_gdp_edu_health -->|valid for| geo_level_cbsa
  metric_pct_real_gdp_edu_health -->|valid for| geo_level_county
  metric_pct_real_gdp_edu_health -->|valid for| geo_level_division
  metric_pct_real_gdp_edu_health -->|valid for| geo_level_place
  metric_pct_real_gdp_edu_health -->|valid for| geo_level_region
  metric_pct_real_gdp_edu_health -->|valid for| geo_level_state
  metric_pct_real_gdp_edu_health -->|valid for| geo_level_tract
  metric_pct_real_gdp_edu_health -->|valid for| geo_level_us
  metric_pct_real_gdp_edu_health -->|valid for| geo_level_zcta
  metric_pct_real_gdp_manufacturing -->|from table| table_economics_industry_wide
  metric_pct_real_gdp_manufacturing -->|subject area| subject_area_industry
  metric_pct_real_gdp_manufacturing -->|tagged to| theme_opportunity
  metric_pct_real_gdp_manufacturing -->|valid for| geo_level_cbsa
  metric_pct_real_gdp_manufacturing -->|valid for| geo_level_county
  metric_pct_real_gdp_manufacturing -->|valid for| geo_level_division
  metric_pct_real_gdp_manufacturing -->|valid for| geo_level_place
  metric_pct_real_gdp_manufacturing -->|valid for| geo_level_region
  metric_pct_real_gdp_manufacturing -->|valid for| geo_level_state
  metric_pct_real_gdp_manufacturing -->|valid for| geo_level_tract
  metric_pct_real_gdp_manufacturing -->|valid for| geo_level_us
  metric_pct_real_gdp_manufacturing -->|valid for| geo_level_zcta
  metric_pct_real_gdp_professional -->|from table| table_economics_industry_wide
  metric_pct_real_gdp_professional -->|subject area| subject_area_industry
  metric_pct_real_gdp_professional -->|tagged to| theme_opportunity
  metric_pct_real_gdp_professional -->|valid for| geo_level_cbsa
  metric_pct_real_gdp_professional -->|valid for| geo_level_county
  metric_pct_real_gdp_professional -->|valid for| geo_level_division
  metric_pct_real_gdp_professional -->|valid for| geo_level_place
  metric_pct_real_gdp_professional -->|valid for| geo_level_region
  metric_pct_real_gdp_professional -->|valid for| geo_level_state
  metric_pct_real_gdp_professional -->|valid for| geo_level_tract
  metric_pct_real_gdp_professional -->|valid for| geo_level_us
  metric_pct_real_gdp_professional -->|valid for| geo_level_zcta
  metric_pct_rent_burden_30plus -->|from table| table_housing_core_wide
  metric_pct_rent_burden_30plus -->|subject area| subject_area_affordability
  metric_pct_rent_burden_30plus -->|tagged to| theme_livability
  metric_pct_rent_burden_30plus -->|valid for| geo_level_cbsa
  metric_pct_rent_burden_30plus -->|valid for| geo_level_county
  metric_pct_rent_burden_30plus -->|valid for| geo_level_division
  metric_pct_rent_burden_30plus -->|valid for| geo_level_place
  metric_pct_rent_burden_30plus -->|valid for| geo_level_region
  metric_pct_rent_burden_30plus -->|valid for| geo_level_state
  metric_pct_rent_burden_30plus -->|valid for| geo_level_tract
  metric_pct_rent_burden_30plus -->|valid for| geo_level_us
  metric_pct_rent_burden_30plus -->|valid for| geo_level_zcta
  metric_pct_rent_burden_50plus -->|from table| table_housing_core_wide
  metric_pct_rent_burden_50plus -->|subject area| subject_area_affordability
  metric_pct_rent_burden_50plus -->|tagged to| theme_livability
  metric_pct_rent_burden_50plus -->|valid for| geo_level_cbsa
  metric_pct_rent_burden_50plus -->|valid for| geo_level_county
  metric_pct_rent_burden_50plus -->|valid for| geo_level_division
  metric_pct_rent_burden_50plus -->|valid for| geo_level_place
  metric_pct_rent_burden_50plus -->|valid for| geo_level_region
  metric_pct_rent_burden_50plus -->|valid for| geo_level_state
  metric_pct_rent_burden_50plus -->|valid for| geo_level_tract
  metric_pct_rent_burden_50plus -->|valid for| geo_level_us
  metric_pct_rent_burden_50plus -->|valid for| geo_level_zcta
  metric_pct_same_house -->|from table| table_migration_wide
  metric_pct_same_house -->|subject area| subject_area_migration
  metric_pct_same_house -->|tagged to| theme_character
  metric_pct_same_house -->|valid for| geo_level_cbsa
  metric_pct_same_house -->|valid for| geo_level_county
  metric_pct_same_house -->|valid for| geo_level_division
  metric_pct_same_house -->|valid for| geo_level_place
  metric_pct_same_house -->|valid for| geo_level_region
  metric_pct_same_house -->|valid for| geo_level_state
  metric_pct_same_house -->|valid for| geo_level_tract
  metric_pct_same_house -->|valid for| geo_level_us
  metric_pct_same_house -->|valid for| geo_level_zcta
  metric_pct_struct_multifam -->|from table| table_housing_core_wide
  metric_pct_struct_multifam -->|subject area| subject_area_built_form
  metric_pct_struct_multifam -->|tagged to| theme_character
  metric_pct_struct_multifam -->|tagged to| theme_livability
  metric_pct_struct_multifam -->|valid for| geo_level_cbsa
  metric_pct_struct_multifam -->|valid for| geo_level_county
  metric_pct_struct_multifam -->|valid for| geo_level_division
  metric_pct_struct_multifam -->|valid for| geo_level_place
  metric_pct_struct_multifam -->|valid for| geo_level_region
  metric_pct_struct_multifam -->|valid for| geo_level_state
  metric_pct_struct_multifam -->|valid for| geo_level_tract
  metric_pct_struct_multifam -->|valid for| geo_level_us
  metric_pct_struct_multifam -->|valid for| geo_level_zcta
  metric_pct_unemployment_rate -->|from table| table_economics_labor_wide
  metric_pct_unemployment_rate -->|subject area| subject_area_labor
  metric_pct_unemployment_rate -->|tagged to| theme_opportunity
  metric_pct_unemployment_rate -->|valid for| geo_level_cbsa
  metric_pct_unemployment_rate -->|valid for| geo_level_county
  metric_pct_unemployment_rate -->|valid for| geo_level_division
  metric_pct_unemployment_rate -->|valid for| geo_level_place
  metric_pct_unemployment_rate -->|valid for| geo_level_region
  metric_pct_unemployment_rate -->|valid for| geo_level_state
  metric_pct_unemployment_rate -->|valid for| geo_level_tract
  metric_pct_unemployment_rate -->|valid for| geo_level_us
  metric_pct_unemployment_rate -->|valid for| geo_level_zcta
  metric_pct_white_nh -->|from table| table_population_demographics
  metric_pct_white_nh -->|subject area| subject_area_race_ethnicity
  metric_pct_white_nh -->|tagged to| theme_character
  metric_pct_white_nh -->|valid for| geo_level_cbsa
  metric_pct_white_nh -->|valid for| geo_level_county
  metric_pct_white_nh -->|valid for| geo_level_division
  metric_pct_white_nh -->|valid for| geo_level_place
  metric_pct_white_nh -->|valid for| geo_level_region
  metric_pct_white_nh -->|valid for| geo_level_state
  metric_pct_white_nh -->|valid for| geo_level_tract
  metric_pct_white_nh -->|valid for| geo_level_us
  metric_pct_white_nh -->|valid for| geo_level_zcta
  metric_permits_per_1000_housing_units -->|from table| table_housing_core_wide
  metric_permits_per_1000_housing_units -->|subject area| subject_area_housing_supply
  metric_permits_per_1000_housing_units -->|tagged to| theme_livability
  metric_permits_per_1000_housing_units -->|tagged to| theme_opportunity
  metric_permits_per_1000_housing_units -->|valid for| geo_level_cbsa
  metric_permits_per_1000_housing_units -->|valid for| geo_level_county
  metric_permits_per_1000_housing_units -->|valid for| geo_level_division
  metric_permits_per_1000_housing_units -->|valid for| geo_level_place
  metric_permits_per_1000_housing_units -->|valid for| geo_level_region
  metric_permits_per_1000_housing_units -->|valid for| geo_level_state
  metric_permits_per_1000_housing_units -->|valid for| geo_level_tract
  metric_permits_per_1000_housing_units -->|valid for| geo_level_us
  metric_permits_per_1000_housing_units -->|valid for| geo_level_zcta
  metric_permits_share_multifam_units -->|from table| table_housing_core_wide
  metric_permits_share_multifam_units -->|subject area| subject_area_housing_supply
  metric_permits_share_multifam_units -->|tagged to| theme_livability
  metric_permits_share_multifam_units -->|tagged to| theme_opportunity
  metric_permits_share_multifam_units -->|valid for| geo_level_cbsa
  metric_permits_share_multifam_units -->|valid for| geo_level_county
  metric_permits_share_multifam_units -->|valid for| geo_level_division
  metric_permits_share_multifam_units -->|valid for| geo_level_place
  metric_permits_share_multifam_units -->|valid for| geo_level_region
  metric_permits_share_multifam_units -->|valid for| geo_level_state
  metric_permits_share_multifam_units -->|valid for| geo_level_tract
  metric_permits_share_multifam_units -->|valid for| geo_level_us
  metric_permits_share_multifam_units -->|valid for| geo_level_zcta
  metric_pi_total -->|from table| table_economics_income_wide
  metric_pi_total -->|subject area| subject_area_income
  metric_pi_total -->|tagged to| theme_opportunity
  metric_pi_total -->|valid for| geo_level_cbsa
  metric_pi_total -->|valid for| geo_level_county
  metric_pi_total -->|valid for| geo_level_division
  metric_pi_total -->|valid for| geo_level_place
  metric_pi_total -->|valid for| geo_level_region
  metric_pi_total -->|valid for| geo_level_state
  metric_pi_total -->|valid for| geo_level_tract
  metric_pi_total -->|valid for| geo_level_us
  metric_pi_total -->|valid for| geo_level_zcta
  metric_pi_wage_share -->|from table| table_economics_income_wide
  metric_pi_wage_share -->|subject area| subject_area_income_structure
  metric_pi_wage_share -->|tagged to| theme_opportunity
  metric_pi_wage_share -->|valid for| geo_level_cbsa
  metric_pi_wage_share -->|valid for| geo_level_county
  metric_pi_wage_share -->|valid for| geo_level_division
  metric_pi_wage_share -->|valid for| geo_level_place
  metric_pi_wage_share -->|valid for| geo_level_region
  metric_pi_wage_share -->|valid for| geo_level_state
  metric_pi_wage_share -->|valid for| geo_level_tract
  metric_pi_wage_share -->|valid for| geo_level_us
  metric_pi_wage_share -->|valid for| geo_level_zcta
  metric_pi_wages_salary -->|from table| table_economics_income_wide
  metric_pi_wages_salary -->|subject area| subject_area_income
  metric_pi_wages_salary -->|tagged to| theme_opportunity
  metric_pi_wages_salary -->|valid for| geo_level_cbsa
  metric_pi_wages_salary -->|valid for| geo_level_county
  metric_pi_wages_salary -->|valid for| geo_level_division
  metric_pi_wages_salary -->|valid for| geo_level_place
  metric_pi_wages_salary -->|valid for| geo_level_region
  metric_pi_wages_salary -->|valid for| geo_level_state
  metric_pi_wages_salary -->|valid for| geo_level_tract
  metric_pi_wages_salary -->|valid for| geo_level_us
  metric_pi_wages_salary -->|valid for| geo_level_zcta
  metric_pop_growth_10yr -->|from table| table_population_demographics
  metric_pop_growth_10yr -->|subject area| subject_area_population
  metric_pop_growth_10yr -->|tagged to| theme_character
  metric_pop_growth_10yr -->|tagged to| theme_opportunity
  metric_pop_growth_10yr -->|valid for| geo_level_cbsa
  metric_pop_growth_10yr -->|valid for| geo_level_county
  metric_pop_growth_10yr -->|valid for| geo_level_division
  metric_pop_growth_10yr -->|valid for| geo_level_place
  metric_pop_growth_10yr -->|valid for| geo_level_region
  metric_pop_growth_10yr -->|valid for| geo_level_state
  metric_pop_growth_10yr -->|valid for| geo_level_tract
  metric_pop_growth_10yr -->|valid for| geo_level_us
  metric_pop_growth_10yr -->|valid for| geo_level_zcta
  metric_pop_growth_1yr -->|from table| table_population_demographics
  metric_pop_growth_1yr -->|subject area| subject_area_population
  metric_pop_growth_1yr -->|tagged to| theme_character
  metric_pop_growth_1yr -->|tagged to| theme_opportunity
  metric_pop_growth_1yr -->|valid for| geo_level_cbsa
  metric_pop_growth_1yr -->|valid for| geo_level_county
  metric_pop_growth_1yr -->|valid for| geo_level_division
  metric_pop_growth_1yr -->|valid for| geo_level_place
  metric_pop_growth_1yr -->|valid for| geo_level_region
  metric_pop_growth_1yr -->|valid for| geo_level_state
  metric_pop_growth_1yr -->|valid for| geo_level_tract
  metric_pop_growth_1yr -->|valid for| geo_level_us
  metric_pop_growth_1yr -->|valid for| geo_level_zcta
  metric_pop_growth_5yr -->|from table| table_population_demographics
  metric_pop_growth_5yr -->|subject area| subject_area_population
  metric_pop_growth_5yr -->|tagged to| theme_character
  metric_pop_growth_5yr -->|tagged to| theme_opportunity
  metric_pop_growth_5yr -->|valid for| geo_level_cbsa
  metric_pop_growth_5yr -->|valid for| geo_level_county
  metric_pop_growth_5yr -->|valid for| geo_level_division
  metric_pop_growth_5yr -->|valid for| geo_level_place
  metric_pop_growth_5yr -->|valid for| geo_level_region
  metric_pop_growth_5yr -->|valid for| geo_level_state
  metric_pop_growth_5yr -->|valid for| geo_level_tract
  metric_pop_growth_5yr -->|valid for| geo_level_us
  metric_pop_growth_5yr -->|valid for| geo_level_zcta
  metric_pop_total -->|from table| table_population_demographics
  metric_pop_total -->|subject area| subject_area_population
  metric_pop_total -->|tagged to| theme_character
  metric_pop_total -->|tagged to| theme_opportunity
  metric_pop_total -->|valid for| geo_level_cbsa
  metric_pop_total -->|valid for| geo_level_county
  metric_pop_total -->|valid for| geo_level_division
  metric_pop_total -->|valid for| geo_level_place
  metric_pop_total -->|valid for| geo_level_region
  metric_pop_total -->|valid for| geo_level_state
  metric_pop_total -->|valid for| geo_level_tract
  metric_pop_total -->|valid for| geo_level_us
  metric_pop_total -->|valid for| geo_level_zcta
  metric_pop_weighted_density_sqmi -->|from table| table_transport_built_form_wide
  metric_pop_weighted_density_sqmi -->|subject area| subject_area_built_form
  metric_pop_weighted_density_sqmi -->|tagged to| theme_character
  metric_pop_weighted_density_sqmi -->|tagged to| theme_livability
  metric_pop_weighted_density_sqmi -->|valid for| geo_level_cbsa
  metric_pop_weighted_density_sqmi -->|valid for| geo_level_county
  metric_pop_weighted_density_sqmi -->|valid for| geo_level_division
  metric_pop_weighted_density_sqmi -->|valid for| geo_level_place
  metric_pop_weighted_density_sqmi -->|valid for| geo_level_region
  metric_pop_weighted_density_sqmi -->|valid for| geo_level_state
  metric_pop_weighted_density_sqmi -->|valid for| geo_level_tract
  metric_pop_weighted_density_sqmi -->|valid for| geo_level_us
  metric_pop_weighted_density_sqmi -->|valid for| geo_level_zcta
  metric_pov_rate -->|from table| table_economics_income_wide
  metric_pov_rate -->|subject area| subject_area_poverty
  metric_pov_rate -->|tagged to| theme_livability
  metric_pov_rate -->|tagged to| theme_opportunity
  metric_pov_rate -->|valid for| geo_level_cbsa
  metric_pov_rate -->|valid for| geo_level_county
  metric_pov_rate -->|valid for| geo_level_division
  metric_pov_rate -->|valid for| geo_level_place
  metric_pov_rate -->|valid for| geo_level_region
  metric_pov_rate -->|valid for| geo_level_state
  metric_pov_rate -->|valid for| geo_level_tract
  metric_pov_rate -->|valid for| geo_level_us
  metric_pov_rate -->|valid for| geo_level_zcta
  metric_productivity_growth_5yr -->|from table| table_economics_gdp_wide
  metric_productivity_growth_5yr -->|subject area| subject_area_productivity
  metric_productivity_growth_5yr -->|tagged to| theme_opportunity
  metric_productivity_growth_5yr -->|valid for| geo_level_cbsa
  metric_productivity_growth_5yr -->|valid for| geo_level_county
  metric_productivity_growth_5yr -->|valid for| geo_level_division
  metric_productivity_growth_5yr -->|valid for| geo_level_place
  metric_productivity_growth_5yr -->|valid for| geo_level_region
  metric_productivity_growth_5yr -->|valid for| geo_level_state
  metric_productivity_growth_5yr -->|valid for| geo_level_tract
  metric_productivity_growth_5yr -->|valid for| geo_level_us
  metric_productivity_growth_5yr -->|valid for| geo_level_zcta
  metric_productivity_index -->|from table| table_economics_gdp_wide
  metric_productivity_index -->|subject area| subject_area_productivity
  metric_productivity_index -->|tagged to| theme_opportunity
  metric_productivity_index -->|valid for| geo_level_cbsa
  metric_productivity_index -->|valid for| geo_level_county
  metric_productivity_index -->|valid for| geo_level_division
  metric_productivity_index -->|valid for| geo_level_place
  metric_productivity_index -->|valid for| geo_level_region
  metric_productivity_index -->|valid for| geo_level_state
  metric_productivity_index -->|valid for| geo_level_tract
  metric_productivity_index -->|valid for| geo_level_us
  metric_productivity_index -->|valid for| geo_level_zcta
  metric_real_gdp_growth_5yr -->|from table| table_economics_gdp_wide
  metric_real_gdp_growth_5yr -->|subject area| subject_area_gdp_growth
  metric_real_gdp_growth_5yr -->|tagged to| theme_opportunity
  metric_real_gdp_growth_5yr -->|valid for| geo_level_cbsa
  metric_real_gdp_growth_5yr -->|valid for| geo_level_county
  metric_real_gdp_growth_5yr -->|valid for| geo_level_division
  metric_real_gdp_growth_5yr -->|valid for| geo_level_place
  metric_real_gdp_growth_5yr -->|valid for| geo_level_region
  metric_real_gdp_growth_5yr -->|valid for| geo_level_state
  metric_real_gdp_growth_5yr -->|valid for| geo_level_tract
  metric_real_gdp_growth_5yr -->|valid for| geo_level_us
  metric_real_gdp_growth_5yr -->|valid for| geo_level_zcta
  metric_real_gdp_pc -->|from table| table_economics_gdp_wide
  metric_real_gdp_pc -->|subject area| subject_area_gdp
  metric_real_gdp_pc -->|tagged to| theme_opportunity
  metric_real_gdp_pc -->|valid for| geo_level_cbsa
  metric_real_gdp_pc -->|valid for| geo_level_county
  metric_real_gdp_pc -->|valid for| geo_level_division
  metric_real_gdp_pc -->|valid for| geo_level_place
  metric_real_gdp_pc -->|valid for| geo_level_region
  metric_real_gdp_pc -->|valid for| geo_level_state
  metric_real_gdp_pc -->|valid for| geo_level_tract
  metric_real_gdp_pc -->|valid for| geo_level_us
  metric_real_gdp_pc -->|valid for| geo_level_zcta
  metric_real_gdp_total -->|from table| table_economics_gdp_wide
  metric_real_gdp_total -->|subject area| subject_area_gdp
  metric_real_gdp_total -->|tagged to| theme_opportunity
  metric_real_gdp_total -->|valid for| geo_level_cbsa
  metric_real_gdp_total -->|valid for| geo_level_county
  metric_real_gdp_total -->|valid for| geo_level_division
  metric_real_gdp_total -->|valid for| geo_level_place
  metric_real_gdp_total -->|valid for| geo_level_region
  metric_real_gdp_total -->|valid for| geo_level_state
  metric_real_gdp_total -->|valid for| geo_level_tract
  metric_real_gdp_total -->|valid for| geo_level_us
  metric_real_gdp_total -->|valid for| geo_level_zcta
  metric_rent50_2br -->|from table| table_housing_core_wide
  metric_rent50_2br -->|subject area| subject_area_housing_benchmark
  metric_rent50_2br -->|tagged to| theme_livability
  metric_rent50_2br -->|valid for| geo_level_cbsa
  metric_rent50_2br -->|valid for| geo_level_county
  metric_rent50_2br -->|valid for| geo_level_division
  metric_rent50_2br -->|valid for| geo_level_place
  metric_rent50_2br -->|valid for| geo_level_region
  metric_rent50_2br -->|valid for| geo_level_state
  metric_rent50_2br -->|valid for| geo_level_tract
  metric_rent50_2br -->|valid for| geo_level_us
  metric_rent50_2br -->|valid for| geo_level_zcta
  metric_rent50_gap_2br_vs_median_rent -->|from table| table_housing_core_wide
  metric_rent50_gap_2br_vs_median_rent -->|subject area| subject_area_housing_benchmark
  metric_rent50_gap_2br_vs_median_rent -->|tagged to| theme_livability
  metric_rent50_gap_2br_vs_median_rent -->|tagged to| theme_opportunity
  metric_rent50_gap_2br_vs_median_rent -->|valid for| geo_level_cbsa
  metric_rent50_gap_2br_vs_median_rent -->|valid for| geo_level_county
  metric_rent50_gap_2br_vs_median_rent -->|valid for| geo_level_division
  metric_rent50_gap_2br_vs_median_rent -->|valid for| geo_level_place
  metric_rent50_gap_2br_vs_median_rent -->|valid for| geo_level_region
  metric_rent50_gap_2br_vs_median_rent -->|valid for| geo_level_state
  metric_rent50_gap_2br_vs_median_rent -->|valid for| geo_level_tract
  metric_rent50_gap_2br_vs_median_rent -->|valid for| geo_level_us
  metric_rent50_gap_2br_vs_median_rent -->|valid for| geo_level_zcta
  metric_rent_to_income -->|from table| table_housing_core_wide
  metric_rent_to_income -->|subject area| subject_area_affordability
  metric_rent_to_income -->|tagged to| theme_livability
  metric_rent_to_income -->|tagged to| theme_opportunity
  metric_rent_to_income -->|valid for| geo_level_cbsa
  metric_rent_to_income -->|valid for| geo_level_county
  metric_rent_to_income -->|valid for| geo_level_division
  metric_rent_to_income -->|valid for| geo_level_place
  metric_rent_to_income -->|valid for| geo_level_region
  metric_rent_to_income -->|valid for| geo_level_state
  metric_rent_to_income -->|valid for| geo_level_tract
  metric_rent_to_income -->|valid for| geo_level_us
  metric_rent_to_income -->|valid for| geo_level_zcta
  metric_rent_to_rpp_income -->|from table| table_affordability_wide
  metric_rent_to_rpp_income -->|subject area| subject_area_affordability
  metric_rent_to_rpp_income -->|tagged to| theme_livability
  metric_rent_to_rpp_income -->|tagged to| theme_opportunity
  metric_rent_to_rpp_income -->|valid for| geo_level_cbsa
  metric_rent_to_rpp_income -->|valid for| geo_level_county
  metric_rent_to_rpp_income -->|valid for| geo_level_division
  metric_rent_to_rpp_income -->|valid for| geo_level_place
  metric_rent_to_rpp_income -->|valid for| geo_level_region
  metric_rent_to_rpp_income -->|valid for| geo_level_state
  metric_rent_to_rpp_income -->|valid for| geo_level_tract
  metric_rent_to_rpp_income -->|valid for| geo_level_us
  metric_rent_to_rpp_income -->|valid for| geo_level_zcta
  metric_renter_occ_rate -->|from table| table_housing_core_wide
  metric_renter_occ_rate -->|subject area| subject_area_housing
  metric_renter_occ_rate -->|tagged to| theme_character
  metric_renter_occ_rate -->|tagged to| theme_livability
  metric_renter_occ_rate -->|valid for| geo_level_cbsa
  metric_renter_occ_rate -->|valid for| geo_level_county
  metric_renter_occ_rate -->|valid for| geo_level_division
  metric_renter_occ_rate -->|valid for| geo_level_place
  metric_renter_occ_rate -->|valid for| geo_level_region
  metric_renter_occ_rate -->|valid for| geo_level_state
  metric_renter_occ_rate -->|valid for| geo_level_tract
  metric_renter_occ_rate -->|valid for| geo_level_us
  metric_renter_occ_rate -->|valid for| geo_level_zcta
  metric_rpp_all_items -->|from table| table_affordability_wide
  metric_rpp_all_items -->|subject area| subject_area_affordability
  metric_rpp_all_items -->|tagged to| theme_livability
  metric_rpp_all_items -->|valid for| geo_level_cbsa
  metric_rpp_all_items -->|valid for| geo_level_county
  metric_rpp_all_items -->|valid for| geo_level_division
  metric_rpp_all_items -->|valid for| geo_level_place
  metric_rpp_all_items -->|valid for| geo_level_region
  metric_rpp_all_items -->|valid for| geo_level_state
  metric_rpp_all_items -->|valid for| geo_level_tract
  metric_rpp_all_items -->|valid for| geo_level_us
  metric_rpp_all_items -->|valid for| geo_level_zcta
  metric_rpp_price_deflator -->|from table| table_affordability_wide
  metric_rpp_price_deflator -->|subject area| subject_area_affordability
  metric_rpp_price_deflator -->|tagged to| theme_livability
  metric_rpp_price_deflator -->|valid for| geo_level_cbsa
  metric_rpp_price_deflator -->|valid for| geo_level_county
  metric_rpp_price_deflator -->|valid for| geo_level_division
  metric_rpp_price_deflator -->|valid for| geo_level_place
  metric_rpp_price_deflator -->|valid for| geo_level_region
  metric_rpp_price_deflator -->|valid for| geo_level_state
  metric_rpp_price_deflator -->|valid for| geo_level_tract
  metric_rpp_price_deflator -->|valid for| geo_level_us
  metric_rpp_price_deflator -->|valid for| geo_level_zcta
  metric_rpp_real_pc_income -->|from table| table_affordability_wide
  metric_rpp_real_pc_income -->|subject area| subject_area_affordability
  metric_rpp_real_pc_income -->|tagged to| theme_livability
  metric_rpp_real_pc_income -->|tagged to| theme_opportunity
  metric_rpp_real_pc_income -->|valid for| geo_level_cbsa
  metric_rpp_real_pc_income -->|valid for| geo_level_county
  metric_rpp_real_pc_income -->|valid for| geo_level_division
  metric_rpp_real_pc_income -->|valid for| geo_level_place
  metric_rpp_real_pc_income -->|valid for| geo_level_region
  metric_rpp_real_pc_income -->|valid for| geo_level_state
  metric_rpp_real_pc_income -->|valid for| geo_level_tract
  metric_rpp_real_pc_income -->|valid for| geo_level_us
  metric_rpp_real_pc_income -->|valid for| geo_level_zcta
  metric_unemployed -->|from table| table_economics_labor_wide
  metric_unemployed -->|subject area| subject_area_labor
  metric_unemployed -->|tagged to| theme_opportunity
  metric_unemployed -->|valid for| geo_level_cbsa
  metric_unemployed -->|valid for| geo_level_county
  metric_unemployed -->|valid for| geo_level_division
  metric_unemployed -->|valid for| geo_level_place
  metric_unemployed -->|valid for| geo_level_region
  metric_unemployed -->|valid for| geo_level_state
  metric_unemployed -->|valid for| geo_level_tract
  metric_unemployed -->|valid for| geo_level_us
  metric_unemployed -->|valid for| geo_level_zcta
  metric_vacancy_rate -->|from table| table_housing_core_wide
  metric_vacancy_rate -->|subject area| subject_area_housing
  metric_vacancy_rate -->|tagged to| theme_livability
  metric_vacancy_rate -->|tagged to| theme_opportunity
  metric_vacancy_rate -->|valid for| geo_level_cbsa
  metric_vacancy_rate -->|valid for| geo_level_county
  metric_vacancy_rate -->|valid for| geo_level_division
  metric_vacancy_rate -->|valid for| geo_level_place
  metric_vacancy_rate -->|valid for| geo_level_region
  metric_vacancy_rate -->|valid for| geo_level_state
  metric_vacancy_rate -->|valid for| geo_level_tract
  metric_vacancy_rate -->|valid for| geo_level_us
  metric_vacancy_rate -->|valid for| geo_level_zcta
  metric_value_to_income -->|from table| table_housing_core_wide
  metric_value_to_income -->|subject area| subject_area_affordability
  metric_value_to_income -->|tagged to| theme_livability
  metric_value_to_income -->|tagged to| theme_opportunity
  metric_value_to_income -->|valid for| geo_level_cbsa
  metric_value_to_income -->|valid for| geo_level_county
  metric_value_to_income -->|valid for| geo_level_division
  metric_value_to_income -->|valid for| geo_level_place
  metric_value_to_income -->|valid for| geo_level_region
  metric_value_to_income -->|valid for| geo_level_state
  metric_value_to_income -->|valid for| geo_level_tract
  metric_value_to_income -->|valid for| geo_level_us
  metric_value_to_income -->|valid for| geo_level_zcta
  metric_value_to_rpp_income -->|from table| table_affordability_wide
  metric_value_to_rpp_income -->|subject area| subject_area_affordability
  metric_value_to_rpp_income -->|tagged to| theme_livability
  metric_value_to_rpp_income -->|tagged to| theme_opportunity
  metric_value_to_rpp_income -->|valid for| geo_level_cbsa
  metric_value_to_rpp_income -->|valid for| geo_level_county
  metric_value_to_rpp_income -->|valid for| geo_level_division
  metric_value_to_rpp_income -->|valid for| geo_level_place
  metric_value_to_rpp_income -->|valid for| geo_level_region
  metric_value_to_rpp_income -->|valid for| geo_level_state
  metric_value_to_rpp_income -->|valid for| geo_level_tract
  metric_value_to_rpp_income -->|valid for| geo_level_us
  metric_value_to_rpp_income -->|valid for| geo_level_zcta
  metric_working_age_pop -->|from table| table_economics_labor_wide
  metric_working_age_pop -->|subject area| subject_area_labor
  metric_working_age_pop -->|tagged to| theme_opportunity
  metric_working_age_pop -->|valid for| geo_level_cbsa
  metric_working_age_pop -->|valid for| geo_level_county
  metric_working_age_pop -->|valid for| geo_level_division
  metric_working_age_pop -->|valid for| geo_level_place
  metric_working_age_pop -->|valid for| geo_level_region
  metric_working_age_pop -->|valid for| geo_level_state
  metric_working_age_pop -->|valid for| geo_level_tract
  metric_working_age_pop -->|valid for| geo_level_us
  metric_working_age_pop -->|valid for| geo_level_zcta
  point_set_curated_poi -->|source| source_manual_curation
  point_set_curated_poi -->|source| source_partner_poi_pipeline
  point_set_curated_poi -->|source| source_web_scrapes
  point_set_curated_poi -->|spatial join| geo_level_place
  point_set_curated_poi -->|spatial join| geo_level_tract
  point_set_parcels -->|source| source_county_assessor
  point_set_parcels -->|source| source_parcel_standardization_pipeline
  point_set_parcels -->|spatial join| geo_level_county
  point_set_parcels -->|spatial join| geo_level_place
  point_set_parcels -->|spatial join| geo_level_tract
  point_set_public_poi -->|source| source_Google_Maps_or_equivalent
  point_set_public_poi -->|source| source_OSM
  point_set_public_poi -->|spatial join| geo_level_tract
  point_set_public_poi -->|spatial join| geo_level_zcta
  question_pattern_character_profile_summary -->|defaults to chart rule| chart_rule_benchmark_default
  question_pattern_character_profile_summary -->|defaults to template| template_trend
  question_pattern_character_profile_summary -->|question for| theme_character
  question_pattern_character_profile_summary -->|question valid for| geo_level_cbsa
  question_pattern_character_profile_summary -->|question valid for| geo_level_place
  question_pattern_character_profile_summary -->|question valid for| geo_level_tract
  question_pattern_character_profile_summary -->|question valid for| geo_level_zcta
  question_pattern_character_profile_summary -->|requires metric| metric_diversity_index
  question_pattern_character_profile_summary -->|requires metric| metric_median_age
  question_pattern_character_profile_summary -->|requires metric| metric_pct_ba_plus
  question_pattern_character_profile_summary -->|requires metric| metric_pct_foreign_born
  question_pattern_character_profile_summary -->|requires metric| metric_pct_same_house
  question_pattern_character_profile_summary -->|requires metric| metric_pct_struct_multifam
  question_pattern_character_profile_summary -->|requires table| table_housing_core_wide
  question_pattern_character_profile_summary -->|requires table| table_migration_wide
  question_pattern_character_profile_summary -->|requires table| table_population_demographics
  question_pattern_compare_selected_geographies -->|defaults to chart rule| chart_rule_comparison_selected
  question_pattern_compare_selected_geographies -->|defaults to template| template_compare_selected
  question_pattern_compare_selected_geographies -->|question for| theme_character
  question_pattern_compare_selected_geographies -->|question for| theme_livability
  question_pattern_compare_selected_geographies -->|question for| theme_opportunity
  question_pattern_compare_selected_geographies -->|question valid for| geo_level_cbsa
  question_pattern_compare_selected_geographies -->|question valid for| geo_level_county
  question_pattern_compare_selected_geographies -->|question valid for| geo_level_place
  question_pattern_compare_selected_geographies -->|question valid for| geo_level_state
  question_pattern_compare_selected_geographies -->|requires metric| metric_median_gross_rent
  question_pattern_compare_selected_geographies -->|requires metric| metric_median_hh_income
  question_pattern_compare_selected_geographies -->|requires metric| metric_pop_total
  question_pattern_compare_selected_geographies -->|requires table| table_economics_income_wide
  question_pattern_compare_selected_geographies -->|requires table| table_housing_core_wide
  question_pattern_compare_selected_geographies -->|requires table| table_population_demographics
  question_pattern_diversity_ranking -->|defaults to chart rule| chart_rule_ranking_default
  question_pattern_diversity_ranking -->|defaults to template| template_ranking
  question_pattern_diversity_ranking -->|question for| theme_character
  question_pattern_diversity_ranking -->|question valid for| geo_level_cbsa
  question_pattern_diversity_ranking -->|question valid for| geo_level_county
  question_pattern_diversity_ranking -->|question valid for| geo_level_place
  question_pattern_diversity_ranking -->|requires metric| metric_diversity_index
  question_pattern_diversity_ranking -->|requires table| table_population_demographics
  question_pattern_income_growth_ranking -->|defaults to chart rule| chart_rule_ranking_default
  question_pattern_income_growth_ranking -->|defaults to template| template_growth
  question_pattern_income_growth_ranking -->|question for| theme_opportunity
  question_pattern_income_growth_ranking -->|question valid for| geo_level_cbsa
  question_pattern_income_growth_ranking -->|question valid for| geo_level_county
  question_pattern_income_growth_ranking -->|question valid for| geo_level_state
  question_pattern_income_growth_ranking -->|requires metric| metric_income_pc_growth_10yr
  question_pattern_income_growth_ranking -->|requires metric| metric_income_pc_growth_5yr
  question_pattern_income_growth_ranking -->|requires table| table_economics_income_wide
  question_pattern_metric_distribution_by_grain -->|defaults to chart rule| chart_rule_distribution_default
  question_pattern_metric_distribution_by_grain -->|defaults to template| template_distribution
  question_pattern_metric_distribution_by_grain -->|question for| theme_character
  question_pattern_metric_distribution_by_grain -->|question for| theme_livability
  question_pattern_metric_distribution_by_grain -->|question for| theme_opportunity
  question_pattern_metric_distribution_by_grain -->|question valid for| geo_level_cbsa
  question_pattern_metric_distribution_by_grain -->|question valid for| geo_level_county
  question_pattern_metric_distribution_by_grain -->|question valid for| geo_level_state
  question_pattern_metric_distribution_by_grain -->|requires metric| metric_median_age
  question_pattern_metric_distribution_by_grain -->|requires metric| metric_median_home_value
  question_pattern_metric_distribution_by_grain -->|requires metric| metric_rent_to_income
  question_pattern_metric_distribution_by_grain -->|requires table| table_housing_core_wide
  question_pattern_metric_distribution_by_grain -->|requires table| table_population_demographics
  question_pattern_metros_highest_cost_burden -->|defaults to chart rule| chart_rule_ranking_default
  question_pattern_metros_highest_cost_burden -->|defaults to template| template_ranking
  question_pattern_metros_highest_cost_burden -->|question for| theme_livability
  question_pattern_metros_highest_cost_burden -->|question valid for| geo_level_cbsa
  question_pattern_metros_highest_cost_burden -->|requires metric| metric_pct_rent_burden_30plus
  question_pattern_metros_highest_cost_burden -->|requires table| table_housing_core_wide
  question_pattern_metros_highest_rent_to_income -->|defaults to chart rule| chart_rule_ranking_default
  question_pattern_metros_highest_rent_to_income -->|defaults to template| template_ranking
  question_pattern_metros_highest_rent_to_income -->|question for| theme_livability
  question_pattern_metros_highest_rent_to_income -->|question for| theme_opportunity
  question_pattern_metros_highest_rent_to_income -->|question valid for| geo_level_cbsa
  question_pattern_metros_highest_rent_to_income -->|requires metric| metric_rent_to_income
  question_pattern_metros_highest_rent_to_income -->|requires table| table_housing_core_wide
  question_pattern_metros_income_trend -->|defaults to chart rule| chart_rule_trend_default
  question_pattern_metros_income_trend -->|defaults to template| template_trend
  question_pattern_metros_income_trend -->|question for| theme_opportunity
  question_pattern_metros_income_trend -->|question valid for| geo_level_cbsa
  question_pattern_metros_income_trend -->|question valid for| geo_level_county
  question_pattern_metros_income_trend -->|question valid for| geo_level_state
  question_pattern_metros_income_trend -->|requires metric| metric_calc_income_pc
  question_pattern_metros_income_trend -->|requires metric| metric_median_hh_income
  question_pattern_metros_income_trend -->|requires table| table_economics_income_wide
  question_pattern_metros_rent_trend -->|defaults to chart rule| chart_rule_trend_default
  question_pattern_metros_rent_trend -->|defaults to template| template_trend
  question_pattern_metros_rent_trend -->|question for| theme_livability
  question_pattern_metros_rent_trend -->|question valid for| geo_level_cbsa
  question_pattern_metros_rent_trend -->|requires metric| metric_median_gross_rent
  question_pattern_metros_rent_trend -->|requires table| table_housing_core_wide
  question_pattern_national_vacancy_trend -->|defaults to chart rule| chart_rule_trend_default
  question_pattern_national_vacancy_trend -->|defaults to template| template_trend
  question_pattern_national_vacancy_trend -->|question for| theme_livability
  question_pattern_national_vacancy_trend -->|question valid for| geo_level_us
  question_pattern_national_vacancy_trend -->|requires metric| metric_vacancy_rate
  question_pattern_national_vacancy_trend -->|requires table| table_housing_core_wide
  question_pattern_population_growth_ranking -->|defaults to chart rule| chart_rule_ranking_default
  question_pattern_population_growth_ranking -->|defaults to template| template_growth
  question_pattern_population_growth_ranking -->|question for| theme_character
  question_pattern_population_growth_ranking -->|question for| theme_opportunity
  question_pattern_population_growth_ranking -->|question valid for| geo_level_cbsa
  question_pattern_population_growth_ranking -->|question valid for| geo_level_county
  question_pattern_population_growth_ranking -->|question valid for| geo_level_place
  question_pattern_population_growth_ranking -->|question valid for| geo_level_state
  question_pattern_population_growth_ranking -->|requires metric| metric_pop_growth_10yr
  question_pattern_population_growth_ranking -->|requires metric| metric_pop_growth_5yr
  question_pattern_population_growth_ranking -->|requires metric| metric_pop_total
  question_pattern_population_growth_ranking -->|requires table| table_population_demographics
  question_pattern_states_highest_household_income -->|defaults to chart rule| chart_rule_ranking_default
  question_pattern_states_highest_household_income -->|defaults to template| template_ranking
  question_pattern_states_highest_household_income -->|question for| theme_opportunity
  question_pattern_states_highest_household_income -->|question valid for| geo_level_state
  question_pattern_states_highest_household_income -->|requires metric| metric_median_hh_income
  question_pattern_states_highest_household_income -->|requires table| table_economics_income_wide
  question_pattern_target_vs_benchmark -->|defaults to chart rule| chart_rule_benchmark_default
  question_pattern_target_vs_benchmark -->|defaults to template| template_benchmark
  question_pattern_target_vs_benchmark -->|question for| theme_character
  question_pattern_target_vs_benchmark -->|question for| theme_livability
  question_pattern_target_vs_benchmark -->|question for| theme_opportunity
  question_pattern_target_vs_benchmark -->|question valid for| geo_level_cbsa
  question_pattern_target_vs_benchmark -->|question valid for| geo_level_county
  question_pattern_target_vs_benchmark -->|question valid for| geo_level_place
  question_pattern_target_vs_benchmark -->|question valid for| geo_level_state
  question_pattern_target_vs_benchmark -->|requires metric| metric_median_gross_rent
  question_pattern_target_vs_benchmark -->|requires metric| metric_median_hh_income
  question_pattern_target_vs_benchmark -->|requires metric| metric_pct_rent_burden_30plus
  question_pattern_target_vs_benchmark -->|requires table| table_benchmark_reference
  question_pattern_target_vs_benchmark -->|requires table| table_economics_income_wide
  question_pattern_target_vs_benchmark -->|requires table| table_housing_core_wide
  question_type_benchmark -->|has question| question_pattern_target_vs_benchmark
  question_type_benchmark -->|maps to| chart_rule_benchmark_default
  question_type_benchmark -->|uses| template_benchmark
  question_type_benchmark -->|uses| template_growth
  question_type_comparison -->|has question| question_pattern_compare_selected_geographies
  question_type_comparison -->|maps to| chart_rule_comparison_selected
  question_type_comparison -->|uses| template_compare_selected
  question_type_comparison -->|uses| template_growth
  question_type_correlation -->|maps to| chart_rule_correlation_default
  question_type_distribution -->|has question| question_pattern_metric_distribution_by_grain
  question_type_distribution -->|maps to| chart_rule_distribution_default
  question_type_distribution -->|uses| template_distribution
  question_type_ranking -->|has question| question_pattern_diversity_ranking
  question_type_ranking -->|has question| question_pattern_income_growth_ranking
  question_type_ranking -->|has question| question_pattern_metros_highest_cost_burden
  question_type_ranking -->|has question| question_pattern_metros_highest_rent_to_income
  question_type_ranking -->|has question| question_pattern_population_growth_ranking
  question_type_ranking -->|has question| question_pattern_states_highest_household_income
  question_type_ranking -->|maps to| chart_rule_ranking_default
  question_type_ranking -->|uses| template_growth
  question_type_ranking -->|uses| template_ranking
  question_type_summary -->|has question| question_pattern_character_profile_summary
  question_type_trend -->|has question| question_pattern_metros_income_trend
  question_type_trend -->|has question| question_pattern_metros_rent_trend
  question_type_trend -->|has question| question_pattern_national_vacancy_trend
  question_type_trend -->|maps to| chart_rule_trend_default
  question_type_trend -->|uses| template_growth
  question_type_trend -->|uses| template_trend
  score_business_opportunity_score -->|score input| metric_acs_industry_concentration_hhi
  score_business_opportunity_score -->|score input| metric_industry_concentration_hhi
  score_business_opportunity_score -->|score input| metric_labor_force
  score_business_opportunity_score -->|score input| metric_pct_ba_plus
  score_business_opportunity_score -->|score input| metric_pct_real_gdp_edu_health
  score_business_opportunity_score -->|score input| metric_pct_real_gdp_professional
  score_business_opportunity_score -->|score valid for| geo_level_cbsa
  score_business_opportunity_score -->|score valid for| geo_level_county
  score_business_opportunity_score -->|score valid for| geo_level_place
  score_business_opportunity_score -->|score valid for| geo_level_state
  score_character_profile_archetype -->|score input| metric_diversity_index
  score_character_profile_archetype -->|score input| metric_median_age
  score_character_profile_archetype -->|score input| metric_pct_ba_plus
  score_character_profile_archetype -->|score input| metric_pct_foreign_born
  score_character_profile_archetype -->|score input| metric_pct_same_house
  score_character_profile_archetype -->|score input| metric_pct_struct_multifam
  score_character_profile_archetype -->|score input| metric_pop_weighted_density_sqmi
  score_character_profile_archetype -->|score valid for| geo_level_cbsa
  score_character_profile_archetype -->|score valid for| geo_level_place
  score_character_profile_archetype -->|score valid for| geo_level_tract
  score_character_profile_archetype -->|score valid for| geo_level_zcta
  score_livability_affordability_subscore -->|score input| metric_pct_rent_burden_30plus
  score_livability_affordability_subscore -->|score input| metric_pct_rent_burden_50plus
  score_livability_affordability_subscore -->|score input| metric_permits_per_1000_housing_units
  score_livability_affordability_subscore -->|score input| metric_rent_to_income
  score_livability_affordability_subscore -->|score input| metric_rent_to_rpp_income
  score_livability_affordability_subscore -->|score input| metric_vacancy_rate
  score_livability_affordability_subscore -->|score valid for| geo_level_cbsa
  score_livability_affordability_subscore -->|score valid for| geo_level_county
  score_livability_affordability_subscore -->|score valid for| geo_level_place
  score_livability_affordability_subscore -->|score valid for| geo_level_state
  score_livability_affordability_subscore -->|score valid for| geo_level_tract
  score_livability_affordability_subscore -->|score valid for| geo_level_zcta
  score_livability_mobility_subscore -->|score input| metric_mean_travel_time
  score_livability_mobility_subscore -->|score input| metric_pct_commute_drive_alone
  score_livability_mobility_subscore -->|score input| metric_pct_commute_transit
  score_livability_mobility_subscore -->|score input| metric_pct_commute_walk
  score_livability_mobility_subscore -->|score input| metric_pct_hh_0_vehicles
  score_livability_mobility_subscore -->|score input| metric_pct_low_car_commute
  score_livability_mobility_subscore -->|score valid for| geo_level_cbsa
  score_livability_mobility_subscore -->|score valid for| geo_level_county
  score_livability_mobility_subscore -->|score valid for| geo_level_place
  score_livability_mobility_subscore -->|score valid for| geo_level_state
  score_livability_mobility_subscore -->|score valid for| geo_level_tract
  score_livability_mobility_subscore -->|score valid for| geo_level_zcta
  score_livability_score -->|score input| metric_mean_travel_time
  score_livability_score -->|score input| metric_pct_hh_0_vehicles
  score_livability_score -->|score input| metric_pct_low_car_commute
  score_livability_score -->|score input| metric_pct_rent_burden_30plus
  score_livability_score -->|score input| metric_rent_to_rpp_income
  score_livability_score -->|score input| metric_vacancy_rate
  score_livability_score -->|score valid for| geo_level_cbsa
  score_livability_score -->|score valid for| geo_level_county
  score_livability_score -->|score valid for| geo_level_place
  score_livability_score -->|score valid for| geo_level_state
  score_livability_score -->|score valid for| geo_level_tract
  score_livability_score -->|score valid for| geo_level_zcta
  score_market_opportunity_score -->|score input| metric_irs_net_migration_rate
  score_market_opportunity_score -->|score input| metric_pop_growth_5yr
  score_market_opportunity_score -->|score input| metric_real_gdp_growth_5yr
  score_market_opportunity_score -->|score input| metric_value_to_income
  score_market_opportunity_score -->|score input| metric_value_to_rpp_income
  score_market_opportunity_score -->|score valid for| geo_level_cbsa
  score_market_opportunity_score -->|score valid for| geo_level_county
  score_market_opportunity_score -->|score valid for| geo_level_place
  score_market_opportunity_score -->|score valid for| geo_level_state
  score_market_opportunity_score -->|score valid for| geo_level_zcta
  score_resident_opportunity_score -->|score input| metric_calc_income_pc
  score_resident_opportunity_score -->|score input| metric_income_pc_growth_5yr
  score_resident_opportunity_score -->|score input| metric_jobs_to_pop_ratio
  score_resident_opportunity_score -->|score input| metric_lfpr
  score_resident_opportunity_score -->|score input| metric_lfpr_growth_5yr
  score_resident_opportunity_score -->|score input| metric_pct_unemployment_rate
  score_resident_opportunity_score -->|score input| metric_productivity_growth_5yr
  score_resident_opportunity_score -->|score valid for| geo_level_cbsa
  score_resident_opportunity_score -->|score valid for| geo_level_county
  score_resident_opportunity_score -->|score valid for| geo_level_place
  score_resident_opportunity_score -->|score valid for| geo_level_state
  table_affordability_wide -->|subject area| subject_area_affordability
  table_affordability_wide -->|subject area| subject_area_housing
  table_affordability_wide -->|subject area| subject_area_income
  table_affordability_wide -->|supports| geo_level_cbsa
  table_affordability_wide -->|supports| geo_level_county
  table_affordability_wide -->|supports| geo_level_division
  table_affordability_wide -->|supports| geo_level_place
  table_affordability_wide -->|supports| geo_level_region
  table_affordability_wide -->|supports| geo_level_state
  table_affordability_wide -->|supports| geo_level_tract
  table_affordability_wide -->|supports| geo_level_us
  table_affordability_wide -->|supports| geo_level_zcta
  table_benchmark_reference -->|subject area| subject_area_benchmarks
  table_benchmark_reference -->|subject area| subject_area_planner_internal
  table_benchmark_reference -->|supports| geo_level_division
  table_benchmark_reference -->|supports| geo_level_region
  table_benchmark_reference -->|supports| geo_level_us
  table_economics_gdp_wide -->|subject area| subject_area_economy
  table_economics_gdp_wide -->|subject area| subject_area_gdp
  table_economics_gdp_wide -->|subject area| subject_area_opportunity
  table_economics_gdp_wide -->|supports| geo_level_cbsa
  table_economics_gdp_wide -->|supports| geo_level_county
  table_economics_gdp_wide -->|supports| geo_level_division
  table_economics_gdp_wide -->|supports| geo_level_place
  table_economics_gdp_wide -->|supports| geo_level_region
  table_economics_gdp_wide -->|supports| geo_level_state
  table_economics_gdp_wide -->|supports| geo_level_tract
  table_economics_gdp_wide -->|supports| geo_level_us
  table_economics_gdp_wide -->|supports| geo_level_zcta
  table_economics_income_wide -->|subject area| subject_area_affordability
  table_economics_income_wide -->|subject area| subject_area_income
  table_economics_income_wide -->|subject area| subject_area_opportunity
  table_economics_income_wide -->|joins to| table_benchmark_reference
  table_economics_income_wide -->|supports| geo_level_cbsa
  table_economics_income_wide -->|supports| geo_level_county
  table_economics_income_wide -->|supports| geo_level_division
  table_economics_income_wide -->|supports| geo_level_place
  table_economics_income_wide -->|supports| geo_level_region
  table_economics_income_wide -->|supports| geo_level_state
  table_economics_income_wide -->|supports| geo_level_tract
  table_economics_income_wide -->|supports| geo_level_us
  table_economics_income_wide -->|supports| geo_level_zcta
  table_economics_industry_wide -->|subject area| subject_area_economy
  table_economics_industry_wide -->|subject area| subject_area_industry
  table_economics_industry_wide -->|subject area| subject_area_opportunity
  table_economics_industry_wide -->|supports| geo_level_cbsa
  table_economics_industry_wide -->|supports| geo_level_county
  table_economics_industry_wide -->|supports| geo_level_division
  table_economics_industry_wide -->|supports| geo_level_place
  table_economics_industry_wide -->|supports| geo_level_region
  table_economics_industry_wide -->|supports| geo_level_state
  table_economics_industry_wide -->|supports| geo_level_tract
  table_economics_industry_wide -->|supports| geo_level_us
  table_economics_industry_wide -->|supports| geo_level_zcta
  table_economics_labor_wide -->|subject area| subject_area_employment
  table_economics_labor_wide -->|subject area| subject_area_labor
  table_economics_labor_wide -->|subject area| subject_area_opportunity
  table_economics_labor_wide -->|supports| geo_level_cbsa
  table_economics_labor_wide -->|supports| geo_level_county
  table_economics_labor_wide -->|supports| geo_level_division
  table_economics_labor_wide -->|supports| geo_level_place
  table_economics_labor_wide -->|supports| geo_level_region
  table_economics_labor_wide -->|supports| geo_level_state
  table_economics_labor_wide -->|supports| geo_level_tract
  table_economics_labor_wide -->|supports| geo_level_us
  table_economics_labor_wide -->|supports| geo_level_zcta
  table_housing_core_wide -->|subject area| subject_area_affordability
  table_housing_core_wide -->|subject area| subject_area_housing
  table_housing_core_wide -->|subject area| subject_area_livability
  table_housing_core_wide -->|joins to| table_benchmark_reference
  table_housing_core_wide -->|supports| geo_level_cbsa
  table_housing_core_wide -->|supports| geo_level_county
  table_housing_core_wide -->|supports| geo_level_division
  table_housing_core_wide -->|supports| geo_level_place
  table_housing_core_wide -->|supports| geo_level_region
  table_housing_core_wide -->|supports| geo_level_state
  table_housing_core_wide -->|supports| geo_level_tract
  table_housing_core_wide -->|supports| geo_level_us
  table_housing_core_wide -->|supports| geo_level_zcta
  table_migration_wide -->|subject area| subject_area_character
  table_migration_wide -->|subject area| subject_area_migration
  table_migration_wide -->|subject area| subject_area_nativity
  table_migration_wide -->|supports| geo_level_cbsa
  table_migration_wide -->|supports| geo_level_county
  table_migration_wide -->|supports| geo_level_division
  table_migration_wide -->|supports| geo_level_place
  table_migration_wide -->|supports| geo_level_region
  table_migration_wide -->|supports| geo_level_state
  table_migration_wide -->|supports| geo_level_tract
  table_migration_wide -->|supports| geo_level_us
  table_migration_wide -->|supports| geo_level_zcta
  table_points_catalog_stub -->|joins to| table_geography_catalog
  table_population_demographics -->|subject area| subject_area_character
  table_population_demographics -->|subject area| subject_area_demographics
  table_population_demographics -->|subject area| subject_area_population
  table_population_demographics -->|joins to| table_benchmark_reference
  table_population_demographics -->|supports| geo_level_cbsa
  table_population_demographics -->|supports| geo_level_county
  table_population_demographics -->|supports| geo_level_division
  table_population_demographics -->|supports| geo_level_place
  table_population_demographics -->|supports| geo_level_region
  table_population_demographics -->|supports| geo_level_state
  table_population_demographics -->|supports| geo_level_tract
  table_population_demographics -->|supports| geo_level_us
  table_population_demographics -->|supports| geo_level_zcta
  table_transport_built_form_wide -->|subject area| subject_area_built_form
  table_transport_built_form_wide -->|subject area| subject_area_livability
  table_transport_built_form_wide -->|subject area| subject_area_mobility
  table_transport_built_form_wide -->|subject area| subject_area_transport
  table_transport_built_form_wide -->|supports| geo_level_cbsa
  table_transport_built_form_wide -->|supports| geo_level_county
  table_transport_built_form_wide -->|supports| geo_level_division
  table_transport_built_form_wide -->|supports| geo_level_place
  table_transport_built_form_wide -->|supports| geo_level_region
  table_transport_built_form_wide -->|supports| geo_level_state
  table_transport_built_form_wide -->|supports| geo_level_tract
  table_transport_built_form_wide -->|supports| geo_level_us
  table_transport_built_form_wide -->|supports| geo_level_zcta
  table_tx_isd_metrics -->|subject area| subject_area_education
  table_tx_isd_metrics -->|subject area| subject_area_texas_school_districts
  table_tx_isd_metrics -->|joins to| table_population_demographics
  table_tx_isd_metrics -->|supports| geo_level_tx_isd
  theme_character -->|has score| score_character_profile_archetype
  theme_character -->|has topic| topic_built_form_context
  theme_character -->|has topic| topic_demographic_profile
  theme_character -->|has topic| topic_education_attainment
  theme_character -->|has topic| topic_race_ethnicity
  theme_character -->|has topic| topic_rootedness_and_mobility
  theme_livability -->|has score| score_livability_affordability_subscore
  theme_livability -->|has score| score_livability_mobility_subscore
  theme_livability -->|has score| score_livability_score
  theme_livability -->|has topic| topic_affordability
  theme_livability -->|has topic| topic_built_environment
  theme_livability -->|has topic| topic_education_and_equity_context
  theme_livability -->|has topic| topic_housing_supply
  theme_livability -->|has topic| topic_mobility
  theme_opportunity -->|has score| score_business_opportunity_score
  theme_opportunity -->|has score| score_market_opportunity_score
  theme_opportunity -->|has score| score_resident_opportunity_score
  theme_opportunity -->|has topic| topic_economic_output
  theme_opportunity -->|has topic| topic_growth_and_momentum
  theme_opportunity -->|has topic| topic_income_and_wages
  theme_opportunity -->|has topic| topic_industry_mix
  theme_opportunity -->|has topic| topic_labor_market
  topic_affordability -->|uses metric| metric_annualized_median_rent
  topic_affordability -->|uses metric| metric_median_gross_rent
  topic_affordability -->|uses metric| metric_median_home_value
  topic_affordability -->|uses metric| metric_pct_rent_burden_30plus
  topic_affordability -->|uses metric| metric_pct_rent_burden_50plus
  topic_affordability -->|uses metric| metric_rent_to_income
  topic_affordability -->|uses metric| metric_rent_to_rpp_income
  topic_affordability -->|uses metric| metric_rpp_all_items
  topic_affordability -->|uses metric| metric_rpp_real_pc_income
  topic_affordability -->|uses metric| metric_value_to_income
  topic_affordability -->|uses metric| metric_value_to_rpp_income
  topic_built_environment -->|uses metric| metric_density_population
  topic_built_environment -->|uses metric| metric_gross_density_sqmi
  topic_built_environment -->|uses metric| metric_pct_struct_multifam
  topic_built_environment -->|uses metric| metric_pop_weighted_density_sqmi
  topic_built_form_context -->|uses metric| metric_gross_density_sqmi
  topic_built_form_context -->|uses metric| metric_owner_occ_rate
  topic_built_form_context -->|uses metric| metric_pct_struct_multifam
  topic_built_form_context -->|uses metric| metric_pop_weighted_density_sqmi
  topic_built_form_context -->|uses metric| metric_renter_occ_rate
  topic_demographic_profile -->|uses metric| metric_aging_index
  topic_demographic_profile -->|uses metric| metric_dependents_per_worker
  topic_demographic_profile -->|uses metric| metric_median_age
  topic_demographic_profile -->|uses metric| metric_pct_age_18_64
  topic_demographic_profile -->|uses metric| metric_pct_age_over_64
  topic_demographic_profile -->|uses metric| metric_pct_age_under_18
  topic_economic_output -->|uses metric| metric_nominal_gdp_growth_5yr
  topic_economic_output -->|uses metric| metric_nominal_gdp_pc
  topic_economic_output -->|uses metric| metric_nominal_gdp_total
  topic_economic_output -->|uses metric| metric_productivity_growth_5yr
  topic_economic_output -->|uses metric| metric_productivity_index
  topic_economic_output -->|uses metric| metric_real_gdp_growth_5yr
  topic_economic_output -->|uses metric| metric_real_gdp_pc
  topic_economic_output -->|uses metric| metric_real_gdp_total
  topic_education_and_equity_context -->|uses metric| metric_gini_index
  topic_education_and_equity_context -->|uses metric| metric_pct_ba_plus
  topic_education_and_equity_context -->|uses metric| metric_pov_rate
  topic_education_attainment -->|uses metric| metric_pct_ba_plus
  topic_education_attainment -->|uses metric| metric_pct_grad_plus
  topic_growth_and_momentum -->|uses metric| metric_irs_net_migration
  topic_growth_and_momentum -->|uses metric| metric_irs_net_migration_rate
  topic_growth_and_momentum -->|uses metric| metric_pop_growth_10yr
  topic_growth_and_momentum -->|uses metric| metric_pop_growth_5yr
  topic_growth_and_momentum -->|uses metric| metric_rent_to_income
  topic_growth_and_momentum -->|uses metric| metric_rent_to_rpp_income
  topic_growth_and_momentum -->|uses metric| metric_value_to_income
  topic_growth_and_momentum -->|uses metric| metric_value_to_rpp_income
  topic_housing_supply -->|uses metric| metric_fmr_gap_2br_vs_median_rent
  topic_housing_supply -->|uses metric| metric_hu_total
  topic_housing_supply -->|uses metric| metric_permits_per_1000_housing_units
  topic_housing_supply -->|uses metric| metric_permits_share_multifam_units
  topic_housing_supply -->|uses metric| metric_rent50_gap_2br_vs_median_rent
  topic_housing_supply -->|uses metric| metric_vacancy_rate
  topic_income_and_wages -->|uses metric| metric_acs_income_pc
  topic_income_and_wages -->|uses metric| metric_calc_income_pc
  topic_income_and_wages -->|uses metric| metric_income_pc_growth_10yr
  topic_income_and_wages -->|uses metric| metric_income_pc_growth_1yr
  topic_income_and_wages -->|uses metric| metric_income_pc_growth_5yr
  topic_income_and_wages -->|uses metric| metric_median_hh_income
  topic_income_and_wages -->|uses metric| metric_pi_total
  topic_income_and_wages -->|uses metric| metric_pi_wage_share
  topic_income_and_wages -->|uses metric| metric_pi_wages_salary
  topic_industry_mix -->|uses metric| metric_acs_ind_total_emp
  topic_industry_mix -->|uses metric| metric_acs_industry_concentration_hhi
  topic_industry_mix -->|uses metric| metric_industry_concentration_hhi
  topic_industry_mix -->|uses metric| metric_pct_acs_ind_arts_accomm_food
  topic_industry_mix -->|uses metric| metric_pct_acs_ind_educ_health
  topic_industry_mix -->|uses metric| metric_pct_acs_ind_manufacturing
  topic_industry_mix -->|uses metric| metric_pct_acs_ind_professional
  topic_industry_mix -->|uses metric| metric_pct_real_gdp_edu_health
  topic_industry_mix -->|uses metric| metric_pct_real_gdp_manufacturing
  topic_industry_mix -->|uses metric| metric_pct_real_gdp_professional
  topic_labor_market -->|uses metric| metric_employed
  topic_labor_market -->|uses metric| metric_jobs_to_pop_ratio
  topic_labor_market -->|uses metric| metric_labor_force
  topic_labor_market -->|uses metric| metric_lfpr
  topic_labor_market -->|uses metric| metric_lfpr_growth_5yr
  topic_labor_market -->|uses metric| metric_pct_unemployment_rate
  topic_labor_market -->|uses metric| metric_unemployed
  topic_labor_market -->|uses metric| metric_working_age_pop
  topic_mobility -->|uses metric| metric_mean_travel_time
  topic_mobility -->|uses metric| metric_pct_commute_drive_alone
  topic_mobility -->|uses metric| metric_pct_commute_transit
  topic_mobility -->|uses metric| metric_pct_commute_walk
  topic_mobility -->|uses metric| metric_pct_commute_wfh
  topic_mobility -->|uses metric| metric_pct_hh_0_vehicles
  topic_mobility -->|uses metric| metric_pct_low_car_commute
  topic_race_ethnicity -->|uses metric| metric_diversity_index
  topic_race_ethnicity -->|uses metric| metric_pct_asian_nh
  topic_race_ethnicity -->|uses metric| metric_pct_black_nh
  topic_race_ethnicity -->|uses metric| metric_pct_hispanic
  topic_race_ethnicity -->|uses metric| metric_pct_white_nh
  topic_rootedness_and_mobility -->|uses metric| metric_migration_churn
  topic_rootedness_and_mobility -->|uses metric| metric_mobility_rate
  topic_rootedness_and_mobility -->|uses metric| metric_pct_foreign_born
  topic_rootedness_and_mobility -->|uses metric| metric_pct_moved_abroad
  topic_rootedness_and_mobility -->|uses metric| metric_pct_moved_diff_st
  topic_rootedness_and_mobility -->|uses metric| metric_pct_non_citizen
  topic_rootedness_and_mobility -->|uses metric| metric_pct_same_house
```
