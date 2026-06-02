# Render proportional symbol map or fallback panel.

source("visual_library/shared/chart_utils.R")

render_proportional_symbol_map <- function(data, config = list(), theme = NULL) {
  # Avoid scales::cut_short_scale() here: ggplot can ask legend formatters to
  # label NA breaks, and the compact formatter currently errors on that path.
  format_symbol_values <- function(values, style = "number", accuracy = NULL) {
    if (identical(style, "percent")) {
      return(format_value_vector(values, style = "percent", accuracy = accuracy, compact = FALSE))
    }
    if (identical(style, "dollar")) {
      return(format_value_vector(values, style = "dollar", accuracy = accuracy, compact = TRUE))
    }
    values <- suppressWarnings(as.numeric(values))
    abs_values <- abs(values)
    scaled <- values
    suffix <- rep("", length(values))
    million <- is.finite(abs_values) & abs_values >= 1e6
    thousand <- is.finite(abs_values) & abs_values >= 1e3 & abs_values < 1e6
    scaled[million] <- values[million] / 1e6
    suffix[million] <- "M"
    scaled[thousand] <- values[thousand] / 1e3
    suffix[thousand] <- "K"
    formatted <- scales::label_number(
      accuracy = accuracy %||% 0.1,
      big.mark = ",",
      trim = TRUE
    )(scaled)
    formatted[!is.finite(values)] <- NA_character_
    paste0(formatted, suffix)
  }

  cfg <- merge_chart_config(
    chart_default_config("map"),
    merge_chart_config(
      list(
        size_range = c(2.5, 18),
        max_size_breaks = 4,
        size_label = NULL,
        legend_title = NULL,
        legend_position = "right",
        point_alpha = 0.72,
        point_color = "#FFFFFF",
        point_stroke = 0.28,
        color_mode = c("none", "color_group", "highlight"),
        color_group_palette = NULL,
        highlight_fill = NULL,
        comparison_fill = NULL,
        show_context = TRUE,
        context_data = NULL,
        context_layers = NULL,
        context_fill = NA,
        context_color = "#C4CFD9",
        context_linewidth = 0.2,
        label_field = NULL,
        label_top_n = NULL,
        label_highlights = FALSE,
        label_include_value = TRUE,
        value_style = "number",
        value_accuracy = NULL,
        xlim = NULL,
        ylim = NULL
      ),
      config
    )
  )
  cfg$color_mode <- match.arg(cfg$color_mode, c("none", "color_group", "highlight"))
  # Reuse choropleth map composition presets so map-family charts share framing,
  # subtitle wrapping, and contiguous-US defaults.
  cfg <- merge_chart_config(
    cfg,
    resolve_map_composition_preset(
      preset = cfg$composition_preset %||% "none",
      data = data,
      config = cfg
    )
  )

  if (is.null(cfg$xlim) && is.null(cfg$ylim)) {
    extent_limits <- map_extent_limits(cfg$map_extent %||% "data")
    cfg$xlim <- extent_limits$xlim
    cfg$ylim <- extent_limits$ylim
  }

  if (!all(c("lon", "lat") %in% names(data))) {
    return(
      render_placeholder_panel(
        data,
        "proportional_symbol_map",
        cfg$title %||% "Proportional Symbol Map Scaffold",
        cfg$subtitle,
        detail_lines = c("Rendering requires lon and lat columns or prep-derived coordinates.")
      )
    )
  }

  plot_data <- data[is.finite(data$lon) & is.finite(data$lat) & is.finite(data$size_value), , drop = FALSE]
  if (nrow(plot_data) == 0) {
    return(
      render_placeholder_panel(
        data,
        "proportional_symbol_map",
        cfg$title %||% "Proportional Symbol Map Scaffold",
        cfg$subtitle,
        detail_lines = c("No finite coordinates and size values were available after filtering.")
      )
    )
  }

  attr(plot_data, "chart_config") <- resolve_chart_config(
    chart_type = "proportional_symbol_map",
    config = cfg
  )

  p <- ggplot2::ggplot()

  # Context layers are intentionally drawn before symbols: boundaries orient the
  # reader without competing with bubble size as the primary encoding.
  if (isTRUE(cfg$show_context) && !is.null(cfg$context_layers) && length(cfg$context_layers) > 0) {
    for (layer_cfg in cfg$context_layers) {
      if (is.null(layer_cfg$data) || !inherits(layer_cfg$data, "sf")) {
        next
      }
      p <- p + ggplot2::geom_sf(
        data = layer_cfg$data,
        inherit.aes = FALSE,
        fill = layer_cfg$fill %||% NA,
        color = layer_cfg$color %||% cfg$context_color,
        linewidth = layer_cfg$linewidth %||% cfg$context_linewidth
      )
    }
  }

  if (isTRUE(cfg$show_context) && !is.null(cfg$context_data) && inherits(cfg$context_data, "sf")) {
    p <- p + ggplot2::geom_sf(
      data = cfg$context_data,
      inherit.aes = FALSE,
      fill = cfg$context_fill,
      color = cfg$context_color,
      linewidth = cfg$context_linewidth
    )
  }

  # Color is secondary to size. Highlight mode uses identity fill so the legend
  # stays focused on symbol scale unless a group legend is explicitly requested.
  if (identical(cfg$color_mode, "highlight") && "highlight_flag" %in% names(plot_data)) {
    plot_data$symbol_fill <- ifelse(
      plot_data$highlight_flag %in% TRUE,
      cfg$highlight_fill %||% cfg$highlight_color,
      cfg$comparison_fill %||% cfg$neutral_color
    )
    p <- p + ggplot2::geom_point(
      data = plot_data,
      ggplot2::aes(x = .data$lon, y = .data$lat, size = .data$size_value, fill = .data$symbol_fill),
      shape = 21,
      alpha = cfg$point_alpha,
      color = cfg$point_color,
      stroke = cfg$point_stroke
    ) +
      ggplot2::scale_fill_identity(guide = "none")
  } else if (identical(cfg$color_mode, "color_group") && "color_group" %in% names(plot_data)) {
    group_levels <- sort(unique(stats::na.omit(as.character(plot_data$color_group))))
    group_palette <- cfg$color_group_palette %||% resolve_peer_palette(length(group_levels))
    p <- p + ggplot2::geom_point(
      data = plot_data,
      ggplot2::aes(x = .data$lon, y = .data$lat, size = .data$size_value, fill = .data$color_group),
      shape = 21,
      alpha = cfg$point_alpha,
      color = cfg$point_color,
      stroke = cfg$point_stroke
    ) +
      ggplot2::scale_fill_manual(
        values = stats::setNames(group_palette[seq_along(group_levels)], group_levels),
        name = cfg$color_legend_title %||% "Group",
        drop = FALSE
      )
  } else {
    p <- p + ggplot2::geom_point(
      data = plot_data,
      ggplot2::aes(x = .data$lon, y = .data$lat, size = .data$size_value),
      shape = 21,
      fill = cfg$base_color,
      alpha = cfg$point_alpha,
      color = cfg$point_color,
      stroke = cfg$point_stroke
    )
  }

  size_label_values <- unique(stats::na.omit(plot_data$size_label))
  default_size_label <- if (length(size_label_values) > 0) size_label_values[[1]] else NULL
  # scale_size_area maps values to bubble area, which keeps radius from
  # exaggerating large totals.
  size_breaks <- scales::breaks_pretty(n = cfg$max_size_breaks)(range(plot_data$size_value, na.rm = TRUE))
  size_breaks <- size_breaks[is.finite(size_breaks) & size_breaks > 0]
  size_label_formatter <- function(x) {
    out <- rep(NA_character_, length(x))
    keep <- is.finite(x)
    out[keep] <- format_symbol_values(x[keep], style = cfg$value_style, accuracy = cfg$value_accuracy)
    out
  }

  p <- p + ggplot2::scale_size_area(
    max_size = max(cfg$size_range),
    breaks = size_breaks,
    labels = size_label_formatter,
    name = cfg$legend_title %||% cfg$size_label %||% default_size_label
  )

  # Highlighting and labeling are deliberately decoupled. Dense Top-N maps can
  # highlight many points but still label only a small readable subset.
  label_rows <- pick_label_rows(
    plot_data,
    flag_col = "label_flag",
    highlight_col = if (isTRUE(cfg$label_highlights)) "highlight_flag" else "__no_highlight_labels__",
    value_col = "size_value",
    top_n = cfg$label_top_n
  )
  if (nrow(label_rows) > 0) {
    label_field <- cfg$label_field %||% "geo_name"
    label_rows$label_text <- as.character(label_rows[[label_field]])
    if (isTRUE(cfg$label_include_value)) {
      label_rows$label_text <- paste0(
        label_rows$label_text,
        "\n",
        format_symbol_values(label_rows$size_value, style = cfg$value_style, accuracy = cfg$value_accuracy)
      )
    }
    p <- p + label_layer(
      label_rows,
      ggplot2::aes(x = .data$lon, y = .data$lat, label = .data$label_text),
      config = cfg,
      boxed = cfg$label_box,
      repel = TRUE,
      max.overlaps = Inf
    )
  }

  p <- apply_plot_labels(
    p,
    data = plot_data,
    title = cfg$title %||% default_chart_title("proportional_symbol_map", default_size_label),
    subtitle = cfg$subtitle,
    caption = chart_caption_from_config(plot_data, cfg)
  )

  final_theme <- theme %||% resolve_chart_theme(cfg, map = TRUE)
  if (!is.null(cfg$plot_margin)) {
    final_theme <- final_theme + ggplot2::theme(plot.margin = cfg$plot_margin)
  }

  p +
    ggplot2::coord_sf(datum = NA, xlim = cfg$xlim, ylim = cfg$ylim) +
    ggplot2::guides(
      size = ggplot2::guide_legend(override.aes = list(alpha = 0.72)),
      fill = ggplot2::guide_legend(override.aes = list(size = 5, alpha = 0.8))
    ) +
    final_theme
}
