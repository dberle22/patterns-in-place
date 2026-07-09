# Section 04 checks script
# Purpose: sanity checks and QA assertions for section outputs.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 04 checks: 04_zones")

zone_candidates <- readRDS(read_artifact_path("04_zones", "section_04_zone_candidate_tracts"))
zone_components <- readRDS(read_artifact_path("04_zones", "section_04_zone_components"))
component_summary <- readRDS(read_artifact_path("04_zones", "section_04_component_summary"))
zones <- readRDS(read_artifact_path("04_zones", "section_04_zones"))
zone_summary <- readRDS(read_artifact_path("04_zones", "section_04_zone_summary"))

schema_checks <- list(
  zone_candidates = validate_columns(
    zone_candidates,
    c("tract_geoid", "zone_candidate"),
    "section_04_zone_candidate_tracts"
  ),
  zone_components = validate_columns(
    zone_components,
    c("tract_geoid", "zone_component_id", "zone_component_label"),
    "section_04_zone_components"
  ),
  component_summary = validate_columns(
    component_summary,
    c("zone_component_id", "zone_component_label", "tract_count"),
    "section_04_component_summary"
  ),
  zones = validate_columns(
    sf::st_drop_geometry(zones),
    c("zone_component_id", "zone_id", "zone_label", "zone_order", "tract_count", "mean_tract_score", "zone_area_sq_mi"),
    "section_04_zones"
  ),
  zone_summary = validate_columns(
    zone_summary,
    c(
      "zone_id", "zone_label", "zone_order", "zone_component_id",
      "tracts", "total_population", "pop_growth_3yr_wtd", "pop_density_median",
      "units_per_1k_3yr_wtd", "price_proxy_pctl_median", "mean_tract_score", "zone_area_sq_mi"
    ),
    "section_04_zone_summary"
  )
)

key_checks <- list(
  zone_candidates = validate_unique_key(zone_candidates, "tract_geoid", "section_04_zone_candidate_tracts"),
  zone_components = validate_unique_key(zone_components, "tract_geoid", "section_04_zone_components"),
  zones = validate_unique_key(sf::st_drop_geometry(zones), "zone_id", "section_04_zones"),
  zone_summary = validate_unique_key(zone_summary, "zone_id", "section_04_zone_summary")
)

geom_checks <- list(
  zones = validate_sf(zones, "section_04_zones", GEOMETRY_ASSUMPTIONS$expected_crs_epsg)
)

assigned_tracts <- zone_components %>% distinct(tract_geoid)
candidate_tracts <- zone_candidates %>% distinct(tract_geoid)

missing_from_components <- setdiff(candidate_tracts$tract_geoid, assigned_tracts$tract_geoid)
extra_in_components <- setdiff(assigned_tracts$tract_geoid, candidate_tracts$tract_geoid)

zone_count <- nrow(zones)
zone_count_in_target_band <- zone_count >= 3 && zone_count <= 8

logic_checks <- list(
  all_candidates_assigned_once = length(missing_from_components) == 0,
  no_extra_assignments = length(extra_in_components) == 0,
  assignment_count_matches_candidates = nrow(zone_components) == nrow(zone_candidates),
  zone_summary_rows_match_zones = nrow(zone_summary) == nrow(zones),
  zone_component_summary_rows_match_zones = nrow(component_summary) == nrow(zones),
  all_zone_areas_positive = all(zones$zone_area_sq_mi > 0, na.rm = TRUE),
  all_zone_labels_present = all(!is.na(zones$zone_label) & nzchar(zones$zone_label)),
  all_zone_ids_present = all(!is.na(zones$zone_id) & nzchar(zones$zone_id)),
  zone_count_in_target_band = zone_count_in_target_band
)

warnings <- character()
if (!zone_count_in_target_band) {
  warnings <- c(warnings, paste0("Zone count ", zone_count, " is outside target band [3, 8]."))
}

schema_pass <- all(vapply(schema_checks, `[[`, logical(1), "pass"))
key_pass <- all(vapply(key_checks, `[[`, logical(1), "pass"))
geom_pass <- all(vapply(geom_checks, `[[`, logical(1), "pass"))

# Exclude target-band warning from hard failure
logic_required <- logic_checks[names(logic_checks) != "zone_count_in_target_band"]
logic_pass <- all(unlist(logic_required))

report <- list(
  run_metadata = run_metadata(),
  schema_checks = schema_checks,
  key_checks = key_checks,
  geometry_checks = geom_checks,
  logic_checks = logic_checks,
  set_differences = list(
    missing_from_components = missing_from_components,
    extra_in_components = extra_in_components
  ),
  warnings = warnings,
  pass = schema_pass && key_pass && geom_pass && logic_pass
)

save_artifact(
  report,
  resolve_output_path("04_zones", "section_04_validation_report")
)

if (!isTRUE(report$pass)) {
  stop("Section 04 checks failed. See section_04_validation_report.rds.", call. = FALSE)
}

message("Section 04 checks complete.")
