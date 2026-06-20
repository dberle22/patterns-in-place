build_phase3_imputation_bundle <- function(livability_df, catalog_check, config) {
  metric_completeness <- config$expected_kpis |>
    dplyr::mutate(
      non_null_cbsas = purrr::map_int(metric_id, \(metric) sum(!is.na(livability_df[[metric]]))),
      missing_cbsas = nrow(livability_df) - non_null_cbsas,
      completeness_pct = non_null_cbsas / nrow(livability_df),
      median_value = purrr::map_dbl(metric_id, \(metric) median(livability_df[[metric]], na.rm = TRUE))
    ) |>
    dplyr::left_join(
      catalog_check |>
        dplyr::select(metric_id, source_table, expected_source_column, reliability, polarity, model_role),
      by = "metric_id"
    ) |>
    dplyr::arrange(audit_bucket, completeness_pct, metric_id)

  imputation_audit <- metric_completeness |>
    dplyr::transmute(
      metric_id,
      audit_bucket,
      reliability,
      polarity,
      model_role,
      missing_before = missing_cbsas,
      completeness_pct,
      imputation_method = dplyr::if_else(missing_before > 0, "median", "none_needed"),
      fill_value = median_value
    ) |>
    dplyr::arrange(audit_bucket, desc(missing_before), metric_id)

  imputed_cells <- livability_df |>
    dplyr::select(cbsa_code, cbsa_name, dplyr::all_of(config$expected_kpis$metric_id)) |>
    tidyr::pivot_longer(
      cols = dplyr::all_of(config$expected_kpis$metric_id),
      names_to = "metric_id",
      values_to = "raw_value"
    ) |>
    dplyr::left_join(
      imputation_audit |>
        dplyr::select(metric_id, polarity, fill_value, imputation_method),
      by = "metric_id"
    ) |>
    dplyr::mutate(
      was_imputed = is.na(raw_value),
      imputed_value = dplyr::coalesce(raw_value, fill_value),
      scoring_value = dplyr::if_else(polarity == "negative", -imputed_value, imputed_value)
    ) |>
    dplyr::filter(was_imputed) |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      metric_id,
      polarity,
      imputation_method,
      fill_value,
      imputed_value
    ) |>
    dplyr::arrange(metric_id, cbsa_name)

  imputed_values_wide <- livability_df |>
    dplyr::select(cbsa_code, dplyr::all_of(config$expected_kpis$metric_id)) |>
    tidyr::pivot_longer(
      cols = dplyr::all_of(config$expected_kpis$metric_id),
      names_to = "metric_id",
      values_to = "raw_value"
    ) |>
    dplyr::left_join(
      imputation_audit |>
        dplyr::select(metric_id, polarity, fill_value),
      by = "metric_id"
    ) |>
    dplyr::mutate(
      imputed_value = dplyr::coalesce(raw_value, fill_value),
      was_imputed = is.na(raw_value),
      scoring_value = dplyr::if_else(polarity == "negative", -imputed_value, imputed_value)
    )

  imputed_kpis_wide <- imputed_values_wide |>
    dplyr::select(cbsa_code, metric_id, imputed_value) |>
    tidyr::pivot_wider(
      names_from = metric_id,
      values_from = imputed_value,
      names_prefix = "imputed_"
    )

  imputation_flags_wide <- imputed_values_wide |>
    dplyr::select(cbsa_code, metric_id, was_imputed) |>
    tidyr::pivot_wider(
      names_from = metric_id,
      values_from = was_imputed,
      names_prefix = "imputed_flag_"
    )

  scoring_inputs_wide <- imputed_values_wide |>
    dplyr::select(cbsa_code, metric_id, scoring_value) |>
    tidyr::pivot_wider(
      names_from = metric_id,
      values_from = scoring_value,
      names_prefix = "scored_"
    )

  livability_model_df <- livability_df |>
    dplyr::left_join(imputed_kpis_wide, by = "cbsa_code") |>
    dplyr::left_join(imputation_flags_wide, by = "cbsa_code") |>
    dplyr::left_join(scoring_inputs_wide, by = "cbsa_code")

  list(
    metric_completeness = metric_completeness,
    imputation_audit = imputation_audit,
    imputed_cells = imputed_cells,
    livability_model_df = livability_model_df
  )
}
