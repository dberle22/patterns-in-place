# Prepare correlation heatmap data.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

correlation_metric_order <- function(corr, method = "clustered") {
  labels <- colnames(corr)
  if (length(labels) <= 2 || identical(method, "input")) {
    return(labels)
  }
  if (identical(method, "alphabetical")) {
    return(sort(labels))
  }

  dist_mat <- stats::as.dist(1 - abs(corr))
  labels[stats::hclust(dist_mat, method = "complete")$order]
}

prep_correlation_heatmap <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      method = "spearman",
      missingness = "pairwise.complete.obs",
      order_method = "clustered",
      weak_threshold = NULL,
      facet_by = NULL,
      include_flag_column = "include_flag"
    ),
    config
  )
  validate_correlation_heatmap_contract(
    data,
    require_single_geo_level = is.null(cfg$facet_by),
    require_single_time_window = is.null(cfg$facet_by)
  )
  out <- prepare_long_metric_frame(
    data,
    required = visual_contracts$correlation_heatmap$required_fields,
    value_columns = "metric_value",
    chart_type = "correlation_heatmap",
    config = cfg
  )

  include_col <- cfg$include_flag_column %||% "include_flag"
  if (include_col %in% names(out)) {
    keep <- is.na(out[[include_col]]) | coerce_logical_column(out[[include_col]])
    out <- out[keep, , drop = FALSE]
  }

  split_var <- cfg$facet_by
  split_keys <- if (!is.null(split_var) && split_var %in% names(out)) unique(out[[split_var]]) else NA_character_
  split_keys <- split_keys[!is.na(split_keys)]
  if (length(split_keys) == 0) {
    split_keys <- NA_character_
  }

  pieces <- lapply(split_keys, function(split_key) {
    subset_df <- out
    if (!is.na(split_key) && !is.null(split_var) && split_var %in% names(out)) {
      subset_df <- subset_df[subset_df[[split_var]] == split_key, , drop = FALSE]
    }

    wide <- stats::reshape(
      subset_df[, c("geo_id", "metric_label", "metric_value")],
      idvar = "geo_id",
      timevar = "metric_label",
      direction = "wide"
    )
    rownames(wide) <- wide$geo_id
    wide$geo_id <- NULL
    metric_matrix <- as.matrix(wide)
    colnames(metric_matrix) <- sub("^metric_value\\.", "", colnames(metric_matrix))

    corr <- stats::cor(metric_matrix, use = cfg$missingness, method = cfg$method)
    metric_order <- correlation_metric_order(corr, method = cfg$order_method)
    corr_df <- expand.grid(
      metric_x = colnames(corr),
      metric_y = rownames(corr),
      stringsAsFactors = FALSE
    )
    corr_df$correlation <- as.vector(corr)
    corr_df$correlation_display <- corr_df$correlation
    if (!is.null(cfg$weak_threshold) && is.finite(cfg$weak_threshold) && cfg$weak_threshold > 0) {
      off_diag <- corr_df$metric_x != corr_df$metric_y
      corr_df$correlation_display[off_diag & abs(corr_df$correlation) < cfg$weak_threshold] <- NA_real_
    }

    corr_df$metric_x <- factor(corr_df$metric_x, levels = metric_order)
    corr_df$metric_y <- factor(corr_df$metric_y, levels = rev(metric_order))
    corr_df$abs_correlation <- abs(corr_df$correlation)
    corr_df$source <- extract_chart_metadata(subset_df, "source")
    corr_df$vintage <- extract_chart_metadata(subset_df, "vintage")
    corr_df$geo_level <- extract_chart_metadata(subset_df, "geo_level")
    corr_df$time_window <- extract_chart_metadata(subset_df, "time_window")
    corr_df$question_id <- extract_chart_metadata(subset_df, "question_id")
    corr_df$missingness_policy <- cfg$missingness
    corr_df$order_method <- cfg$order_method
    corr_df$method <- cfg$method
    corr_df$label <- sprintf("%.2f", corr_df$correlation)
    if (!is.null(split_var) && split_var %in% names(subset_df)) {
      corr_df[[split_var]] <- split_key
    }
    corr_df
  })

  out_df <- do.call(rbind, pieces)
  rownames(out_df) <- NULL
  attr(out_df, "chart_config") <- resolve_chart_config("correlation_heatmap", cfg)
  out_df
}
