phase4_opportunity_config <- function() {
  output_dir <- here::here(
    "exploration",
    "intelligence_framework",
    "phase_4_opportunity_calibration",
    "outputs"
  )

  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  expected_kpis <- tibble::tribble(
    ~metric_id, ~audit_bucket, ~expected_source_column, ~use_for_clustering,
    "income_pc_growth_5yr", "recurring_core", "income_pc_growth_5yr", TRUE,
    "pct_unemployment_rate", "recurring_core", "pct_unemployment_rate", TRUE,
    "lfpr", "recurring_core", "lfpr", TRUE,
    "pov_rate_change_5yr", "recurring_core", "pov_rate_change_5yr", TRUE,
    "qcew_private_avg_wkly_wage", "recurring_core", "qcew_private_avg_wkly_wage", TRUE,
    "hpi_5yr_pct", "recurring_core", "hpi_5yr_pct", TRUE,
    "hpi_yoy_pct", "recurring_core", "hpi_yoy_pct", TRUE,
    "zori_annual_avg_yoy_pct", "coverage_caution", "zori_annual_avg_yoy_pct", TRUE,
    "pop_growth_5yr", "recurring_core", "pop_growth_5yr", TRUE,
    "irs_net_migration_rate", "recurring_core", "irs_net_migration_rate", TRUE,
    "irs_net_agi", "recurring_core", "irs_net_agi", TRUE,
    "permits_per_1000_housing_units", "recurring_core", "permits_per_1000_housing_units", FALSE,
    "permits_share_units_5_plus", "recurring_core", "permits_share_units_5_plus", TRUE,
    "productivity_growth_5yr", "recurring_core", "productivity_growth_5yr", TRUE,
    "industry_concentration_hhi", "recurring_core", "industry_concentration_hhi", TRUE,
    "bfs_business_application_rate_per_1000_establishments", "recurring_core", "bfs_business_application_rate_per_1000_establishments", TRUE,
    "cbp_estabs_per_1000_residents", "recurring_core", "cbp_estabs_per_1000_residents", TRUE,
    "pct_ba_plus_change_5yr", "recurring_core", "pct_ba_plus_change_5yr", TRUE,
    "lq_professional", "recurring_core", "lq_professional", TRUE,
    "lq_information", "recurring_core", "lq_information", TRUE,
    "lq_manufacturing", "recurring_core", "lq_manufacturing", TRUE,
    "pct_real_gdp_information", "recurring_core", "pct_real_gdp_information", FALSE,
    "economic_connectedness", "proxy_audit_only", "economic_connectedness", FALSE
  )

  clustering_metric_decisions <- expected_kpis |>
    dplyr::transmute(
      metric_id,
      use_for_clustering,
      decision_reason = dplyr::case_when(
        metric_id == "economic_connectedness" ~ "retain as audit and hypothesis proxy until direct mobility data lands",
        metric_id == "zori_annual_avg_yoy_pct" ~ "retain for clustering with explicit coverage caution and median imputation",
        metric_id == "pct_real_gdp_information" ~ "drop from default clustering because it strongly overlaps with lq_information in the PCA and correlation audit",
        metric_id == "permits_per_1000_housing_units" ~ "drop from default clustering because it overlaps with pop_growth_5yr as a market-intensity signal; retain as descriptive context",
        TRUE ~ "retain for clustering and scoring"
      )
    )

  list(
    output_dir = output_dir,
    expected_kpis = expected_kpis,
    clustering_metric_decisions = clustering_metric_decisions,
    final_k = 6L,
    comparison_k = c(5L, 6L),
    candidate_k = 5:9,
    candidate_k_extended = 2:12
  )
}
