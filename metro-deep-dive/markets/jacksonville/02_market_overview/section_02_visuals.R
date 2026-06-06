# Section 02 visuals script
# Purpose: generate plots/tables from section outputs.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 02 visuals: 02_market_overview")

market_profile <- get_market_profile()
target_market_label <- market_label("market_name", market_profile)
target_flag_label <- market_label("target_flag", market_profile)
benchmark_region_label <- market_profile$benchmark_region_label

kpi_tiles <- readRDS(read_artifact_path("02_market_overview", "section_02_kpi_tiles"))
peer_table <- readRDS(read_artifact_path("02_market_overview", "section_02_peer_table"))
benchmark_table <- readRDS(read_artifact_path("02_market_overview", "section_02_benchmark_table"))
pop_trend_indexed <- readRDS(read_artifact_path("02_market_overview", "section_02_pop_trend_indexed"))
distribution_long <- readRDS(read_artifact_path("02_market_overview", "section_02_distribution_long"))
market_tract_sf <- readRDS(read_artifact_path("02_market_overview", "section_02_market_tract_sf"))
market_county_sf <- readRDS(read_artifact_path("02_market_overview", "section_02_market_county_sf"))

read_optional_sf <- function(section_id, artifact_name, subdir = NULL) {
  path <- tryCatch(
    read_artifact_path(section_id, artifact_name, subdir = subdir),
    error = function(e) NULL
  )
  if (is.null(path)) return(NULL)
  if (!file.exists(path)) return(NULL)
  obj <- readRDS(path)
  if (!inherits(obj, "sf")) return(NULL)
  if (nrow(obj) == 0) return(NULL)
  obj
}

context_cbsa_sf <- read_optional_sf("02_market_overview", "section_02_context_cbsa_boundary_sf", subdir = "context_layers")
context_county_sf <- read_optional_sf("02_market_overview", "section_02_context_county_sf", subdir = "context_layers")
context_places_sf <- read_optional_sf("02_market_overview", "section_02_context_places_sf", subdir = "context_layers")
context_roads_sf <- read_optional_sf("02_market_overview", "section_02_context_major_roads_sf", subdir = "context_layers")
context_water_sf <- read_optional_sf("02_market_overview", "section_02_context_water_sf", subdir = "context_layers")

align_crs <- function(x, target) {
  if (is.null(x)) return(NULL)
  if (is.na(sf::st_crs(x))) return(x)
  if (sf::st_crs(x) != sf::st_crs(target)) sf::st_transform(x, sf::st_crs(target)) else x
}

context_cbsa_sf <- align_crs(context_cbsa_sf, market_tract_sf)
context_county_sf <- align_crs(context_county_sf, market_tract_sf)
context_places_sf <- align_crs(context_places_sf, market_tract_sf)
context_roads_sf <- align_crs(context_roads_sf, market_tract_sf)
context_water_sf <- align_crs(context_water_sf, market_tract_sf)
market_county_sf <- align_crs(market_county_sf, market_tract_sf)

base_county_sf <- market_county_sf
if (!is.null(context_places_sf)) {
  context_places_sf <- suppressWarnings(sf::st_make_valid(context_places_sf)) %>%
    suppressWarnings(sf::st_filter(sf::st_union(base_county_sf), .predicate = sf::st_intersects))
}
if (!is.null(context_roads_sf)) {
  context_roads_sf <- suppressWarnings(sf::st_make_valid(context_roads_sf)) %>%
    suppressWarnings(sf::st_filter(sf::st_union(base_county_sf), .predicate = sf::st_intersects))
}
if (!is.null(context_water_sf)) {
  context_water_sf <- suppressWarnings(sf::st_make_valid(context_water_sf)) %>%
    suppressWarnings(sf::st_filter(sf::st_union(base_county_sf), .predicate = sf::st_intersects))
}

roads_plot_sf <- NULL
if (!is.null(context_roads_sf) && "MTFCC" %in% names(context_roads_sf)) {
  roads_plot_sf <- context_roads_sf %>%
    mutate(
      road_class = dplyr::case_when(
        MTFCC == "S1100" ~ "Primary highways",
        MTFCC == "S1200" ~ "Secondary highways",
        TRUE ~ "Other roads"
      )
    )
}

kpi_tile <- function(label, value, subtitle = NULL) {
  bslib::card(
    bslib::card_body(
      htmltools::tags$div(style = "font-size: 12px; color: #666;", label),
      htmltools::tags$div(style = "font-size: 28px; font-weight: 700; line-height: 1.1;", value),
      if (!is.null(subtitle)) htmltools::tags$div(style = "font-size: 11px; color: #888; margin-top: 6px;", subtitle)
    ),
    style = "height: 120px;"
  )
}

tiles_ui <- list(
  kpi_tile("Population (2024)", kpi_tiles$population_fmt),
  kpi_tile("Pop growth (5y)", kpi_tiles$pop_growth_5yr_fmt, "2019-2024 (ACS 5-year)"),
  kpi_tile("Units per 1k (3y avg)", kpi_tiles$units_per_1k_3yr_fmt, "BPS rolling avg"),
  kpi_tile("Median rent", kpi_tiles$median_rent_fmt),
  kpi_tile("Median home value", kpi_tiles$median_home_value_fmt),
  kpi_tile("Mean commute", kpi_tiles$mean_commute_min_fmt)
)

tiles_layout <- bslib::layout_column_wrap(width = 1 / 3, !!!tiles_ui)

peer_gt <- peer_table %>%
  arrange(pop_growth_rank) %>%
  gt::gt(rowname_col = "metro_name") %>%
  gt::tab_header(title = "Peer context: ranks and raw values (2024)") %>%
  gt::cols_label(
    pop_growth_rank = "Growth rank",
    pop_growth_5yr = "Pop growth (5y)",
    units_per_1k_rank = "Units rank",
    units_per_1k_3yr = "Units/1k (3y)",
    median_rent_rank = "Rent rank",
    median_rent = "Median rent",
    home_value_rank = "Home value rank",
    median_home_value = "Median home value",
    mean_travel_time_rank = "Commute rank",
    mean_travel_time = "Mean commute"
  ) %>%
  gt::fmt_percent(columns = pop_growth_5yr, decimals = 1) %>%
  gt::fmt_number(columns = units_per_1k_3yr, decimals = 1) %>%
  gt::fmt_currency(columns = c(median_rent, median_home_value), currency = "USD", decimals = 0) %>%
  gt::fmt_number(columns = mean_travel_time, decimals = 1, suffixing = FALSE) %>%
  gt::fmt(columns = mean_travel_time, fns = function(x) paste0(x, " min")) %>%
  gt::cols_align(align = "center", columns = ends_with("_rank")) %>%
  gt::cols_align(align = "right", columns = c(pop_growth_5yr, units_per_1k_3yr, median_rent, median_home_value, mean_travel_time)) %>%
  gt::tab_options(table.font.size = 12, data_row.padding = gt::px(3), column_labels.font.weight = "600")

benchmark_gt <- benchmark_table %>%
  select(
    geo_name,
    population,
    pop_growth_5yr,
    units_per_1k_3yr,
    median_gross_rent,
    median_home_value,
    mean_travel_time
  ) %>%
  gt::gt(rowname_col = "geo_name") %>%
  gt::tab_header(title = glue("Benchmark comparison: {target_flag_label} vs region vs US ({TARGET_YEAR})")) %>%
  gt::tab_spanner(label = "Demand", columns = c(population, pop_growth_5yr)) %>%
  gt::tab_spanner(label = "Supply", columns = c(units_per_1k_3yr)) %>%
  gt::tab_spanner(label = "Housing costs", columns = c(median_gross_rent, median_home_value)) %>%
  gt::tab_spanner(label = "Mobility", columns = c(mean_travel_time)) %>%
  gt::fmt_number(columns = population, decimals = 0) %>%
  gt::fmt_percent(columns = pop_growth_5yr, decimals = 1) %>%
  gt::fmt_number(columns = units_per_1k_3yr, decimals = 1) %>%
  gt::fmt_currency(columns = c(median_gross_rent, median_home_value), currency = "USD", decimals = 0) %>%
  gt::fmt_number(columns = mean_travel_time, decimals = 2) %>%
  gt::fmt(columns = mean_travel_time, fns = function(x) paste0(formatC(x, format = "f", digits = 2), " min")) %>%
  gt::tab_options(table.font.size = 12, data_row.padding = gt::px(4), column_labels.font.weight = "600")

baseline_year <- pop_trend_indexed %>%
  summarise(b = min(year[abs(pop_index - 100) < 1e-9], na.rm = TRUE)) %>%
  pull(b)

pop_trend_plot <- ggplot(pop_trend_indexed, aes(x = year, y = pop_index, color = geo)) +
  geom_line(linewidth = 1) +
  theme_minimal() +
  ggplot2::scale_x_continuous(
    breaks = scales::pretty_breaks(n = 6),
    labels = function(x) paste0(x, " 5yr")
  ) +
  labs(
    title = "Population trend (indexed to 100 at baseline)",
    subtitle = paste0("Baseline year: ", baseline_year, " (ACS 5-year vintages)"),
    x = NULL,
    y = "Population index",
    color = NULL
  )

target_points <- distribution_long %>% filter(is_target_market) %>% mutate(metric_x = "All metros")
distribution_long <- distribution_long %>% mutate(metric_x = "All metros")

distribution_plot <- ggplot(distribution_long, aes(x = metric_x, y = value_plot)) +
  geom_jitter(width = 0.15, alpha = 0.10, size = 0.8, color = "#94A3B8") +
  geom_boxplot(width = 0.25, outlier.shape = NA, fill = "#E2E8F0", color = "#475569", linewidth = 0.4) +
  geom_point(data = target_points, aes(x = metric_x, y = value_plot), size = 2.8, color = "#B42318") +
  geom_label(
    data = target_points,
    aes(x = metric_x, y = value_plot, label = target_flag_label),
    nudge_x = 0.12,
    size = 2.8,
    label.size = 0.1,
    color = "#7A271A",
    fill = "white",
    alpha = 0.9
  ) +
  facet_wrap(~ metric_label, scales = "free_y", nrow = 2) +
  theme_minimal() +
  theme(
    axis.title = element_blank(),
    axis.text.x = element_blank(),
    axis.ticks.x = element_blank(),
    strip.text = element_text(face = "bold", size = 11),
    panel.grid.minor = element_blank(),
    legend.position = "none"
  ) +
  labs(
    title = glue("Where {target_flag_label} sits vs all U.S. metros ({TARGET_YEAR})"),
    subtitle = glue("Each panel shows all U.S. metro values with {target_flag_label} highlighted."),
    caption = "Source: section_02_distribution_long.rds"
  )

market_context_map_plot_style_a <- ggplot(market_tract_sf) +
  geom_sf(aes(fill = pop_growth_3yr), color = "white", linewidth = 0.05) +
  {
    if (!is.null(context_water_sf)) {
      geom_sf(data = context_water_sf, fill = "#BFDBFE", color = "#60A5FA", linewidth = 0.25, alpha = 0.45)
    }
  } +
  {
    if (!is.null(context_places_sf)) {
      geom_sf(data = context_places_sf, fill = NA, color = "#475467", linewidth = 0.25, alpha = 0.75, linetype = "dotted")
    }
  } +
  {
    if (!is.null(roads_plot_sf)) {
      geom_sf(data = roads_plot_sf, aes(color = road_class, linetype = road_class, linewidth = road_class), alpha = 0.95)
    } else if (!is.null(context_roads_sf)) {
      geom_sf(data = context_roads_sf, color = "#B54708", linewidth = 0.45, alpha = 0.90)
    }
  } +
  geom_sf(
    data = base_county_sf,
    fill = NA,
    color = "#0F172A",
    linewidth = 0.70,
    alpha = 0.95
  ) +
  {
    if (!is.null(context_cbsa_sf)) {
      geom_sf(data = context_cbsa_sf, fill = NA, color = "#111827", linewidth = 1.0, alpha = 1)
    }
  } +
  scale_fill_viridis_c(
    option = "C",
    direction = 1,
    labels = scales::percent_format(accuracy = 1),
    na.value = "#D1D5DB",
    name = "Pop growth\n(3y)"
  ) +
  {
    if (!is.null(roads_plot_sf)) {
      list(
        scale_color_manual(
          values = c(
            "Primary highways" = "#991B1B",
            "Secondary highways" = "#1D4ED8",
            "Other roads" = "#9CA3AF"
          ),
          name = "Road network"
        ),
        scale_linetype_manual(
          values = c(
            "Primary highways" = "solid",
            "Secondary highways" = "dashed",
            "Other roads" = "dotted"
          ),
          name = "Road network"
        ),
        scale_linewidth_manual(
          values = c(
            "Primary highways" = 0.70,
            "Secondary highways" = 0.45,
            "Other roads" = 0.25
          ),
          guide = "none"
        )
      )
    } else {
      NULL
    }
  } +
  coord_sf(expand = FALSE) +
  theme_void() +
  theme(
    panel.background = element_rect(fill = "#F8FAFC", color = NA),
    plot.background = element_rect(fill = "#F8FAFC", color = NA),
    plot.title = element_text(face = "bold"),
    plot.subtitle = element_text(color = "#475467"),
    legend.position = "right"
  ) +
  labs(
    title = glue("{target_market_label} context at tract level"),
    subtitle = "Road style test A: color + linetype + linewidth",
    caption = "Sources: Section 02 tract/county artifacts + TIGER roads/water/places context layers"
  )

market_context_map_plot_style_b <- ggplot(market_tract_sf) +
  geom_sf(aes(fill = pop_growth_3yr), color = "white", linewidth = 0.05) +
  {
    if (!is.null(context_water_sf)) {
      geom_sf(data = context_water_sf, fill = "#BFDBFE", color = "#60A5FA", linewidth = 0.25, alpha = 0.45)
    }
  } +
  {
    if (!is.null(context_places_sf)) {
      geom_sf(data = context_places_sf, fill = NA, color = "#475467", linewidth = 0.25, alpha = 0.75, linetype = "dotted")
    }
  } +
  {
    if (!is.null(roads_plot_sf)) {
      geom_sf(data = roads_plot_sf, aes(color = road_class, linewidth = road_class), alpha = 0.95)
    } else if (!is.null(context_roads_sf)) {
      geom_sf(data = context_roads_sf, color = "#B54708", linewidth = 0.45, alpha = 0.90)
    }
  } +
  geom_sf(
    data = base_county_sf,
    fill = NA,
    color = "#0F172A",
    linewidth = 0.70,
    alpha = 0.95
  ) +
  {
    if (!is.null(context_cbsa_sf)) {
      geom_sf(data = context_cbsa_sf, fill = NA, color = "#111827", linewidth = 1.0, alpha = 1)
    }
  } +
  scale_fill_viridis_c(
    option = "C",
    direction = 1,
    labels = scales::percent_format(accuracy = 1),
    na.value = "#D1D5DB",
    name = "Pop growth\n(3y)"
  ) +
  {
    if (!is.null(roads_plot_sf)) {
      list(
        scale_color_manual(
          values = c(
            "Primary highways" = "#991B1B",
            "Secondary highways" = "#0F766E",
            "Other roads" = "#9CA3AF"
          ),
          name = "Road network"
        ),
        scale_linewidth_manual(
          values = c(
            "Primary highways" = 0.70,
            "Secondary highways" = 0.50,
            "Other roads" = 0.25
          ),
          guide = "none"
        )
      )
    } else {
      NULL
    }
  } +
  coord_sf(expand = FALSE) +
  theme_void() +
  theme(
    panel.background = element_rect(fill = "#F8FAFC", color = NA),
    plot.background = element_rect(fill = "#F8FAFC", color = NA),
    plot.title = element_text(face = "bold"),
    plot.subtitle = element_text(color = "#475467"),
    legend.position = "right"
  ) +
  labs(
    title = glue("{target_market_label} context at tract level"),
    subtitle = "Road style test B: high-contrast colors",
    caption = "Sources: Section 02 tract/county artifacts + TIGER roads/water/places context layers"
  )

# Temporary default while road-style decision is in progress.
market_context_map_plot <- market_context_map_plot_style_b

save_artifact(
  list(
    tiles_layout = tiles_layout,
    peer_gt = peer_gt,
    benchmark_gt = benchmark_gt,
    market_context_map_plot_style_a = market_context_map_plot_style_a,
    market_context_map_plot_style_b = market_context_map_plot_style_b,
    market_context_map_plot = market_context_map_plot,
    pop_trend_plot = pop_trend_plot,
    distribution_plot = distribution_plot
  ),
  resolve_output_path("02_market_overview", "section_02_visual_objects")
)

ggplot2::ggsave(
  filename = resolve_output_path("02_market_overview", "section_02_pop_trend_plot", ext = "png"),
  plot = pop_trend_plot,
  width = 9,
  height = 5,
  dpi = 150
)

ggplot2::ggsave(
  filename = resolve_output_path("02_market_overview", "section_02_market_context_map", ext = "png"),
  plot = market_context_map_plot,
  width = 8,
  height = 7,
  dpi = 150
)
ggplot2::ggsave(
  filename = resolve_output_path("02_market_overview", "section_02_market_context_map_style_a", ext = "png"),
  plot = market_context_map_plot_style_a,
  width = 8,
  height = 7,
  dpi = 150
)
ggplot2::ggsave(
  filename = resolve_output_path("02_market_overview", "section_02_market_context_map_style_b", ext = "png"),
  plot = market_context_map_plot_style_b,
  width = 8,
  height = 7,
  dpi = 150
)

ggplot2::ggsave(
  filename = resolve_output_path("02_market_overview", "section_02_distribution_plot", ext = "png"),
  plot = distribution_plot,
  width = 14,
  height = 4.5,
  dpi = 150
)

message("Section 02 visuals complete.")
