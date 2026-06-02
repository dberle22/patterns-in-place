# Prepare ranked bar chart datasets for rendering.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

prep_bar <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      time_window = NULL,
      metric_id = NULL,
      top_n = NULL,
      bottom_n = NULL,
      sort_desc = TRUE,
      sort_by = "metric_value",
      preserve_existing_rank = TRUE,
      include_geo_ids = NULL,
      include_highlighted = FALSE,
      drop_na_metric = TRUE,
      variant = "ranked_horizontal"
    ),
    config
  )

  validate_bar_contract(data)
  out <- prepare_long_metric_frame(
    data = data,
    required = visual_contracts$bar$required_fields,
    value_columns = c("metric_value", "benchmark_value", "share_value", "rank"),
    chart_type = "bar",
    config = cfg
  )

  if (!is.null(cfg$question_id) && "question_id" %in% names(out)) {
    out <- out[out$question_id == cfg$question_id, , drop = FALSE]
  }
  if (!is.null(cfg$time_window) && "time_window" %in% names(out)) {
    out <- out[out$time_window == cfg$time_window, , drop = FALSE]
  }
  if (!is.null(cfg$metric_id)) {
    out <- out[out$metric_id == cfg$metric_id, , drop = FALSE]
  }
  if (isTRUE(cfg$drop_na_metric)) {
    out <- out[is.finite(out$metric_value), , drop = FALSE]
  }
  if (nrow(out) == 0) {
    stop("No rows left after bar prep filtering; adjust config.")
  }

  if ("highlight_flag" %in% names(out)) {
    out$highlight_flag <- coerce_logical_column(out$highlight_flag)
  } else {
    out$highlight_flag <- FALSE
  }

  if ("note" %in% names(out)) {
    out$note <- as.character(out$note)
  }

  out$plot_value <- out$metric_value
  out$sort_value <- out$metric_value
  if (identical(cfg$sort_by, "abs_metric_value")) {
    out$sort_value <- abs(out$metric_value)
  } else if (identical(cfg$sort_by, "benchmark_delta") && "benchmark_value" %in% names(out)) {
    out$sort_value <- abs(out$metric_value - out$benchmark_value)
  }

  out <- out[order(out$sort_value, decreasing = isTRUE(cfg$sort_desc), out$geo_name), , drop = FALSE]

  if (isTRUE(cfg$preserve_existing_rank) && "rank" %in% names(out)) {
    out$overall_rank <- suppressWarnings(as.numeric(out$rank))
  } else {
    out$overall_rank <- NA_real_
  }

  if (!is.null(cfg$top_n) && !is.null(cfg$bottom_n)) {
    stop("Use only one of top_n or bottom_n in prep_bar().")
  }

  pre_trim_n <- nrow(out)

  if (!is.null(cfg$top_n) || !is.null(cfg$bottom_n)) {
    trimmed <- if (!is.null(cfg$top_n)) {
      utils::head(out, cfg$top_n)
    } else {
      utils::tail(out, cfg$bottom_n)
    }

    if (!is.null(cfg$include_geo_ids)) {
      keep_extra <- out$geo_id %in% cfg$include_geo_ids
      extras <- out[keep_extra & !(out$geo_id %in% trimmed$geo_id), , drop = FALSE]
      if (nrow(extras) > 0) {
        trimmed <- rbind(trimmed, extras)
      }
    }

    if (isTRUE(cfg$include_highlighted) && "highlight_flag" %in% names(out)) {
      extras <- out[out$highlight_flag %in% TRUE & !(out$geo_id %in% trimmed$geo_id), , drop = FALSE]
      if (nrow(extras) > 0) {
        trimmed <- rbind(trimmed, extras)
      }
    }

    trimmed <- trimmed[order(trimmed$sort_value, decreasing = isTRUE(cfg$sort_desc), trimmed$geo_name), , drop = FALSE]
    out <- trimmed
  }

  out$display_order <- seq_len(nrow(out))
  out$display_rank <- seq_len(nrow(out))

  if (all(!is.finite(out$overall_rank))) {
    rank_input <- if (isTRUE(cfg$sort_desc)) -out$sort_value else out$sort_value
    out$overall_rank <- rank(rank_input, ties.method = "first")
  }

  out$rank <- out$overall_rank
  out$truncated_flag <- FALSE
  if (!is.null(cfg$top_n) || !is.null(cfg$bottom_n)) {
    out$truncated_flag <- nrow(out) < pre_trim_n
  }

  out
}
