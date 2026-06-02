# Prepare hexbin data.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

prep_hexbin <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      time_window = NULL,
      geo_ids = NULL,
      group_values = NULL,
      require_single_time_window = TRUE,
      drop_na_xy = TRUE,
      non_negative_weights = TRUE,
      x_quantile_limits = NULL,
      y_quantile_limits = NULL,
      winsorize = FALSE
    ),
    config
  )

  validate_hexbin_contract(
    data,
    require_single_time_window = isTRUE(cfg$require_single_time_window)
  )

  out <- prepare_long_metric_frame(
    data,
    required = visual_contracts$hexbin$required_fields,
    value_columns = c("x_value", "y_value", "weight_value"),
    chart_type = "hexbin",
    config = cfg
  )

  if (!is.null(cfg$question_id) && "question_id" %in% names(out)) {
    out <- out[out$question_id == cfg$question_id, , drop = FALSE]
  }
  if (!is.null(cfg$time_window)) {
    out <- out[out$time_window == cfg$time_window, , drop = FALSE]
  }
  if (!is.null(cfg$geo_ids)) {
    out <- out[out$geo_id %in% cfg$geo_ids, , drop = FALSE]
  }
  if (!is.null(cfg$group_values) && "group" %in% names(out)) {
    out <- out[out$group %in% cfg$group_values, , drop = FALSE]
  }

  if ("highlight_flag" %in% names(out)) {
    out$highlight_flag <- coerce_logical_column(out$highlight_flag)
  } else {
    out$highlight_flag <- FALSE
  }
  if ("label_flag" %in% names(out)) {
    out$label_flag <- coerce_logical_column(out$label_flag)
  }

  if (isTRUE(cfg$drop_na_xy)) {
    out <- out[is.finite(out$x_value) & is.finite(out$y_value), , drop = FALSE]
  }

  if ("weight_value" %in% names(out)) {
    if (isTRUE(cfg$non_negative_weights) &&
        any(out$weight_value < 0, na.rm = TRUE)) {
      stop("Hexbin weights must be non-negative.")
    }
  }

  apply_quantile_rule <- function(df, column, limits, winsorize = FALSE) {
    if (is.null(limits) || !(column %in% names(df))) {
      return(df)
    }

    values <- df[[column]]
    finite_values <- values[is.finite(values)]
    if (length(finite_values) == 0) {
      return(df[0, , drop = FALSE])
    }

    bounds <- stats::quantile(
      finite_values,
      probs = limits,
      na.rm = TRUE,
      names = FALSE,
      type = 7
    )

    if (isTRUE(winsorize)) {
      df[[column]] <- pmin(pmax(df[[column]], bounds[[1]]), bounds[[2]])
      return(df)
    }

    df[df[[column]] >= bounds[[1]] & df[[column]] <= bounds[[2]], , drop = FALSE]
  }

  out <- apply_quantile_rule(
    out,
    column = "x_value",
    limits = cfg$x_quantile_limits,
    winsorize = cfg$winsorize
  )
  out <- apply_quantile_rule(
    out,
    column = "y_value",
    limits = cfg$y_quantile_limits,
    winsorize = cfg$winsorize
  )

  if (nrow(out) == 0) {
    stop("No rows left after hexbin prep filtering; adjust config.")
  }

  out
}
