# Render correlation heatmap.

source("visual_library/shared/chart_utils.R")

render_correlation_heatmap <- function(data, config = list(), theme = NULL) {
  cfg <- merge_chart_config(chart_default_config("correlation_heatmap"), config)
  ensure_columns(data, c("metric_x", "metric_y", "correlation"), chart_type = "correlation_heatmap")
  fill_col <- if ("correlation_display" %in% names(data)) "correlation_display" else "correlation"
  facet_by <- cfg$facet_by %||% if ("group" %in% names(data)) "group" else NULL
  show_cell_labels <- isTRUE(cfg$show_cell_labels) || (nlevels(data$metric_x) <= 8 && isTRUE(cfg$auto_cell_labels %||% TRUE))
  methodology_note <- cfg$caption_methodology_note %||%
    paste(
      toupper(substr(extract_chart_metadata(data, "method") %||% cfg$method %||% "spearman", 1, 1)),
      substring(extract_chart_metadata(data, "method") %||% cfg$method %||% "spearman", 2),
      "correlation | Missingness:",
      extract_chart_metadata(data, "missingness_policy") %||% cfg$missingness %||% "pairwise.complete.obs",
      "| Order:",
      extract_chart_metadata(data, "order_method") %||% cfg$order_method %||% "clustered"
    )

  p <- ggplot2::ggplot(
    data,
    ggplot2::aes(
      x = .data$metric_x,
      y = .data$metric_y,
      fill = .data[[fill_col]]
    )
  ) +
    ggplot2::geom_tile(color = cfg$tile_color, linewidth = 0.3) +
    ggplot2::scale_fill_gradient2(
      low = cfg$diverging_low,
      mid = cfg$diverging_mid,
      high = cfg$diverging_high,
      midpoint = 0,
      limits = c(-1, 1),
      breaks = c(-1, -0.5, 0, 0.5, 1),
      labels = scales::label_number(accuracy = 0.1),
      na.value = cfg$missing_fill,
      name = cfg$legend_title %||% "Correlation"
    ) +
    ggplot2::coord_equal()

  if (isTRUE(show_cell_labels) && "label" %in% names(data)) {
    label_df <- data
    if (fill_col %in% names(label_df)) {
      label_df <- label_df[!is.na(label_df[[fill_col]]), , drop = FALSE]
    }
    p <- p +
      ggplot2::geom_text(
        data = label_df,
        ggplot2::aes(label = .data$label),
        color = visual_neutral_palette()$text,
        size = cfg$cell_label_size %||% 3
      )
  }

  if (!is.null(facet_by) && facet_by %in% names(data)) {
    p <- p + ggplot2::facet_wrap(stats::as.formula(paste("~", facet_by)))
  }

  p <- apply_plot_labels(
    p,
    data = data,
    title = cfg$title %||% "Correlation Heatmap",
    subtitle = cfg$subtitle,
    x = NULL,
    y = NULL,
    side_note = cfg$caption_side_note,
    footer_note = cfg$caption_footer_note,
    methodology_note = methodology_note
  )

  p +
    (theme %||% resolve_chart_theme(cfg)) +
    ggplot2::theme(
      axis.text.x = ggplot2::element_text(angle = 40, hjust = 1, vjust = 1),
      axis.text.y = ggplot2::element_text(hjust = 1),
      axis.ticks = ggplot2::element_blank(),
      panel.grid = ggplot2::element_blank(),
      panel.spacing = grid::unit(1.1, "lines"),
      plot.margin = cfg$plot_margin
    )
}
