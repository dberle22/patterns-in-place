`%fallback%` <- function(x, y) {
  if (is.null(x)) y else x
}

safe_zscore <- function(x) {
  mean_x <- mean(x, na.rm = TRUE)
  sd_x <- stats::sd(x, na.rm = TRUE)

  if (is.na(sd_x) || sd_x == 0) {
    return(rep(0, length(x)))
  }

  (x - mean_x) / sd_x
}

flatten_cutree <- function(hclust_fit, k) {
  cutree_output <- stats::cutree(hclust_fit, k = k)

  if (is.matrix(cutree_output)) {
    return(as.integer(cutree_output[, 1]))
  }

  as.integer(cutree_output)
}

phase7_percent_rank <- function(x) {
  dplyr::percent_rank(x) * 100
}

phase7_slugify_zone_type <- function(x) {
  x |>
    stringr::str_to_lower() |>
    stringr::str_replace_all("[^a-z0-9]+", "_") |>
    stringr::str_replace_all("^_+|_+$", "")
}

fit_diagonal_gmm <- function(x, k, init_clusters, max_iter = 200, tol = 1e-6, min_variance = 1e-4) {
  n <- nrow(x)
  p <- ncol(x)
  z <- matrix(0, nrow = n, ncol = k)
  z[cbind(seq_len(n), init_clusters)] <- 1

  update_parameters <- function(z_matrix) {
    nk <- colSums(z_matrix)
    pi_k <- nk / n
    means <- matrix(0, nrow = k, ncol = p)
    vars <- matrix(min_variance, nrow = k, ncol = p)

    for (j in seq_len(k)) {
      weights <- z_matrix[, j]
      means[j, ] <- colSums(x * weights) / nk[j]
      centered <- sweep(x, 2, means[j, ], "-")
      vars[j, ] <- pmax(colSums((centered ^ 2) * weights) / nk[j], min_variance)
    }

    list(pi = pi_k, means = means, vars = vars)
  }

  log_sum_exp <- function(log_mat) {
    row_max <- apply(log_mat, 1, max)
    row_max + log(rowSums(exp(log_mat - row_max)))
  }

  params <- update_parameters(z)
  prev_loglik <- -Inf

  for (iter in seq_len(max_iter)) {
    log_resp <- matrix(0, nrow = n, ncol = k)

    for (j in seq_len(k)) {
      centered <- sweep(x, 2, params$means[j, ], "-")
      quad_term <- rowSums((centered ^ 2) / params$vars[j, ])
      log_det <- sum(log(params$vars[j, ]))
      log_resp[, j] <- log(params$pi[j]) - 0.5 * (p * log(2 * pi) + log_det + quad_term)
    }

    row_loglik <- log_sum_exp(log_resp)
    loglik <- sum(row_loglik)
    z <- exp(log_resp - row_loglik)
    params <- update_parameters(z)

    if (abs(loglik - prev_loglik) < tol) {
      break
    }

    prev_loglik <- loglik
  }

  list(
    pi = params$pi,
    means = params$means,
    vars = params$vars,
    responsibilities = z,
    cluster = max.col(z, ties.method = "first"),
    loglik = prev_loglik,
    iterations = iter
  )
}

phase7_cluster_distance_to_center <- function(cluster_input_matrix, assignments, centers) {
  purrr::map_dbl(seq_len(nrow(cluster_input_matrix)), \(i) {
    center_row <- centers[assignments[i], , drop = TRUE]
    sqrt(sum((cluster_input_matrix[i, ] - center_row) ^ 2))
  })
}

build_phase7_draft_label_scores <- function(subject_centroids) {
  subject_centroids |>
    dplyr::mutate(
      label_score_knowledge_corridor =
        subject_score_character * 0.20 +
        subject_score_livability * 0.15 +
        subject_score_opportunity * 0.30 +
        pct_ba_plus * 0.30 +
        jobs_per_resident * 0.20 +
        pct_jobs_professional_services * 0.20 +
        pop_weighted_density_sqmi * 0.15 +
        walkability_index * 0.10 -
        pov_rate * 0.10,
      label_score_established_residential =
        owner_occ_rate * 0.30 +
        pct_same_house * 0.25 +
        pct_age_over_64 * 0.20 +
        vacancy_rate * -0.10 +
        jobs_per_resident * -0.15 +
        pop_weighted_density_sqmi * -0.10,
      label_score_emerging_transitional =
        pct_ba_plus_change_3yr * 0.30 +
        pct_ba_plus * 0.15 +
        pct_commute_walk * 0.10 +
        pop_weighted_density_sqmi * 0.10 +
        pct_same_house * -0.15 +
        pov_rate * -0.10 +
        pct_rent_burden_30plus * -0.05,
      label_score_affordable_working_class =
        jobs_per_resident * 0.15 +
        pct_jobs_high_wage * -0.10 +
        pct_jobs_professional_services * -0.10 +
        owner_occ_rate * 0.10 +
        pct_ba_plus * -0.10 +
        pov_rate * 0.05 +
        pct_rent_burden_30plus * -0.05 +
        vacancy_rate * -0.10,
      label_score_distressed =
        pov_rate * 0.35 +
        pct_unemployment_rate * 0.25 +
        vacancy_rate * 0.20 +
        pct_rent_burden_30plus * 0.15 +
        pct_no_internet_access * 0.10 -
        pct_ba_plus * 0.15 -
        jobs_per_resident * 0.10,
      label_score_growth_periphery =
        pct_ba_plus_change_3yr * 0.20 +
        subject_score_opportunity * 0.15 +
        owner_occ_rate * 0.10 +
        pct_rent_burden_30plus * -0.10 +
        pop_weighted_density_sqmi * -0.20 +
        jobs_per_resident * -0.10 +
        pct_age_over_64 * -0.10,
      label_score_jobs_center_commercial_core =
        jobs_per_resident * 0.45 +
        pct_jobs_professional_services * 0.15 +
        pop_weighted_density_sqmi * 0.15 +
        owner_occ_rate * -0.20 +
        pct_same_house * -0.15,
      label_score_environmental_risk_zone =
        ejs_pm25 * 0.40 +
        fema_risk_score * 0.40 +
        subject_score_livability * -0.10 +
        pov_rate * 0.10
    )
}

build_phase7_provisional_label_map <- function(subject_centroids, config) {
  label_score_lookup <- tibble::tribble(
    ~draft_zone_type, ~score_column,
    "Knowledge Corridor", "label_score_knowledge_corridor",
    "Established Residential", "label_score_established_residential",
    "Emerging Knowledge Districts", "label_score_emerging_transitional",
    "Working Neighborhoods", "label_score_affordable_working_class",
    "Entry-Market Neighborhoods", "label_score_growth_periphery",
    "Commercial Core / Jobs Center", "label_score_jobs_center_commercial_core",
    "Mixed-Income Middle Neighborhoods", "label_score_environmental_risk_zone"
  )

  scoring_frame <- build_phase7_draft_label_scores(subject_centroids) |>
    dplyr::select(zone_kmeans_cluster, dplyr::starts_with("label_score_")) |>
    tidyr::pivot_longer(
      cols = dplyr::starts_with("label_score_"),
      names_to = "score_column",
      values_to = "label_score"
    ) |>
    dplyr::left_join(label_score_lookup, by = "score_column") |>
    dplyr::arrange(dplyr::desc(label_score))

  assigned_clusters <- integer()
  assigned_labels <- character()
  assignments <- vector("list", length = 0)

  for (row_id in seq_len(nrow(scoring_frame))) {
    candidate <- scoring_frame[row_id, ]

    if (candidate$zone_kmeans_cluster %in% assigned_clusters) {
      next
    }

    if (candidate$draft_zone_type %in% assigned_labels) {
      next
    }

    assignments[[length(assignments) + 1]] <- tibble::tibble(
      zone_kmeans_cluster = candidate$zone_kmeans_cluster,
      provisional_zone_type = candidate$draft_zone_type,
      label_score = candidate$label_score
    )
    assigned_clusters <- c(assigned_clusters, candidate$zone_kmeans_cluster)
    assigned_labels <- c(assigned_labels, candidate$draft_zone_type)
  }

  assigned_map <- dplyr::bind_rows(assignments)

  remaining_clusters <- subject_centroids |>
    dplyr::anti_join(assigned_map, by = "zone_kmeans_cluster") |>
    dplyr::arrange(zone_kmeans_cluster) |>
    dplyr::mutate(
      provisional_zone_type = paste("Unassigned Hybrid", dplyr::row_number()),
      label_score = NA_real_
    ) |>
    dplyr::select(zone_kmeans_cluster, provisional_zone_type, label_score)

  dplyr::bind_rows(assigned_map, remaining_clusters) |>
    dplyr::mutate(
      zone_type_name_status = dplyr::if_else(
        provisional_zone_type %in% config$draft_zone_labels,
        "draft_label_pending_review",
        "fallback_label_pending_review"
      )
    ) |>
    dplyr::arrange(zone_kmeans_cluster)
}
