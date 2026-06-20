phase6_trajectory_config <- function() {
  phase_dir <- here::here(
    "exploration",
    "intelligence_framework",
    "phase_6_trajectory"
  )

  output_dir <- file.path(phase_dir, "outputs")
  notebook_dir <- file.path(phase_dir, "notebooks")
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  dir.create(notebook_dir, recursive = TRUE, showWarnings = FALSE)

  ct_cbsa_exclusion <- tibble::tribble(
    ~cbsa_code, ~cbsa_name,
    "14860", "Bridgeport-Stamford-Danbury, CT",
    "25540", "Hartford-West Hartford-East Hartford, CT",
    "35300", "New Haven, CT",
    "35980", "Norwich-New London-Willimantic, CT",
    "39480", "Putnam, CT",
    "45860", "Torrington, CT",
    "47930", "Waterbury-Shelton, CT"
  )

  frame_metric_spec <- tibble::tribble(
    ~frame_id, ~metric_id, ~expected_source_column, ~trajectory_window, ~trajectory_role, ~coverage_rule,
    "character", "diversity_index", "diversity_index", "5yr", "trajectory", "standard",
    "character", "pct_black_nh", "pct_black_nh", "5yr", "trajectory", "standard",
    "character", "pct_asian_nh", "pct_asian_nh", "5yr", "trajectory", "standard",
    "character", "pct_hispanic", "pct_hispanic", "5yr", "trajectory", "standard",
    "character", "pct_age_over_64", "pct_age_over_64", "5yr", "trajectory", "standard",
    "character", "pct_ba_plus", "pct_ba_plus", "5yr", "trajectory", "standard",
    "character", "pct_foreign_born", "pct_foreign_born", "5yr", "trajectory", "standard",
    "character", "pop_weighted_density_sqmi", "pop_weighted_density_sqmi", "5yr", "trajectory", "standard",
    "character", "friending_bias", "friending_bias", "static_only", "context_only", "single_vintage_or_not_yet_verified",
    "character", "civic_engagement_volunteering_rate", "civic_engagement_volunteering_rate", "static_only", "context_only", "single_vintage_or_not_yet_verified",
    "character", "civic_organizations_per_1000", "civic_organizations_per_1000", "static_only", "context_only", "single_vintage_or_not_yet_verified",
    "character", "nonprofits_per_100k", "nonprofits_per_100k", "static_only", "context_only", "single_vintage_or_not_yet_verified",
    "character", "irs_net_migration_rate", "irs_net_migration_rate", "5yr", "trajectory", "standard",
    "character", "pct_moved_diff_st", "pct_moved_diff_st", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "character", "pct_moved_abroad", "pct_moved_abroad", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "character", "social_associations_per_10k", "social_associations_per_10k", "5yr", "trajectory", "standard",
    "character", "pct_struct_multifam", "pct_struct_multifam", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "livability", "value_to_income", "value_to_income", "5yr", "trajectory", "standard",
    "livability", "pct_rent_burden_30plus", "pct_rent_burden_30plus", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "livability", "pov_rate", "pov_rate", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "livability", "permits_per_1000_housing_units", "permits_per_1000_housing_units", "5yr", "trajectory", "standard",
    "livability", "permits_share_units_5_plus", "permits_share_units_5_plus", "5yr", "trajectory", "standard",
    "livability", "pct_struct_mobile", "pct_struct_mobile", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "livability", "pct_struct_small_mf", "pct_struct_small_mf", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "livability", "pct_struct_mid_mf", "pct_struct_mid_mf", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "livability", "premature_death_rate", "premature_death_rate", "5yr", "trajectory", "standard",
    "livability", "mental_health_provider_ratio", "mental_health_provider_ratio", "5yr", "trajectory", "standard",
    "livability", "drug_overdose_death_rate", "drug_overdose_death_rate", "5yr", "trajectory", "standard",
    "livability", "pct_uninsured_adults", "pct_uninsured_adults", "5yr", "trajectory", "standard",
    "livability", "preventable_hospital_stay_rate", "preventable_hospital_stay_rate", "5yr", "trajectory", "standard",
    "livability", "firearm_fatality_rate", "firearm_fatality_rate", "5yr", "trajectory", "standard",
    "livability", "motor_vehicle_crash_rate", "motor_vehicle_crash_rate", "5yr", "trajectory", "standard",
    "livability", "pct_commute_walk", "pct_commute_walk", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "livability", "pct_commute_wfh", "pct_commute_wfh", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "livability", "vacancy_rate", "vacancy_rate", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "livability", "pct_hh_0_vehicles", "pct_hh_0_vehicles", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "livability", "pct_no_internet_access", "pct_no_internet_access", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "livability", "walkability_index", "walkability_index", "static_only", "context_only", "exclude_single_vintage",
    "livability", "jobs_access_45min_transit", "jobs_access_45min_transit", "static_only", "context_only", "exclude_single_vintage",
    "livability", "pct_population_low_income_low_access_1_10", "pct_population_low_income_low_access_1_10", "static_only", "context_only", "exclude_single_vintage",
    "livability", "pop_weighted_density_sqmi", "pop_weighted_density_sqmi", "5yr", "trajectory", "standard",
    "livability", "aqi_unhealthy_days", "unhealthy_days", "5yr", "trajectory", "standard",
    "livability", "fema_risk_score", "fema_risk_score", "5yr", "trajectory", "standard",
    "opportunity", "income_pc_growth_5yr", "income_pc_growth_5yr", "5yr", "trajectory", "standard",
    "opportunity", "pct_unemployment_rate", "pct_unemployment_rate", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "lfpr", "lfpr", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "pov_rate_change_5yr", "pov_rate_change_5yr", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "opportunity", "qcew_private_avg_wkly_wage", "qcew_private_avg_wkly_wage", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "hpi_5yr_pct", "hpi_5yr_pct", "5yr", "trajectory", "standard",
    "opportunity", "hpi_yoy_pct", "hpi_yoy_pct", "1yr", "trajectory", "standard",
    "opportunity", "zori_annual_avg_yoy_pct", "zori_annual_avg_yoy_pct", "1yr", "trajectory", "annotate_zori_coverage",
    "opportunity", "pop_growth_5yr", "pop_growth_5yr", "5yr", "trajectory", "standard",
    "opportunity", "irs_net_migration_rate", "irs_net_migration_rate", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "irs_net_agi", "irs_net_agi", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "permits_per_1000_housing_units", "permits_per_1000_housing_units", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "permits_share_units_5_plus", "permits_share_units_5_plus", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "productivity_growth_5yr", "productivity_growth_5yr", "5yr", "trajectory", "standard",
    "opportunity", "industry_concentration_hhi", "industry_concentration_hhi", "5yr", "trajectory", "standard",
    "opportunity", "bfs_business_application_rate_per_1000_establishments", "bfs_business_application_rate_per_1000_establishments", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "cbp_estabs_per_1000_residents", "cbp_estabs_per_1000_residents", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "pct_ba_plus_change_5yr", "pct_ba_plus_change_5yr", "5yr", "trajectory", "exclude_all_ct_for_acs_5yr",
    "opportunity", "lq_professional", "lq_professional", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "lq_information", "lq_information", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "lq_manufacturing", "lq_manufacturing", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "pct_real_gdp_information", "pct_real_gdp_information", "1yr_and_5yr", "trajectory", "standard",
    "opportunity", "economic_connectedness", "economic_connectedness", "static_only", "context_only", "single_vintage_or_not_yet_verified"
  )

  frame_output_paths <- tibble::tribble(
    ~frame_id, ~score_path, ~percentile_column, ~score_column,
    "character",
    here::here(
      "exploration",
      "intelligence_framework",
      "phase_2_character_calibration",
      "outputs",
      "character_scores.parquet"
    ),
    "character_percentile",
    "character_score",
    "livability",
    here::here(
      "exploration",
      "intelligence_framework",
      "phase_3_livability_calibration",
      "outputs",
      "livability_scores.parquet"
    ),
    "livability_percentile",
    "livability_score",
    "opportunity",
    here::here(
      "exploration",
      "intelligence_framework",
      "phase_4_opportunity_calibration",
      "outputs",
      "opportunity_scores.parquet"
    ),
    "opportunity_percentile",
    "opportunity_score"
  )

  static_context_metrics <- frame_metric_spec |>
    dplyr::filter(trajectory_role == "context_only")

  trajectory_metrics <- frame_metric_spec |>
    dplyr::filter(trajectory_role == "trajectory")

  list(
    phase_dir = phase_dir,
    output_dir = output_dir,
    notebook_dir = notebook_dir,
    target_year = 2024L,
    min_pop = 100000L,
    reference_spine_size = 396L,
    exclude_puerto_rico = TRUE,
    ct_cbsa_exclusion = ct_cbsa_exclusion,
    ct_exclusion_rule = "exclude_all_7_ct_cbsas_from_acs_derived_5yr_trajectory_metrics",
    frame_time_windows = tibble::tribble(
      ~frame_id, ~default_window, ~secondary_window, ~notes,
      "character", "5yr", NA_character_, "Character trajectories use the 5-year pass only.",
      "livability", "5yr", "1yr_sensitivity_only", "Livability trajectories use the 5-year pass only in the canonical output.",
      "opportunity", "5yr", "1yr", "Opportunity compares both 1-year and 5-year movement and keeps contradiction flags."
    ),
    frame_metric_spec = frame_metric_spec,
    trajectory_metrics = trajectory_metrics,
    static_context_metrics = static_context_metrics,
    frame_output_paths = frame_output_paths,
    phase5_overlap_flags_path = here::here(
      "exploration",
      "intelligence_framework",
      "phase_5_cross_frame_integration",
      "outputs",
      "cross_frame_phase5_overlap_flags.csv"
    ),
    phase5_scores_path = here::here(
      "exploration",
      "intelligence_framework",
      "phase_5_cross_frame_integration",
      "outputs",
      "cross_frame_scores.parquet"
    ),
    trajectory_scores_path = file.path(output_dir, "trajectory_scores.parquet"),
    kpi_trajectory_long_path = file.path(output_dir, "phase6_kpi_trajectory_long.csv"),
    pattern_summary_path = file.path(output_dir, "phase6_pattern_summary.csv"),
    opp_turn_signals_path = file.path(output_dir, "phase6_opp_turn_signals.csv"),
    candidate_list_path = file.path(output_dir, "phase6_candidate_list.csv"),
    direction_levels = c(
      "diverging-improving",
      "diverging-declining",
      "converging-improving",
      "converging-declining"
    ),
    pattern_flag_columns = c(
      "is_bounce_back",
      "is_hidden_livability_winner",
      "is_diverging_from_themselves",
      "is_fast_demographic_changer",
      "is_environmental_risk_outlier"
    )
  )
}
