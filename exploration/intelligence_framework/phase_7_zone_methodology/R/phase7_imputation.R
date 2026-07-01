build_phase7_imputation_bundle <- function(tract_frame, coverage_audit, config) {
  metric_ids <- config$expected_kpis$metric_id
  source_year_lookup <- config$expected_kpis |>
    dplyr::select(metric_id, expected_source_table) |>
    dplyr::distinct() |>
    dplyr::mutate(
      source_year_column = dplyr::case_when(
        metric_id == "ejs_pm25" ~ "environment_ejs_year",
        metric_id == "fema_risk_score" ~ "environment_fema_year",
        TRUE ~ paste0(expected_source_table, "_year")
      )
    )

  metric_completeness <- coverage_audit |>
    dplyr::left_join(
      source_year_lookup,
      by = "metric_id"
    ) |>
    dplyr::mutate(
      imputation_method = dplyr::case_when(
        missing_tracts == 0 ~ "none_needed",
        TRUE ~ "median"
      ),
      knn_review_flag = missing_tracts > 0 & completeness_pct < 0.85,
      imputation_note = dplyr::case_when(
        knn_review_flag ~ "missingness exceeds the KNN review threshold, but Sprint 2 keeps median imputation until the post-review pass",
        missing_tracts > 0 ~ "median imputation used for the initial national model pass",
        TRUE ~ "metric is complete in the current tract universe"
      )
    ) |>
    dplyr::arrange(completeness_pct, metric_id)

  raw_values_long <- tract_frame |>
    dplyr::select(
      tract_geoid,
      geo_name,
      cbsa_code,
      cbsa_name,
      county_geoid,
      county_name,
      dplyr::all_of(metric_ids)
    ) |>
    tidyr::pivot_longer(
      cols = dplyr::all_of(metric_ids),
      names_to = "metric_id",
      values_to = "raw_value"
    )

  source_year_long <- tract_frame |>
    dplyr::select(
      tract_geoid,
      dplyr::all_of(unique(source_year_lookup$source_year_column))
    ) |>
    tidyr::pivot_longer(
      cols = dplyr::all_of(unique(source_year_lookup$source_year_column)),
      names_to = "source_year_column",
      values_to = "source_year"
    )

  missing_tracts_long <- raw_values_long |>
    dplyr::left_join(source_year_lookup, by = "metric_id") |>
    dplyr::left_join(source_year_long, by = c("tract_geoid", "source_year_column")) |>
    dplyr::left_join(
      metric_completeness |>
        dplyr::select(metric_id, theme, audit_bucket, completeness_pct, imputation_method),
      by = "metric_id"
    ) |>
    dplyr::filter(is.na(raw_value)) |>
    dplyr::arrange(metric_id, tract_geoid)

  imputation_log <- metric_completeness |>
    dplyr::transmute(
      metric_id,
      theme,
      polarity,
      use_for_clustering,
      missing_tracts_before = missing_tracts,
      completeness_pct,
      imputation_method,
      fill_value = median_value,
      knn_review_flag,
      imputation_note
    ) |>
    dplyr::arrange(dplyr::desc(missing_tracts_before), metric_id)

  imputed_values_long <- raw_values_long |>
    dplyr::left_join(
      imputation_log |>
        dplyr::select(metric_id, polarity, fill_value, imputation_method),
      by = "metric_id"
    ) |>
    dplyr::mutate(
      raw_value = dplyr::if_else(
        metric_id %in% config$log_transform_kpis & !is.na(raw_value),
        log1p(pmax(raw_value, 0)),
        raw_value
      ),
      fill_value = dplyr::if_else(
        metric_id %in% config$log_transform_kpis & !is.na(fill_value),
        log1p(pmax(fill_value, 0)),
        fill_value
      ),
      was_imputed = is.na(raw_value),
      imputed_value = dplyr::coalesce(raw_value, fill_value),
      scoring_value = dplyr::if_else(polarity == "negative", -imputed_value, imputed_value)
    )

  imputed_cells <- imputed_values_long |>
    dplyr::filter(was_imputed) |>
    dplyr::select(
      tract_geoid,
      geo_name,
      cbsa_code,
      cbsa_name,
      county_geoid,
      county_name,
      metric_id,
      imputation_method,
      fill_value,
      imputed_value
    ) |>
    dplyr::arrange(metric_id, tract_geoid)

  imputed_kpis_wide <- imputed_values_long |>
    dplyr::select(tract_geoid, metric_id, imputed_value) |>
    tidyr::pivot_wider(
      names_from = metric_id,
      values_from = imputed_value,
      names_prefix = "imputed_"
    )

  imputation_flags_wide <- imputed_values_long |>
    dplyr::select(tract_geoid, metric_id, was_imputed) |>
    tidyr::pivot_wider(
      names_from = metric_id,
      values_from = was_imputed,
      names_prefix = "imputed_flag_"
    )

  scoring_inputs_wide <- imputed_values_long |>
    dplyr::select(tract_geoid, metric_id, scoring_value) |>
    tidyr::pivot_wider(
      names_from = metric_id,
      values_from = scoring_value,
      names_prefix = "scored_"
    )

  phase7_model_df <- tract_frame |>
    dplyr::left_join(imputed_kpis_wide, by = "tract_geoid") |>
    dplyr::left_join(imputation_flags_wide, by = "tract_geoid") |>
    dplyr::left_join(scoring_inputs_wide, by = "tract_geoid")

  list(
    metric_completeness = metric_completeness,
    missing_tracts_long = missing_tracts_long,
    imputation_log = imputation_log,
    imputed_cells = imputed_cells,
    phase7_model_df = phase7_model_df
  )
}
