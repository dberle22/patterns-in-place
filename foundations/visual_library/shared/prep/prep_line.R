# Prepare line chart data for rendering.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

prep_line <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      time_window = NULL,
      metric_id = NULL,
      variant = "single",
      geo_ids = NULL,
      period_min = NULL,
      period_max = NULL,
      base_period = NULL,
      rolling_k = 3,
      complete_periods = TRUE,
      drop_na_metric = FALSE
    ),
    config
  )

  validate_line_contract(data)
  out <- prepare_long_metric_frame(
    data = data,
    required = visual_contracts$line$required_fields,
    value_columns = c("period", "metric_value", "benchmark_value", "index_base_period"),
    chart_type = "line",
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
  if (!is.null(cfg$geo_ids)) {
    out <- out[out$geo_id %in% cfg$geo_ids, , drop = FALSE]
  }
  if (!is.null(cfg$period_min)) {
    out <- out[out$period >= cfg$period_min, , drop = FALSE]
  }
  if (!is.null(cfg$period_max)) {
    out <- out[out$period <= cfg$period_max, , drop = FALSE]
  }
  if (isTRUE(cfg$drop_na_metric)) {
    out <- out[is.finite(out$metric_value), , drop = FALSE]
  }
  if (nrow(out) == 0) {
    stop("No rows left after line prep filtering; adjust config.")
  }

  if ("highlight_flag" %in% names(out)) {
    out$highlight_flag <- coerce_logical_column(out$highlight_flag)
  } else {
    out$highlight_flag <- FALSE
  }

  key <- paste(out$geo_id, out$metric_id, out$period, sep = "::")
  if (anyDuplicated(key) > 0) {
    stop("Line prep expects one row per geo_id, metric_id, and period after filtering.")
  }

  out <- out[order(out$geo_id, out$period), , drop = FALSE]

  if (isTRUE(cfg$complete_periods) && all(is.finite(out$period))) {
    period_seq <- seq(min(out$period, na.rm = TRUE), max(out$period, na.rm = TRUE), by = 1)
    parts <- split(out, out$geo_id)
    parts <- lapply(parts, function(df) {
      template <- df[1, , drop = FALSE]
      expanded <- merge(
        data.frame(period = period_seq),
        df,
        by = "period",
        all.x = TRUE,
        sort = TRUE
      )
      fill_cols <- setdiff(names(template), c("period", "metric_value", "benchmark_value", "plot_value", "index_base_period"))
      for (col in fill_cols) {
        if (col %in% names(expanded)) {
          expanded[[col]][is.na(expanded[[col]])] <- template[[col]][[1]]
        }
      }
      expanded
    })
    out <- do.call(rbind, parts)
  }

  out$plot_value <- out$metric_value
  out$variant <- cfg$variant

  if (identical(cfg$variant, "indexed")) {
    base_period <- cfg$base_period %||% min(out$period, na.rm = TRUE)
    parts <- split(out, out$geo_id)
    parts <- lapply(parts, function(df) {
      base_row <- df[df$period == base_period, , drop = FALSE]
      if (nrow(base_row) == 0 || !is.finite(base_row$metric_value[1]) || base_row$metric_value[1] == 0) {
        df$plot_value <- NA_real_
      } else {
        df$plot_value <- (df$metric_value / base_row$metric_value[1]) * 100
      }
      df$time_window <- "indexed"
      df$index_base_period <- base_period
      df
    })
    out <- do.call(rbind, parts)
  }

  if (identical(cfg$variant, "rolling")) {
    if (cfg$rolling_k < 2) {
      stop("rolling_k must be >= 2.")
    }
    parts <- split(out, out$geo_id)
    parts <- lapply(parts, function(df) {
      df$plot_value <- as.numeric(stats::filter(df$metric_value, rep(1 / cfg$rolling_k, cfg$rolling_k), sides = 1))
      df$time_window <- paste0("rolling_", cfg$rolling_k, "yr")
      df
    })
    out <- do.call(rbind, parts)
  }

  out <- out[order(out$geo_id, out$period), , drop = FALSE]
  out
}
