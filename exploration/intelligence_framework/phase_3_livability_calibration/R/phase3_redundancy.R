build_phase3_redundancy_bundle <- function(livability_model_df, config) {
  clustering_matrix_long <- livability_model_df |>
    dplyr::select(cbsa_code, dplyr::all_of(paste0("imputed_", config$expected_kpis$metric_id))) |>
    tidyr::pivot_longer(
      cols = dplyr::all_of(paste0("imputed_", config$expected_kpis$metric_id)),
      names_to = "metric_column",
      values_to = "imputed_value"
    ) |>
    dplyr::mutate(metric_id = stringr::str_remove(metric_column, "^imputed_")) |>
    dplyr::select(-metric_column) |>
    dplyr::group_by(metric_id) |>
    dplyr::mutate(clustering_z = safe_zscore(imputed_value)) |>
    dplyr::ungroup()

  clustering_matrix_wide_all <- clustering_matrix_long |>
    dplyr::select(cbsa_code, metric_id, clustering_z) |>
    tidyr::pivot_wider(names_from = metric_id, values_from = clustering_z) |>
    dplyr::arrange(cbsa_code)

  clustering_matrix_all <- clustering_matrix_wide_all |>
    dplyr::select(-cbsa_code) |>
    as.matrix()

  correlation_audit <- stats::cor(clustering_matrix_all, use = "pairwise.complete.obs") |>
    as.data.frame() |>
    tibble::rownames_to_column("metric_a") |>
    tidyr::pivot_longer(
      cols = -metric_a,
      names_to = "metric_b",
      values_to = "correlation"
    ) |>
    dplyr::filter(metric_a < metric_b) |>
    dplyr::arrange(desc(abs(correlation)))

  redundant_pairs <- correlation_audit |>
    dplyr::filter(abs(correlation) >= 0.75)

  pca_fit <- stats::prcomp(clustering_matrix_all, center = FALSE, scale. = FALSE)
  pca_variance <- tibble::tibble(
    principal_component = paste0("PC", seq_along(pca_fit$sdev)),
    variance_explained = (pca_fit$sdev ^ 2) / sum(pca_fit$sdev ^ 2),
    cumulative_variance = cumsum((pca_fit$sdev ^ 2) / sum(pca_fit$sdev ^ 2))
  )

  pca_loadings <- as.data.frame(unclass(pca_fit$rotation[, 1:6])) |>
    tibble::rownames_to_column("metric_id")

  list(
    clustering_matrix_long = clustering_matrix_long,
    clustering_matrix_wide_all = clustering_matrix_wide_all,
    clustering_matrix_all = clustering_matrix_all,
    correlation_audit = correlation_audit,
    redundant_pairs = redundant_pairs,
    pca_variance = pca_variance,
    pca_loadings = pca_loadings
  )
}
