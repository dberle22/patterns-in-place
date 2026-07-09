# Section 04 visuals script
# Purpose: generate plots/tables from section outputs.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 04 visuals: 04_zones")

zones <- readRDS(read_artifact_path("04_zones", "section_04_zones"))
zone_summary <- readRDS(read_artifact_path("04_zones", "section_04_zone_summary"))
eligible_inputs <- readRDS(read_artifact_path("04_zones", "section_04_zone_input_candidates"))

# Step 6: zone visuals
zone_map_plot <- ggplot() +
  geom_sf(data = zones, aes(fill = mean_tract_score), color = "white", linewidth = 0.3, alpha = 0.9) +
  geom_sf(data = eligible_inputs, fill = NA, color = "#4d4d4d", linewidth = 0.1, alpha = 0.4) +
  geom_text(
    data = sf::st_drop_geometry(zones),
    aes(x = label_lon, y = label_lat, label = zone_label),
    size = 3.2,
    fontface = "bold"
  ) +
  scale_fill_viridis_c(option = "C", direction = 1) +
  theme_void() +
  labs(
    title = "Zone Map (Eligible Tracts Dissolved into Contiguous Components)",
    subtitle = "Fill indicates mean tract score within each zone",
    fill = "Mean tract score"
  )

zone_summary_gt <- zone_summary %>%
  select(
    zone_label,
    tracts,
    total_population,
    pop_growth_3yr_wtd,
    pop_density_median,
    units_per_1k_3yr_wtd,
    price_proxy_pctl_median,
    mean_tract_score,
    zone_area_sq_mi
  ) %>%
  arrange(zone_label) %>%
  gt::gt() %>%
  gt::tab_header(title = "Zone Summary Metrics") %>%
  gt::cols_label(
    zone_label = "Zone",
    tracts = "Tracts",
    total_population = "Population",
    pop_growth_3yr_wtd = "Pop growth (3y, wtd)",
    pop_density_median = "Median density",
    units_per_1k_3yr_wtd = "Units per 1k (wtd)",
    price_proxy_pctl_median = "Price proxy pctl",
    mean_tract_score = "Mean tract score",
    zone_area_sq_mi = "Area (sq mi)"
  ) %>%
  gt::fmt_number(columns = c(tracts, total_population), decimals = 0) %>%
  gt::fmt_percent(columns = c(pop_growth_3yr_wtd, price_proxy_pctl_median), decimals = 1) %>%
  gt::fmt_number(columns = c(pop_density_median, units_per_1k_3yr_wtd, mean_tract_score), decimals = 2) %>%
  gt::fmt_number(columns = zone_area_sq_mi, decimals = 1)

save_artifact(
  list(
    zone_map_plot = zone_map_plot,
    zone_summary_gt = zone_summary_gt
  ),
  resolve_output_path("04_zones", "section_04_visual_objects")
)

ggplot2::ggsave(
  filename = resolve_output_path("04_zones", "section_04_zone_map", ext = "png"),
  plot = zone_map_plot,
  width = 9,
  height = 7,
  dpi = 150
)

message("Section 04 visuals complete.")
