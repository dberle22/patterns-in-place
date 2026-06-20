phase2_character_config <- function() {
  output_dir <- here::here(
    "exploration",
    "intelligence_framework",
    "phase_2_character_calibration",
    "outputs"
  )

  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  expected_kpis <- tibble::tribble(
    ~metric_id, ~audit_bucket, ~expected_source_column, ~use_for_clustering,
    "diversity_index", "recurring_core", "diversity_index", TRUE,
    "pct_black_nh", "recurring_core", "pct_black_nh", TRUE,
    "pct_asian_nh", "recurring_core", "pct_asian_nh", TRUE,
    "pct_hispanic", "recurring_core", "pct_hispanic", TRUE,
    "pct_age_over_64", "recurring_core", "pct_age_over_64", TRUE,
    "pct_ba_plus", "recurring_core", "pct_ba_plus", TRUE,
    "pct_foreign_born", "recurring_core", "pct_foreign_born", TRUE,
    "pop_weighted_density_sqmi", "recurring_core", "pop_weighted_density_sqmi", TRUE,
    "friending_bias", "recurring_core", "friending_bias", TRUE,
    "civic_engagement_volunteering_rate", "recurring_core", "civic_engagement_volunteering_rate", TRUE,
    "civic_organizations_per_1000", "recurring_core", "civic_organizations_per_1000", TRUE,
    "nonprofits_per_100k", "recurring_core", "nonprofits_per_100k", TRUE,
    "irs_net_migration_rate", "recurring_core", "irs_net_migration_rate", TRUE,
    "pct_moved_diff_st", "recurring_core", "pct_moved_diff_st", TRUE,
    "pct_moved_abroad", "recurring_core", "pct_moved_abroad", TRUE,
    "social_associations_per_10k", "recurring_core", "social_associations_per_10k", TRUE,
    "pct_struct_multifam", "recurring_core", "pct_struct_multifam", TRUE
  )

  clustering_metric_decisions <- expected_kpis |>
    dplyr::transmute(
      metric_id,
      use_for_clustering,
      decision_reason = "keep in the published Character clustering set after the redundancy audit; no pair exceeded the |r| >= 0.75 reduction threshold"
    )

  list(
    output_dir = output_dir,
    expected_kpis = expected_kpis,
    clustering_metric_decisions = clustering_metric_decisions,
    comparison_k = 4:8,
    candidate_k_extended = 2:12,
    final_k = 7L
  )
}
