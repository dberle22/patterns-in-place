# Section 05 visuals script
# Purpose: generate plots/tables from section outputs.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 05 visuals: 05_parcels")

zones_canonical <- readRDS(read_artifact_path("05_parcels", "section_05_zones_canonical"))
zone_overlay_cluster <- readRDS(read_artifact_path("05_parcels", "section_05_zone_overlay_cluster"))
parcel_shortlist_cluster <- readRDS(read_artifact_path("05_parcels", "section_05_parcel_shortlist_cluster"))
retail_classified_parcels <- readRDS(read_artifact_path("05_parcels", "section_05_retail_classified_parcels"))
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

context_cbsa_sf <- align_crs(context_cbsa_sf, zones_canonical)
context_places_sf <- align_crs(context_places_sf, zones_canonical)
context_roads_sf <- align_crs(context_roads_sf, zones_canonical)
context_water_sf <- align_crs(context_water_sf, zones_canonical)
market_county_sf <- align_crs(market_county_sf, zones_canonical)
retail_classified_parcels <- align_crs(retail_classified_parcels, zones_canonical)
parcel_shortlist_cluster <- align_crs(parcel_shortlist_cluster, zones_canonical)

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

sample_parcels_for_plot <- function(parcel_sf, max_total = 120000L, retail_floor = 25000L) {
  parcel_df <- parcel_sf %>%
    mutate(parcel_segment = dplyr::if_else(retail_flag, "Retail parcel", "Residential/other parcel"))

  retail <- parcel_df %>% filter(parcel_segment == "Retail parcel")
  other <- parcel_df %>% filter(parcel_segment == "Residential/other parcel")

  n_retail <- min(nrow(retail), max(retail_floor, floor(max_total * 0.35)))
  n_other <- min(nrow(other), max_total - n_retail)

  retail_s <- if (nrow(retail) > n_retail) dplyr::slice_sample(retail, n = n_retail) else retail
  other_s <- if (nrow(other) > n_other) dplyr::slice_sample(other, n = n_other) else other

  dplyr::bind_rows(retail_s, other_s)
}

parcel_plot_sf <- sample_parcels_for_plot(retail_classified_parcels)
analysis_crs_epsg <- if (!is.null(GEOMETRY_ASSUMPTIONS$analysis_crs_epsg)) GEOMETRY_ASSUMPTIONS$analysis_crs_epsg else 5070
parcel_plot_points <- parcel_plot_sf %>%
  sf::st_transform(analysis_crs_epsg) %>%
  dplyr::mutate(geometry = sf::st_point_on_surface(geometry)) %>%
  dplyr::mutate(
    plot_size = dplyr::if_else(parcel_segment == "Retail parcel", 0.35, 0.18),
    plot_alpha = dplyr::if_else(parcel_segment == "Retail parcel", 0.50, 0.25)
  ) %>%
  sf::st_transform(sf::st_crs(zones_canonical))

zones_for_map <- zones_canonical %>%
  left_join(
    zone_overlay_cluster %>% select(zone_id, zone_label, retail_area_density, zone_quality_score),
    by = "zone_id"
  )

market_parcel_context_map <- ggplot() +
  {
    if (!is.null(context_water_sf)) {
      geom_sf(data = context_water_sf, fill = "#BFDBFE", color = "#60A5FA", linewidth = 0.25, alpha = 0.45)
    }
  } +
  geom_sf(
    data = parcel_plot_points,
    aes(color = parcel_segment),
    shape = 16,
    size = parcel_plot_points$plot_size,
    alpha = parcel_plot_points$plot_alpha
  ) +
  {
    if (!is.null(context_places_sf)) {
      geom_sf(data = context_places_sf, fill = NA, color = "#475467", linewidth = 0.25, alpha = 0.70, linetype = "dotted")
    }
  } +
  {
    if (!is.null(roads_plot_sf)) {
      list(
        geom_sf(data = dplyr::filter(roads_plot_sf, road_class == "Primary highways"), color = "#991B1B", linewidth = 0.70, alpha = 0.90),
        geom_sf(data = dplyr::filter(roads_plot_sf, road_class == "Secondary highways"), color = "#0F766E", linewidth = 0.50, alpha = 0.90),
        geom_sf(data = dplyr::filter(roads_plot_sf, road_class == "Other roads"), color = "#9CA3AF", linewidth = 0.25, alpha = 0.60)
      )
    } else if (!is.null(context_roads_sf)) {
      geom_sf(data = context_roads_sf, color = "#B54708", linewidth = 0.35, alpha = 0.75)
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
  scale_color_manual(
    values = c(
      "Retail parcel" = "#B42318",
      "Residential/other parcel" = "#475467"
    ),
    name = "Parcel type"
  ) +
  coord_sf(expand = FALSE) +
  theme_void() +
  theme(
    panel.background = element_rect(fill = "#F8FAFC", color = NA),
    plot.background = element_rect(fill = "#F8FAFC", color = NA),
    plot.title = element_text(face = "bold"),
    plot.subtitle = element_text(color = "#475467"),
    legend.position = "right"
  ) +
  guides(
    color = guide_legend(override.aes = list(size = c(3.5, 2.2), alpha = c(1, 1)))
  ) +
  labs(
    title = "Parcel market context across Jacksonville",
    subtitle = "Residential/other and retail parcels shown together to reveal corridor pattern before zone filtering",
    caption = "Sources: Section 05 classified parcels + Section 02 TIGER context layers"
  )

cluster_parcel_overlay_map <- ggplot() +
  {
    if (!is.null(context_water_sf)) {
      geom_sf(data = context_water_sf, fill = "#BFDBFE", color = "#60A5FA", linewidth = 0.25, alpha = 0.45)
    }
  } +
  geom_sf(
    data = zones_for_map,
    aes(fill = zone_quality_score),
    color = "#111827",
    linewidth = 0.35,
    alpha = 0.40
  ) +
  geom_sf(
    data = parcel_plot_points,
    aes(color = parcel_segment),
    shape = 16,
    size = 0.22,
    alpha = 0.28
  ) +
  {
    if (!is.null(context_places_sf)) {
      geom_sf(data = context_places_sf, fill = NA, color = "#475467", linewidth = 0.25, alpha = 0.70, linetype = "dotted")
    }
  } +
  {
    if (!is.null(roads_plot_sf)) {
      list(
        geom_sf(data = dplyr::filter(roads_plot_sf, road_class == "Primary highways"), color = "#991B1B", linewidth = 0.70, alpha = 0.90),
        geom_sf(data = dplyr::filter(roads_plot_sf, road_class == "Secondary highways"), color = "#0F766E", linewidth = 0.50, alpha = 0.90),
        geom_sf(data = dplyr::filter(roads_plot_sf, road_class == "Other roads"), color = "#9CA3AF", linewidth = 0.25, alpha = 0.60)
      )
    } else if (!is.null(context_roads_sf)) {
      geom_sf(data = context_roads_sf, color = "#B54708", linewidth = 0.35, alpha = 0.70)
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
  scale_fill_viridis_c(option = "C", direction = 1, na.value = "#E5E7EB", name = "Mean tract score percentile") +
  scale_color_manual(
    values = c(
      "Retail parcel" = "#B42318",
      "Residential/other parcel" = "#98A2B3"
    ),
    name = "Parcel type"
  ) +
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
    title = "Cluster zones over parcel context",
    subtitle = "Cluster quality and parcel pattern combined to frame shortlist decisions",
    caption = "Sources: Section 04 clusters + Section 05 classified parcels + Section 02 context layers"
  )

overlay_map_cluster <- ggplot(zones_for_map) +
  geom_sf(aes(fill = zone_quality_score), color = "#111827", linewidth = 0.35, alpha = 0.85) +
  geom_sf(data = base_county_sf, fill = NA, color = "#0F172A", linewidth = 0.70, alpha = 0.95) +
  scale_fill_viridis_c(option = "C", direction = 1, na.value = "#f0f0f0") +
  theme_void() +
  theme(
    panel.background = element_rect(fill = "#F8FAFC", color = NA),
    plot.background = element_rect(fill = "#F8FAFC", color = NA),
    plot.title = element_text(face = "bold"),
    plot.subtitle = element_text(color = "#475467")
  ) +
  labs(
    title = "Cluster zone quality map",
    subtitle = "Zone fill reflects mean tract score percentile from the Section 04 cluster summary",
    fill = "Mean tract\nscore percentile"
  )

select_hybrid_shortlist <- function(shortlist_sf, n_total = 200L, min_per_zone = 10L) {
  core <- shortlist_sf %>%
    group_by(zone_id) %>%
    arrange(shortlist_rank_zone, .by_group = TRUE) %>%
    slice_head(n = min_per_zone) %>%
    ungroup()

  remaining_n <- max(0L, n_total - nrow(core))
  if (remaining_n == 0L) return(core)

  extra <- shortlist_sf %>%
    anti_join(
      core %>% sf::st_drop_geometry() %>% select(parcel_uid, zone_id),
      by = c("parcel_uid", "zone_id")
    ) %>%
    arrange(shortlist_rank_system) %>%
    slice_head(n = remaining_n)

  dplyr::bind_rows(core, extra)
}

build_shortlist_map <- function(shortlist_sf) {
  shortlist_top <- select_hybrid_shortlist(shortlist_sf, n_total = 200L, min_per_zone = 10L) %>%
    mutate(plot_weight = 1 / pmax(shortlist_rank_system, 1))

  shortlist_top_pts <- shortlist_top %>%
    sf::st_transform(analysis_crs_epsg) %>%
    dplyr::mutate(geometry = sf::st_point_on_surface(geometry)) %>%
    sf::st_transform(sf::st_crs(zones_canonical))

  ggplot() +
    {
      if (!is.null(context_water_sf)) {
        geom_sf(data = context_water_sf, fill = "#BFDBFE", color = "#60A5FA", linewidth = 0.25, alpha = 0.45)
      }
    } +
    geom_sf(
      data = zones_for_map,
      aes(fill = zone_quality_score),
      color = "#111827",
      linewidth = 0.30,
      alpha = 0.35
    ) +
    geom_sf(
      data = shortlist_top_pts,
      aes(color = shortlist_score, size = plot_weight),
      alpha = 0.75,
      show.legend = c(size = FALSE, color = TRUE)
    ) +
    {
      if (!is.null(context_places_sf)) {
        geom_sf(data = context_places_sf, fill = NA, color = "#475467", linewidth = 0.25, alpha = 0.70, linetype = "dotted")
      }
    } +
    {
      if (!is.null(roads_plot_sf)) {
        list(
          geom_sf(data = dplyr::filter(roads_plot_sf, road_class == "Primary highways"), color = "#991B1B", linewidth = 0.70, alpha = 0.90),
          geom_sf(data = dplyr::filter(roads_plot_sf, road_class == "Secondary highways"), color = "#0F766E", linewidth = 0.50, alpha = 0.90),
          geom_sf(data = dplyr::filter(roads_plot_sf, road_class == "Other roads"), color = "#9CA3AF", linewidth = 0.25, alpha = 0.60)
        )
      } else if (!is.null(context_roads_sf)) {
        geom_sf(data = context_roads_sf, color = "#B54708", linewidth = 0.35, alpha = 0.70)
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
    scale_fill_viridis_c(option = "C", direction = 1, na.value = "#E5E7EB", name = "Mean tract score percentile") +
    scale_color_viridis_c(option = "D", direction = 1) +
    scale_size_continuous(range = c(0.8, 2.3)) +
    coord_sf(expand = FALSE) +
    theme_void() +
    theme(
      panel.background = element_rect(fill = "#F8FAFC", color = NA),
      plot.background = element_rect(fill = "#F8FAFC", color = NA)
    ) +
    labs(
      title = "Top shortlisted parcels over cluster zones",
      subtitle = "Hybrid selection: min 10 parcels per cluster, then top remaining by score",
      color = "Shortlist\nscore"
    )
}

shortlist_map_cluster <- build_shortlist_map(parcel_shortlist_cluster)

if (!("use_code_definition" %in% names(parcel_shortlist_cluster))) {
  mapping_path <- read_artifact_path("05_parcels", "section_05_retail_land_use_mapping_candidates_v0_1", ext = "csv")
  if (file.exists(mapping_path)) {
    usecode_lookup <- readr::read_csv(mapping_path, show_col_types = FALSE) %>%
      transmute(
        land_use_code = as.character(use_code),
        use_code_definition = dplyr::coalesce(
          if ("definition" %in% names(.)) as.character(.data$definition) else NA_character_,
          if ("definition.x" %in% names(.)) as.character(.data$definition.x) else NA_character_
        ),
        use_code_type = dplyr::coalesce(
          if ("type" %in% names(.)) as.character(.data$type) else NA_character_,
          if ("type.x" %in% names(.)) as.character(.data$type.x) else NA_character_
        )
      ) %>%
      distinct(land_use_code, .keep_all = TRUE)
    parcel_shortlist_cluster <- parcel_shortlist_cluster %>% left_join(usecode_lookup, by = "land_use_code")
  }
}

shortlist_table_cluster <- parcel_shortlist_cluster %>%
  sf::st_drop_geometry() %>%
  group_by(zone_id, zone_label) %>%
  arrange(shortlist_rank_zone, .by_group = TRUE) %>%
  slice_head(n = 10) %>%
  ungroup() %>%
  arrange(zone_label, shortlist_rank_zone) %>%
  mutate(
    use_code_description = dplyr::coalesce(use_code_definition, review_note, "Unknown"),
    use_code_group = dplyr::coalesce(use_code_type, "Unknown")
  ) %>%
  select(
    zone_label,
    shortlist_rank_zone,
    parcel_uid,
    owner_name,
    owner_addr,
    site_addr,
    land_use_code,
    use_code_description,
    use_code_group,
    retail_subtype,
    parcel_area_sqmi,
    just_value_clean,
    assessed_value_psf,
    last_sale_date,
    last_sale_price,
    zone_quality_score,
    local_retail_context_score,
    parcel_characteristics_score,
    shortlist_score
  )

save_artifact(
  list(
    market_parcel_context_map = market_parcel_context_map,
    cluster_parcel_overlay_map = cluster_parcel_overlay_map,
    overlay_map_cluster = overlay_map_cluster,
    shortlist_map_cluster = shortlist_map_cluster,
    shortlist_table_cluster = shortlist_table_cluster
  ),
  resolve_output_path("05_parcels", "section_05_visual_objects")
)

ggplot2::ggsave(
  filename = resolve_output_path("05_parcels", "section_05_market_parcel_context_map", ext = "png"),
  plot = market_parcel_context_map,
  width = 9,
  height = 7,
  dpi = 150
)
ggplot2::ggsave(
  filename = resolve_output_path("05_parcels", "section_05_cluster_parcel_overlay_map", ext = "png"),
  plot = cluster_parcel_overlay_map,
  width = 9,
  height = 7,
  dpi = 150
)
ggplot2::ggsave(
  filename = resolve_output_path("05_parcels", "section_05_overlay_map_cluster", ext = "png"),
  plot = overlay_map_cluster,
  width = 9,
  height = 7,
  dpi = 150
)
ggplot2::ggsave(
  filename = resolve_output_path("05_parcels", "section_05_shortlist_map_cluster", ext = "png"),
  plot = shortlist_map_cluster,
  width = 9,
  height = 7,
  dpi = 150
)

message("Section 05 visuals complete.")
