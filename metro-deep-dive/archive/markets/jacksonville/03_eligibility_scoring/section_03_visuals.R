# Section 03 visuals script
# Purpose: generate plots/tables from section outputs.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 03 visuals: 03_eligibility_scoring")

funnel_counts <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_funnel_counts"))
scored_tracts <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_scored_tracts"))
top_tracts <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_top_tracts"))
price_hist_input <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_price_hist_input"))
growth_hist_input <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_growth_hist_input"))
tract_sf <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_tract_sf"))
tract_component_scores <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_tract_component_scores"))
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

context_cbsa_sf <- align_crs(context_cbsa_sf, tract_sf)
context_county_sf <- align_crs(context_county_sf, tract_sf)
context_places_sf <- align_crs(context_places_sf, tract_sf)
context_roads_sf <- align_crs(context_roads_sf, tract_sf)
context_water_sf <- align_crs(context_water_sf, tract_sf)
market_county_sf <- align_crs(market_county_sf, tract_sf)

# Use the canonical market county artifact for base boundaries/extents.
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

funnel_gt <- funnel_counts %>%
  arrange(step_order) %>%
  mutate(
    pct_of_start = tracts_remaining / first(tracts_remaining)
  ) %>%
  select(step, tracts_remaining, pct_of_start) %>%
  gt::gt() %>%
  gt::tab_header(title = "Eligibility Funnel") %>%
  gt::cols_label(
    step = "Gate Step",
    tracts_remaining = "Tracts Remaining",
    pct_of_start = "% of Start"
  ) %>%
  gt::fmt_number(columns = tracts_remaining, decimals = 0) %>%
  gt::fmt_percent(columns = pct_of_start, decimals = 1)

price_hist_plot <- ggplot(price_hist_input, aes(x = price_proxy_pctl)) +
  geom_histogram(bins = 30, fill = "#4575b4", alpha = 0.8) +
  geom_vline(xintercept = MODEL_PARAMS$price_proxy_pctl_max, color = "#d73027", linetype = "dashed", linewidth = 1) +
  theme_minimal() +
  labs(
    title = "Price Proxy Percentile Distribution",
    subtitle = "Dashed line marks the v1 threshold",
    x = "Price proxy percentile",
    y = "Tract count"
  )

growth_median <- median(growth_hist_input$pop_growth_3yr, na.rm = TRUE)
growth_hist_plot <- ggplot(growth_hist_input, aes(x = pop_growth_3yr)) +
  geom_histogram(bins = 30, fill = "#1a9850", alpha = 0.8) +
  geom_vline(xintercept = growth_median, color = "#d73027", linetype = "dashed", linewidth = 1) +
  theme_minimal() +
  labs(
    title = "Population Growth (3y) Distribution",
    subtitle = "Dashed line marks median tract growth",
    x = "3-year population growth",
    y = "Tract count"
  )

scored_map_sf <- tract_sf %>%
  left_join(scored_tracts %>% select(tract_geoid, tract_score), by = "tract_geoid")

eligible_map_plot <- ggplot(scored_map_sf) +
  geom_sf(aes(fill = tract_score), color = "white", linewidth = 0.05) +
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
    na.value = "#D1D5DB",
    name = "Tract score"
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
    title = "Tract score map across the Jacksonville market",
    subtitle = "Tracts shaded by composite score with visible county/place boundaries, roads, and water context",
    caption = "Sources: Section 03 scored tracts + Section 02 context layers"
  )

score_hist_plot <- ggplot(scored_tracts, aes(x = tract_score)) +
  geom_histogram(bins = 30, fill = "#5e3c99", alpha = 0.85) +
  theme_minimal() +
  labs(
    title = "Tract Score Distribution (All Tracts)",
    x = "Tract score",
    y = "Tract count"
  )

highlight_n <- min(20, nrow(scored_tracts))
top_highlight <- scored_tracts %>%
  filter(eligible_v1 == 1) %>%
  arrange(desc(tract_score)) %>%
  slice_head(n = highlight_n)

growth_density_scatter <- ggplot(scored_tracts, aes(x = pop_density, y = pop_growth_3yr)) +
  geom_point(alpha = 0.25, color = "#636363") +
  geom_point(data = top_highlight, color = "#d73027", size = 2) +
  theme_minimal() +
  labs(
    title = "Growth vs Density (Eligible Tracts)",
    subtitle = paste0("Top ", highlight_n, " scored tracts highlighted"),
    x = "Population density",
    y = "Population growth (3y)"
  )

top_tracts_gt <- top_tracts %>%
  slice_head(n = 25) %>%
  gt::gt() %>%
  gt::tab_header(title = "Top 25 Tracts with Score Components") %>%
  gt::fmt_number(columns = c(tract_score, starts_with("contrib_")), decimals = 3) %>%
  gt::fmt_percent(columns = c(pop_growth_3yr, price_proxy_pctl), decimals = 1) %>%
  gt::fmt_number(columns = c(units_per_1k_3yr, pop_density, commute_intensity_b), decimals = 1) %>%
  gt::fmt_currency(columns = median_hh_income, currency = "USD", decimals = 0)

component_mix_plot <- top_tracts %>%
  select(starts_with("contrib_")) %>%
  summarise(across(everything(), ~ mean(.x, na.rm = TRUE))) %>%
  tidyr::pivot_longer(
    cols = everything(),
    names_to = "component",
    values_to = "avg_contribution"
  ) %>%
  mutate(
    component = gsub("^contrib_", "", component),
    component = factor(component, levels = component[order(avg_contribution)])
  ) %>%
  ggplot(aes(x = avg_contribution, y = component, fill = avg_contribution > 0)) +
  geom_col(width = 0.7, show.legend = FALSE) +
  scale_fill_manual(values = c("TRUE" = "#2b8cbe", "FALSE" = "#d73027")) +
  theme_minimal() +
  labs(
    title = "Top-Tract Score Drivers",
    subtitle = "Positive values add to score; negative values reduce score",
    x = "Average contribution",
    y = NULL
  )

component_score_table <- tract_component_scores %>%
  select(
    tract_geoid,
    eligible_v1,
    tract_rank,
    tract_score,
    z_growth,
    z_units,
    z_headroom,
    z_price,
    z_commute,
    z_income,
    contrib_growth,
    contrib_units,
    contrib_headroom,
    contrib_price,
    contrib_commute,
    contrib_income,
    why_tags
  )

save_artifact(
  list(
    funnel_gt = funnel_gt,
    price_hist_plot = price_hist_plot,
    growth_hist_plot = growth_hist_plot,
    eligible_map_plot = eligible_map_plot,
    score_hist_plot = score_hist_plot,
    growth_density_scatter = growth_density_scatter,
    component_mix_plot = component_mix_plot,
    top_tracts_gt = top_tracts_gt,
    component_score_table = component_score_table
  ),
  resolve_output_path("03_eligibility_scoring", "section_03_visual_objects")
)

ggplot2::ggsave(
  filename = resolve_output_path("03_eligibility_scoring", "section_03_price_hist", ext = "png"),
  plot = price_hist_plot,
  width = 8,
  height = 5,
  dpi = 150
)
ggplot2::ggsave(
  filename = resolve_output_path("03_eligibility_scoring", "section_03_growth_hist", ext = "png"),
  plot = growth_hist_plot,
  width = 8,
  height = 5,
  dpi = 150
)
ggplot2::ggsave(
  filename = resolve_output_path("03_eligibility_scoring", "section_03_eligible_map", ext = "png"),
  plot = eligible_map_plot,
  width = 8,
  height = 6,
  dpi = 150
)
ggplot2::ggsave(
  filename = resolve_output_path("03_eligibility_scoring", "section_03_score_hist", ext = "png"),
  plot = score_hist_plot,
  width = 8,
  height = 5,
  dpi = 150
)
ggplot2::ggsave(
  filename = resolve_output_path("03_eligibility_scoring", "section_03_growth_density_scatter", ext = "png"),
  plot = growth_density_scatter,
  width = 8,
  height = 5,
  dpi = 150
)

message("Section 03 visuals complete.")
