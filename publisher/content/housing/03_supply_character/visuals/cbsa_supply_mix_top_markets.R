#!/usr/bin/env Rscript

# This visual pairs two stacked-bar views for the fastest-building major metros:
# one for the new permit mix and one for the current housing stock mix. Keeping
# the same metro order in both panels makes it easier to see where building
# patterns look more multifamily-heavy than the inherited stock.

source("publisher/content/housing/03_supply_character/visuals/_shared_supply_character_visuals.R")

script_path <- supply_get_script_path("publisher/content/housing/03_supply_character/visuals/cbsa_supply_mix_top_markets.R")
ctx <- supply_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_supply_mix_top_markets.png")

supply_load_visual_library(ctx$foundations_dir)

con <- supply_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

mix_df <- supply_run_sql_file(con, ctx$sql_dir, "cbsa_supply_mix_top_markets.sql")
mix_df$geo_name <- factor(
  mix_df$geo_name,
  levels = rev(unique(mix_df$geo_name[order(mix_df$permit_rank, mix_df$geo_name)]))
)

permits_df <- mix_df[mix_df$question_id == "supply_mix_permits", , drop = FALSE]
stock_df <- mix_df[mix_df$question_id == "supply_mix_stock", , drop = FALSE]

permits_palette <- c(
  "Single-unit permits" = "#A6B8C7",
  "Multifamily permits" = "#1D7F5F"
)

stock_palette <- c(
  "Single-unit stock" = "#A6B8C7",
  "Multifamily stock" = "#2C7FB8",
  "Other stock types" = "#D7DEE6"
)

build_mix_panel <- function(data, palette, title, subtitle = NULL) {
  ggplot(
    data,
    aes(x = geo_name, y = metric_value, fill = series)
  ) +
    geom_col(width = 0.76) +
    coord_flip(clip = "off") +
    scale_y_continuous(
      labels = scales::label_number(accuracy = 1, suffix = "%"),
      expand = expansion(mult = c(0, 0.02))
    ) +
    scale_fill_manual(values = palette, name = NULL) +
    labs(
      title = title,
      subtitle = subtitle,
      x = NULL,
      y = NULL
    ) +
    visual_theme(base_size = 12.2, mode = "presentation", legend_position = "bottom") +
    theme(
      plot.title = element_text(face = "bold"),
      panel.grid.major.y = element_blank(),
      panel.grid.minor = element_blank(),
      axis.text.y = element_text(size = rel(0.82))
    )
}

permits_plot <- build_mix_panel(
  permits_df,
  permits_palette,
  title = "New permits leaned more multifamily in some of the fastest-building metros",
  subtitle = "Top 15 major CBSAs by permits per 1,000 housing units, 2024"
)

stock_plot <- build_mix_panel(
  stock_df,
  stock_palette,
  title = "But the inherited housing stock in those markets is still mostly single-unit",
  subtitle = "Current housing-stock mix, using the same metro ordering"
)

caption_text <- build_chart_notes(
  source = "mart_housing.core_metrics",
  vintage = "2026-07-05",
  side_note = "Metros are ranked by 2024 permits per 1,000 housing units. The stock panel includes an Other category for mobile or uncategorized structure types.",
  methodology_note = "Permit mix uses single-unit versus multifamily permit shares. Stock mix uses the current structure shares on the 2024 section mart surface."
)

if (requireNamespace("patchwork", quietly = TRUE)) {
  combined_plot <- (permits_plot / stock_plot) +
    patchwork::plot_annotation(
      title = "What is being built still looks different from what already exists",
      subtitle = paste(
        "Fast-building major metros, 2024 | The top panel shows the new permit mix and the bottom panel shows the current stock mix",
        "| Together they show where supply is tilting more multifamily than the existing housing base"
      ),
      caption = caption_text,
      theme = theme(
        plot.title = element_text(
          family = visual_font_family(),
          face = "bold",
          size = 16,
          color = visual_neutral_palette()$text,
          hjust = 0
        ),
        plot.subtitle = element_text(
          family = visual_font_family(),
          size = 11,
          color = visual_neutral_palette()$text_muted,
          hjust = 0
        ),
        plot.caption = element_text(
          family = visual_font_family(),
          size = 8.8,
          color = visual_neutral_palette()$text_muted,
          hjust = 0
        )
      )
    )
} else {
  combined_plot <- permits_plot
}

supply_save_plot(
  combined_plot,
  output_path = output_path,
  width = 11.4,
  height = 12
)

message(sprintf("Saved %s", output_path))
