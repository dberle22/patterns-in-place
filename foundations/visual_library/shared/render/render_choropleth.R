# Render choropleth map or fallback summary panel.

source("visual_library/shared/chart_utils.R")

render_choropleth <- function(data, config = list(), theme = NULL) {
  cfg <- merge_chart_config(
    chart_default_config("map"),
    merge_chart_config(
      list(
        variant = c("continuous", "binned", "diverging"),
        fill_field = NULL,
        fill_label = NULL,
        legend_title = NULL,
        legend_position = "right",
        show_borders = TRUE,
        border_color = "white",
        border_linewidth = 0.12,
        context_linewidth = 0.3,
        show_highlight_outline = TRUE,
        highlight_outline_color = NULL,
        highlight_outline_linewidth = 0.5,
        context_data = NULL,
        context_layers = NULL,
        context_fill = NA,
        context_color = "#9AA5B1",
        context_linewidth = 0.25,
        facet_by = NULL,
        facet_ncol = NULL,
        trim_quantiles = NULL,
        midpoint = 0,
        xlim = NULL,
        ylim = NULL
      ),
      config
    )
  )
  cfg$variant <- match.arg(cfg$variant, c("continuous", "binned", "diverging"))
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

  if (!("geometry" %in% names(data)) || !inherits(data, "sf") || !requireNamespace("sf", quietly = TRUE)) {
    return(
      render_placeholder_panel(
        data = data,
        chart_type = "choropleth",
        title = cfg$title %||% "Choropleth Scaffold",
        subtitle = cfg$subtitle,
        detail_lines = c("Geometry-backed rendering requires an sf object in the geometry column.")
      )
    )
  }

  fill_field <- cfg$fill_field %||% if (identical(cfg$variant, "binned")) "bin" else "fill_value"
  if (!(fill_field %in% names(data))) {
    stop(sprintf("Choropleth fill field '%s' not found.", fill_field))
  }

  plot_data <- data
  if (!is.null(cfg$trim_quantiles) &&
      is.numeric(plot_data[[fill_field]])) {
    bounds <- stats::quantile(
      plot_data[[fill_field]],
      probs = cfg$trim_quantiles,
      na.rm = TRUE,
      names = FALSE,
      type = 7
    )
    plot_data[[fill_field]] <- pmin(pmax(plot_data[[fill_field]], bounds[[1]]), bounds[[2]])
  }

  attr(plot_data, "chart_config") <- resolve_chart_config(config = cfg)

  palette_values <- if (identical(cfg$binned_palette, "viridis")) {
    viridisLite::viridis(max(length(unique(stats::na.omit(plot_data[[fill_field]]))), 3))
  } else {
    grDevices::hcl.colors(max(length(unique(stats::na.omit(plot_data[[fill_field]]))), 3), palette = cfg$binned_palette)
  }

  p <- ggplot2::ggplot(plot_data)

  if (!is.null(cfg$context_layers) && length(cfg$context_layers) > 0) {
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

  p <- p + ggplot2::geom_sf(
      ggplot2::aes(fill = .data[[fill_field]]),
      color = if (isTRUE(cfg$show_borders)) cfg$border_color else NA,
      linewidth = cfg$border_linewidth
    )

  if (identical(cfg$variant, "binned")) {
    fill_levels <- sort(unique(stats::na.omit(as.character(plot_data[[fill_field]]))))
    p <- p + ggplot2::scale_fill_manual(
      values = stats::setNames(palette_values[seq_along(fill_levels)], fill_levels),
      na.value = cfg$na_fill,
      drop = FALSE,
      name = cfg$legend_title %||% cfg$fill_label %||% NULL
    )
  } else if (identical(cfg$variant, "diverging")) {
    p <- p + ggplot2::scale_fill_gradient2(
      low = cfg$diverging_low,
      mid = cfg$diverging_mid,
      high = cfg$diverging_high,
      midpoint = cfg$midpoint,
      na.value = cfg$na_fill,
      name = cfg$legend_title %||% cfg$fill_label %||% NULL
    )
  } else {
    p <- p + ggplot2::scale_fill_viridis_c(
      option = "viridis",
      na.value = cfg$na_fill,
      name = cfg$legend_title %||% cfg$fill_label %||% NULL
    )
  }

  if (isTRUE(cfg$show_highlight_outline) &&
      "highlight_flag" %in% names(plot_data) &&
      any(plot_data$highlight_flag %in% TRUE, na.rm = TRUE)) {
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

  p <- apply_plot_labels(
    p,
    data = plot_data,
    title = cfg$title %||% default_chart_title("choropleth", unique(plot_data$metric_label)[1] %||% NULL),
    subtitle = cfg$subtitle,
    caption = chart_caption_from_config(plot_data, cfg)
  )

  final_theme <- theme %||% resolve_chart_theme(cfg, map = TRUE)
  if (!is.null(cfg$plot_margin)) {
    final_theme <- final_theme + ggplot2::theme(plot.margin = cfg$plot_margin)
  }

  p + ggplot2::coord_sf(datum = NA, xlim = cfg$xlim, ylim = cfg$ylim) + final_theme
}
