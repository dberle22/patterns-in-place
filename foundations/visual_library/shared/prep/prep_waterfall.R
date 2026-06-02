# Prepare waterfall data.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

prep_waterfall <- function(data, config = list()) {
  # Merge caller overrides into the chart-level prep defaults. These options
  # control which question slice is used, which value column drives the bars,
  # and whether prep should add the terminal total bar expected by the renderer.
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      geo_ids = NULL,
      time_window = NULL,
      value_mode = c("auto", "delta", "level", "percent"),
      group_fields = NULL,
      include_total = TRUE,
      total_label = NULL,
      total_component_id = "total",
      total_row_type = "total",
      additive_tolerance = 1e-6,
      require_single_geo_level = FALSE,
      require_single_time_window = FALSE,
      drop_missing_components = TRUE
    ),
    config
  )
  cfg$value_mode <- match.arg(cfg$value_mode, c("auto", "delta", "level", "percent"))

  # Validate the incoming chart contract before applying filters. This catches
  # missing required fields close to the SQL/query source rather than later in
  # ggplot where the error would be harder to read.
  validate_waterfall_contract(data)
  out <- prepare_long_metric_frame(
    data,
    required = visual_contracts$waterfall$required_fields,
    value_columns = c("component_value", "component_delta"),
    chart_type = "waterfall",
    config = cfg
  )

  # Apply standard chart-runner filters. Question ID is optional in the shared
  # contract, so these filters only activate when the field/config is present.
  if (!is.null(cfg$question_id) && "question_id" %in% names(out)) {
    out <- out[out$question_id == cfg$question_id, , drop = FALSE]
  }
  if (!is.null(cfg$geo_ids)) {
    out <- out[out$geo_id %in% cfg$geo_ids, , drop = FALSE]
  }
  if (!is.null(cfg$time_window) && "time_window" %in% names(out)) {
    out <- out[out$time_window == cfg$time_window, , drop = FALSE]
  }

  # Revalidate after filtering so empty or mixed-grain slices fail before any
  # cumulative waterfall math is computed.
  validation <- validate_waterfall_contract(
    out,
    require_single_geo_level = isTRUE(cfg$require_single_geo_level),
    require_single_time_window = isTRUE(cfg$require_single_time_window),
    require_non_empty = TRUE
  )
  if (!isTRUE(validation$pass)) {
    stop("Waterfall prep filters produced a contract-invalid dataset.")
  }

  # Normalize optional logical fields so SQL booleans, 0/1 values, and strings
  # behave the same way in downstream rendering.
  if ("highlight_flag" %in% names(out)) {
    out$highlight_flag <- coerce_logical_column(out$highlight_flag)
  } else {
    out$highlight_flag <- FALSE
  }

  # Choose the numeric contribution field. Change waterfalls use component_delta;
  # level and percent waterfalls use component_value. Auto mode prefers delta
  # when the query provides it with finite values.
  if (identical(cfg$value_mode, "delta")) {
    value_col <- "component_delta"
  } else if (identical(cfg$value_mode, "level") || identical(cfg$value_mode, "percent")) {
    value_col <- "component_value"
  } else {
    value_col <- if ("component_delta" %in% names(out) && any(is.finite(out$component_delta))) {
      "component_delta"
    } else {
      "component_value"
    }
  }

  if (!(value_col %in% names(out))) {
    stop(sprintf("Waterfall value column '%s' not found.", value_col))
  }
  out$plot_value <- suppressWarnings(as.numeric(out[[value_col]]))

  # Drop invalid contributions by default; a waterfall without finite component
  # values cannot produce a meaningful cumulative path.
  if (isTRUE(cfg$drop_missing_components)) {
    out <- out[is.finite(out$plot_value), , drop = FALSE]
  }
  if (nrow(out) == 0) {
    stop("No rows left after waterfall prep filtering; adjust config.")
  }

  # Preserve canonical component order from SQL/spec when present. If the query
  # does not provide sort_order, fall back to stable row order within geo/window.
  if (!"sort_order" %in% names(out) || all(is.na(out$sort_order))) {
    out$sort_order <- ave(seq_len(nrow(out)), out$geo_id, out$time_window, FUN = seq_along)
  }
  out$sort_order <- suppressWarnings(as.numeric(out$sort_order))

  # Define independent waterfall paths. By default, each geo/window/benchmark
  # gets its own cumulative sequence so faceted benchmark views do not leak into
  # each other.
  default_group_fields <- intersect(c("geo_level", "geo_id", "geo_name", "time_window", "benchmark_label"), names(out))
  group_fields <- cfg$group_fields %||% default_group_fields
  group_fields <- intersect(group_fields, names(out))
  if (length(group_fields) == 0) {
    group_fields <- NULL
    group_key <- rep("all", nrow(out))
  } else {
    group_data <- out[, group_fields, drop = FALSE]
    group_data[] <- lapply(group_data, function(x) {
      x <- as.character(x)
      x[is.na(x) | !nzchar(x)] <- "none"
      x
    })
    group_key <- interaction(group_data, drop = TRUE, lex.order = TRUE)
  }

  # Sort once before deriving group keys again, so cumulative positions are based
  # on the same canonical component order the chart will display.
  out <- out[order(group_key, out$sort_order, out$component_label), , drop = FALSE]
  group_key <- if (is.null(group_fields)) {
    rep("all", nrow(out))
  } else {
    group_data <- out[, group_fields, drop = FALSE]
    group_data[] <- lapply(group_data, function(x) {
      x <- as.character(x)
      x[is.na(x) | !nzchar(x)] <- "none"
      x
    })
    interaction(group_data, drop = TRUE, lex.order = TRUE)
  }

  # Preallocate render fields. This keeps the structure consistent before the
  # per-group loop fills in running starts, ends, shares, and QA values.
  out$row_type <- "component"
  out$waterfall_group <- as.character(group_key)
  out$component_group <- NA_character_
  out$cumulative_end <- NA_real_
  out$cumulative_start <- NA_real_
  out$component_share <- NA_real_
  out$additive_total <- NA_real_
  out$additive_residual <- NA_real_
  out$additive_pass <- NA
  out$waterfall_position <- NA_real_

  # Compute the actual waterfall path for each independent group. The start of
  # each component is the prior cumulative end; the end is the new cumulative sum.
  pieces <- split(seq_len(nrow(out)), out$waterfall_group)
  for (idx in pieces) {
    cumulative_end <- cumsum(out$plot_value[idx])
    out$cumulative_end[idx] <- cumulative_end
    out$cumulative_start[idx] <- c(0, utils::head(cumulative_end, -1))
    out$component_share[idx] <- if (isTRUE(sum(out$plot_value[idx]) != 0)) {
      out$plot_value[idx] / sum(out$plot_value[idx])
    } else {
      NA_real_
    }
    out$additive_total[idx] <- sum(out$plot_value[idx])
    out$additive_residual[idx] <- out$additive_total[idx] - sum(out$plot_value[idx])
    out$additive_pass[idx] <- abs(out$additive_residual[idx]) <= cfg$additive_tolerance
    out$waterfall_position[idx] <- seq_along(idx)
  }

  # Add a terminal total bar for each path. It starts at zero and ends at the sum
  # of the components, making the final additive result visible in every sample.
  if (isTRUE(cfg$include_total)) {
    total_rows <- lapply(pieces, function(idx) {
      template <- out[idx[length(idx)], , drop = FALSE]
      total_value <- sum(out$plot_value[idx])
      template$component_id <- cfg$total_component_id
      template$component_label <- cfg$total_label %||% unique(stats::na.omit(out$total_label[idx]))[1] %||% "Total"
      template$component_value <- total_value
      if ("component_delta" %in% names(template)) {
        template$component_delta <- total_value
      }
      template$plot_value <- total_value
      template$cumulative_start <- 0
      template$cumulative_end <- total_value
      template$sort_order <- max(out$sort_order[idx], na.rm = TRUE) + 1
      template$row_type <- cfg$total_row_type
      template$component_group <- "Total"
      template$component_share <- 1
      template$additive_total <- total_value
      template$additive_residual <- 0
      template$additive_pass <- TRUE
      template$waterfall_position <- length(idx) + 1
      template
    })
    out <- rbind(out, do.call(rbind, total_rows))
  }

  # Return rows in drawing order and attach resolved chart config for shared
  # label/caption helpers used by render_waterfall().
  group_key <- out$waterfall_group
  out$waterfall_position <- suppressWarnings(as.numeric(unlist(out$waterfall_position, use.names = FALSE)))
  out <- out[order(group_key, out$waterfall_position), , drop = FALSE]
  attr(out, "chart_config") <- resolve_chart_config(chart_type = "waterfall", config = cfg)
  out
}
