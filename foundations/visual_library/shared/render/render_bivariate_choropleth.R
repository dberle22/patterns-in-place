# Render bivariate choropleth map or fallback panel.
#
# How to use this file:
# - Call render_bivariate_choropleth(prepped_df, config = list(...)) after
#   prep_bivariate_choropleth().
# - prepped_df should be an sf object with geometry, x_bin, y_bin, and
#   bivar_class. If geometry is missing, this returns a placeholder panel.
# - Most callers only change title/subtitle, composition_preset, context_layers,
#   facet_by, border styling, and caption notes.
# - The bivariate key is drawn beside the map with patchwork when available.

source("visual_library/shared/chart_utils.R")

bivariate_palette_values <- function(x_levels, y_levels, palette = NULL) {
  # palette may be a named vector keyed by bivar_class, e.g. c("1-1" = ...).
  # If all class names are present, the caller's palette wins.
  classes <- as.vector(outer(x_levels, y_levels, paste, sep = "-"))
  if (!is.null(palette)) {
    missing_classes <- setdiff(classes, names(palette))
    if (length(missing_classes) == 0) {
      return(palette[classes])
    }
  }

  if (length(x_levels) == 3 && length(y_levels) == 3) {
    # Default 3x3 palette: light/low in the lower-left, stronger cyan/purple
    # tradeoff corners, and deepest blue for high-high.
    values <- c(
      "1-1" = "#e8e8e8", "2-1" = "#dfb0d6", "3-1" = "#be64ac",
      "1-2" = "#ace4e4", "2-2" = "#a5add3", "3-2" = "#8c62aa",
      "1-3" = "#5ac8c8", "2-3" = "#5698b9", "3-3" = "#3b4994"
    )
    return(values[classes])
  }

  generated <- grDevices::colorRampPalette(c("#e8e8e8", "#ace4e4", "#8c62aa", "#3b4994"))(length(classes))
  stats::setNames(generated, classes)
}

bivariate_legend_plot <- function(palette_values,
                                  x_levels,
                                  y_levels,
                                  x_label,
                                  y_label,
                                  config = list()) {
  # The legend is a real ggplot so it can be composed with the map and exported
  # consistently. Axis labels describe the direction of higher values.
  cfg <- resolve_chart_config(config = config)
  legend_df <- expand.grid(
    x_bin = x_levels,
    y_bin = y_levels,
    KEEP.OUT.ATTRS = FALSE,
    stringsAsFactors = FALSE
  )
  legend_df$bivar_class <- paste(legend_df$x_bin, legend_df$y_bin, sep = "-")
  legend_df$x_bin <- factor(legend_df$x_bin, levels = x_levels)
  legend_df$y_bin <- factor(legend_df$y_bin, levels = y_levels)

  ggplot2::ggplot(legend_df, ggplot2::aes(x = .data$x_bin, y = .data$y_bin, fill = .data$bivar_class)) +
    ggplot2::geom_tile(color = "white", linewidth = 0.45) +
    ggplot2::scale_fill_manual(values = palette_values, guide = "none", drop = FALSE) +
    ggplot2::labs(
      title = "Bivariate key",
      x = paste("Higher", x_label, "->"),
      y = paste("Higher", y_label, "->")
    ) +
    ggplot2::coord_equal(expand = FALSE) +
    visual_theme(
      base_size = max((cfg$base_size %||% 11.8) - 1.4, 8),
      base_family = cfg$base_family,
      mode = cfg$output_mode,
      background = cfg$background_fill,
      grid = "none",
      legend_position = "none"
    ) +
    ggplot2::theme(
      plot.title = ggplot2::element_text(size = ggplot2::rel(0.95), margin = ggplot2::margin(b = 6)),
      axis.text = ggplot2::element_text(size = ggplot2::rel(0.75)),
      axis.title.x = ggplot2::element_text(size = ggplot2::rel(0.8), margin = ggplot2::margin(t = 7)),
      axis.title.y = ggplot2::element_text(size = ggplot2::rel(0.8), margin = ggplot2::margin(r = 7)),
      plot.margin = ggplot2::margin(8, 8, 8, 8)
    )
}

render_bivariate_choropleth <- function(data, config = list(), theme = NULL) {
  cfg <- merge_chart_config(
    chart_default_config("map"),
    merge_chart_config(
      list(
        # fill_field defaults to bivar_class. Override only when experimenting
        # with an alternate precomputed class column.
        fill_field = "bivar_class",
        legend_position = "right",
        # Set show_bivariate_key = FALSE for notebooks where a separate legend
        # is handled outside the map.
        show_bivariate_key = TRUE,
        # Larger values give the side key more horizontal room.
        bivariate_key_width = 1.1,
        show_borders = TRUE,
        border_color = "white",
        border_linewidth = 0.12,
        show_highlight_outline = TRUE,
        highlight_outline_color = NULL,
        highlight_outline_linewidth = 0.5,
        context_data = NULL,
        context_layers = NULL,
        context_fill = NA,
        context_color = "#9AA5B1",
        context_linewidth = 0.25,
        # facet_by works like choropleth: pass a column name, commonly
        # time_window, and optionally facet_ncol.
        facet_by = NULL,
        facet_ncol = NULL,
        xlim = NULL,
        ylim = NULL,
        # Named palette override for bivar_class colors.
        palette_values = NULL
      ),
      config
    )
  )
  cfg <- merge_chart_config(
    cfg,
    resolve_map_composition_preset(
      # Reuses shared choropleth map presets: national_compact,
      # facet_national, local_focus, or none.
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

  if (!("geometry" %in% names(data)) || !inherits(data, "sf") || !requireNamespace("sf", quietly = TRUE)) {
    # This makes contract/scaffold tests readable instead of failing deep in
    # geom_sf(). Real review maps should not hit this path.
    return(
      render_placeholder_panel(
        data = data,
        chart_type = "bivariate_choropleth",
        title = cfg$title %||% "Bivariate Choropleth Scaffold",
        subtitle = cfg$subtitle,
        detail_lines = c("Geometry-backed rendering requires an sf object in the geometry column."),
        config = cfg
      )
    )
  }

  fill_field <- cfg$fill_field %||% "bivar_class"
  if (!(fill_field %in% names(data))) {
    stop(sprintf("Bivariate choropleth fill field '%s' not found.", fill_field))
  }

  plot_data <- data
  attr(plot_data, "chart_config") <- resolve_chart_config(config = cfg)

  x_levels <- cfg$x_bin_levels %||% sort(unique(stats::na.omit(as.character(plot_data$x_bin))))
  y_levels <- cfg$y_bin_levels %||% sort(unique(stats::na.omit(as.character(plot_data$y_bin))))
  # x_levels/y_levels control legend order and which palette entries appear.
  # Override them in config if you use custom labels instead of 1/2/3.
  palette_values <- bivariate_palette_values(x_levels, y_levels, cfg$palette_values)

  p <- ggplot2::ggplot(plot_data)

  if (!is.null(cfg$context_layers) && length(cfg$context_layers) > 0) {
    # Context layers are optional sf outlines, usually states or the US outline.
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

  if (!is.null(cfg$context_data) && inherits(cfg$context_data, "sf")) {
    p <- p + ggplot2::geom_sf(
      data = cfg$context_data,
      inherit.aes = FALSE,
      fill = cfg$context_fill,
      color = cfg$context_color,
      linewidth = cfg$context_linewidth
    )
  }

  p <- p +
    ggplot2::geom_sf(
      ggplot2::aes(fill = .data[[fill_field]]),
      color = if (isTRUE(cfg$show_borders)) cfg$border_color else NA,
      linewidth = cfg$border_linewidth
    ) +
    ggplot2::scale_fill_manual(
      values = palette_values,
      na.value = cfg$na_fill,
      drop = FALSE,
      guide = "none"
    )

  if (isTRUE(cfg$show_highlight_outline) &&
      "highlight_flag" %in% names(plot_data) &&
      any(plot_data$highlight_flag %in% TRUE, na.rm = TRUE)) {
    # highlight_flag is meant for sparse callouts; avoid outlining many geos.
    p <- p + ggplot2::geom_sf(
      data = plot_data[plot_data$highlight_flag %in% TRUE, , drop = FALSE],
      fill = NA,
      color = cfg$highlight_outline_color %||% cfg$highlight_color,
      linewidth = cfg$highlight_outline_linewidth
    )
  }

  if (!is.null(cfg$facet_by) && cfg$facet_by %in% names(plot_data)) {
    p <- p + ggplot2::facet_wrap(stats::as.formula(paste("~", cfg$facet_by)), ncol = cfg$facet_ncol)
  }

  x_label <- cfg$x_label %||% unique(stats::na.omit(plot_data$x_label))[1] %||% "X metric"
  y_label <- cfg$y_label %||% unique(stats::na.omit(plot_data$y_label))[1] %||% "Y metric"
  p <- apply_plot_labels(
    p,
    data = plot_data,
    title = cfg$title %||% paste("Bivariate map:", x_label, "and", y_label),
    subtitle = cfg$subtitle,
    caption = chart_caption_from_config(plot_data, cfg)
  )

  final_theme <- theme %||% resolve_chart_theme(cfg, map = TRUE)
  if (!is.null(cfg$plot_margin)) {
    final_theme <- final_theme + ggplot2::theme(plot.margin = cfg$plot_margin)
  }

  map_plot <- p + ggplot2::coord_sf(datum = NA, xlim = cfg$xlim, ylim = cfg$ylim) + final_theme

  if (!isTRUE(cfg$show_bivariate_key) || !requireNamespace("patchwork", quietly = TRUE)) {
    # Without patchwork, return the map alone rather than failing the render.
    return(map_plot)
  }

  key_plot <- bivariate_legend_plot(
    palette_values = palette_values,
    x_levels = x_levels,
    y_levels = y_levels,
    x_label = x_label,
    y_label = y_label,
    config = cfg
  )

  map_plot + key_plot + patchwork::plot_layout(widths = c(4, cfg$bivariate_key_width))
}
