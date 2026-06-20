build_phase4_imputation_bundle <- function(opportunity_frame, catalog_check, config) {
  metric_ids <- config$expected_kpis$metric_id
  source_year_cols <- paste0(metric_ids, "_source_year")

  metric_completeness <- config$expected_kpis |>
    dplyr::mutate(
      non_null_cbsas = purrr::map_int(metric_id, \(metric) sum(!is.na(opportunity_frame[[metric]]))),
      missing_cbsas = nrow(opportunity_frame) - non_null_cbsas,
      completeness_pct = non_null_cbsas / nrow(opportunity_frame),
      median_value = purrr::map_dbl(metric_id, \(metric) median(opportunity_frame[[metric]], na.rm = TRUE))
    ) |>
    dplyr::left_join(
      catalog_check |>
        dplyr::select(metric_id, source_table, reliability, polarity, model_role),
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
      use_for_clustering,
      missing_before = missing_cbsas,
      completeness_pct,
      imputation_method = dplyr::if_else(missing_before > 0, "median", "none_needed"),
      fill_value = median_value
    ) |>
    dplyr::arrange(audit_bucket, dplyr::desc(missing_before), metric_id)

  raw_values_long <- opportunity_frame |>
    dplyr::select(cbsa_code, cbsa_name, dplyr::all_of(metric_ids)) |>
    tidyr::pivot_longer(
      cols = dplyr::all_of(metric_ids),
      names_to = "metric_id",
      values_to = "raw_value"
    )

  source_year_long <- opportunity_frame |>
    dplyr::select(cbsa_code, dplyr::all_of(source_year_cols)) |>
    tidyr::pivot_longer(
      cols = dplyr::all_of(source_year_cols),
      names_to = "metric_year_col",
      values_to = "source_year"
    ) |>
    dplyr::mutate(metric_id = stringr::str_remove(metric_year_col, "_source_year$")) |>
    dplyr::select(-metric_year_col)

  missing_cbsas_long <- raw_values_long |>
    dplyr::left_join(source_year_long, by = c("cbsa_code", "metric_id")) |>
    dplyr::left_join(
      metric_completeness |>
        dplyr::select(metric_id, audit_bucket, use_for_clustering, source_table, reliability, polarity),
      by = "metric_id"
    ) |>
    dplyr::filter(is.na(raw_value)) |>
    dplyr::arrange(metric_id, cbsa_name)

  imputation_sensitive_metros <- missing_cbsas_long |>
    dplyr::count(cbsa_code, cbsa_name, name = "missing_kpis") |>
    dplyr::arrange(dplyr::desc(missing_kpis), cbsa_name)

  imputed_cells <- raw_values_long |>
    dplyr::left_join(source_year_long, by = c("cbsa_code", "metric_id")) |>
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
      source_year,
      polarity,
      imputation_method,
      fill_value,
      imputed_value
    ) |>
    dplyr::arrange(metric_id, cbsa_name)

  imputed_values_wide <- raw_values_long |>
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

  opportunity_model_df <- opportunity_frame |>
    dplyr::left_join(imputed_kpis_wide, by = "cbsa_code") |>
    dplyr::left_join(imputation_flags_wide, by = "cbsa_code") |>
    dplyr::left_join(scoring_inputs_wide, by = "cbsa_code")

  list(
    metric_completeness = metric_completeness,
    imputation_audit = imputation_audit,
    missing_cbsas_long = missing_cbsas_long,
    imputation_sensitive_metros = imputation_sensitive_metros,
    imputed_cells = imputed_cells,
    opportunity_model_df = opportunity_model_df
  )
}
