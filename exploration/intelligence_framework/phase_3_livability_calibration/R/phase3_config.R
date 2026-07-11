phase3_livability_config <- function(
  aqi_metric_id = "aqi_median",
  aqi_source_column = NULL,
  output_dir_name = "outputs"
) {
  if (is.null(aqi_source_column)) {
    aqi_source_column <- dplyr::case_when(
      aqi_metric_id == "aqi_unhealthy_days" ~ "unhealthy_days",
      aqi_metric_id == "aqi_median" ~ "aqi_median",
      TRUE ~ NA_character_
    )
  }

  if (is.na(aqi_source_column)) {
    stop(
      sprintf(
        "Unsupported AQI metric_id for Phase 3 config: %s",
        aqi_metric_id
      ),
      call. = FALSE
    )
  }

  output_dir <- here::here(
    "exploration",
    "intelligence_framework",
    "phase_3_livability_calibration",
    output_dir_name
  )

  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  expected_kpis <- tibble::tribble(
    ~metric_id, ~audit_bucket, ~expected_source_column,
    "value_to_income", "recurring_core", "value_to_income",
    "pct_rent_burden_30plus", "recurring_core", "pct_rent_burden_30plus",
    "pov_rate", "recurring_core", "pov_rate",
    "permits_per_1000_housing_units", "recurring_core", "permits_per_1000_housing_units",
    "permits_share_units_5_plus", "recurring_core", "permits_share_units_5_plus",
    "pct_struct_mobile", "recurring_core", "pct_struct_mobile",
    "pct_struct_small_mf", "recurring_core", "pct_struct_small_mf",
    "pct_struct_mid_mf", "recurring_core", "pct_struct_mid_mf",
    "premature_death_rate", "recurring_core", "premature_death_rate",
    "mental_health_provider_ratio", "recurring_core", "mental_health_provider_ratio",
    "drug_overdose_death_rate", "recurring_core", "drug_overdose_death_rate",
    "pct_uninsured_adults", "recurring_core", "pct_uninsured_adults",
    "preventable_hospital_stay_rate", "recurring_core", "preventable_hospital_stay_rate",
    "firearm_fatality_rate", "recurring_core", "firearm_fatality_rate",
    "motor_vehicle_crash_rate", "recurring_core", "motor_vehicle_crash_rate",
    "pct_commute_walk", "recurring_core", "pct_commute_walk",
    "pct_commute_wfh", "recurring_core", "pct_commute_wfh",
    "vacancy_rate", "recurring_core", "vacancy_rate",
    "pct_hh_0_vehicles", "recurring_core", "pct_hh_0_vehicles",
    "pct_no_internet_access", "recurring_core", "pct_no_internet_access",
    "walkability_index", "supplemental_or_caution", "walkability_index",
    "jobs_access_45min_transit", "supplemental_or_caution", "jobs_access_45min_transit",
    "pct_population_low_income_low_access_1_10", "supplemental_or_caution", "pct_population_low_income_low_access_1_10",
    "pop_weighted_density_sqmi", "supplemental_or_caution", "pop_weighted_density_sqmi",
    aqi_metric_id, "supplemental_or_caution", aqi_source_column,
    "fema_risk_score", "supplemental_or_caution", "fema_risk_score"
  )

  clustering_metric_decisions <- tibble::tribble(
    ~metric_id, ~use_for_clustering, ~decision_reason,
    "value_to_income", TRUE, "retain for clustering and scoring",
    "pct_rent_burden_30plus", TRUE, "retain for clustering and scoring",
    "pov_rate", TRUE, "retain for clustering and scoring",
    "permits_per_1000_housing_units", TRUE, "retain for clustering and scoring",
    "permits_share_units_5_plus", TRUE, "retain for clustering and scoring",
    "pct_struct_mobile", TRUE, "retain for clustering and scoring",
    "pct_struct_small_mf", TRUE, "retain for clustering and scoring",
    "pct_struct_mid_mf", TRUE, "retain for clustering and scoring",
    "premature_death_rate", TRUE, "retain for clustering and scoring",
    "mental_health_provider_ratio", TRUE, "retain for clustering and scoring",
    "drug_overdose_death_rate", TRUE, "retain for clustering and scoring",
    "pct_uninsured_adults", TRUE, "retain for clustering and scoring",
    "preventable_hospital_stay_rate", TRUE, "retain for clustering and scoring",
    "firearm_fatality_rate", TRUE, "retain for clustering and scoring",
    "motor_vehicle_crash_rate", TRUE, "retain for clustering and scoring",
    "pct_commute_walk", TRUE, "retain for clustering and scoring",
    "pct_commute_wfh", TRUE, "retain for clustering and scoring",
    "vacancy_rate", TRUE, "retain for clustering and scoring",
    "pct_hh_0_vehicles", TRUE, "retain for clustering and scoring",
    "pct_no_internet_access", TRUE, "retain for clustering and scoring",
    "walkability_index", TRUE, "retain for clustering and scoring",
    "jobs_access_45min_transit", TRUE, "retain for clustering and scoring",
    "pct_population_low_income_low_access_1_10", TRUE, "retain for clustering and scoring",
    "pop_weighted_density_sqmi", TRUE, "retain for clustering and scoring",
    aqi_metric_id, TRUE, "retain for clustering and scoring",
    "fema_risk_score", TRUE, "retain for clustering and scoring"
  )

  cluster_name_map <- tibble::tibble(
    livability_kmeans_cluster = c(1, 2, 3, 4, 5, 6),
    livability_cluster_name = c(
      "Healthy Affordable Havens",
      "Knowledge And Care Hubs",
      "High-Access Prosperous Hubs",
      "Strained Interior Markets",
      "Amenity Growth Markets",
      "Megametro Extremes"
    ),
    cluster_interpretation = c(
      "Strong affordability, health, and environmental fundamentals with more modest access intensity.",
      "Knowledge-heavy and college-adjacent metros with strong health scores and solid overall livability.",
      "Highly connected, high-performing hubs with strong health outcomes and somewhat thinner affordability.",
      "Interior and legacy markets with weaker health outcomes and lower overall livability.",
      "Fast-growing lifestyle and Sunbelt-adjacent markets with middling access and affordability pressure.",
      "Very large, unusual metros where extreme access coexists with major affordability and environmental strain."
    )
  )

  list(
    output_dir = output_dir,
    output_dir_name = output_dir_name,
    aqi_metric_id = aqi_metric_id,
    aqi_source_column = aqi_source_column,
    expected_kpis = expected_kpis,
    clustering_metric_decisions = clustering_metric_decisions,
    cluster_name_map = cluster_name_map,
    selected_natural_k = 6,
    candidate_k = 5:9,
    candidate_k_extended = 2:12
  )
}
