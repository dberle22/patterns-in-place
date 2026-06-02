# Render age pyramid charts from prepared demographic structure data.

source("visual_library/shared/chart_utils.R")

age_pyramid_axis_formatter <- function(measure = "share", accuracy = NULL) {
  if (identical(measure, "count")) {
    return(function(x) format_value_vector(abs(x), style = "integer", accuracy = accuracy))
  }
  function(x) format_value_vector(abs(x), style = "percent", accuracy = accuracy %||% 0.1)
}

age_pyramid_value_labels <- function(values, measure = "share", accuracy = NULL) {
  if (identical(measure, "count")) {
    return(format_value_vector(values, style = "integer", accuracy = accuracy))
  }
  format_value_vector(values, style = "percent", accuracy = accuracy %||% 0.1)
}

build_age_pyramid_title <- function(data, config) {
  if (is_nonempty_string(config$title)) {
    return(config$title)
  }

  target_names <- unique(stats::na.omit(data$geo_name[data$highlight_flag %in% TRUE]))
  bench_names <- unique(stats::na.omit(data$benchmark_label[!(data$highlight_flag %in% TRUE)]))

  if (length(target_names) == 1 && length(bench_names) > 0) {
    return(paste0("Age structure: ", target_names[[1]], " vs ", bench_names[[1]]))
  }
  if (length(target_names) == 1) {
    return(paste0("Age structure: ", target_names[[1]]))
  }

  "Age structure comparison"
}

build_age_pyramid_subtitle <- function(data, config) {
  if (is_nonempty_string(config$subtitle)) {
    return(config$subtitle)
  }

  periods <- sort(unique(stats::na.omit(data$period)))
  measure <- unique(stats::na.omit(data$measure))[1] %||% "share"
  metric_text <- if (identical(measure, "count")) "population count" else "percent of total population"
  parts <- c()
  if (length(periods) > 0) {
    parts <- c(parts, paste("Period:", format_year_range(min(periods), max(periods))))
  }
  parts <- c(parts, paste("Measure:", metric_text))
  parts <- c(parts, "Male plotted left; female plotted right")

  paste(parts, collapse = " | ")
}

build_age_pyramid_caption_note <- function(data, config) {
  notes <- c()
  if (any(!(data$highlight_flag %in% TRUE), na.rm = TRUE)) {
    labels <- unique(stats::na.omit(data$benchmark_label[!(data$highlight_flag %in% TRUE)]))
    label <- if (length(labels) > 0) labels[[1]] else "benchmark"
    notes <- c(notes, paste0("Gray outlines show ", label, " using the same age bins and period when available."))
  }
  if (any(data$missing_bin_flag %in% TRUE, na.rm = TRUE)) {
    notes <- c(notes, "Missing age-sex bins are displayed as zero-width segments.")
  }
  if (identical(unique(stats::na.omit(data$measure))[1] %||% "share", "share")) {
    notes <- c(notes, "Shares are computed within each geography across both sexes and all displayed age bins.")
  }
  paste(compact_chr(c(config$caption_side_note, notes)), collapse = " ")
}

render_age_pyramid <- function(data, config = list(), theme = NULL) {
  cfg <- resolve_chart_config(
    "age_pyramid",
    merge_chart_config(
      list(
        measure = NULL,
        show_labels = TRUE,
        label_threshold = NULL,
        label_accuracy = NULL,
        bar_width = 0.72,
        benchmark_bar_width = 0.86,
        benchmark_outline_color = visual_neutral_palette()$text_muted,
        benchmark_outline_linewidth = 0.45,
        benchmark_outline_alpha = 0.85,
        selected_alpha = 0.95,
        facet_by = NULL,
        facet_ncol = NULL,
        symmetric_axis = TRUE,
        axis_expand = 0.08,
        legend_position = "bottom",
        left_fill = "#4C78A8",
        right_fill = "#2A9D8F"
      ),
      config
    )
  )

  ensure_columns(data, c("age_bin", "plot_value", "plot_abs_value", "sex", "highlight_flag"), chart_type = "age_pyramid")
  plot_data <- data
  plot_data$highlight_flag <- coerce_logical_column(plot_data$highlight_flag)
  measure <- cfg$measure %||% unique(stats::na.omit(plot_data$measure))[1] %||% "share"
  formatter <- age_pyramid_axis_formatter(measure, cfg$label_accuracy)

  if (!is.factor(plot_data$age_bin)) {
    plot_data$age_bin <- factor(plot_data$age_bin, levels = unique(plot_data$age_bin), ordered = TRUE)
  }
  plot_data$age_bin <- factor(plot_data$age_bin, levels = levels(plot_data$age_bin), ordered = TRUE)

  if (is.null(cfg$facet_by)) {
    facet_candidates <- c("facet_label", "period")
    unique_facets <- if ("facet_label" %in% names(plot_data)) length(unique(stats::na.omit(plot_data$facet_label))) else 1
    unique_periods <- length(unique(stats::na.omit(plot_data$period)))
    cfg$facet_by <- if (unique_facets > 1) "facet_label" else if (unique_periods > 1) "period" else NULL
  }

  selected_data <- plot_data[plot_data$highlight_flag %in% TRUE, , drop = FALSE]
  benchmark_data <- plot_data[!(plot_data$highlight_flag %in% TRUE), , drop = FALSE]
  if (nrow(selected_data) == 0) {
    selected_data <- plot_data
    benchmark_data <- plot_data[FALSE, , drop = FALSE]
  }

  sex_levels <- unique(stats::na.omit(as.character(plot_data$sex)))
  fill_values <- stats::setNames(
    c(cfg$left_fill, cfg$right_fill, resolve_peer_palette(max(length(sex_levels) - 2, 0)))[seq_along(sex_levels)],
    sex_levels
  )

  max_abs <- max(abs(plot_data$plot_value), na.rm = TRUE)
  if (!is.finite(max_abs) || max_abs == 0) {
    max_abs <- 1
  }
  x_limits <- if (isTRUE(cfg$symmetric_axis)) c(-max_abs, max_abs) * (1 + cfg$axis_expand) else NULL

  p <- ggplot2::ggplot()

  if (nrow(benchmark_data) > 0) {
    p <- p +
      ggplot2::geom_col(
        data = benchmark_data,
        ggplot2::aes(
          x = .data$plot_value,
          y = .data$age_bin,
          color = "Benchmark outline"
        ),
        fill = NA,
        width = cfg$benchmark_bar_width,
        linewidth = cfg$benchmark_outline_linewidth,
        alpha = cfg$benchmark_outline_alpha
      )
  }

  p <- p +
    ggplot2::geom_col(
      data = selected_data,
      ggplot2::aes(x = .data$plot_value, y = .data$age_bin, fill = .data$sex),
      width = cfg$bar_width,
      alpha = cfg$selected_alpha
    ) +
    ggplot2::geom_vline(xintercept = 0, color = visual_neutral_palette()$axis, linewidth = 0.35) +
    ggplot2::scale_fill_manual(values = fill_values, name = "Group", drop = FALSE) +
    ggplot2::scale_color_manual(
      values = c("Benchmark outline" = cfg$benchmark_outline_color),
      name = "Context",
      drop = FALSE
    ) +
    ggplot2::scale_x_continuous(
      labels = formatter,
      limits = x_limits,
      expand = ggplot2::expansion(mult = c(0.02, 0.02))
    )

  if (isTRUE(cfg$show_labels)) {
    threshold <- cfg$label_threshold %||% if (identical(measure, "count")) max_abs * 0.18 else 0.035
      label_data <- selected_data[
        is.finite(selected_data$plot_abs_value) & selected_data$plot_abs_value >= threshold,
        ,
        drop = FALSE
      ]
      if (nrow(label_data) > 0) {
        label_offset <- max_abs * 0.015
        near_edge <- label_data$plot_abs_value >= max_abs * 0.9
        label_data$label <- age_pyramid_value_labels(label_data$plot_abs_value, measure, cfg$label_accuracy)
        label_data$label_x <- ifelse(
          near_edge,
          label_data$plot_value - sign(label_data$plot_value) * label_offset,
          label_data$plot_value + sign(label_data$plot_value) * label_offset
        )
        label_data$label_hjust <- ifelse(
          label_data$plot_value < 0,
          ifelse(near_edge, 0, 1),
          ifelse(near_edge, 1, 0)
        )
      p <- p +
        ggplot2::geom_text(
          data = label_data,
          ggplot2::aes(x = .data$label_x, y = .data$age_bin, label = .data$label),
          hjust = label_data$label_hjust,
          size = cfg$label_size * 0.86,
          color = visual_neutral_palette()$text,
          show.legend = FALSE
        )
    }
  }

  if (!is.null(cfg$facet_by) && cfg$facet_by %in% names(plot_data)) {
    p <- p + ggplot2::facet_wrap(stats::as.formula(paste("~", cfg$facet_by)), ncol = cfg$facet_ncol)
  }

  p <- apply_plot_labels(
    plot = p,
    data = plot_data,
    title = build_age_pyramid_title(plot_data, cfg),
    subtitle = build_age_pyramid_subtitle(plot_data, cfg),
    x = if (identical(measure, "count")) "Population count" else "Share of total population",
    y = NULL,
    side_note = build_age_pyramid_caption_note(plot_data, cfg),
    footer_note = cfg$caption_footer_note,
    methodology_note = cfg$caption_methodology_note
  )

  p + (theme %||% resolve_chart_theme(cfg)) +
    ggplot2::theme(
      legend.position = cfg$legend_position,
      legend.title = ggplot2::element_text(face = "plain"),
      panel.grid.major.y = ggplot2::element_blank(),
      panel.grid.minor = ggplot2::element_blank(),
      axis.title.y = ggplot2::element_blank(),
      strip.text = ggplot2::element_text(face = "plain"),
      plot.margin = ggplot2::margin(t = 12, r = 18, b = 12, l = 12)
    )
}
