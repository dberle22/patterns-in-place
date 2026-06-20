build_phase2_hypothesis_bundle <- function(character_scores, model, con, config) {
  size_dominance_test <- character_scores |>
    dplyr::transmute(
      cbsa_code,
      cbsa_name,
      character_cluster_name,
      pop_total,
      log_pop_total = log(pop_total),
      diversity_index = imputed_diversity_index,
      pop_weighted_density_sqmi = imputed_pop_weighted_density_sqmi,
      character_score,
      character_percentile
    )

  size_dominance_lm <- stats::lm(
    character_score ~ log_pop_total + pop_weighted_density_sqmi,
    data = size_dominance_test
  )

  size_cluster_lm <- stats::lm(
    log_pop_total ~ as.factor(character_cluster_name),
    data = size_dominance_test
  )

  size_dominance_summary <- tibble::tibble(
    raw_correlation_log_pop = cor(size_dominance_test$log_pop_total, size_dominance_test$character_score),
    raw_correlation_density = cor(size_dominance_test$pop_weighted_density_sqmi, size_dominance_test$character_score),
    density_adjusted_log_pop_beta = unname(stats::coef(size_dominance_lm)[["log_pop_total"]]),
    density_adjusted_log_pop_p_value = summary(size_dominance_lm)$coefficients["log_pop_total", "Pr(>|t|)"],
    size_only_cluster_r_squared = summary(size_cluster_lm)$r.squared
  )

  size_dominance_outliers <- size_dominance_test |>
    dplyr::mutate(
      fitted_character_score = stats::predict(size_dominance_lm),
      size_adjusted_residual = character_score - fitted_character_score,
      abs_size_adjusted_residual = abs(size_adjusted_residual)
    ) |>
    dplyr::arrange(dplyr::desc(abs_size_adjusted_residual)) |>
    dplyr::slice_head(n = 20)

  economic_connectedness <- DBI::dbGetQuery(
    con,
    "
    select
      geo_id as cbsa_code,
      cast(economic_connectedness as double) as economic_connectedness
    from gold.social_fabric_wide
    where geo_level = 'cbsa'
    "
  ) |>
    tibble::as_tibble()

  connectedness_input <- model$cluster_input_wide |>
    dplyr::left_join(economic_connectedness, by = "cbsa_code") |>
    dplyr::mutate(
      economic_connectedness = dplyr::coalesce(
        economic_connectedness,
        stats::median(economic_connectedness, na.rm = TRUE)
      ),
      cluster_z_economic_connectedness = safe_zscore(economic_connectedness)
    )

  connectedness_matrix <- connectedness_input |>
    dplyr::select(-cbsa_code, -economic_connectedness) |>
    as.matrix()

  row.names(connectedness_matrix) <- connectedness_input$cbsa_code

  set.seed(20270618 + config$final_k + ncol(connectedness_matrix))
  connectedness_fit <- stats::kmeans(
    connectedness_matrix,
    centers = config$final_k,
    nstart = 100,
    iter.max = 100
  )

  connectedness_comparison <- tibble::tibble(
    cbsa_code = connectedness_input$cbsa_code,
    connectedness_augmented_cluster = connectedness_fit$cluster
  ) |>
    dplyr::left_join(
      character_scores |>
        dplyr::select(cbsa_code, cbsa_name, character_kmeans_cluster, character_cluster_name),
      by = "cbsa_code"
    )

  crosswalk <- connectedness_comparison |>
    dplyr::count(connectedness_augmented_cluster, character_kmeans_cluster, name = "metros_in_overlap") |>
    dplyr::group_by(connectedness_augmented_cluster) |>
    dplyr::slice_max(order_by = metros_in_overlap, n = 1, with_ties = FALSE) |>
    dplyr::ungroup() |>
    dplyr::rename(majority_character_cluster = character_kmeans_cluster)

  cluster_shift_test <- connectedness_comparison |>
    dplyr::left_join(crosswalk, by = "connectedness_augmented_cluster") |>
    dplyr::mutate(changed_under_connectedness = character_kmeans_cluster != majority_character_cluster)

  cluster_shift_summary <- tibble::tibble(
    sample_size = nrow(cluster_shift_test),
    metros_changed = sum(cluster_shift_test$changed_under_connectedness),
    share_changed = mean(cluster_shift_test$changed_under_connectedness),
    raw_correlation_connectedness_character_score = cor(
      connectedness_input$economic_connectedness,
      character_scores$character_score[match(connectedness_input$cbsa_code, character_scores$cbsa_code)]
    )
  )

  cluster_shift_outliers <- cluster_shift_test |>
    dplyr::filter(changed_under_connectedness) |>
    dplyr::arrange(cbsa_name) |>
    dplyr::slice_head(n = 30)

  list(
    size_dominance_test = size_dominance_test,
    size_dominance_summary = size_dominance_summary,
    size_dominance_outliers = size_dominance_outliers,
    cluster_shift_test = cluster_shift_test,
    cluster_shift_summary = cluster_shift_summary,
    cluster_shift_outliers = cluster_shift_outliers
  )
}
