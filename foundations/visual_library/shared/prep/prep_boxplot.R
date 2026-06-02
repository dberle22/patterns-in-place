# Prepare boxplot data.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

prep_boxplot <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      time_window = NULL,
      metric_id = NULL,
      geo_ids = NULL,
      group_values = NULL,
      group_field = "group",
      require_single_geo_level = TRUE,
      require_single_metric = TRUE,
      require_single_time_window = TRUE,
      drop_missing_metric = TRUE,
      trim_quantiles = NULL,
      winsorize_display = FALSE,
      order_groups = "median_desc"
    ),
    config
  )

  validate_boxplot_contract(data)

  out <- prepare_long_metric_frame(
    data,
    required = visual_contracts$boxplot$required_fields,
    value_columns = c("metric_value", "benchmark_value", "weight_value"),
    chart_type = "boxplot",
    config = cfg
  )

  if (!is.null(cfg$question_id) && "question_id" %in% names(out)) {
    out <- out[out$question_id == cfg$question_id, , drop = FALSE]
  }
  if (!is.null(cfg$time_window) && "time_window" %in% names(out)) {
    out <- out[out$time_window == cfg$time_window, , drop = FALSE]
  }
  if (!is.null(cfg$metric_id) && "metric_id" %in% names(out)) {
    out <- out[out$metric_id == cfg$metric_id, , drop = FALSE]
  }
  if (!is.null(cfg$geo_ids)) {
    out <- out[out$geo_id %in% cfg$geo_ids, , drop = FALSE]
  }
  if (!is.null(cfg$group_values) && cfg$group_field %in% names(out)) {
    out <- out[out[[cfg$group_field]] %in% cfg$group_values, , drop = FALSE]
  }

  validation <- validate_boxplot_contract(
    out,
    require_single_geo_level = isTRUE(cfg$require_single_geo_level),
    require_single_time_window = isTRUE(cfg$require_single_time_window),
    require_non_empty = TRUE
  )
  if (!isTRUE(validation$pass)) {
    stop("Boxplot prep filters produced a contract-invalid dataset.")
  }

  if (isTRUE(cfg$require_single_metric)) {
    metrics <- unique(stats::na.omit(out$metric_id))
    if (length(metrics) != 1) {
      stop("Boxplot prep requires one metric_id unless require_single_metric is FALSE.")
    }
  }

  if ("highlight_flag" %in% names(out)) {
    out$highlight_flag <- coerce_logical_column(out$highlight_flag)
  } else {
    out$highlight_flag <- FALSE
  }
  if ("label_flag" %in% names(out)) {
    out$label_flag <- coerce_logical_column(out$label_flag)
  } else {
    out$label_flag <- FALSE
  }

  out$missing_metric_count <- sum(!is.finite(out$metric_value))
  if (isTRUE(cfg$drop_missing_metric)) {
    out <- out[is.finite(out$metric_value), , drop = FALSE]
  }

  if (nrow(out) == 0) {
    stop("No rows left after boxplot prep filtering; adjust config.")
  }

  if (cfg$group_field %in% names(out)) {
    group_values <- as.character(out[[cfg$group_field]])
    group_values[is.na(group_values) | !nzchar(group_values)] <- "Ungrouped"
    out$box_group <- group_values
  } else {
    out$box_group <- "All observations"
  }

  out$plot_value <- out$metric_value
  if (!is.null(cfg$trim_quantiles)) {
    finite_values <- out$plot_value[is.finite(out$plot_value)]
    if (length(finite_values) > 0) {
      bounds <- stats::quantile(
        finite_values,
        probs = cfg$trim_quantiles,
        na.rm = TRUE,
        names = FALSE,
        type = 7
      )
      if (isTRUE(cfg$winsorize_display)) {
        out$plot_value <- pmin(pmax(out$plot_value, bounds[[1]]), bounds[[2]])
      } else {
        out <- out[out$plot_value >= bounds[[1]] & out$plot_value <= bounds[[2]], , drop = FALSE]
      }
    }
  }

  group_levels <- unique(out$box_group)
  group_medians <- stats::aggregate(
    out$plot_value,
    by = list(box_group = out$box_group),
    FUN = function(x) stats::median(x, na.rm = TRUE)
  )
  names(group_medians)[names(group_medians) == "x"] <- "group_median"
  group_counts <- stats::aggregate(
    out$plot_value,
    by = list(box_group = out$box_group),
    FUN = function(x) sum(is.finite(x))
  )
  names(group_counts)[names(group_counts) == "x"] <- "group_n"
  group_stats <- merge(group_medians, group_counts, by = "box_group", all = TRUE)

  if (identical(cfg$order_groups, "median_desc")) {
    group_levels <- group_stats$box_group[order(group_stats$group_median, decreasing = TRUE, na.last = TRUE)]
  } else if (identical(cfg$order_groups, "median_asc")) {
    group_levels <- group_stats$box_group[order(group_stats$group_median, decreasing = FALSE, na.last = TRUE)]
  } else if (identical(cfg$order_groups, "alphabetical")) {
    group_levels <- sort(group_levels)
  }

  out <- merge(out, group_stats, by = "box_group", all.x = TRUE, sort = FALSE)
  out$box_group <- factor(out$box_group, levels = unique(group_levels))
  attr(out, "chart_config") <- resolve_chart_config("boxplot", cfg)

  out
}
