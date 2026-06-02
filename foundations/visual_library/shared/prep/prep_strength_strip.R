# Prepare strength strip data.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

strength_direction_flag <- function(direction) {
  direction <- tolower(as.character(direction %||% "higher_is_better"))
  !(direction %in% c("lower_is_better", "lower-better", "lower"))
}

normalize_benchmark_value <- function(values, benchmark_value, higher_is_better = TRUE) {
  if (!is.finite(benchmark_value)) {
    return(NA_real_)
  }

  combined <- c(values, benchmark_value)
  pct <- compute_percentile(combined, higher_is_better = higher_is_better)
  pct[[length(pct)]]
}

prep_strength_strip <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      time_window = NULL,
      metric_ids = NULL,
      normalize = TRUE,
      keep_missing_metrics = TRUE,
      metric_order = NULL,
      geo_order = NULL
    ),
    config
  )

  validate_strength_strip_contract(data)
  out <- prepare_long_metric_frame(
    data,
    required = visual_contracts$strength_strip$required_fields,
    value_columns = c("metric_value", "normalized_value", "benchmark_value", "benchmark_normalized_value", "metric_order"),
    chart_type = "strength_strip",
    config = cfg
  )

  if (!is.null(cfg$question_id) && "question_id" %in% names(out)) {
    out <- out[out$question_id == cfg$question_id, , drop = FALSE]
  }
  if (!is.null(cfg$time_window) && "time_window" %in% names(out)) {
    out <- out[out$time_window %in% cfg$time_window, , drop = FALSE]
  }
  if (!is.null(cfg$metric_ids)) {
    out <- out[out$metric_id %in% cfg$metric_ids, , drop = FALSE]
  }
  if (nrow(out) == 0) {
    stop("No rows left after strength strip prep filtering; adjust config.")
  }

  out$metric_label <- as.character(out$metric_label)
  out$geo_name <- as.character(out$geo_name)
  out$time_window <- as.character(out$time_window)
  out$metric_group <- if ("metric_group" %in% names(out)) as.character(out$metric_group) else NA_character_
  out$direction <- if ("direction" %in% names(out)) as.character(out$direction) else "higher_is_better"
  out$highlight_flag <- if ("highlight_flag" %in% names(out)) coerce_logical_column(out$highlight_flag) else FALSE
  out$benchmark_label <- if ("benchmark_label" %in% names(out)) as.character(out$benchmark_label) else NA_character_
  out$note <- if ("note" %in% names(out)) as.character(out$note) else NA_character_

  metric_sequence <- unique(out$metric_id)
  if (!is.null(cfg$metric_order)) {
    metric_sequence <- unique(c(cfg$metric_order, metric_sequence))
  }

  if ("metric_order" %in% names(out) && any(is.finite(out$metric_order))) {
    metric_rank <- stats::setNames(out$metric_order, out$metric_id)
    metric_sequence <- names(sort(metric_rank[metric_sequence], na.last = TRUE))
  }

  if (!is.null(cfg$geo_order)) {
    geo_sequence <- unique(c(cfg$geo_order, out$geo_name))
  } else {
    highlight_names <- unique(out$geo_name[out$highlight_flag %in% TRUE])
    geo_sequence <- unique(c(highlight_names, sort(unique(out$geo_name))))
  }
  out$geo_name <- factor(out$geo_name, levels = geo_sequence)

  group_vars <- interaction(out$metric_id, out$time_window, drop = TRUE, lex.order = TRUE)

  if (!"normalized_value" %in% names(out)) {
    out$normalized_value <- NA_real_
  }
  if (!"benchmark_value" %in% names(out)) {
    out$benchmark_value <- NA_real_
  }
  if (!"benchmark_normalized_value" %in% names(out)) {
    out$benchmark_normalized_value <- NA_real_
  }

  split_idx <- split(seq_len(nrow(out)), group_vars)
  for (idx in split_idx) {
    metric_values <- out$metric_value[idx]
    direction_values <- stats::na.omit(out$direction[idx])
    direction_value <- if (length(direction_values) > 0) direction_values[[1]] else "higher_is_better"
    higher_is_better <- strength_direction_flag(direction_value)

    if (isTRUE(cfg$normalize) || all(is.na(out$normalized_value[idx]))) {
      out$normalized_value[idx] <- compute_percentile(metric_values, higher_is_better = higher_is_better)
    } else if (!isTRUE(higher_is_better)) {
      out$normalized_value[idx] <- 100 - out$normalized_value[idx]
    }

    benchmark_values <- unique(stats::na.omit(out$benchmark_value[idx]))
    if (length(benchmark_values) > 0) {
      benchmark_pct <- normalize_benchmark_value(
        metric_values,
        benchmark_value = benchmark_values[[1]],
        higher_is_better = higher_is_better
      )
      out$benchmark_normalized_value[idx] <- benchmark_pct
    }
  }

  out$metric_order <- match(out$metric_id, metric_sequence)
  out$metric_group <- ifelse(
    is.na(out$metric_group) | !nzchar(out$metric_group),
    "Profile",
    out$metric_group
  )
  out$metric_display_label <- paste(out$metric_group, out$metric_label, sep = ": ")
  out$missing_flag <- !is.finite(out$normalized_value)

  if (!isTRUE(cfg$keep_missing_metrics)) {
    out <- out[!out$missing_flag, , drop = FALSE]
  }

  out <- out[order(out$time_window, out$metric_order, out$geo_name), , drop = FALSE]
  rownames(out) <- NULL
  out
}
