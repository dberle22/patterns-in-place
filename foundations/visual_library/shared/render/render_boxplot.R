# Render grouped boxplots.

source("visual_library/shared/chart_utils.R")

boxplot_axis_formatter <- function(style = "number", accuracy = NULL, compact = TRUE) {
  value_label_formatter(
    style = style,
    accuracy = accuracy,
    compact = compact
  )
}

boxplot_metric_label <- function(data) {
  labels <- unique(stats::na.omit(data$metric_label))
  if (length(labels) > 0) labels[[1]] else "Metric value"
}

build_boxplot_title <- function(data, config) {
  if (is_nonempty_string(config$title)) {
    return(config$title)
  }

  geo_levels <- unique(stats::na.omit(data$geo_level))
  metric <- boxplot_metric_label(data)
  geo_label <- if (length(geo_levels) == 1) paste0(geo_levels[[1]], " distribution") else "distribution"
  paste(metric, "by", config$group_label %||% "group", "-", geo_label)
}

build_boxplot_subtitle <- function(data, config) {
  if (is_nonempty_string(config$subtitle)) {
    return(config$subtitle)
  }

  windows <- unique(stats::na.omit(data$time_window))
  groups <- unique(stats::na.omit(as.character(data$box_group)))
  parts <- c()
  if (length(windows) == 1) {
    parts <- c(parts, paste("Time window:", windows[[1]]))
  }
  parts <- c(parts, paste("Grouped by", config$group_label %||% "group"))
  if (length(groups) > 1 && config$order_groups %in% c("median_desc", "median_asc")) {
    parts <- c(parts, "Groups ordered by median")
  }
  if (isTRUE(config$winsorize_display) && !is.null(config$trim_quantiles)) {
    parts <- c(parts, "Displayed values are winsorized for readability")
  }
  paste(parts, collapse = " | ")
}

build_boxplot_caption_note <- function(data, config) {
  notes <- c(config$caption_side_note)

  missing_n <- unique(stats::na.omit(data$missing_metric_count))
  if (length(missing_n) > 0 && missing_n[[1]] > 0) {
    notes <- c(notes, paste0("Dropped ", missing_n[[1]], " rows with missing metric values."))
  }

  if ("highlight_flag" %in% names(data) && any(data$highlight_flag %in% TRUE, na.rm = TRUE)) {
    notes <- c(notes, "Highlighted points show selected geographies overlaid on the distribution.")
  }

  if (!is.null(config$trim_quantiles) && !isTRUE(config$winsorize_display)) {
    notes <- c(notes, "Extreme display tails were trimmed before plotting.")
  }

  paste(compact_chr(notes), collapse = " ")
}

render_boxplot <- function(data, config = list(), theme = NULL) {
  cfg <- resolve_chart_config(
    "boxplot",
    merge_chart_config(
      list(
        value_field = "plot_value",
        group_field = "box_group",
        group_label = "group",
        label_style = "number",
        label_accuracy = NULL,
        label_compact = TRUE,
        facet_by = NULL,
        facet_ncol = NULL,
        show_benchmark = FALSE,
        benchmark_method = "median",
        benchmark_value = NULL,
        benchmark_label = NULL,
        benchmark_label_position = NULL,
        show_outliers = TRUE
      ),
      config
    )
  )

  ensure_columns(data, c(cfg$value_field, cfg$group_field, "metric_label"), chart_type = "boxplot")

  plot_data <- data
  if ("highlight_flag" %in% names(plot_data)) {
    plot_data$highlight_flag <- coerce_logical_column(plot_data$highlight_flag)
  } else {
    plot_data$highlight_flag <- FALSE
  }
  if ("label_flag" %in% names(plot_data)) {
    plot_data$label_flag <- coerce_logical_column(plot_data$label_flag)
  } else {
    plot_data$label_flag <- FALSE
  }

  neutrals <- visual_neutral_palette()
  p <- ggplot2::ggplot(
    plot_data,
    ggplot2::aes(x = .data[[cfg$group_field]], y = .data[[cfg$value_field]])
  )

  if (isTRUE(cfg$show_jitter)) {
    p <- p + ggplot2::geom_jitter(
      width = cfg$jitter_width,
      height = 0,
      size = 1.2,
      alpha = cfg$point_alpha,
      color = neutrals$outline
    )
  }

  p <- p + ggplot2::geom_boxplot(
    width = cfg$box_width,
    fill = cfg$neutral_color,
    color = neutrals$text_muted,
    alpha = cfg$box_alpha,
    linewidth = 0.35,
    outlier.alpha = if (isTRUE(cfg$show_outliers)) cfg$outlier_alpha else 0,
    outlier.size = cfg$outlier_size,
    outlier.color = neutrals$outline
  )

  if (isTRUE(cfg$show_benchmark)) {
    benchmark_value <- cfg$benchmark_value %||%
      if ("benchmark_value" %in% names(plot_data) &&
          any(is.finite(suppressWarnings(as.numeric(plot_data$benchmark_value))))) {
        stats::median(suppressWarnings(as.numeric(plot_data$benchmark_value)), na.rm = TRUE)
      } else {
        derive_reference_value(plot_data, cfg$value_field, method = cfg$benchmark_method)
      }

    p <- apply_benchmark_layer(
      p,
      benchmark_layer(
        plot_data,
        orientation = "horizontal",
        intercept = benchmark_value,
        label = cfg$benchmark_label %||% "Reference",
        value = benchmark_value,
        value_style = cfg$label_style,
        accuracy = cfg$label_accuracy,
        config = cfg,
        position = cfg$benchmark_label_position
      )
    )
  }

  highlight_df <- plot_data[plot_data$highlight_flag %in% TRUE, , drop = FALSE]
  if (isTRUE(cfg$show_highlights) && nrow(highlight_df) > 0) {
    p <- p + ggplot2::geom_point(
      data = highlight_df,
      ggplot2::aes(x = .data[[cfg$group_field]], y = .data[[cfg$value_field]]),
      inherit.aes = FALSE,
      shape = 21,
      size = 2.7,
      stroke = 0.85,
      fill = neutrals$background_white,
      color = cfg$highlight_color
    )
  }

  label_df <- pick_label_rows(plot_data, value_col = cfg$value_field, top_n = cfg$label_top_n)
  if (isTRUE(cfg$show_highlight_labels) && nrow(label_df) > 0) {
    p <- p + label_layer(
      data = label_df,
      mapping = ggplot2::aes(
        x = .data[[cfg$group_field]],
        y = .data[[cfg$value_field]],
        label = .data$geo_name
      ),
      config = cfg,
      boxed = TRUE,
      repel = TRUE
    )
  }

  if (!is.null(cfg$facet_by) && cfg$facet_by %in% names(plot_data)) {
    p <- p + ggplot2::facet_wrap(
      stats::as.formula(paste("~", cfg$facet_by)),
      ncol = cfg$facet_ncol %||% NULL,
      scales = cfg$facet_scales %||% "fixed"
    )
  }

  p <- p +
    ggplot2::scale_y_continuous(
      labels = boxplot_axis_formatter(cfg$label_style, cfg$label_accuracy, cfg$label_compact),
      expand = ggplot2::expansion(mult = c(0.04, 0.08))
    ) +
    ggplot2::scale_x_discrete(drop = FALSE)

  if (isTRUE(cfg$flip)) {
    p <- p + ggplot2::coord_flip(clip = "off")
  } else {
    p <- p + ggplot2::coord_cartesian(clip = "off")
  }

  p <- apply_plot_labels(
    p,
    data = plot_data,
    title = build_boxplot_title(plot_data, cfg),
    subtitle = build_boxplot_subtitle(plot_data, cfg),
    x = cfg$group_label %||% NULL,
    y = cfg$value_label %||% boxplot_metric_label(plot_data),
    caption = chart_caption_from_config(
      plot_data,
      cfg,
      caption = build_chart_notes(
        source = extract_chart_metadata(plot_data, "source"),
        vintage = extract_chart_metadata(plot_data, "vintage"),
        side_note = build_boxplot_caption_note(plot_data, cfg),
        footer_note = cfg$caption_footer_note,
        methodology_note = cfg$caption_methodology_note
      )
    )
  )

  p + (theme %||% resolve_chart_theme(cfg)) +
    ggplot2::theme(
      panel.grid.minor = ggplot2::element_blank(),
      axis.title.y = ggplot2::element_text(margin = ggplot2::margin(r = 8))
    )
}
