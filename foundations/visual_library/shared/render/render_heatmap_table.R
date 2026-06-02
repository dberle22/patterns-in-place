# Render heatmap table.

source("visual_library/shared/chart_utils.R")

heatmap_table_method_note <- function(data, cfg) {
  variant <- extract_chart_metadata(data, "heatmap_variant") %||% cfg$variant %||% "geo_metric"
  fill_field <- cfg$fill_value_field %||% "normalized_value"
  fill_note <- if (identical(fill_field, "normalized_value")) {
    "Fill shows polarity-aligned percentile, where higher is better."
  } else {
    "Fill shows raw metric values; use only when units are comparable."
  }

  missing_n <- if ("missing_flag" %in% names(data)) sum(data$missing_flag %in% TRUE, na.rm = TRUE) else 0
  missing_note <- if (missing_n > 0) {
    paste0(missing_n, " missing cells are shown as No data.")
  } else {
    NULL
  }

  paste(compact_chr(c(
    paste("Matrix:", gsub("_", " x ", variant)),
    fill_note,
    missing_note
  )), collapse = " ")
}

heatmap_table_label_color <- function(fill_value, missing_flag) {
  out <- rep(visual_neutral_palette()$text, length(fill_value))
  out[is.finite(fill_value) & fill_value >= 78] <- "#FFFFFF"
  out[is.finite(fill_value) & fill_value <= 18] <- "#FFFFFF"
  out[missing_flag %in% TRUE] <- visual_neutral_palette()$text_muted
  out
}

render_heatmap_table <- function(data, config = list(), theme = NULL) {
  cfg <- resolve_chart_config(
    "heatmap_table",
    merge_chart_config(
      list(
        title = NULL,
        subtitle = NULL,
        fill_value_field = "normalized_value",
        legend_title = NULL,
        fill_limits = NULL,
        fill_breaks = NULL,
        show_cell_labels = NULL,
        auto_label_max_cells = 96,
        show_missing_labels = TRUE,
        missing_label = "No data",
        tile_linewidth = 0.35,
        label_size = NULL,
        missing_label_size = NULL,
        x_text_angle = 35,
        row_highlight_color = NULL,
        right_margin_pt = 18
      ),
      config
    )
  )

  ensure_columns(
    data,
    c("row_label", "column_label", "metric_value", "fill_value", "missing_flag"),
    chart_type = "heatmap_table"
  )

  plot_data <- data
  plot_data$missing_flag <- coerce_logical_column(plot_data$missing_flag)
  plot_data$label_color <- heatmap_table_label_color(plot_data$fill_value, plot_data$missing_flag)
  plot_data$label_to_show <- plot_data$cell_label %||% plot_data$fill_label
  plot_data$label_to_show[plot_data$missing_flag %in% TRUE] <- cfg$missing_label

  n_cells <- nrow(plot_data)
  show_cell_labels <- cfg$show_cell_labels %||% (n_cells <= cfg$auto_label_max_cells)
  fill_limits <- cfg$fill_limits %||% if (identical(cfg$fill_value_field, "normalized_value")) c(0, 100) else NULL
  fill_breaks <- cfg$fill_breaks %||% if (identical(cfg$fill_value_field, "normalized_value")) c(0, 25, 50, 75, 100) else ggplot2::waiver()
  legend_title <- cfg$legend_title %||% if (identical(cfg$fill_value_field, "normalized_value")) {
    "Better percentile"
  } else {
    "Value"
  }

  p <- ggplot2::ggplot(
    plot_data,
    ggplot2::aes(x = .data$column_label, y = .data$row_label, fill = .data$fill_value)
  ) +
    ggplot2::geom_tile(
      color = cfg$tile_color,
      linewidth = cfg$tile_linewidth
    )

  if ("highlight_flag" %in% names(plot_data) && any(plot_data$highlight_flag %in% TRUE, na.rm = TRUE)) {
    p <- p +
      ggplot2::geom_tile(
        data = plot_data[plot_data$highlight_flag %in% TRUE, , drop = FALSE],
        ggplot2::aes(x = .data$column_label, y = .data$row_label),
        inherit.aes = FALSE,
        fill = NA,
        color = cfg$row_highlight_color %||% cfg$highlight_color,
        linewidth = cfg$tile_linewidth * 1.8
      )
  }

  p <- p +
    ggplot2::scale_fill_gradient2(
      low = cfg$diverging_low,
      mid = cfg$diverging_mid,
      high = cfg$diverging_high,
      midpoint = if (!is.null(fill_limits) && length(fill_limits) == 2) mean(fill_limits) else 0,
      limits = fill_limits,
      breaks = fill_breaks,
      labels = if (identical(cfg$fill_value_field, "normalized_value")) scales::label_number(accuracy = 1) else scales::label_number(accuracy = 0.1, scale_cut = scales::cut_short_scale()),
      na.value = cfg$missing_fill,
      name = legend_title
    )

  if (isTRUE(show_cell_labels)) {
    label_df <- plot_data
    if (!isTRUE(cfg$show_missing_labels)) {
      label_df <- label_df[!label_df$missing_flag, , drop = FALSE]
    }
    value_label_df <- label_df[!label_df$missing_flag, , drop = FALSE]
    missing_label_df <- label_df[label_df$missing_flag %in% TRUE, , drop = FALSE]
    if (nrow(value_label_df) > 0) {
      p <- p +
        ggplot2::geom_text(
          data = value_label_df,
          ggplot2::aes(label = .data$label_to_show),
          color = value_label_df$label_color,
          size = cfg$label_size %||% 2.8,
          lineheight = 0.95
        )
    }
    if (nrow(missing_label_df) > 0) {
      p <- p +
        ggplot2::geom_text(
          data = missing_label_df,
          ggplot2::aes(label = .data$label_to_show),
          color = missing_label_df$label_color,
          size = cfg$missing_label_size %||% 2.4,
          lineheight = 0.95
        )
    }
  }

  p <- p + ggplot2::coord_cartesian(clip = "off")

  p <- apply_plot_labels(
    p,
    data = plot_data,
    title = cfg$title %||% "Heatmap Table",
    subtitle = cfg$subtitle,
    x = NULL,
    y = NULL,
    side_note = cfg$caption_side_note,
    footer_note = cfg$caption_footer_note,
    methodology_note = cfg$caption_methodology_note %||% heatmap_table_method_note(plot_data, cfg)
  )

  p +
    (theme %||% resolve_chart_theme(cfg)) +
    ggplot2::theme(
      axis.text.x = ggplot2::element_text(angle = cfg$x_text_angle, hjust = 1, vjust = 1),
      axis.text.y = ggplot2::element_text(hjust = 1),
      axis.ticks = ggplot2::element_blank(),
      panel.grid = ggplot2::element_blank(),
      legend.position = cfg$legend_position,
      plot.margin = ggplot2::margin(t = 12, r = cfg$right_margin_pt, b = 12, l = 12)
    )
}
