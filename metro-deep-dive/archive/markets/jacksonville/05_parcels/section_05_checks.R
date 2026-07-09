# Section 05 checks script
# Purpose: sanity checks and QA assertions for section outputs.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 05 checks: 05_parcels")

parcels_canonical <- readRDS(read_artifact_path("05_parcels", "section_05_parcels_canonical"))
retail_classified_parcels <- readRDS(read_artifact_path("05_parcels", "section_05_retail_classified_parcels"))
retail_intensity <- readRDS(read_artifact_path("05_parcels", "section_05_retail_intensity"))
zone_overlay_cluster <- readRDS(read_artifact_path("05_parcels", "section_05_zone_overlay_cluster"))
parcel_shortlist_cluster <- readRDS(read_artifact_path("05_parcels", "section_05_parcel_shortlist_cluster"))
retail_intensity_report <- readRDS(read_artifact_path("05_parcels", "section_05_retail_intensity_report"))
shortlist_report <- readRDS(read_artifact_path("05_parcels", "section_05_shortlist_report"))

schema_checks <- list(
  parcels_canonical = validate_columns(
    parcels_canonical,
    c("parcel_uid", "join_key", "county", "land_use_code", "assessed_value", "source_mode"),
    "section_05_parcels_canonical"
  ),
  retail_classified_parcels = validate_columns(
    sf::st_drop_geometry(retail_classified_parcels),
    c("parcel_uid", "retail_flag", "retail_subtype", "parcel_area_sqmi", "parcel_segment"),
    "section_05_retail_classified_parcels"
  ),
  retail_intensity = validate_columns(
    retail_intensity,
    c("tract_geoid", "retail_parcel_count", "retail_area", "retail_area_density"),
    "section_05_retail_intensity"
  ),
  zone_overlay_cluster = validate_columns(
    zone_overlay_cluster,
    c("zone_system", "zone_id", "zone_label", "retail_parcel_count", "zone_quality_score"),
    "section_05_zone_overlay_cluster"
  ),
  parcel_shortlist_cluster = validate_columns(
    sf::st_drop_geometry(parcel_shortlist_cluster),
    c(
      "parcel_uid", "zone_system", "zone_id", "zone_label", "shortlist_score",
      "shortlist_rank_system", "shortlist_rank_zone", "zone_quality_score",
      "local_retail_context_score", "parcel_characteristics_score",
      "just_value_clean",
      "assessed_value_clean", "assessed_value_psf", "assessed_value_psf_winsorized",
      "pctl_assessed_value_psf", "inv_pctl_assessed_value_psf"
    ),
    "section_05_parcel_shortlist_cluster"
  )
)

key_checks <- list(
  parcels_canonical = validate_unique_key(parcels_canonical, "parcel_uid", "section_05_parcels_canonical"),
  retail_classified_parcels = validate_unique_key(sf::st_drop_geometry(retail_classified_parcels), "parcel_uid", "section_05_retail_classified_parcels"),
  retail_intensity = validate_unique_key(retail_intensity, "tract_geoid", "section_05_retail_intensity"),
  zone_overlay_cluster = validate_unique_key(zone_overlay_cluster, "zone_id", "section_05_zone_overlay_cluster"),
  parcel_shortlist_cluster = list(
    dataset = "section_05_parcel_shortlist_cluster",
    key = "parcel_uid + zone_id",
    duplicates = sum(duplicated(paste(parcel_shortlist_cluster$parcel_uid, parcel_shortlist_cluster$zone_id, sep = "::"))),
    pass = sum(duplicated(paste(parcel_shortlist_cluster$parcel_uid, parcel_shortlist_cluster$zone_id, sep = "::"))) == 0
  )
)

geometry_checks <- list(
  retail_classified_parcels = list(
    dataset = "section_05_retail_classified_parcels",
    crs_epsg = sf::st_crs(retail_classified_parcels)$epsg,
    empty_geometries = sum(sf::st_is_empty(retail_classified_parcels)),
    invalid_geometries = sum(!sf::st_is_valid(retail_classified_parcels), na.rm = TRUE),
    pass = !is.na(sf::st_crs(retail_classified_parcels)$epsg) &&
      sf::st_crs(retail_classified_parcels)$epsg == GEOMETRY_ASSUMPTIONS$expected_crs_epsg &&
      sum(sf::st_is_empty(retail_classified_parcels)) == 0
  ),
  parcel_shortlist_cluster = list(
    dataset = "section_05_parcel_shortlist_cluster",
    crs_epsg = sf::st_crs(parcel_shortlist_cluster)$epsg,
    empty_geometries = sum(sf::st_is_empty(parcel_shortlist_cluster)),
    invalid_geometries = sum(!sf::st_is_valid(parcel_shortlist_cluster), na.rm = TRUE),
    pass = !is.na(sf::st_crs(parcel_shortlist_cluster)$epsg) &&
      sf::st_crs(parcel_shortlist_cluster)$epsg == GEOMETRY_ASSUMPTIONS$expected_crs_epsg &&
      sum(sf::st_is_empty(parcel_shortlist_cluster)) == 0
  )
)

coverage_metrics <- list(
  parcel_to_tract_assignment_rate = retail_intensity_report$counts$parcels_retail_assigned_to_tract / retail_intensity_report$counts$parcels_retail_flagged,
  parcel_to_zone_assignment_rate_cluster = nrow(parcel_shortlist_cluster) / retail_intensity_report$counts$parcels_retail_flagged
)

recompute_system_rank <- function(df) {
  o <- order(-df$shortlist_score, -df$zone_quality_score, -df$parcel_area_sqmi, df$parcel_uid, na.last = TRUE)
  expected <- seq_len(nrow(df))
  actual <- df$shortlist_rank_system[o]
  identical(actual, expected)
}

recompute_zone_rank <- function(df) {
  split_df <- split(df, df$zone_id)
  all(vapply(split_df, function(d) {
    o <- order(-d$shortlist_score, -d$parcel_area_sqmi, d$parcel_uid, na.last = TRUE)
    expected <- seq_len(nrow(d))
    actual <- d$shortlist_rank_zone[o]
    identical(actual, expected)
  }, logical(1)))
}

logic_checks <- list(
  retail_intensity_report_pass = isTRUE(retail_intensity_report$pass),
  shortlist_report_pass = isTRUE(shortlist_report$pass),
  cluster_system_only = all(sf::st_drop_geometry(parcel_shortlist_cluster)$zone_system == "cluster"),
  coverage_parcel_to_tract_min_95 = is.finite(coverage_metrics$parcel_to_tract_assignment_rate) &&
    coverage_metrics$parcel_to_tract_assignment_rate >= 0.95,
  coverage_parcel_to_zone_cluster_min_20 = is.finite(coverage_metrics$parcel_to_zone_assignment_rate_cluster) &&
    coverage_metrics$parcel_to_zone_assignment_rate_cluster >= 0.20,
  value_psf_nonnegative_when_present = all(
    is.na(parcel_shortlist_cluster$assessed_value_psf) | parcel_shortlist_cluster$assessed_value_psf >= 0
  ),
  shortlist_rank_system_deterministic_cluster = recompute_system_rank(sf::st_drop_geometry(parcel_shortlist_cluster)),
  shortlist_rank_zone_deterministic_cluster = recompute_zone_rank(sf::st_drop_geometry(parcel_shortlist_cluster))
)

warnings <- character()
if (is.finite(coverage_metrics$parcel_to_tract_assignment_rate) && coverage_metrics$parcel_to_tract_assignment_rate < 0.99) {
  warnings <- c(warnings, paste0("Parcel->tract assignment rate below warning threshold 0.99: ", round(coverage_metrics$parcel_to_tract_assignment_rate, 4)))
}
if (is.finite(coverage_metrics$parcel_to_zone_assignment_rate_cluster) && coverage_metrics$parcel_to_zone_assignment_rate_cluster < 0.30) {
  warnings <- c(warnings, paste0("Parcel->zone (cluster) assignment rate below warning threshold 0.30: ", round(coverage_metrics$parcel_to_zone_assignment_rate_cluster, 4)))
}

invalid_cluster <- geometry_checks$parcel_shortlist_cluster$invalid_geometries
if (is.finite(invalid_cluster) && invalid_cluster > 0) {
  warnings <- c(warnings, paste0("Cluster shortlist has invalid geometries: ", invalid_cluster))
}
missing_classified_geom <- retail_intensity_report$counts$retail_classified_missing_geometry
if (is.finite(missing_classified_geom) && missing_classified_geom > 0) {
  warnings <- c(warnings, paste0("Retail classified parcels missing geometry after late attach: ", missing_classified_geom))
}

schema_pass <- all(vapply(schema_checks, `[[`, logical(1), "pass"))
key_pass <- all(vapply(key_checks, `[[`, logical(1), "pass"))
geometry_pass <- all(vapply(geometry_checks, `[[`, logical(1), "pass"))
logic_pass <- all(unlist(logic_checks))

validation_report <- list(
  run_metadata = run_metadata(),
  schema_checks = schema_checks,
  key_checks = key_checks,
  geometry_checks = geometry_checks,
  coverage_metrics = coverage_metrics,
  logic_checks = logic_checks,
  warnings = warnings,
  pass = schema_pass && key_pass && geometry_pass && logic_pass
)

save_artifact(
  validation_report,
  resolve_output_path("05_parcels", "section_05_validation_report")
)

if (!isTRUE(validation_report$pass)) {
  stop("Section 05 checks failed. See section_05_validation_report.rds.", call. = FALSE)
}

message("Section 05 checks complete.")
