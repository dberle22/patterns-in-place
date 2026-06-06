# Section 04 cluster visuals script
# Purpose: create cluster-zone map and summary visual outputs.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 04 cluster visuals")

cluster_zones <- readRDS(read_artifact_path("04_zones", "section_04_cluster_zones"))
cluster_zone_summary <- readRDS(read_artifact_path("04_zones", "section_04_cluster_zone_summary"))
zone_inputs <- readRDS(read_artifact_path("04_zones", "section_04_zone_input_candidates"))
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
context_places_sf <- read_optional_sf("02_market_overview", "section_02_context_places_sf", subdir = "context_layers")
context_roads_sf <- read_optional_sf("02_market_overview", "section_02_context_major_roads_sf", subdir = "context_layers")
context_water_sf <- read_optional_sf("02_market_overview", "section_02_context_water_sf", subdir = "context_layers")

align_crs <- function(x, target) {
  if (is.null(x)) return(NULL)
  if (is.na(sf::st_crs(x))) return(x)
  if (sf::st_crs(x) != sf::st_crs(target)) sf::st_transform(x, sf::st_crs(target)) else x
}

market_county_sf <- align_crs(market_county_sf, cluster_zones)
context_cbsa_sf <- align_crs(context_cbsa_sf, cluster_zones)
context_places_sf <- align_crs(context_places_sf, cluster_zones)
context_roads_sf <- align_crs(context_roads_sf, cluster_zones)
context_water_sf <- align_crs(context_water_sf, cluster_zones)

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

cluster_zone_map_plot <- ggplot() +
  geom_sf(data = cluster_zones, aes(fill = factor(cluster_order)), color = "white", linewidth = 0.3, alpha = 0.92) +
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
  geom_sf(data = zone_inputs, fill = NA, color = "#6B7280", linewidth = 0.10, alpha = 0.30) +
  geom_sf(data = base_county_sf, fill = NA, color = "#0F172A", linewidth = 0.70, alpha = 0.95) +
  {
    if (!is.null(context_cbsa_sf)) {
      geom_sf(data = context_cbsa_sf, fill = NA, color = "#111827", linewidth = 1.0, alpha = 1)
    }
  } +
  geom_text(
    data = sf::st_drop_geometry(cluster_zones),
    aes(x = label_lon, y = label_lat, label = cluster_label),
    size = 3.0,
    fontface = "bold"
  ) +
  scale_fill_viridis_d(option = "C", direction = -1, name = "Cluster") +
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
    title = "Cluster Zones Map",
    subtitle = "Top-scoring tract seeds grouped by proximity-based clustering",
    caption = "Sources: Section 04 cluster outputs + Section 02 context layers"
  )

cluster_summary_gt <- cluster_zone_summary %>%
  select(
    cluster_label,
    tracts,
    total_population,
    pop_growth_3yr_wtd,
    pop_density_median,
    units_per_1k_3yr_wtd,
    price_proxy_pctl_median,
    mean_tract_score,
    zone_area_sq_mi
  ) %>%
  arrange(cluster_label) %>%
  gt::gt() %>%
  gt::tab_header(title = "Cluster Zone Summary Metrics") %>%
  gt::cols_label(
    cluster_label = "Cluster Zone",
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
    cluster_zone_map_plot = cluster_zone_map_plot,
    cluster_summary_gt = cluster_summary_gt
  ),
  resolve_output_path("04_zones", "section_04_cluster_visual_objects")
)

ggplot2::ggsave(
  filename = resolve_output_path("04_zones", "section_04_cluster_zone_map", ext = "png"),
  plot = cluster_zone_map_plot,
  width = 9,
  height = 7,
  dpi = 150
)

message("Section 04 cluster visuals complete.")
