# Prepare heatmap table data.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

heatmap_direction_flag <- function(direction) {
  direction <- tolower(as.character(direction %||% "higher_is_better"))
  !(direction %in% c("lower_is_better", "lower-better", "lower"))
}

heatmap_make_display_label <- function(values,
                                       style = "number",
                                       accuracy = NULL,
                                       na_label = "No data") {
  numeric_values <- suppressWarnings(as.numeric(values))
  labels <- rep(na_label, length(numeric_values))
  finite <- is.finite(numeric_values)
  if (any(finite)) {
    labels[finite] <- format_value_vector(
      numeric_values[finite],
      style = style,
      accuracy = accuracy,
      compact = TRUE
    )
  }
  labels
}

complete_heatmap_matrix <- function(data) {
  row_lookup <- unique(data[, c("row_id", "row_label", "geo_level", "geo_id", "geo_name"), drop = FALSE])
  row_lookup <- row_lookup[!duplicated(row_lookup$row_id), , drop = FALSE]

  column_fields <- intersect(
    c("column_id", "column_label", "metric_id", "metric_label", "metric_group", "metric_order", "period"),
    names(data)
  )
  column_lookup <- unique(data[, column_fields, drop = FALSE])
  column_lookup <- column_lookup[!duplicated(column_lookup$column_id), , drop = FALSE]

  grid <- merge(
    row_lookup,
    column_lookup,
    by = NULL,
    all = TRUE,
    sort = FALSE
  )

  value_fields <- setdiff(
    names(data),
    union(names(row_lookup), setdiff(names(column_lookup), c("metric_id", "metric_label", "period")))
  )
  value_fields <- unique(c("row_id", "column_id", value_fields))
  value_fields <- intersect(value_fields, names(data))

  out <- merge(
    grid,
    data[, value_fields, drop = FALSE],
    by = c("row_id", "column_id"),
    all.x = TRUE,
    sort = FALSE
  )

  for (field in c("source", "vintage", "time_window", "question_id", "group")) {
    if (field %in% names(data) && !field %in% names(out)) {
      out[[field]] <- extract_chart_metadata(data, field)
    }
  }
  out
}

prep_heatmap_table <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      time_window = NULL,
      metric_ids = NULL,
      periods = NULL,
      variant = NULL,
      normalize = TRUE,
      fill_value_field = "normalized_value",
      label_value_field = "metric_value",
      label_style = "number",
      label_accuracy = NULL,
      normalized_label_accuracy = 1,
      row_order = NULL,
      column_order = NULL,
      sort_rows = "mean_normalized_desc",
      complete_matrix = TRUE,
      keep_missing = TRUE,
      missing_label = "No data"
    ),
    config
  )

  validate_heatmap_table_contract(data)
  out <- prepare_long_metric_frame(
    data,
    required = visual_contracts$heatmap_table$required_fields,
    value_columns = c("metric_value", "normalized_value", "metric_order", "row_order"),
    chart_type = "heatmap_table",
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
  if (!is.null(cfg$periods) && "period" %in% names(out)) {
    out <- out[as.character(out$period) %in% as.character(cfg$periods), , drop = FALSE]
  }
  if (nrow(out) == 0) {
    stop("No rows left after heatmap table prep filtering; adjust config.")
  }

  out$geo_name <- as.character(out$geo_name)
  out$geo_id <- as.character(out$geo_id)
  out$metric_id <- as.character(out$metric_id)
  out$metric_label <- as.character(out$metric_label)
  out$metric_group <- if ("metric_group" %in% names(out)) as.character(out$metric_group) else NA_character_
  out$direction <- if ("direction" %in% names(out)) as.character(out$direction) else "higher_is_better"
  out$highlight_flag <- if ("highlight_flag" %in% names(out)) coerce_logical_column(out$highlight_flag) else FALSE
  out$note <- if ("note" %in% names(out)) as.character(out$note) else NA_character_
  out$period <- if ("period" %in% names(out)) as.character(out$period) else NA_character_
  out$time_window <- if ("time_window" %in% names(out)) as.character(out$time_window) else NA_character_

  variant <- cfg$variant
  if (is.null(variant)) {
    metric_n <- length(unique(stats::na.omit(out$metric_id)))
    period_n <- length(unique(stats::na.omit(out$period)))
    geo_n <- length(unique(stats::na.omit(out$geo_id)))
    variant <- if (metric_n == 1 && period_n > 1) {
      "geo_period"
    } else if (geo_n == 1 && period_n > 1 && metric_n > 1) {
      "metric_period"
    } else {
      "geo_metric"
    }
  }
  out$heatmap_variant <- variant

  if (identical(variant, "metric_period")) {
    out$row_id <- out$metric_id
    out$row_label <- out$metric_label
    out$column_id <- out$period
    out$column_label <- out$period
  } else if (identical(variant, "geo_period")) {
    out$row_id <- out$geo_id
    out$row_label <- out$geo_name
    out$column_id <- out$period
    out$column_label <- out$period
  } else {
    out$row_id <- out$geo_id
    out$row_label <- out$geo_name
    out$column_id <- out$metric_id
    out$column_label <- out$metric_label
  }

  out$column_label <- as.character(out$column_label)
  out$row_label <- as.character(out$row_label)

  if (!"normalized_value" %in% names(out)) {
    out$normalized_value <- NA_real_
  }

  should_normalize <- isTRUE(cfg$normalize) || all(is.na(out$normalized_value))
  if (isTRUE(should_normalize)) {
    norm_group <- if (identical(variant, "geo_metric")) {
      interaction(out$metric_id, out$time_window, drop = TRUE, lex.order = TRUE)
    } else if (identical(variant, "geo_period")) {
      interaction(out$metric_id, out$period, drop = TRUE, lex.order = TRUE)
    } else {
      interaction(out$metric_id, drop = TRUE, lex.order = TRUE)
    }

    for (idx in split(seq_len(nrow(out)), norm_group)) {
      direction_values <- stats::na.omit(out$direction[idx])
      higher_is_better <- heatmap_direction_flag(if (length(direction_values) > 0) direction_values[[1]] else "higher_is_better")
      out$normalized_value[idx] <- compute_percentile(out$metric_value[idx], higher_is_better = higher_is_better)
    }
  }

  out$missing_flag <- !is.finite(out$metric_value)
  if (identical(cfg$fill_value_field, "normalized_value")) {
    out$missing_flag <- out$missing_flag | !is.finite(out$normalized_value)
  }

  if (isTRUE(cfg$complete_matrix)) {
    out <- complete_heatmap_matrix(out)
    out$highlight_flag <- if ("highlight_flag" %in% names(out)) coerce_logical_column(out$highlight_flag) else FALSE
    out$missing_flag <- if ("missing_flag" %in% names(out)) coerce_logical_column(out$missing_flag) else TRUE
    out$missing_flag[is.na(out$metric_value)] <- TRUE
    out$heatmap_variant <- variant
    out$note <- if ("note" %in% names(out)) as.character(out$note) else NA_character_
  }

  if (!isTRUE(cfg$keep_missing)) {
    out <- out[!out$missing_flag, , drop = FALSE]
  }

  label_field <- cfg$label_value_field
  if ("cell_label" %in% names(out)) {
    out$cell_label <- as.character(out$cell_label)
    out$cell_label[is.na(out$cell_label) | !nzchar(out$cell_label)] <- cfg$missing_label
  } else if ("value_label" %in% names(out) && identical(label_field, "metric_value")) {
    out$cell_label <- as.character(out$value_label)
    out$cell_label[is.na(out$cell_label) | !nzchar(out$cell_label)] <- cfg$missing_label
  } else if (identical(label_field, "normalized_value")) {
    out$cell_label <- heatmap_make_display_label(
      out$normalized_value,
      style = "number",
      accuracy = cfg$normalized_label_accuracy,
      na_label = cfg$missing_label
    )
  } else {
    out$cell_label <- heatmap_make_display_label(
      out[[label_field]],
      style = cfg$label_style,
      accuracy = cfg$label_accuracy,
      na_label = cfg$missing_label
    )
  }
  out$normalized_label <- heatmap_make_display_label(
    out$normalized_value,
    style = "number",
    accuracy = cfg$normalized_label_accuracy,
    na_label = cfg$missing_label
  )

  row_scores <- stats::aggregate(
    normalized_value ~ row_label,
    data = out,
    FUN = function(x) mean(x, na.rm = TRUE)
  )
  names(row_scores)[names(row_scores) == "normalized_value"] <- "row_score"
  out <- merge(out, row_scores, by = "row_label", all.x = TRUE, sort = FALSE)

  if (!"row_order" %in% names(out)) {
    out$row_order <- NA_real_
  }
  if (!"metric_order" %in% names(out)) {
    out$metric_order <- NA_real_
  }

  if (!is.null(cfg$row_order)) {
    row_levels <- unique(c(cfg$row_order, out$row_label))
  } else if (any(is.finite(out$row_order))) {
    row_order_df <- unique(out[, c("row_label", "row_order"), drop = FALSE])
    row_order_df <- row_order_df[order(-row_order_df$row_order, row_order_df$row_label, na.last = TRUE), , drop = FALSE]
    row_levels <- row_order_df$row_label
  } else if (identical(cfg$sort_rows, "input")) {
    row_levels <- unique(out$row_label)
  } else {
    row_order_df <- unique(out[, c("row_label", "row_score", "highlight_flag"), drop = FALSE])
    row_order_df <- row_order_df[order(
      row_order_df$highlight_flag %in% TRUE,
      row_order_df$row_score,
      row_order_df$row_label,
      decreasing = TRUE,
      na.last = TRUE
    ), , drop = FALSE]
    row_levels <- row_order_df$row_label
  }

  if (!is.null(cfg$column_order)) {
    column_levels <- unique(c(cfg$column_order, out$column_label))
  } else if (identical(variant, "geo_metric") && any(is.finite(out$metric_order))) {
    column_order_df <- unique(out[, c("column_label", "metric_order"), drop = FALSE])
    column_order_df <- column_order_df[order(column_order_df$metric_order, column_order_df$column_label), , drop = FALSE]
    column_levels <- column_order_df$column_label
  } else if (identical(variant, "geo_metric")) {
    column_levels <- unique(out$column_label)
  } else {
    numeric_period <- suppressWarnings(as.numeric(out$column_label))
    if (any(is.finite(numeric_period))) {
      column_levels <- unique(out$column_label[order(numeric_period, out$column_label)])
    } else {
      column_levels <- unique(out$column_label)
    }
  }

  out$row_label <- factor(out$row_label, levels = rev(unique(row_levels)))
  out$column_label <- factor(out$column_label, levels = unique(column_levels))
  out$fill_value <- suppressWarnings(as.numeric(out[[cfg$fill_value_field]]))
  out$fill_label <- if (identical(cfg$fill_value_field, "normalized_value")) out$normalized_label else out$cell_label

  rownames(out) <- NULL
  attr(out, "chart_config") <- resolve_chart_config("heatmap_table", cfg)
  out
}
