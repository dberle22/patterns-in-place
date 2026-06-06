# Section 04 cluster checks script
# Purpose: validate cluster zone assignment and geometry outputs.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 04 cluster checks")

zone_inputs <- readRDS(read_artifact_path("04_zones", "section_04_zone_input_candidates"))
cluster_assignments <- readRDS(read_artifact_path("04_zones", "section_04_cluster_assignments"))
cluster_zones <- readRDS(read_artifact_path("04_zones", "section_04_cluster_zones"))
cluster_zone_summary <- readRDS(read_artifact_path("04_zones", "section_04_cluster_zone_summary"))
cluster_params <- readRDS(read_artifact_path("04_zones", "section_04_cluster_params"))

schema_checks <- list(
  cluster_assignments = validate_columns(
    cluster_assignments,
    c("tract_geoid", "cluster_raw_id", "cluster_id", "cluster_label", "cluster_order", "tracts", "tract_score"),
    "section_04_cluster_assignments"
  ),
  cluster_zones = validate_columns(
    sf::st_drop_geometry(cluster_zones),
    c("cluster_id", "cluster_label", "cluster_order", "cluster_raw_id", "zone_area_sq_mi", "label_lon", "label_lat"),
    "section_04_cluster_zones"
  ),
  cluster_zone_summary = validate_columns(
    cluster_zone_summary,
    c(
      "cluster_id", "cluster_label", "cluster_order", "tracts", "total_population",
      "pop_growth_3yr_wtd", "pop_density_median", "units_per_1k_3yr_wtd",
      "price_proxy_pctl_median", "mean_tract_score", "zone_area_sq_mi"
    ),
    "section_04_cluster_zone_summary"
  )
)

key_checks <- list(
  zone_inputs = validate_unique_key(sf::st_drop_geometry(zone_inputs), "tract_geoid", "section_04_zone_input_candidates"),
  cluster_assignments = validate_unique_key(cluster_assignments, "tract_geoid", "section_04_cluster_assignments"),
  cluster_zones = validate_unique_key(sf::st_drop_geometry(cluster_zones), "cluster_id", "section_04_cluster_zones"),
  cluster_zone_summary = validate_unique_key(cluster_zone_summary, "cluster_id", "section_04_cluster_zone_summary")
)

geometry_checks <- list(
  cluster_zones = validate_sf(cluster_zones, "section_04_cluster_zones", GEOMETRY_ASSUMPTIONS$expected_crs_epsg)
)

candidate_tracts <- zone_inputs %>% sf::st_drop_geometry() %>% distinct(tract_geoid)
assigned_tracts <- cluster_assignments %>% distinct(tract_geoid)

missing_assignments <- setdiff(candidate_tracts$tract_geoid, assigned_tracts$tract_geoid)
extra_assignments <- setdiff(assigned_tracts$tract_geoid, candidate_tracts$tract_geoid)

zone_count <- nrow(cluster_zone_summary)
zone_count_in_target_band <- zone_count >= 3 && zone_count <= 8

logic_checks <- list(
  all_candidates_assigned = length(missing_assignments) == 0,
  no_extra_assignments = length(extra_assignments) == 0,
  assignment_row_count_matches = nrow(cluster_assignments) == nrow(zone_inputs),
  summary_matches_zones = nrow(cluster_zone_summary) == nrow(cluster_zones),
  positive_zone_area = all(cluster_zone_summary$zone_area_sq_mi > 0, na.rm = TRUE),
  deterministic_labels_present = all(!is.na(cluster_zone_summary$cluster_label) & nzchar(cluster_zone_summary$cluster_label)),
  zone_count_in_target_band = zone_count_in_target_band
)

warnings <- character()
if (!zone_count_in_target_band) {
  warnings <- c(warnings, paste0("Cluster zone count ", zone_count, " is outside target band [3, 8]."))
}

schema_pass <- all(vapply(schema_checks, `[[`, logical(1), "pass"))
key_pass <- all(vapply(key_checks, `[[`, logical(1), "pass"))
geometry_pass <- all(vapply(geometry_checks, `[[`, logical(1), "pass"))
logic_required <- logic_checks[names(logic_checks) != "zone_count_in_target_band"]
logic_pass <- all(unlist(logic_required))

validation_report <- list(
  run_metadata = run_metadata(),
  cluster_params = cluster_params,
  schema_checks = schema_checks,
  key_checks = key_checks,
  geometry_checks = geometry_checks,
  logic_checks = logic_checks,
  set_differences = list(
    missing_assignments = missing_assignments,
    extra_assignments = extra_assignments
  ),
  warnings = warnings,
  pass = schema_pass && key_pass && geometry_pass && logic_pass
)

save_artifact(
  validation_report,
  resolve_output_path("04_zones", "section_04_cluster_validation_report")
)

if (!isTRUE(validation_report$pass)) {
  stop("Cluster checks failed. See section_04_cluster_validation_report.rds.", call. = FALSE)
}

message("Section 04 cluster checks complete.")
