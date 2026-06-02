# Prepare age pyramid data for mirrored demographic structure charts.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

age_pyramid_bin_start <- function(age_bin) {
  labels <- tolower(trimws(as.character(age_bin)))
  labels <- gsub("\u2013|\u2014", "-", labels)
  labels <- gsub("plus", "+", labels)
  labels <- gsub("[^0-9+\\-]", "", labels)
  out <- suppressWarnings(as.numeric(sub("^([0-9]+).*$", "\\1", labels)))
  out[is.na(out) & grepl("under|less", tolower(as.character(age_bin)))] <- 0
  out
}

standardize_age_pyramid_sex <- function(sex) {
  x <- tolower(trimws(as.character(sex)))
  ifelse(
    x %in% c("male", "m", "men"),
    "Male",
    ifelse(x %in% c("female", "f", "women"), "Female", as.character(sex))
  )
}

complete_age_pyramid_bins <- function(data, config) {
  if (!isTRUE(config$complete_bins)) {
    data$missing_bin_flag <- FALSE
    return(data)
  }

  age_levels <- config$age_bin_levels %||% levels(data$age_bin)
  if (is.null(age_levels) || length(age_levels) == 0) {
    age_levels <- unique(as.character(data$age_bin))
  }
  sex_levels <- config$sex_levels %||% c("Male", "Female")

  id_cols <- intersect(
    c("question_id", "geo_level", "geo_id", "geo_name", "period", "benchmark_label", "facet_label", "highlight_flag"),
    names(data)
  )
  keys <- unique(data[id_cols])

  templates <- lapply(seq_len(nrow(keys)), function(i) {
    expanded <- expand.grid(
      age_bin = age_levels,
      sex = sex_levels,
      stringsAsFactors = FALSE
    )
    for (col in id_cols) {
      expanded[[col]] <- keys[[col]][[i]]
    }
    expanded
  })
  full <- do.call(rbind, templates)
  merged <- merge(
    full,
    data,
    by = c(id_cols, "age_bin", "sex"),
    all.x = TRUE,
    sort = FALSE
  )
  merged$missing_bin_flag <- !is.finite(merged$pop_value)
  merged$pop_value[!is.finite(merged$pop_value)] <- 0
  merged
}

age_pyramid_validation <- function(data,
                                   question_id = NULL,
                                   allow_multiple_periods = FALSE,
                                   expected_age_bins = NULL,
                                   check_share_sums = FALSE,
                                   share_tolerance = 0.01) {
  validation <- validate_age_pyramid_contract(data, require_non_empty = TRUE)
  issues <- character()

  if (!isTRUE(validation$pass)) {
    issues <- c(
      issues,
      sprintf(
        "Missing required fields: %s",
        paste(validation$missing_required, collapse = ", ")
      )
    )
  }

  if (!is.null(question_id) && "question_id" %in% names(data)) {
    data <- data[data$question_id == question_id, , drop = FALSE]
  }

  if (nrow(data) == 0) {
    issues <- c(issues, "No rows are available after question filtering.")
  }

  grain_cols <- c("geo_id", "period", "age_bin", "sex")
  grain_cols <- c(grain_cols, intersect(c("benchmark_label", "facet_label"), names(data)))
  if (length(setdiff(grain_cols, names(data))) == 0 && nrow(data) > 0) {
    key <- do.call(paste, c(data[grain_cols], sep = "::"))
    if (anyDuplicated(key) > 0) {
      issues <- c(
        issues,
        paste("Duplicate age pyramid grain rows for:", paste(grain_cols, collapse = ", "))
      )
    }
  }

  if (!isTRUE(allow_multiple_periods) && "period" %in% names(data)) {
    periods <- unique(stats::na.omit(data$period))
    if (length(periods) != 1) {
      issues <- c(issues, sprintf("Expected one period; found %s.", length(periods)))
    }
  }

  if (!is.null(expected_age_bins) && "age_bin" %in% names(data)) {
    missing_bins <- setdiff(expected_age_bins, unique(as.character(data$age_bin)))
    if (length(missing_bins) > 0) {
      issues <- c(issues, paste("Missing expected age bins:", paste(missing_bins, collapse = ", ")))
    }
  }

  if ("pop_value" %in% names(data) && any(data$pop_value < 0, na.rm = TRUE)) {
    issues <- c(issues, "pop_value contains negative values.")
  }

  if (isTRUE(check_share_sums)) {
    share_data <- data
    if (!"pop_share" %in% names(share_data) || all(!is.finite(share_data$pop_share))) {
      if (all(c("pop_value", "pop_total") %in% names(share_data))) {
        share_data$pop_share <- ifelse(share_data$pop_total > 0, share_data$pop_value / share_data$pop_total, NA_real_)
      }
    }

    if ("pop_share" %in% names(share_data)) {
      group_cols <- c("geo_id", "period", intersect(c("benchmark_label", "facet_label"), names(share_data)))
      for (col in group_cols) {
        if (col %in% names(share_data)) {
          share_data[[col]] <- ifelse(is.na(share_data[[col]]), "", as.character(share_data[[col]]))
        }
      }
      share_sums <- stats::aggregate(
        share_data$pop_share,
        by = share_data[group_cols],
        FUN = function(x) sum(x, na.rm = TRUE)
      )
      names(share_sums)[names(share_sums) == "x"] <- "pop_share_sum"
      bad <- share_sums[!is.finite(share_sums$pop_share_sum) | abs(share_sums$pop_share_sum - 1) > share_tolerance, , drop = FALSE]
      if (nrow(bad) > 0) {
        issues <- c(
          issues,
          sprintf("Population shares do not sum to 1 within %s group(s).", nrow(bad))
        )
      }
    }
  }

  result <- list(
    pass = length(issues) == 0,
    issues = issues,
    rows = nrow(data),
    base_contract = validation
  )
  class(result) <- c("age_pyramid_readiness_validation", class(result))
  result
}

assert_age_pyramid_ready <- function(data, ...) {
  result <- age_pyramid_validation(data, ...)
  if (!isTRUE(result$pass)) {
    stop(
      paste(c("Age pyramid readiness validation failed.", result$issues), collapse = "\n- "),
      call. = FALSE
    )
  }
  invisible(result)
}

prep_age_pyramid <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      geo_ids = NULL,
      period = NULL,
      period_min = NULL,
      period_max = NULL,
      measure = c("share", "count"),
      sex_left = "Male",
      sex_right = "Female",
      sex_levels = c("Male", "Female"),
      age_bin_levels = NULL,
      complete_bins = TRUE,
      require_single_period = TRUE,
      allow_multiple_periods = FALSE,
      drop_missing_pop = FALSE
    ),
    config
  )
  cfg$measure <- match.arg(cfg$measure, c("share", "count"))

  assert_age_pyramid_ready(
    data,
    question_id = cfg$question_id,
    allow_multiple_periods = isTRUE(cfg$allow_multiple_periods) || !isTRUE(cfg$require_single_period),
    expected_age_bins = cfg$age_bin_levels
  )

  out <- prepare_long_metric_frame(
    data,
    required = visual_contracts$age_pyramid$required_fields,
    value_columns = c("pop_value", "pop_total", "pop_share"),
    chart_type = "age_pyramid",
    config = cfg
  )

  if (!is.null(cfg$question_id) && "question_id" %in% names(out)) {
    out <- out[out$question_id == cfg$question_id, , drop = FALSE]
  }
  if (!is.null(cfg$geo_ids)) {
    out <- out[out$geo_id %in% cfg$geo_ids, , drop = FALSE]
  }
  if (!is.null(cfg$period)) {
    out <- out[out$period %in% cfg$period, , drop = FALSE]
  }
  if (!is.null(cfg$period_min)) {
    out <- out[out$period >= cfg$period_min, , drop = FALSE]
  }
  if (!is.null(cfg$period_max)) {
    out <- out[out$period <= cfg$period_max, , drop = FALSE]
  }
  if (isTRUE(cfg$drop_missing_pop)) {
    out <- out[is.finite(out$pop_value), , drop = FALSE]
  }
  if (nrow(out) == 0) {
    stop("No rows left after age pyramid prep filtering; adjust config.")
  }

  out$sex <- standardize_age_pyramid_sex(out$sex)
  if ("highlight_flag" %in% names(out)) {
    out$highlight_flag <- coerce_logical_column(out$highlight_flag)
  } else {
    out$highlight_flag <- TRUE
  }
  if (!"benchmark_label" %in% names(out)) {
    out$benchmark_label <- NA_character_
  }
  if (!"facet_label" %in% names(out)) {
    out$facet_label <- out$geo_name
  }

  assert_age_pyramid_ready(
    out,
    question_id = cfg$question_id,
    allow_multiple_periods = isTRUE(cfg$allow_multiple_periods) || !isTRUE(cfg$require_single_period),
    expected_age_bins = cfg$age_bin_levels
  )

  age_levels <- cfg$age_bin_levels
  if (is.null(age_levels)) {
    age_order <- unique(data.frame(
      age_bin = as.character(out$age_bin),
      age_start = age_pyramid_bin_start(out$age_bin),
      stringsAsFactors = FALSE
    ))
    age_order <- age_order[order(age_order$age_start, age_order$age_bin), , drop = FALSE]
    age_levels <- age_order$age_bin
  }
  out$age_bin <- factor(as.character(out$age_bin), levels = age_levels, ordered = TRUE)

  out <- complete_age_pyramid_bins(out, modifyList(cfg, list(age_bin_levels = age_levels)))
  out$age_bin <- factor(as.character(out$age_bin), levels = age_levels, ordered = TRUE)
  out$sex <- factor(standardize_age_pyramid_sex(out$sex), levels = cfg$sex_levels)

  total_label <- ifelse(is.na(out$benchmark_label), "", as.character(out$benchmark_label))
  facet_label <- ifelse(is.na(out$facet_label), "", as.character(out$facet_label))
  if (!"pop_total" %in% names(out) || all(!is.finite(out$pop_total))) {
    total_key <- interaction(out$geo_id, out$period, total_label, facet_label, drop = TRUE)
    out$pop_total <- ave(out$pop_value, total_key, FUN = function(x) sum(x, na.rm = TRUE))
  } else {
    total_key <- interaction(out$geo_id, out$period, total_label, facet_label, drop = TRUE)
    missing_total <- !is.finite(out$pop_total) | out$pop_total <= 0
    derived_total <- ave(out$pop_value, total_key, FUN = function(x) sum(x, na.rm = TRUE))
    out$pop_total[missing_total] <- derived_total[missing_total]
  }

  if (!"pop_share" %in% names(out) || all(!is.finite(out$pop_share))) {
    out$pop_share <- ifelse(out$pop_total > 0, out$pop_value / out$pop_total, NA_real_)
  } else {
    missing_share <- !is.finite(out$pop_share)
    out$pop_share[missing_share] <- ifelse(
      out$pop_total[missing_share] > 0,
      out$pop_value[missing_share] / out$pop_total[missing_share],
      NA_real_
    )
  }

  out$display_value <- if (identical(cfg$measure, "count")) out$pop_value else out$pop_share
  out$measure <- cfg$measure
  out$plot_value <- ifelse(as.character(out$sex) == cfg$sex_left, -out$display_value, out$display_value)
  out$plot_abs_value <- abs(out$plot_value)
  out$comparison_role <- ifelse(out$highlight_flag %in% TRUE, "Selected geography", "Benchmark")
  out <- out[order(out$facet_label, out$period, out$age_bin, out$sex), , drop = FALSE]

  assert_age_pyramid_ready(
    out,
    question_id = cfg$question_id,
    allow_multiple_periods = isTRUE(cfg$allow_multiple_periods) || !isTRUE(cfg$require_single_period),
    expected_age_bins = age_levels,
    check_share_sums = identical(cfg$measure, "share")
  )

  attr(out, "chart_config") <- resolve_chart_config("age_pyramid", cfg)
  out
}
