# Render bar charts from prepared bar data.

source("visual_library/shared/chart_utils.R")

bar_value_labeler <- function(values, label_style = "number", accuracy = NULL) {
  if (identical(label_style, "dollar")) {
    return(scales::label_dollar(accuracy = accuracy %||% 1)(values))
  }
  format_value_vector(
    values,
    style = label_style,
    accuracy = accuracy,
    compact = TRUE
  )
}

bar_axis_formatter <- function(label_style = "number", accuracy = NULL) {
  if (identical(label_style, "dollar")) {
    return(scales::label_dollar(accuracy = accuracy %||% 1))
  }

  value_label_formatter(
    style = label_style,
    accuracy = accuracy
  )
}

build_bar_subtitle <- function(data, config) {
  time_window <- if ("time_window" %in% names(data)) unique(stats::na.omit(data$time_window)) else character()
  groups <- if ("group" %in% names(data)) unique(stats::na.omit(data$group)) else character()

  parts <- c()
  if (length(time_window) > 0) {
    parts <- c(parts, paste("Window:", time_window[[1]]))
  }
  if (length(groups) == 1 && nzchar(groups[[1]])) {
    parts <- c(parts, paste("Scope:", groups[[1]]))
  }
  parts <- c(
    parts,
    if (isTRUE(config$sort_desc)) "Sorted highest to lowest" else "Sorted lowest to highest"
  )

  paste(parts, collapse = " | ")
}

build_bar_caption_note <- function(data, config) {
  notes <- c()

  if (isTRUE(any(data$truncated_flag %in% TRUE, na.rm = TRUE))) {
    if (!is.null(config$top_n)) {
      notes <- c(notes, paste0("Showing top ", config$top_n, " rows after filtering."))
    } else if (!is.null(config$bottom_n)) {
      notes <- c(notes, paste0("Showing bottom ", config$bottom_n, " rows after filtering."))
    }
  }

  if (isTRUE(any(data$highlight_flag %in% TRUE, na.rm = TRUE))) {
    notes <- c(notes, "Highlighted bar marks the selected geography.")
  }

  if (identical(config$bar_variant, "diverging")) {
    notes <- c(notes, "Positive values sit above the benchmark; negative values sit below it.")
  }

  paste(compact_chr(notes), collapse = " ")
}

render_bar <- function(data, config = list(), theme = NULL) {
  cfg <- resolve_chart_config(
    "bar",
    merge_chart_config(
      list(
        title = NULL,
        subtitle = NULL,
        bar_variant = "ranked_horizontal",
        show_labels = TRUE,
        label_style = "number",
        label_accuracy = NULL,
        show_axis_labels = TRUE,
        highlight_legend = FALSE,
        bar_width = 0.72,
        show_benchmark = FALSE,
        benchmark_value = NULL,
        benchmark_label = NULL,
        sort_desc = TRUE,
        top_n = NULL,
        bottom_n = NULL,
        axis_expand_lower = 0.04,
        axis_expand_upper = 0.16,
        right_margin_pt = 16
      ),
      config
    )
  )

  ensure_columns(data, c("geo_name", "metric_value"), chart_type = "bar")

  plot_data <- data
  value_var <- if ("plot_value" %in% names(plot_data)) "plot_value" else "metric_value"
  order_var <- if ("display_order" %in% names(plot_data)) "display_order" else value_var
  plot_data <- plot_data[order(plot_data[[order_var]], decreasing = FALSE), , drop = FALSE]
  plot_data$geo_name <- factor(plot_data$geo_name, levels = rev(plot_data$geo_name))

  fill_scale <- NULL
  if ("highlight_flag" %in% names(plot_data) && any(plot_data$highlight_flag %in% TRUE, na.rm = TRUE)) {
    plot_data$fill_group <- ifelse(plot_data$highlight_flag, "Target", "Comparison")
    fill_scale <- ggplot2::scale_fill_manual(
      values = c("Comparison" = cfg$neutral_color, "Target" = cfg$highlight_color),
      guide = if (isTRUE(cfg$highlight_legend)) "legend" else "none"
    )
  } else if (identical(cfg$bar_variant, "diverging")) {
    plot_data$fill_group <- ifelse(
      plot_data[[value_var]] >= 0,
      "Above benchmark",
      "Below benchmark"
    )
    fill_scale <- ggplot2::scale_fill_manual(
      values = c(
        "Above benchmark" = cfg$positive_fill,
        "Below benchmark" = cfg$negative_fill
      ),
      guide = if (isTRUE(cfg$highlight_legend)) "legend" else "none"
    )
  } else if ("series" %in% names(plot_data) && length(unique(stats::na.omit(plot_data$series))) > 1) {
    plot_data$fill_group <- as.character(plot_data$series)
    series_levels <- unique(stats::na.omit(plot_data$fill_group))
    series_palette <- resolve_peer_palette(
      length(series_levels),
      palette = cfg$series_palette %||% cfg$peer_palette
    )
    fill_scale <- ggplot2::scale_fill_manual(
      values = stats::setNames(series_palette, series_levels)
    )
  } else {
    plot_data$fill_group <- "Default"
    fill_scale <- ggplot2::scale_fill_manual(
      values = c("Default" = cfg$base_color),
      guide = "none"
    )
  }

  p <- ggplot2::ggplot(
    plot_data,
    ggplot2::aes(x = .data$geo_name, y = .data[[value_var]], fill = .data$fill_group)
  ) +
    ggplot2::geom_col(width = cfg$bar_width, show.legend = isTRUE(cfg$highlight_legend))

  benchmark_value <- cfg$benchmark_value
  if (is.null(benchmark_value) && isTRUE(cfg$show_benchmark) && "benchmark_value" %in% names(plot_data)) {
    bench_values <- unique(stats::na.omit(plot_data$benchmark_value))
    if (length(bench_values) == 1) {
      benchmark_value <- bench_values[[1]]
    }
  }

  if (isTRUE(cfg$show_benchmark) && is.finite(benchmark_value)) {
    benchmark <- benchmark_layer(
      data = plot_data,
      orientation = "horizontal",
      intercept = benchmark_value,
      label = cfg$benchmark_label,
      value = benchmark_value,
      value_style = cfg$label_style,
      accuracy = cfg$label_accuracy,
      config = cfg
    )
    p <- apply_benchmark_layer(p, benchmark)
  }

  formatter <- bar_axis_formatter(
    label_style = cfg$label_style,
    accuracy = cfg$label_accuracy
  )

  if (isTRUE(cfg$show_axis_labels)) {
    p <- p + ggplot2::scale_y_continuous(
      labels = formatter,
      expand = ggplot2::expansion(mult = c(cfg$axis_expand_lower, cfg$axis_expand_upper))
    )
  } else {
    p <- p + ggplot2::scale_y_continuous(
      labels = NULL,
      breaks = ggplot2::waiver(),
      expand = ggplot2::expansion(mult = c(cfg$axis_expand_lower, cfg$axis_expand_upper))
    )
  }

  if (isTRUE(cfg$show_labels)) {
    value_range <- range(plot_data[[value_var]], na.rm = TRUE)
    offset <- diff(value_range) * 0.025
    if (!is.finite(offset) || offset == 0) {
      offset <- max(abs(value_range), na.rm = TRUE) * 0.04
    }
    if (!is.finite(offset) || offset == 0) {
      offset <- 0.5
    }

    plot_data$label_value <- bar_value_labeler(
      plot_data[[value_var]],
      label_style = cfg$label_style,
      accuracy = cfg$label_accuracy
    )
    plot_data$label_position <- ifelse(
      plot_data[[value_var]] >= 0,
      plot_data[[value_var]] + offset,
      plot_data[[value_var]] - offset
    )
    plot_data$label_hjust <- ifelse(plot_data[[value_var]] >= 0, 0, 1)

    p <- p +
      ggplot2::geom_text(
        data = plot_data,
        ggplot2::aes(y = .data$label_position, label = .data$label_value),
        hjust = plot_data$label_hjust,
        size = cfg$label_size,
        color = visual_neutral_palette()$text,
        show.legend = FALSE
      )
  }

  if (!is.null(fill_scale)) {
    p <- p + fill_scale
  }

  if (isTRUE(cfg$flip %||% TRUE)) {
    p <- p + ggplot2::coord_flip(clip = "off")
  }

  p <- apply_plot_labels(
    plot = p,
    data = plot_data,
    title = cfg$title %||% default_chart_title("bar", unique(plot_data$metric_label)[1] %||% NULL),
    subtitle = cfg$subtitle %||% build_bar_subtitle(plot_data, cfg),
    x = NULL,
    y = cfg$y_label %||% unique(plot_data$metric_label)[1] %||% NULL,
    side_note = compact_chr(c(cfg$caption_side_note, build_bar_caption_note(plot_data, cfg))),
    footer_note = cfg$caption_footer_note,
    methodology_note = cfg$caption_methodology_note
  )

  p + (theme %||% resolve_chart_theme(cfg)) +
    ggplot2::theme(
      axis.title.y = ggplot2::element_blank(),
      panel.grid.major.y = ggplot2::element_blank(),
      panel.grid.minor = ggplot2::element_blank(),
      legend.title = ggplot2::element_blank(),
      plot.margin = ggplot2::margin(t = 12, r = cfg$right_margin_pt, b = 12, l = 12)
    )
}
