build_phase4_redundancy_bundle <- function(opportunity_model_df, catalog_check, config) {
  full_metric_ids <- config$expected_kpis |>
    dplyr::filter(audit_bucket != "proxy_audit_only") |>
    dplyr::pull(metric_id)

  reduced_metric_ids <- config$clustering_metric_decisions |>
    dplyr::filter(use_for_clustering) |>
    dplyr::pull(metric_id)

  metric_metadata <- catalog_check |>
    dplyr::select(metric_id, subject_id, topic_id)

  modeling_wide <- opportunity_model_df |>
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

  pca_loadings <- tibble::as_tibble(pca_fit$rotation[, seq_len(min(10, ncol(pca_fit$rotation))), drop = FALSE], rownames = "metric_id") |>
    dplyr::left_join(metric_metadata, by = "metric_id")

  full_metric_set <- tibble::tibble(
    metric_set = "full_kpi_set",
    metric_id = full_metric_ids
  )

  pca_recommended_metric_set <- tibble::tibble(
    metric_set = "pca_recommended_set",
    metric_id = reduced_metric_ids
  )

  compare_metric_sets <- list(
    full_kpi_set = full_matrix,
    reduced_kpi_set = reduced_matrix
  )

  comparison_k <- 3:6

  hclust_vs_kmeans_summary <- purrr::imap_dfr(compare_metric_sets, \(metric_matrix, metric_set_name) {
    metric_distance <- stats::dist(metric_matrix)
    hclust_fit <- stats::hclust(metric_distance, method = "ward.D2")

    purrr::map_dfr(comparison_k, \(k) {
      h_clusters <- stats::cutree(hclust_fit, k = k)
      h_sizes <- as.integer(table(h_clusters))
      h_silhouette <- cluster::silhouette(h_clusters, metric_distance)

      set.seed(20270618 + k + ncol(metric_matrix))
      kmeans_fit <- stats::kmeans(metric_matrix, centers = k, nstart = 100, iter.max = 100)
      k_sizes <- as.integer(kmeans_fit$size)
      k_silhouette <- cluster::silhouette(kmeans_fit$cluster, metric_distance)

      tibble::tibble(
        metric_set = metric_set_name,
        metric_count = ncol(metric_matrix),
        k = k,
        hierarchical_avg_silhouette = mean(h_silhouette[, 3]),
        kmeans_avg_silhouette = mean(k_silhouette[, 3]),
        hierarchical_min_cluster = min(h_sizes),
        hierarchical_max_cluster = max(h_sizes),
        kmeans_min_cluster = min(k_sizes),
        kmeans_max_cluster = max(k_sizes),
        hierarchical_clusters_under_10 = sum(h_sizes < 10),
        kmeans_clusters_under_10 = sum(k_sizes < 10)
      )
    })
  })

  hclust_vs_kmeans_sizes <- purrr::imap_dfr(compare_metric_sets, \(metric_matrix, metric_set_name) {
    metric_distance <- stats::dist(metric_matrix)
    hclust_fit <- stats::hclust(metric_distance, method = "ward.D2")

    purrr::map_dfr(comparison_k, \(k) {
      h_clusters <- stats::cutree(hclust_fit, k = k)
      h_sizes <- tibble::tibble(
        metric_set = metric_set_name,
        method = "hierarchical",
        k = k,
        cluster = seq_along(table(h_clusters)),
        cluster_size = as.integer(table(h_clusters))
      )

      set.seed(20270618 + k + ncol(metric_matrix))
      kmeans_fit <- stats::kmeans(metric_matrix, centers = k, nstart = 100, iter.max = 100)
      k_sizes <- tibble::tibble(
        metric_set = metric_set_name,
        method = "kmeans",
        k = k,
        cluster = seq_along(kmeans_fit$size),
        cluster_size = as.integer(kmeans_fit$size)
      )

      dplyr::bind_rows(h_sizes, k_sizes)
    })
  })

  hclust_vs_kmeans_membership <- purrr::imap_dfr(compare_metric_sets, \(metric_matrix, metric_set_name) {
    metric_distance <- stats::dist(metric_matrix)
    hclust_fit <- stats::hclust(metric_distance, method = "ward.D2")

    purrr::map_dfr(comparison_k, \(k) {
      set.seed(20270618 + k + ncol(metric_matrix))
      kmeans_fit <- stats::kmeans(metric_matrix, centers = k, nstart = 100, iter.max = 100)

      tibble::tibble(
        metric_set = metric_set_name,
        cbsa_code = as.character(row.names(metric_matrix)),
        k = k,
        hierarchical_cluster = as.integer(stats::cutree(hclust_fit, k = k)[, 1]),
        kmeans_cluster = kmeans_fit$cluster
      )
    })
  }) |>
    dplyr::left_join(
      modeling_wide |>
        dplyr::select(cbsa_code, cbsa_name),
      by = "cbsa_code"
    )

  list(
    full_metric_set = full_metric_set,
    pca_recommended_metric_set = pca_recommended_metric_set,
    redundant_pairs = redundant_pairs,
    pca_variance = pca_variance,
    pca_loadings = pca_loadings,
    hclust_vs_kmeans_summary = hclust_vs_kmeans_summary,
    hclust_vs_kmeans_sizes = hclust_vs_kmeans_sizes,
    hclust_vs_kmeans_membership = hclust_vs_kmeans_membership
  )
}
