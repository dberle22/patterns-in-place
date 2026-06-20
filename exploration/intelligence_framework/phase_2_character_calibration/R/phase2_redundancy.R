build_phase2_redundancy_bundle <- function(character_model_df, catalog_check, config) {
  full_metric_ids <- config$expected_kpis$metric_id
  reduced_metric_ids <- config$clustering_metric_decisions |>
    dplyr::filter(use_for_clustering) |>
    dplyr::pull(metric_id)

  metric_metadata <- catalog_check |>
    dplyr::select(metric_id, subject_id, topic_id)

  modeling_wide <- character_model_df |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      dplyr::all_of(paste0("imputed_", full_metric_ids))
    ) |>
    dplyr::rename_with(
      .fn = \(x) stringr::str_remove(x, "^imputed_"),
      .cols = dplyr::starts_with("imputed_")
    )

  full_matrix <- modeling_wide |>
    dplyr::select(dplyr::all_of(full_metric_ids)) |>
    scale() |>
    as.matrix()

  reduced_matrix <- modeling_wide |>
    dplyr::select(dplyr::all_of(reduced_metric_ids)) |>
    scale() |>
    as.matrix()

  row.names(full_matrix) <- modeling_wide$cbsa_code
  row.names(reduced_matrix) <- modeling_wide$cbsa_code

  full_correlation <- stats::cor(full_matrix)

  redundant_pairs <- which(abs(full_correlation) >= 0.75 & upper.tri(full_correlation), arr.ind = TRUE) |>
    as.data.frame() |>
    tibble::as_tibble() |>
    dplyr::transmute(
      metric_a = colnames(full_correlation)[col],
      metric_b = rownames(full_correlation)[row],
      correlation = full_correlation[cbind(row, col)]
    ) |>
    dplyr::left_join(
      metric_metadata |>
        dplyr::rename(topic_a = topic_id, subject_a = subject_id),
      by = c("metric_a" = "metric_id")
    ) |>
    dplyr::left_join(
      metric_metadata |>
        dplyr::rename(topic_b = topic_id, subject_b = subject_id),
      by = c("metric_b" = "metric_id")
    ) |>
    dplyr::mutate(abs_correlation = abs(correlation)) |>
    dplyr::arrange(dplyr::desc(abs_correlation), dplyr::desc(correlation))

  pca_fit <- stats::prcomp(full_matrix, center = FALSE, scale. = FALSE)
  variance_explained <- (pca_fit$sdev ^ 2) / sum(pca_fit$sdev ^ 2)

  pca_variance <- tibble::tibble(
    principal_component = paste0("PC", seq_along(variance_explained)),
    variance_explained = variance_explained,
    cumulative_variance = cumsum(variance_explained)
  )

  pca_loadings <- tibble::as_tibble(
    pca_fit$rotation[, seq_len(min(10, ncol(pca_fit$rotation))), drop = FALSE],
    rownames = "metric_id"
  ) |>
    dplyr::left_join(metric_metadata, by = "metric_id")

  full_metric_set <- tibble::tibble(
    metric_set = "full_kpi_set",
    metric_id = full_metric_ids
  )

  pca_recommended_metric_set <- tibble::tibble(
    metric_set = "current_clustering_set",
    metric_id = reduced_metric_ids
  )

  list(
    full_metric_set = full_metric_set,
    pca_recommended_metric_set = pca_recommended_metric_set,
    redundant_pairs = redundant_pairs,
    pca_variance = pca_variance,
    pca_loadings = pca_loadings
  )
}
