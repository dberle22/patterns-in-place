build_phase5_redundancy_bundle <- function(input_bundle, config) {
  feature_spec <- input_bundle$feature_spec

  standardized_wide <- input_bundle$combined_model_df |>
    dplyr::select(cbsa_code, cbsa_name, pop_total, spine_year, dplyr::all_of(feature_spec$feature_id)) |>
    dplyr::mutate(
      dplyr::across(
        dplyr::all_of(feature_spec$feature_id),
        safe_zscore
      )
    )

  standardization_audit <- standardized_wide |>
    dplyr::select(dplyr::all_of(feature_spec$feature_id)) |>
    purrr::imap_dfr(\(values, feature_id) {
      tibble::tibble(
        feature_id = feature_id,
        z_mean = mean(values),
        z_sd = stats::sd(values)
      )
    }) |>
    dplyr::left_join(feature_spec, by = "feature_id")

  metric_matrix <- standardized_wide |>
    dplyr::select(dplyr::all_of(feature_spec$feature_id)) |>
    as.matrix()

  row.names(metric_matrix) <- standardized_wide$cbsa_code

  correlation_matrix <- stats::cor(metric_matrix)

  redundant_pairs <- which(
    abs(correlation_matrix) >= config$correlation_flag_threshold &
      upper.tri(correlation_matrix),
    arr.ind = TRUE
  ) |>
    as.data.frame() |>
    tibble::as_tibble() |>
    dplyr::transmute(
      feature_a = colnames(correlation_matrix)[col],
      feature_b = rownames(correlation_matrix)[row],
      correlation = correlation_matrix[cbind(row, col)]
    ) |>
    dplyr::mutate(abs_correlation = abs(correlation)) |>
    dplyr::left_join(
      feature_spec |>
        dplyr::rename_with(\(x) paste0(x, "_a"), -c(feature_id)) |>
        dplyr::rename(feature_a = feature_id),
      by = "feature_a"
    ) |>
    dplyr::left_join(
      feature_spec |>
        dplyr::rename_with(\(x) paste0(x, "_b"), -c(feature_id)) |>
        dplyr::rename(feature_b = feature_id),
      by = "feature_b"
    ) |>
    dplyr::arrange(dplyr::desc(abs_correlation), dplyr::desc(correlation))

  pca_fit <- stats::prcomp(metric_matrix, center = FALSE, scale. = FALSE)
  variance_explained <- (pca_fit$sdev ^ 2) / sum(pca_fit$sdev ^ 2)

  pca_variance <- tibble::tibble(
    principal_component = paste0("PC", seq_along(variance_explained)),
    variance_explained = variance_explained,
    cumulative_variance = cumsum(variance_explained),
    eigenvalue = pca_fit$sdev ^ 2
  )

  retained_pc_count <- which(pca_variance$cumulative_variance >= config$target_cumulative_variance)[1]

  retained_pc_names <- paste0("PC", seq_len(retained_pc_count))

  loadings_matrix <- pca_fit$rotation[, seq_len(retained_pc_count), drop = FALSE]
  retained_pc_colnames <- paste0("loading_", retained_pc_names)
  colnames(loadings_matrix) <- retained_pc_colnames

  communalities <- rowSums(loadings_matrix ^ 2)
  max_abs_loading <- apply(abs(loadings_matrix), 1, max)

  kpi_decisions <- feature_spec |>
    dplyr::mutate(
      communality_retained_pcs = communalities[feature_id],
      max_abs_loading_retained_pcs = max_abs_loading[feature_id],
      keep_for_now = TRUE,
      drop_reason = NA_character_,
      recommendation_stage = "initial_keep"
    )

  low_signal_ids <- kpi_decisions |>
    dplyr::filter(
      communality_retained_pcs < config$low_communality_threshold &
        max_abs_loading_retained_pcs < config$low_loading_threshold
    ) |>
    dplyr::pull(feature_id)

  if (length(low_signal_ids) > 0) {
    kpi_decisions <- kpi_decisions |>
      dplyr::mutate(
        keep_for_now = dplyr::if_else(feature_id %in% low_signal_ids, FALSE, keep_for_now),
        drop_reason = dplyr::if_else(
          feature_id %in% low_signal_ids,
          sprintf(
            "low signal in retained PCs: communality < %.2f and max absolute loading < %.2f",
            config$low_communality_threshold,
            config$low_loading_threshold
          ),
          drop_reason
        ),
        recommendation_stage = dplyr::if_else(
          feature_id %in% low_signal_ids,
          "drop_low_signal",
          recommendation_stage
        )
      )
  }

  severe_pairs <- redundant_pairs |>
    dplyr::filter(abs_correlation >= config$correlation_drop_threshold)

  if (nrow(severe_pairs) > 0) {
    for (i in seq_len(nrow(severe_pairs))) {
      pair_features <- severe_pairs[i, c("feature_a", "feature_b")]

      pair_candidates <- kpi_decisions |>
        dplyr::filter(feature_id %in% c(pair_features$feature_a, pair_features$feature_b))

      chosen <- phase5_pick_preferred_metric(pair_candidates)
      drop_feature_id <- setdiff(pair_candidates$feature_id, chosen$feature_id)

      if (length(drop_feature_id) == 1) {
        kpi_decisions <- kpi_decisions |>
          dplyr::mutate(
            keep_for_now = dplyr::if_else(feature_id == drop_feature_id, FALSE, keep_for_now),
            drop_reason = dplyr::if_else(
              feature_id == drop_feature_id,
              sprintf(
                "high-correlation pair (|r| >= %.2f); kept %s because it had stronger retained-PC signal",
                config$correlation_drop_threshold,
                chosen$feature_id
              ),
              drop_reason
            ),
            recommendation_stage = dplyr::if_else(
              feature_id == drop_feature_id,
              "drop_high_correlation_pair",
              recommendation_stage
            )
          )
      }
    }
  }

  kpi_decisions <- kpi_decisions |>
    dplyr::mutate(
      recommended_for_clustering = keep_for_now,
      recommendation = dplyr::if_else(
        recommended_for_clustering,
        "keep",
        "drop"
      )
    ) |>
    dplyr::arrange(frame_id, metric_id)

  pca_loadings <- tibble::as_tibble(
    loadings_matrix,
    rownames = "feature_id"
  ) |>
    dplyr::mutate(
      communality_retained_pcs = communalities[feature_id],
      max_abs_loading_retained_pcs = max_abs_loading[feature_id]
    ) |>
    dplyr::left_join(kpi_decisions, by = "feature_id")

  recommended_metric_set <- kpi_decisions |>
    dplyr::filter(recommended_for_clustering) |>
    dplyr::select(
      frame_id,
      feature_id,
      metric_id,
      communality_retained_pcs,
      max_abs_loading_retained_pcs,
      drop_reason
    )

  list(
    standardized_wide = standardized_wide,
    standardization_audit = standardization_audit,
    redundant_pairs = redundant_pairs,
    pca_variance = pca_variance,
    pca_loadings = pca_loadings,
    kpi_decisions = kpi_decisions,
    recommended_metric_set = recommended_metric_set,
    retained_pc_count = retained_pc_count
  )
}
