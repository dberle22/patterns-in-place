phase7_zone_config <- function(
  output_dir = Sys.getenv("PHASE7_OUTPUT_DIR"),
  input_frame_path = Sys.getenv("PHASE7_INPUT_FRAME")
) {
  # Output and input overrides for side-by-side reruns (e.g. the 2026-10 labor
  # fix rerun). Both default to the canonical behaviour: write to `outputs/`,
  # which the mart loaders read, and build the tract frame from Gold.
  # - PHASE7_OUTPUT_DIR: repo-relative folder to write every Phase 7 artifact to
  #   instead of `outputs/`, so a rerun never overwrites the promoted outputs.
  # - PHASE7_INPUT_FRAME: repo-relative path to a saved
  #   `phase7_tract_frame.parquet`; when set, the frame build reads it instead
  #   of querying `gold.intelligence_zone_inputs` (used to replay old inputs).
  output_dir <- if (nzchar(output_dir)) {
    here::here(output_dir)
  } else {
    here::here(
      "exploration",
      "intelligence_framework",
      "phase_7_zone_methodology",
      "outputs"
    )
  }
  input_frame_path <- if (nzchar(input_frame_path)) here::here(input_frame_path) else NA_character_

  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  # This table is the canonical Sprint 1.2 KPI contract for the first national
  # tract clustering pass. Each row tells the later frame-build, imputation, and
  # scoring steps which source field to pull, how to orient the KPI for scoring,
  # and whether the KPI stays in the default clustering vector.
  expected_kpis <- tibble::tribble(
    ~metric_id, ~theme, ~audit_bucket, ~expected_source_table, ~expected_source_column, ~polarity, ~use_for_clustering, ~coverage_rule, ~baseline_note,
    "pct_hispanic", "character", "recurring_core", "population_demographics", "pct_hispanic", "neutral", TRUE, "median_impute_if_missing", NA_character_,
    "pct_black_nh", "character", "recurring_core", "population_demographics", "pct_black_nh", "neutral", TRUE, "median_impute_if_missing", NA_character_,
    "pct_asian_nh", "character", "recurring_core", "population_demographics", "pct_asian_nh", "neutral", TRUE, "median_impute_if_missing", NA_character_,
    "pct_age_over_64", "character", "recurring_core", "population_demographics", "pct_age_over_64", "neutral", TRUE, "median_impute_if_missing", NA_character_,
    "pct_ba_plus", "character", "recurring_core", "population_demographics", "pct_ba_plus", "positive", TRUE, "median_impute_if_missing", NA_character_,
    "pct_same_house", "character", "recurring_core", "migration_wide", "pct_same_house", "positive", TRUE, "median_impute_if_missing", "treat as residential stability proxy rather than a universal welfare measure",
    "owner_occ_rate", "character", "recurring_core", "housing_core_wide", "owner_occ_rate", "positive", TRUE, "median_impute_if_missing", "zero-denominator NaNs are structural and should be treated as missing before imputation",
    "pop_weighted_density_sqmi", "character", "recurring_core", "transport_built_form_wide", "pop_weighted_density_sqmi", "positive", TRUE, "median_impute_if_missing", "high-skew KPI; evaluate log transform before final z-scoring",
    "pct_rent_burden_30plus", "livability", "recurring_core", "housing_core_wide", "pct_rent_burden_30plus", "negative", TRUE, "median_impute_if_missing", NA_character_,
    "vacancy_rate", "livability", "recurring_core", "housing_core_wide", "vacancy_rate", "negative", TRUE, "median_impute_if_missing", "zero-denominator NaNs are structural and should be treated as missing before imputation",
    "pct_commute_walk", "livability", "recurring_core", "transport_built_form_wide", "pct_commute_walk", "positive", TRUE, "median_impute_if_missing", "distribution is heavily right-skewed near zero but still carries strong within-CBSA signal",
    "walkability_index", "livability", "coverage_caution", "transport_built_form_sld", "walkability_index", "positive", TRUE, "median_impute_if_missing_with_ct_audit", "one-time 2021 SLD baseline; residual tract misses are concentrated in Connecticut",
    "pct_no_internet_access", "livability", "recurring_core", "social_infra_wide", "pct_no_internet_access", "negative", TRUE, "median_impute_if_missing", NA_character_,
    "ejs_pm25", "livability", "recurring_core", "environment_wide", "ejs_pm25", "negative", TRUE, "latest_non_null_year_then_median_impute", "mixed-vintage environmental field pulled from latest non-null tract slice",
    "fema_risk_score", "livability", "recurring_core", "environment_wide", "fema_risk_score", "negative", TRUE, "latest_non_null_year_then_median_impute", "mixed-vintage environmental field pulled from latest non-null tract slice",
    "pov_rate", "opportunity", "recurring_core", "economics_income_wide", "pov_rate", "negative", TRUE, "median_impute_if_missing", NA_character_,
    "pct_unemployment_rate", "opportunity", "recurring_core", "economics_labor_wide", "pct_unemployment_rate", "negative", TRUE, "median_impute_if_missing", "check negative-value edge cases before final model run",
    "pov_rate_change_3yr", "opportunity", "coverage_caution", "economics_income_wide", "pov_rate_change_3yr", "negative", TRUE, "median_impute_if_missing", "use 3yr fallback until a harmonized tract-safe 5yr series exists",
    "pct_ba_plus_change_3yr", "opportunity", "coverage_caution", "population_demographics", "pct_ba_plus_change_3yr", "positive", TRUE, "median_impute_if_missing", "use 3yr fallback until a harmonized tract-safe 5yr series exists",
    "jobs_per_resident", "opportunity", "coverage_caution", "economics_lodes_wide", "jobs_to_workers_ratio", "positive", TRUE, "median_impute_if_missing", "LODES coverage is mildly incomplete nationally but acceptable for the first tract model pass",
    "pct_jobs_high_wage", "opportunity", "coverage_caution", "economics_lodes_wide", "pct_jobs_earnings_high", "positive", TRUE, "median_impute_if_missing", "LODES coverage is mildly incomplete nationally but acceptable for the first tract model pass",
    "pct_jobs_professional_services", "opportunity", "coverage_caution", "economics_lodes_wide", "pct_jobs_ind_professional_scientific_technical", "positive", TRUE, "median_impute_if_missing", "LODES coverage is mildly incomplete nationally but acceptable for the first tract model pass"
  )

  # These are the fields we explicitly reviewed during Sprint 1.2 and decided
  # not to keep in the default clustering vector. They still matter as
  # diagnostic or interpretive context, so we keep the reasons close to the
  # final contract instead of scattering them across notes.
  excluded_kpis <- tibble::tribble(
    ~metric_id, ~expected_source_table, ~expected_source_column, ~decision_reason,
    "diversity_index", "population_demographics", "diversity_index", "drop from default clustering because the race and ethnicity shares already represent this dimension more transparently",
    "pct_foreign_born", "migration_wide", "pct_foreign_born", "drop from default clustering because within-CBSA signal was weaker and the KPI is largely absorbed into the broader urbanity and composition bundle",
    "pct_struct_multifam", "housing_core_wide", "pct_struct_multifam", "drop from default clustering because it is the strongest direct redundancy pair with owner_occ_rate",
    "median_gross_rent", "housing_core_wide", "median_gross_rent", "drop from default clustering because it has the weakest coverage and does not add enough beyond other affordability fields",
    "median_home_value", "housing_core_wide", "median_home_value", "drop from default clustering because it overlaps with the broader socioeconomic bundle and is better kept for sensitivity checks",
    "pct_hh_0_vehicles", "transport_built_form_wide", "pct_hh_0_vehicles", "drop from default clustering because PCA showed it is heavily absorbed by density and walkability structure",
    "pct_commute_transit", "transport_built_form_wide", "pct_commute_transit", "drop from default clustering because within-CBSA signal is weak and the KPI overlaps with density and auto-access structure",
    "jobs_access_45min_transit", "transport_built_form_sld", "jobs_access_45min_transit", "drop from default clustering because the tract SLD story is already represented by walkability_index in the lean default model",
    "median_hh_income", "economics_income_wide", "median_hh_income", "drop from default clustering because PCA showed it is one of the more replaceable fields once pct_ba_plus and pov_rate are retained",
    "jobs_inflow_ratio", "economics_lodes_od", "jobs_inflow_ratio", "keep out of the initial model because WAC is the priority and the current jobs-side vector is already adequate without OD expansion"
  )

  clustering_metric_decisions <- dplyr::bind_rows(
    expected_kpis |>
      dplyr::transmute(
        metric_id,
        use_for_clustering,
        decision_reason = "retain in the default 22-KPI Phase 7 clustering vector"
      ),
    excluded_kpis |>
      dplyr::transmute(
        metric_id,
        use_for_clustering = FALSE,
        decision_reason
      )
  )

  list(
    output_dir = output_dir,
    input_frame_path = input_frame_path,
    expected_kpis = expected_kpis,
    excluded_kpis = excluded_kpis,
    clustering_metric_decisions = clustering_metric_decisions,
    final_kpi_count = nrow(expected_kpis),
    theme_counts = expected_kpis |>
      dplyr::count(theme, name = "kpi_count"),
    dbscan_packages = c("dbscan", "sf", "proxy", "dplyr"),
    spatial_optional_packages = c("spdep", "rgeoda"),
    corridor_distance_formula = "alpha * cosine_distance(kpi_vector) + (1 - alpha) * normalized_spatial_distance(centroid)",
    corridor_name_template = "{county_name}_{zone_type}_{rank}",
    corridor_alpha_default = 0.70,
    corridor_alpha_rationale = paste(
      "Default alpha keeps corridor detection feature-primary while still",
      "penalizing geographically distant tracts enough to avoid implausibly",
      "scattered same-type corridors."
    ),
    corridor_dbscan_defaults = tibble::tibble(
      parameter = c("eps", "min_samples"),
      default_value = c(NA_real_, NA_real_),
      calibration_status = c("set in Sprint 3 Jacksonville stress test", "set in Sprint 3 Jacksonville stress test"),
      calibration_note = c(
        "Use k-distance review plus corridor map coherence checks before locking.",
        "Start with small corridor-forming thresholds and adjust against map coherence."
      )
    ),
    corridor_noise_policy = "Retain zone_type label, assign corridor_id = NA for DBSCAN noise tracts.",
    sld_tract_baseline_year = 2021L,
    candidate_k = 7:10,
    calibration_sample_size = 5000L,
    run_gmm = FALSE,
    log_transform_kpis = c("pop_weighted_density_sqmi"),
    # Fixed name map for the current build (Dan, 2026-10-23). It replaces the
    # automatic centroid-score labeler, which left one cluster unnamed after the
    # ACS labor fix (see PHASE7_LABOR_FIX_RERUN_REVIEW.md). Names are the July
    # names carried forward to the matched clusters; renaming happens CBSA by
    # CBSA during issue work. `expected_tracts` is a guard: k-means IDs are only
    # stable for identical inputs, so if any cluster size changes the run stops
    # and the clusters must be re-matched before this map is updated.
    zone_name_map = tibble::tribble(
      ~zone_kmeans_cluster, ~zone_type, ~expected_tracts,
      1L, "Entry-Market Neighborhoods", 9770L,
      2L, "Knowledge Corridor", 10899L,
      3L, "Emerging Knowledge Districts", 2111L,
      4L, "Mixed-Income Middle Neighborhoods", 27469L,
      5L, "Working Neighborhoods", 11497L,
      6L, "Established Residential", 16385L,
      7L, "Commercial Core / Jobs Center", 68L
    ),
    draft_zone_labels = c(
      "Entry-Market Neighborhoods",
      "Emerging Knowledge Districts",
      "Knowledge Corridor",
      "Established Residential",
      "Mixed-Income Middle Neighborhoods",
      "Working Neighborhoods",
      "Commercial Core / Jobs Center"
    ),
    light_validation_cbsa_names = c(
      "Jacksonville, FL",
      "Richmond, VA"
    )
  )
}
