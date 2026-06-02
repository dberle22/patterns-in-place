# Render scatter chart from prepared data.

render_scatter <- function(data,
                           title,
                           subtitle = NULL,
                           highlight_mode = c("none", "labels", "color"),
                           add_trend_line = TRUE,
                           add_reference_line = FALSE,
                           add_quadrants = FALSE,
                           palette = NULL,
                           point_alpha = NULL,
                           trend_line_alpha = NULL,
                           base_color = NULL,
                           highlight_color = NULL,
                           side_note = NULL,
                           footer_note = NULL) {
  stopifnot(is.data.frame(data))
  highlight_mode <- match.arg(highlight_mode)

  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    stop("Package 'ggplot2' is required.")
  }

  if (!exists("scatter_style_defaults", mode = "list")) {
    source("visual_library/shared/standards.R")
  }

  if (is.null(point_alpha)) point_alpha <- scatter_style_defaults$point_alpha
  if (is.null(palette)) palette <- scatter_style_defaults$palette
  if (is.null(trend_line_alpha)) trend_line_alpha <- scatter_style_defaults$trend_line_alpha
  if (is.null(base_color)) base_color <- scatter_style_defaults$base_color
  if (is.null(highlight_color)) highlight_color <- scatter_style_defaults$highlight_color

  plot_data <- data
  has_group <- "group" %in% names(plot_data)
  has_size <- "size_value" %in% names(plot_data)

  if (has_size) {
    plot_data$size_value <- suppressWarnings(as.numeric(plot_data$size_value))
    finite_sizes <- plot_data$size_value[is.finite(plot_data$size_value)]
    if (length(finite_sizes) == 0) {
      has_size <- FALSE
    } else {
      fill_size <- stats::median(finite_sizes, na.rm = TRUE)
      plot_data$size_value[!is.finite(plot_data$size_value)] <- fill_size
    }
  }

  if (!("label_flag" %in% names(plot_data))) {
    plot_data$label_flag <- FALSE
  }

  if (highlight_mode == "color") {
    plot_data$.color_flag <- ifelse(plot_data$label_flag %in% TRUE, "highlight", "base")
  }

  if (has_group) {
    plot_data$group <- as.character(plot_data$group)
    plot_data$group[is.na(plot_data$group) | !nzchar(plot_data$group)] <- "Unknown"
  }

  p <- ggplot2::ggplot(plot_data, ggplot2::aes(x = .data$x_value, y = .data$y_value))

  if (highlight_mode == "color") {
    p <- p + ggplot2::geom_point(
      ggplot2::aes(color = .data$.color_flag, size = if (has_size) .data$size_value else NULL),
      alpha = point_alpha
    ) +
      ggplot2::scale_color_manual(values = c(base = base_color, highlight = highlight_color), guide = "none")
  } else if (has_group) {
    p <- p + ggplot2::geom_point(
      ggplot2::aes(color = .data$group, size = if (has_size) .data$size_value else NULL),
      alpha = point_alpha
    )
    if (identical(palette, "viridis")) {
      p <- p + ggplot2::scale_color_viridis_d(option = "viridis", na.translate = FALSE)
    } else if (identical(palette, "set2")) {
      p <- p + ggplot2::scale_color_brewer(palette = "Set2", na.translate = FALSE)
    }
  } else {
    p <- p + ggplot2::geom_point(
      ggplot2::aes(size = if (has_size) .data$size_value else NULL),
      alpha = point_alpha,
      color = base_color
    )
  }

  if (add_trend_line) {
    p <- p + ggplot2::geom_smooth(
      method = "lm",
      se = FALSE,
      linewidth = 0.8,
      linetype = scatter_style_defaults$trend_line_linetype,
      color = scatter_style_defaults$trend_line_color,
      alpha = trend_line_alpha
    )
  }

  if (add_reference_line) {
    p <- p + ggplot2::geom_abline(slope = 1, intercept = 0, linetype = "dashed", linewidth = 0.6, color = "grey60")
  }

  if (add_quadrants) {
    p <- p +
      ggplot2::geom_vline(xintercept = stats::median(plot_data$x_value, na.rm = TRUE), linetype = "dashed", linewidth = 0.4, color = "grey60") +
      ggplot2::geom_hline(yintercept = stats::median(plot_data$y_value, na.rm = TRUE), linetype = "dashed", linewidth = 0.4, color = "grey60")
  }

  if (highlight_mode == "labels" && any(plot_data$label_flag)) {
    if (requireNamespace("ggrepel", quietly = TRUE)) {
      p <- p + ggrepel::geom_label_repel(
        data = plot_data[plot_data$label_flag %in% TRUE, , drop = FALSE],
        ggplot2::aes(label = .data$geo_name),
        size = scatter_style_defaults$label_size,
        label.size = scatter_style_defaults$label_outline_size,
        seed = 123,
        min.segment.length = 0,
        max.overlaps = Inf
      )
    } else {
      p <- p + ggplot2::geom_text(
        data = plot_data[plot_data$label_flag %in% TRUE, , drop = FALSE],
        ggplot2::aes(label = .data$geo_name),
        hjust = -0.1,
        size = scatter_style_defaults$label_size
      )
    }
  }

  if (has_size) {
    p <- p + ggplot2::scale_size_continuous(
      range = scatter_style_defaults$size_range,
      breaks = scatter_style_defaults$size_breaks,
      labels = scales::label_comma(),
      name = NULL
    )
  }

  cap <- if (all(c("source", "vintage") %in% names(plot_data))) {
    build_chart_notes(
      source = unique(plot_data$source)[1],
      vintage = unique(plot_data$vintage)[1],
      side_note = side_note,
      footer_note = footer_note
    )
  } else {
    build_chart_notes(
      side_note = side_note,
      footer_note = footer_note
    )
  }

  p <- p + ggplot2::labs(
    title = title,
    subtitle = subtitle,
    x = unique(plot_data$x_label)[1],
    y = unique(plot_data$y_label)[1],
    caption = cap
  )

  if (exists("visual_theme", mode = "function")) {
    p <- p + visual_theme(base_size = 12)
  } else {
    p <- p + ggplot2::theme_minimal(base_size = 12)
  }

  p
}
