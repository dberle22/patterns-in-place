build_phase3_model_bundle <- function(livability_model_df, livability_frame, catalog_check, config) {
  topic_metadata <- livability_frame$subjects |>
    purrr::map_dfr(\(subject) {
      purrr::map_dfr(or_empty(subject$topics), \(topic) {
        tibble::tibble(
          subject_id = subject$subject_id,
          subject_display_name = subject$display_name,
          subject_weight = subject$subject_weight,
          topic_id = topic$topic_id,
          topic_display_name = topic$display_name,
          reliability = topic$reliability,
          coverage = topic$coverage
        )
      })
    })

  selected_metric_metadata <- catalog_check |>
    dplyr::select(metric_id, subject_id, topic_id, reliability, polarity, model_role) |>
    dplyr::filter(metric_id %in% config$expected_kpis$metric_id)

  topic_weight_reference <- topic_metadata |>
    dplyr::inner_join(
      selected_metric_metadata |>
        dplyr::count(subject_id, topic_id, name = "n_selected_kpis"),
      by = c("subject_id", "topic_id")
    ) |>
    dplyr::mutate(
      reliability_factor = dplyr::case_when(
        reliability == "core" ~ 1.00,
        reliability == "supplemental_baseline" ~ 0.75,
        reliability == "coverage_caution" ~ 0.60,
        TRUE ~ 1.00
      ),
      raw_topic_weight = coverage * reliability_factor
    ) |>
    dplyr::group_by(subject_id) |>
    dplyr::mutate(topic_weight_within_subject = raw_topic_weight / sum(raw_topic_weight)) |>
    dplyr::ungroup()

  modeling_long <- livability_model_df |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      pop_total,
      dplyr::all_of(paste0("imputed_", config$expected_kpis$metric_id))
    ) |>
    tidyr::pivot_longer(
      cols = dplyr::all_of(paste0("imputed_", config$expected_kpis$metric_id)),
      names_to = "metric_column",
      values_to = "imputed_value"
    ) |>
    dplyr::mutate(metric_id = stringr::str_remove(metric_column, "^imputed_")) |>
    dplyr::select(-metric_column) |>
    dplyr::left_join(
      livability_model_df |>
        dplyr::select(cbsa_code, dplyr::all_of(paste0("scored_", config$expected_kpis$metric_id))) |>
        tidyr::pivot_longer(
          cols = dplyr::all_of(paste0("scored_", config$expected_kpis$metric_id)),
          names_to = "score_column",
          values_to = "scoring_value"
        ) |>
        dplyr::mutate(metric_id = stringr::str_remove(score_column, "^scored_")) |>
        dplyr::select(cbsa_code, metric_id, scoring_value),
      by = c("cbsa_code", "metric_id")
    ) |>
    dplyr::left_join(selected_metric_metadata, by = "metric_id") |>
    dplyr::group_by(metric_id) |>
    dplyr::mutate(
      clustering_z = safe_zscore(imputed_value),
      scoring_z = safe_zscore(scoring_value)
    ) |>
    dplyr::ungroup()

  standardization_audit <- modeling_long |>
    dplyr::group_by(metric_id, polarity, reliability, model_role) |>
    dplyr::summarise(
      clustering_mean = mean(clustering_z),
      clustering_sd = stats::sd(clustering_z),
      scoring_mean = mean(scoring_z),
      scoring_sd = stats::sd(scoring_z),
      .groups = "drop"
    ) |>
    dplyr::arrange(metric_id)

  cluster_metric_ids <- config$clustering_metric_decisions |>
    dplyr::filter(use_for_clustering) |>
    dplyr::pull(metric_id)

  cluster_input_wide <- modeling_long |>
    dplyr::filter(metric_id %in% cluster_metric_ids) |>
    dplyr::select(cbsa_code, metric_id, clustering_z) |>
    tidyr::pivot_wider(
      names_from = metric_id,
      values_from = clustering_z,
      names_prefix = "cluster_z_"
    ) |>
    dplyr::arrange(cbsa_code)

  cluster_input_matrix <- cluster_input_wide |>
    dplyr::select(-cbsa_code) |>
    as.matrix()

  row.names(cluster_input_matrix) <- cluster_input_wide$cbsa_code
  cluster_distance <- stats::dist(cluster_input_matrix)

  cluster_diagnostics <- purrr::map_dfr(config$candidate_k, \(k) {
    set.seed(20260617 + k)
    kmeans_fit <- stats::kmeans(cluster_input_matrix, centers = k, nstart = 50, iter.max = 100)
    silhouette_values <- cluster::silhouette(kmeans_fit$cluster, cluster_distance)

    tibble::tibble(
      k = k,
      avg_silhouette = mean(silhouette_values[, 3]),
      median_silhouette = stats::median(silhouette_values[, 3]),
      tot_withinss = kmeans_fit$tot.withinss,
      betweenss_ratio = kmeans_fit$betweenss / kmeans_fit$totss
    )
  })

  cluster_count_calibration <- purrr::map_dfr(config$candidate_k_extended, \(k) {
    set.seed(20270617 + k)
    kmeans_fit <- stats::kmeans(cluster_input_matrix, centers = k, nstart = 100, iter.max = 100)
    silhouette_values <- cluster::silhouette(kmeans_fit$cluster, cluster_distance)
    cluster_sizes <- as.integer(kmeans_fit$size)

    tibble::tibble(
      k = k,
      avg_silhouette = mean(silhouette_values[, 3]),
      median_silhouette = stats::median(silhouette_values[, 3]),
      tot_withinss = kmeans_fit$tot.withinss,
      betweenss_ratio = kmeans_fit$betweenss / kmeans_fit$totss,
      min_cluster_size = min(cluster_sizes),
      max_cluster_size = max(cluster_sizes),
      singleton_clusters = sum(cluster_sizes == 1),
      clusters_under_5 = sum(cluster_sizes < 5),
      clusters_under_10 = sum(cluster_sizes < 10)
    )
  })

  cluster_count_sizes <- purrr::map_dfr(config$candidate_k_extended, \(k) {
    set.seed(20270617 + k)
    kmeans_fit <- stats::kmeans(cluster_input_matrix, centers = k, nstart = 100, iter.max = 100)

    tibble::tibble(
      k = k,
      cluster = seq_along(kmeans_fit$size),
      cluster_size = as.integer(kmeans_fit$size)
    )
  })

  natural_k <- cluster_diagnostics$k[which.max(cluster_diagnostics$avg_silhouette)]

  set.seed(20270617 + 5)
  kmeans_k5 <- stats::kmeans(cluster_input_matrix, centers = 5, nstart = 100, iter.max = 100)

  set.seed(20270617 + 6)
  kmeans_k6 <- stats::kmeans(cluster_input_matrix, centers = 6, nstart = 100, iter.max = 100)

  split_summary <- tibble::tibble(
    cbsa_code = cluster_input_wide$cbsa_code,
    k5 = kmeans_k5$cluster,
    k6 = kmeans_k6$cluster
  ) |>
    dplyr::count(k5, k6, name = "metros_in_split") |>
    dplyr::arrange(k5, k6)

  k6_majority_crosswalk <- split_summary |>
    dplyr::group_by(k6) |>
    dplyr::slice_max(order_by = metros_in_split, n = 1, with_ties = FALSE) |>
    dplyr::ungroup() |>
    dplyr::select(k6, majority_k5 = k5)

  k5_to_k6_changed_metros <- tibble::tibble(
    cbsa_code = cluster_input_wide$cbsa_code,
    k5 = kmeans_k5$cluster,
    k6 = kmeans_k6$cluster
  ) |>
    dplyr::left_join(k6_majority_crosswalk, by = "k6") |>
    dplyr::mutate(changed_under_k6 = k5 != majority_k5)

  hclust_fit <- stats::hclust(cluster_distance, method = "ward.D2")

  set.seed(20260617 + config$selected_natural_k)
  kmeans_fit <- stats::kmeans(
    cluster_input_matrix,
    centers = config$selected_natural_k,
    nstart = 100,
    iter.max = 100
  )

  gmm_fit <- fit_diagonal_gmm(
    x = cluster_input_matrix,
    k = config$selected_natural_k,
    init_clusters = kmeans_fit$cluster
  )

  cluster_assignments <- tibble::tibble(
    cbsa_code = cluster_input_wide$cbsa_code,
    livability_hclust_cluster = stats::cutree(hclust_fit, k = config$selected_natural_k),
    livability_kmeans_cluster = kmeans_fit$cluster,
    livability_gmm_cluster = gmm_fit$cluster
  )

  colnames(gmm_fit$responsibilities) <- paste0("livability_prob_cluster_", seq_len(config$selected_natural_k))

  gmm_probabilities <- tibble::as_tibble(gmm_fit$responsibilities) |>
    dplyr::mutate(cbsa_code = cluster_input_wide$cbsa_code, .before = 1)

  gmm_cluster_summary <- gmm_probabilities |>
    dplyr::left_join(cluster_assignments, by = "cbsa_code") |>
    tidyr::pivot_longer(
      cols = dplyr::starts_with("livability_prob_cluster_"),
      names_to = "probability_column",
      values_to = "membership_probability"
    ) |>
    dplyr::mutate(gmm_cluster = readr::parse_number(probability_column)) |>
    dplyr::group_by(gmm_cluster) |>
    dplyr::summarise(
      avg_membership_probability = mean(membership_probability),
      max_membership_probability = max(membership_probability),
      metros_as_top_membership = sum(gmm_cluster == livability_gmm_cluster),
      .groups = "drop"
    )

  topic_scores_long <- modeling_long |>
    dplyr::group_by(cbsa_code, cbsa_name, topic_id) |>
    dplyr::summarise(topic_score = mean(scoring_z), .groups = "drop") |>
    dplyr::left_join(topic_weight_reference, by = "topic_id")

  subject_scores_long <- topic_scores_long |>
    dplyr::group_by(cbsa_code, cbsa_name, subject_id, subject_display_name, subject_weight) |>
    dplyr::summarise(
      subject_score = stats::weighted.mean(topic_score, topic_weight_within_subject),
      .groups = "drop"
    )

  frame_scores <- subject_scores_long |>
    dplyr::group_by(cbsa_code, cbsa_name) |>
    dplyr::summarise(
      livability_score = stats::weighted.mean(subject_score, subject_weight),
      .groups = "drop"
    ) |>
    dplyr::mutate(livability_percentile = dplyr::percent_rank(livability_score) * 100)

  topic_scores_wide <- topic_scores_long |>
    dplyr::select(cbsa_code, topic_id, topic_score) |>
    tidyr::pivot_wider(names_from = topic_id, values_from = topic_score, names_prefix = "topic_score_")

  subject_scores_wide <- subject_scores_long |>
    dplyr::select(cbsa_code, subject_id, subject_score) |>
    tidyr::pivot_wider(names_from = subject_id, values_from = subject_score, names_prefix = "subject_score_")

  livability_scores <- livability_model_df |>
    dplyr::left_join(cluster_assignments, by = "cbsa_code") |>
    dplyr::left_join(gmm_probabilities, by = "cbsa_code") |>
    dplyr::left_join(topic_scores_wide, by = "cbsa_code") |>
    dplyr::left_join(subject_scores_wide, by = "cbsa_code") |>
    dplyr::left_join(frame_scores, by = c("cbsa_code", "cbsa_name"))

  subject_centroids <- livability_scores |>
    dplyr::group_by(livability_kmeans_cluster) |>
    dplyr::summarise(
      metros_in_cluster = dplyr::n(),
      dplyr::across(dplyr::starts_with("subject_score_"), mean),
      livability_score = mean(livability_score),
      livability_percentile = mean(livability_percentile),
      .groups = "drop"
    )

  subject_lookup <- topic_metadata |>
    dplyr::distinct(subject_id, subject_display_name)

  cluster_labels <- subject_centroids |>
    tidyr::pivot_longer(
      cols = dplyr::starts_with("subject_score_"),
      names_to = "subject_column",
      values_to = "subject_score"
    ) |>
    dplyr::mutate(subject_id = stringr::str_remove(subject_column, "^subject_score_")) |>
    dplyr::left_join(subject_lookup, by = "subject_id") |>
    dplyr::group_by(livability_kmeans_cluster) |>
    dplyr::summarise(
      top_subject = subject_display_name[which.max(subject_score)],
      bottom_subject = subject_display_name[which.min(subject_score)],
      livability_cluster_label = paste0(
        "Type ",
        dplyr::first(livability_kmeans_cluster),
        ": ",
        top_subject,
        " strength, ",
        bottom_subject,
        " drag"
      ),
      .groups = "drop"
    )

  # K-means cluster IDs are arbitrary across reruns, so assign the published
  # Livability names from the observed cluster pattern rather than the raw
  # numeric label. This keeps the 3-metro outlier group tagged as
  # "Megametro Extremes" even if k-means renumbers it in a later run.
  megametro_cluster <- subject_centroids |>
    dplyr::slice_min(metros_in_cluster, n = 1, with_ties = FALSE) |>
    dplyr::pull(livability_kmeans_cluster)

  remaining_clusters <- subject_centroids |>
    dplyr::filter(livability_kmeans_cluster != megametro_cluster)

  strained_cluster <- remaining_clusters |>
    dplyr::slice_min(livability_score, n = 1, with_ties = FALSE) |>
    dplyr::pull(livability_kmeans_cluster)

  remaining_clusters <- remaining_clusters |>
    dplyr::filter(livability_kmeans_cluster != strained_cluster)

  high_access_cluster <- remaining_clusters |>
    dplyr::slice_max(subject_score_access_and_infrastructure, n = 1, with_ties = FALSE) |>
    dplyr::pull(livability_kmeans_cluster)

  remaining_clusters <- remaining_clusters |>
    dplyr::filter(livability_kmeans_cluster != high_access_cluster)

  knowledge_cluster <- remaining_clusters |>
    dplyr::slice_max(subject_score_health_and_safety, n = 1, with_ties = FALSE) |>
    dplyr::pull(livability_kmeans_cluster)

  remaining_clusters <- remaining_clusters |>
    dplyr::filter(livability_kmeans_cluster != knowledge_cluster)

  healthy_affordable_cluster <- remaining_clusters |>
    dplyr::slice_max(subject_score_affordability, n = 1, with_ties = FALSE) |>
    dplyr::pull(livability_kmeans_cluster)

  amenity_cluster <- remaining_clusters |>
    dplyr::filter(livability_kmeans_cluster != healthy_affordable_cluster) |>
    dplyr::pull(livability_kmeans_cluster)

  cluster_name_map <- tibble::tibble(
    livability_kmeans_cluster = c(
      healthy_affordable_cluster,
      knowledge_cluster,
      high_access_cluster,
      strained_cluster,
      amenity_cluster,
      megametro_cluster
    ),
    livability_cluster_name = c(
      "Healthy Affordable Havens",
      "Knowledge And Care Hubs",
      "High-Access Prosperous Hubs",
      "Strained Interior Markets",
      "Amenity Growth Markets",
      "Megametro Extremes"
    ),
    cluster_interpretation = c(
      "Strong affordability, health, and environmental fundamentals with more modest access intensity.",
      "Knowledge-heavy and college-adjacent metros with strong health scores and solid overall livability.",
      "Highly connected, high-performing hubs with strong health outcomes and somewhat thinner affordability.",
      "Interior and legacy markets with weaker health outcomes and lower overall livability.",
      "Fast-growing lifestyle and Sunbelt-adjacent markets with middling access and affordability pressure.",
      "Very large, unusual metros where extreme access coexists with major affordability and environmental strain."
    )
  )

  livability_scores <- livability_scores |>
    dplyr::left_join(cluster_labels, by = "livability_kmeans_cluster") |>
    dplyr::left_join(cluster_name_map, by = "livability_kmeans_cluster")

  k5_to_k6_changed_metros <- k5_to_k6_changed_metros |>
    dplyr::left_join(
      livability_scores |>
        dplyr::select(cbsa_code, cbsa_name, livability_score, livability_percentile),
      by = "cbsa_code"
    ) |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      livability_score,
      livability_percentile,
      k5,
      k6,
      majority_k5,
      changed_under_k6
    ) |>
    dplyr::arrange(dplyr::desc(changed_under_k6), k5, k6, cbsa_name)

  cluster_centroids_output <- subject_centroids |>
    dplyr::left_join(cluster_labels, by = "livability_kmeans_cluster") |>
    dplyr::left_join(cluster_name_map, by = "livability_kmeans_cluster")

  cluster_representatives <- livability_scores |>
    dplyr::group_by(livability_kmeans_cluster, livability_cluster_name) |>
    dplyr::arrange(desc(livability_percentile), .by_group = TRUE) |>
    dplyr::slice_head(n = 8) |>
    dplyr::ungroup() |>
    dplyr::select(livability_kmeans_cluster, livability_cluster_name, cbsa_name, livability_percentile)

  gmm_hybrids <- livability_scores |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      livability_cluster_name,
      livability_gmm_cluster,
      dplyr::starts_with("livability_prob_cluster_")
    ) |>
    tidyr::pivot_longer(
      cols = dplyr::starts_with("livability_prob_cluster_"),
      names_to = "probability_column",
      values_to = "membership_probability"
    ) |>
    dplyr::mutate(gmm_cluster = readr::parse_number(probability_column)) |>
    dplyr::arrange(cbsa_code, desc(membership_probability)) |>
    dplyr::group_by(cbsa_code, cbsa_name, livability_cluster_name, livability_gmm_cluster) |>
    dplyr::mutate(probability_rank = dplyr::row_number()) |>
    dplyr::filter(probability_rank <= 2) |>
    dplyr::summarise(
      top_gmm_cluster = dplyr::first(gmm_cluster),
      top_gmm_probability = dplyr::first(membership_probability),
      second_gmm_cluster = dplyr::nth(gmm_cluster, 2),
      second_gmm_probability = dplyr::nth(membership_probability, 2),
      membership_gap = top_gmm_probability - second_gmm_probability,
      .groups = "drop"
    ) |>
    dplyr::arrange(membership_gap)

  cosine_input <- cluster_input_matrix
  row_norms <- sqrt(rowSums(cosine_input ^ 2))
  row_norms[row_norms == 0] <- 1
  cosine_normalized <- cosine_input / row_norms
  cosine_similarity <- cosine_normalized %*% t(cosine_normalized)

  similarity_top10 <- purrr::map_dfr(seq_len(nrow(cosine_similarity)), \(i) {
    similarity_values <- cosine_similarity[i, ]
    ranking <- order(similarity_values, decreasing = TRUE)
    ranking <- ranking[ranking != i][1:10]

    tibble::tibble(
      cbsa_code = row.names(cosine_similarity)[i],
      peer_rank = seq_along(ranking),
      peer_cbsa_code = row.names(cosine_similarity)[ranking],
      cosine_similarity = similarity_values[ranking]
    )
  }) |>
    dplyr::left_join(
      livability_scores |>
        dplyr::select(cbsa_code, cbsa_name),
      by = "cbsa_code"
    ) |>
    dplyr::left_join(
      livability_scores |>
        dplyr::select(peer_cbsa_code = cbsa_code, peer_cbsa_name = cbsa_name),
      by = "peer_cbsa_code"
    ) |>
    dplyr::select(cbsa_code, cbsa_name, peer_rank, peer_cbsa_code, peer_cbsa_name, cosine_similarity)

  list(
    topic_metadata = topic_metadata,
    selected_metric_metadata = selected_metric_metadata,
    topic_weight_reference = topic_weight_reference,
    modeling_long = modeling_long,
    standardization_audit = standardization_audit,
    cluster_input_wide = cluster_input_wide,
    cluster_input_matrix = cluster_input_matrix,
    cluster_diagnostics = cluster_diagnostics,
    cluster_count_calibration = cluster_count_calibration,
    cluster_count_sizes = cluster_count_sizes,
    natural_k = natural_k,
    cluster_name_map = cluster_name_map,
    k5_to_k6_changed_metros = k5_to_k6_changed_metros,
    k5_to_k6_split_summary = split_summary,
    cluster_assignments = cluster_assignments,
    gmm_probabilities = gmm_probabilities,
    gmm_cluster_summary = gmm_cluster_summary,
    livability_scores = livability_scores,
    cluster_centroids_output = cluster_centroids_output,
    cluster_representatives = cluster_representatives,
    gmm_hybrids = gmm_hybrids,
    similarity_top10 = similarity_top10
  )
}
