`%fallback%` <- function(x, y) {
  if (is.null(x)) y else x
}

or_empty <- function(x) {
  if (is.null(x)) list() else x
}

safe_zscore <- function(x) {
  mean_x <- mean(x, na.rm = TRUE)
  sd_x <- stats::sd(x, na.rm = TRUE)

  if (is.na(sd_x) || sd_x == 0) {
    return(rep(0, length(x)))
  }

  (x - mean_x) / sd_x
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
