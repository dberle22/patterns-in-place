#!/usr/bin/env Rscript

# This visual compares current permit intensity with medium-run population
# growth. The quadrant framing helps separate growth markets that look more
# supply-responsive from those that are still adding people without much new
# building relative to existing stock.

source("publisher/content/housing/03_supply_character/visuals/_shared_supply_character_visuals.R")

script_path <- supply_get_script_path("publisher/content/housing/03_supply_character/visuals/cbsa_supply_vs_growth.R")
ctx <- supply_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_supply_vs_growth.png")

supply_load_visual_library(ctx$foundations_dir, chart_types = c("scatter"))

con <- supply_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

scatter_df <- supply_run_sql_file(con, ctx$sql_dir, "cbsa_supply_vs_growth.sql")
scatter_df <- prep_scatter(
  scatter_df,
  time_window = "2024_snapshot_vs_2019_2024_growth",
  require_single_geo_level = TRUE,
  drop_missing_xy = TRUE
)

scatter_df$group[is.na(scatter_df$group) | !nzchar(scatter_df$group)] <- "Unknown"
scatter_df$group <- factor(
  scatter_df$group,
  levels = c("Northeast", "Midwest", "South", "West", "Unknown")
)

if ("size_value" %in% names(scatter_df)) {
  finite_sizes <- scatter_df$size_value[is.finite(scatter_df$size_value)]
  if (length(finite_sizes) > 0) {
    scatter_df$size_value[!is.finite(scatter_df$size_value)] <- stats::median(finite_sizes, na.rm = TRUE)
  }
}

label_df <- scatter_df[scatter_df$label_flag %in% TRUE, , drop = FALSE]

median_x <- stats::median(scatter_df$x_value, na.rm = TRUE)
median_y <- stats::median(scatter_df$y_value, na.rm = TRUE)

caption_text <- build_chart_notes(
  source = "mart_housing.core_metrics",
  vintage = "2026-07-05",
  side_note = "Points are major CBSAs sized by 2024 population. Labels call out selected high-growth metros on both the high-supply and low-supply sides of the chart.",
  methodology_note = "X-axis uses 2024 permits per 1,000 housing units. Y-axis uses the 2024 five-year population growth field, which corresponds to 2019 to 2024 growth."
)

scatter_plot <- ggplot(
  scatter_df,
  aes(x = x_value, y = y_value, color = group, size = size_value)
) +
  geom_vline(
    xintercept = median_x,
    linetype = "dashed",
    linewidth = 0.45,
    color = visual_neutral_palette()$outline
  ) +
  geom_hline(
    yintercept = median_y,
    linetype = "dashed",
    linewidth = 0.45,
    color = visual_neutral_palette()$outline
  ) +
  geom_point(alpha = 0.78) +
  scale_color_brewer(palette = "Set2", na.translate = FALSE, name = NULL) +
  scale_size_continuous(
    range = c(2.2, 11),
    labels = scales::label_comma(),
    name = "2024 population"
  ) +
  scale_x_continuous(
    labels = scales::label_number(accuracy = 0.1),
    expand = expansion(mult = c(0.04, 0.1))
  ) +
  scale_y_continuous(
    labels = scales::label_number(accuracy = 1, suffix = "%"),
    expand = expansion(mult = c(0.05, 0.14))
  ) +
  labs(
    title = "Some of the fastest-growing metros were also building aggressively, but not all of them",
    subtitle = paste(
      "Major CBSAs, 2024 permits versus 2019 to 2024 population growth",
      "| The upper-left quadrant is where growth outran relatively weaker new-building intensity"
    ),
    x = unique(scatter_df$x_label)[1],
    y = unique(scatter_df$y_label)[1],
    caption = caption_text
  ) +
  visual_theme(base_size = 12.5, mode = "presentation", legend_position = "bottom")

if (nrow(label_df) > 0) {
  if (requireNamespace("ggrepel", quietly = TRUE)) {
    scatter_plot <- scatter_plot +
      ggrepel::geom_label_repel(
        data = label_df,
        aes(label = geo_name),
        size = 3.1,
        label.size = 0.15,
        seed = 123,
        min.segment.length = 0,
        max.overlaps = Inf,
        show.legend = FALSE
      )
  } else {
    scatter_plot <- scatter_plot +
      geom_text(
        data = label_df,
        aes(label = geo_name),
        size = 3,
        hjust = -0.1,
        show.legend = FALSE
      )
  }
}

supply_save_plot(
  scatter_plot,
  output_path = output_path,
  width = 10.8,
  height = 7.4
)

message(sprintf("Saved %s", output_path))
