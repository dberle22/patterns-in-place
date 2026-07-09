# Section 05 build script
# Purpose: consumer-first parcel/overlay/shortlist build for section 05_parcels.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()
source("notebooks/retail_opportunity_finder/sections/05_parcels/section_05_inputs.R")

message("Running section 05 build: 05_parcels")

storage_crs_epsg <- GEOMETRY_ASSUMPTIONS$expected_crs_epsg
analysis_crs_epsg <- if (!is.null(GEOMETRY_ASSUMPTIONS$analysis_crs_epsg)) GEOMETRY_ASSUMPTIONS$analysis_crs_epsg else 5070
section_output_dir <- resolve_market_output_dir("05_parcels")
duckdb_con <- connect_project_duckdb(read_only = TRUE)
on.exit(DBI::dbDisconnect(duckdb_con, shutdown = TRUE), add = TRUE)
section_05_duckdb_inputs <- load_section_05_duckdb_inputs(duckdb_con, profile = get_market_profile())
previous_s2_option <- sf::sf_use_s2(FALSE)
on.exit(sf::sf_use_s2(previous_s2_option), add = TRUE)

normalize_for_spatial_ops <- function(sf_obj, object_name, target_epsg = analysis_crs_epsg) {
  if (!inherits(sf_obj, "sf")) {
    stop(glue::glue("{object_name} is not an sf object."), call. = FALSE)
  }
  sf_obj <- suppressWarnings(sf::st_make_valid(sf_obj))
  source_epsg <- sf::st_crs(sf_obj)$epsg
  if (is.na(source_epsg)) {
    stop(glue::glue("{object_name} has undefined CRS and cannot be transformed."), call. = FALSE)
  }
  if (identical(source_epsg, target_epsg)) {
    return(sf_obj)
  }
  sf::st_transform(sf_obj, target_epsg)
}

validate_sf_light <- function(
  sf_obj,
  name,
  expected_epsg = 4326,
  validity_sample_n = 5000L,
  require_no_empty = TRUE
) {
  is_sf <- inherits(sf_obj, "sf")
  n <- if (is_sf) nrow(sf_obj) else NA_integer_
  crs <- if (is_sf) sf::st_crs(sf_obj)$epsg else NA_integer_
  n_empty <- if (is_sf) sum(sf::st_is_empty(sf_obj)) else NA_integer_

  sample_n <- if (is_sf) min(validity_sample_n, n) else 0L
  invalid_sample <- NA_integer_
  if (is_sf && sample_n > 0) {
    idx <- seq_len(sample_n)
    valid_sample <- sf::st_is_valid(sf_obj[idx, ])
    invalid_sample <- sum(!valid_sample, na.rm = TRUE)
  }

  list(
    dataset = name,
    is_sf = is_sf,
    n_rows = n,
    crs_epsg = crs,
    empty_geometries = n_empty,
    validity_sample_n = sample_n,
    invalid_geometries_sample = invalid_sample,
    pass = is_sf &&
      !is.na(n) && n > 0 &&
      !is.na(crs) && crs == expected_epsg &&
      !is.na(n_empty) && (!isTRUE(require_no_empty) || n_empty == 0)
  )
}

safe_numeric <- function(x) suppressWarnings(as.numeric(x))

safe_percent_rank <- function(x) {
  if (all(is.na(x))) return(rep(0.5, length(x)))
  out <- dplyr::percent_rank(x)
  out[is.na(out)] <- 0.5
  out
}

winsorize_vector <- function(x, lower_q = 0.05, upper_q = 0.95) {
  if (all(is.na(x))) return(x)
  bounds <- stats::quantile(x, probs = c(lower_q, upper_q), na.rm = TRUE, names = FALSE)
  pmax(pmin(x, bounds[2]), bounds[1])
}

enrich_shortlist_metrics <- function(df) {
  df %>%
    mutate(
      just_value_clean = dplyr::if_else(!is.na(just_value) & just_value > 0, just_value, NA_real_),
      assessed_value_clean = dplyr::if_else(!is.na(assessed_value) & assessed_value > 0, assessed_value, NA_real_),
      parcel_area_sqft_est = parcel_area_sqmi * 27878400,
      parcel_area_sqft_clean = dplyr::if_else(
        !is.na(parcel_area_sqft_est) & parcel_area_sqft_est >= 1000,
        parcel_area_sqft_est,
        NA_real_
      ),
      assessed_value_psf = dplyr::if_else(
        !is.na(just_value_clean) & !is.na(parcel_area_sqft_clean) & parcel_area_sqft_clean > 0,
        just_value_clean / parcel_area_sqft_clean,
        NA_real_
      ),
      assessed_value_psf_winsorized = winsorize_vector(assessed_value_psf, lower_q = 0.05, upper_q = 0.95),
      pctl_assessed_value_psf = safe_percent_rank(assessed_value_psf_winsorized),
      inv_pctl_assessed_value_psf = 1 - pctl_assessed_value_psf
    )
}

build_geometry_lookup <- function(parcel_root, parcel_join_qa, expected_epsg = storage_crs_epsg) {
  parcel_geometry_paths <- resolve_parcel_analysis_paths(parcel_root)
  market_geometry_tags <- if (!is.null(parcel_join_qa) &&
    nrow(parcel_join_qa) > 0 &&
    "source_county_tag" %in% names(parcel_join_qa)) {
    unique(stats::na.omit(parcel_join_qa$source_county_tag))
  } else {
    character()
  }

  if (length(market_geometry_tags) > 0) {
    parcel_geometry_paths <- parcel_geometry_paths[basename(dirname(parcel_geometry_paths)) %in% market_geometry_tags]
  }

  if (length(parcel_geometry_paths) == 0) {
    stop(
      glue::glue("No county parcel geometry files found under {parcel_root}/county_outputs/*/parcel_geometries_analysis.rds"),
      call. = FALSE
    )
  }

  parcel_county_list <- lapply(parcel_geometry_paths, function(path) {
    sf_obj <- readRDS(path)
    sf_obj$source_county_tag <- basename(dirname(path))
    sf_obj
  })

  parcels_raw <- dplyr::bind_rows(parcel_county_list)

  parcel_required_cols <- c(
    "join_key", "parcel_id", "county", "county_name", "use_code",
    "land_value", "total_value", "sale_price1", "sale_yr1", "sale_mo1",
    "qa_missing_join_key", "qa_zero_county", "geometry"
  )
  parcel_schema_check <- validate_columns(
    parcels_raw,
    parcel_required_cols,
    "parcel_geometries_analysis_combined"
  )
  parcel_geom_check <- validate_sf_light(
    parcels_raw,
    "parcel_geometries_analysis_combined",
    expected_epsg,
    require_no_empty = FALSE
  )

  geometry_lookup <- parcels_raw %>%
    mutate(
      join_key = trimws(as.character(join_key)),
      county = as.character(county),
      parcel_uid = paste0(county, "::", join_key),
      source_county_tag = dplyr::coalesce(
        as.character(source_county_tag),
        if ("county_tag" %in% names(parcels_raw)) as.character(.data$county_tag) else NA_character_
      )
    ) %>%
    select(parcel_uid, source_county_tag, geometry) %>%
    filter(!is.na(parcel_uid), !stringr::str_detect(parcel_uid, "^NA::"), parcel_uid != "NA::NA") %>%
    distinct(parcel_uid, .keep_all = TRUE)

  list(
    parcel_geometry_paths = parcel_geometry_paths,
    parcels_raw = parcels_raw,
    parcel_schema_check = parcel_schema_check,
    parcel_geom_check = parcel_geom_check,
    geometry_lookup = geometry_lookup
  )
}

attach_geometry <- function(df, geometry_lookup, dataset_name, crs_epsg = storage_crs_epsg) {
  sf_obj <- df %>%
    left_join(geometry_lookup, by = "parcel_uid") %>%
    sf::st_as_sf(sf_column_name = "geometry", crs = crs_epsg)

  geom_check <- validate_sf_light(
    sf_obj,
    dataset_name,
    crs_epsg,
    require_no_empty = FALSE
  )

  list(
    data = sf_obj,
    geometry_check = geom_check,
    missing_geometry = sum(is.na(sf::st_dimension(sf_obj$geometry)))
  )
}

build_parcels_canonical_from_raw <- function(parcels_raw) {
  parcels_raw %>%
    mutate(
      join_key = trimws(as.character(join_key)),
      parcel_id = as.character(parcel_id),
      county = as.character(county),
      county_name = as.character(county_name),
      land_use_code = as.character(use_code),
      owner_name = dplyr::coalesce(
        if ("OWN_NAME" %in% names(parcels_raw)) as.character(.data$OWN_NAME) else NA_character_,
        if ("owner_name" %in% names(.)) as.character(.data$owner_name) else NA_character_
      ),
      owner_addr = dplyr::coalesce(
        if ("OWN_ADDR1" %in% names(parcels_raw)) as.character(.data$OWN_ADDR1) else NA_character_,
        if ("owner_addr" %in% names(.)) as.character(.data$owner_addr) else NA_character_
      ),
      site_addr = dplyr::coalesce(
        if ("PHY_ADDR1" %in% names(parcels_raw)) as.character(.data$PHY_ADDR1) else NA_character_,
        if ("phys_addr" %in% names(.)) as.character(.data$phys_addr) else NA_character_
      ),
      parcel_uid = paste0(county, "::", join_key),
      parcel_area_sqft = if ("LND_SQFOOT" %in% names(parcels_raw)) safe_numeric(.data$LND_SQFOOT) else NA_real_,
      just_value = if ("JV" %in% names(parcels_raw)) safe_numeric(.data$JV) else NA_real_,
      assessed_value = dplyr::coalesce(safe_numeric(total_value), safe_numeric(land_value)),
      last_sale_price = safe_numeric(sale_price1),
      sale_yr1 = suppressWarnings(as.integer(sale_yr1)),
      sale_mo1 = suppressWarnings(as.integer(sale_mo1)),
      sale_mo1 = dplyr::if_else(!is.na(sale_mo1) & sale_mo1 >= 1L & sale_mo1 <= 12L, sale_mo1, NA_integer_),
      last_sale_date = lubridate::make_date(year = sale_yr1, month = sale_mo1, day = 1L),
      source_mode = "legacy_geometry_fallback"
    ) %>%
    sf::st_drop_geometry() %>%
    select(
      parcel_uid,
      parcel_id,
      join_key,
      county,
      county_name,
      source_county_tag,
      land_use_code,
      owner_name,
      owner_addr,
      site_addr,
      parcel_area_sqft,
      just_value,
      assessed_value,
      last_sale_date,
      last_sale_price,
      qa_missing_join_key,
      qa_zero_county,
      source_mode
    ) %>%
    filter(!is.na(join_key), join_key != "", !is.na(county), county != "") %>%
    mutate(
      qa_missing_join_key = as.logical(qa_missing_join_key),
      qa_zero_county = as.logical(qa_zero_county)
    )
}

# Step D1: Input readiness and canonicalization (cluster-only)
cluster_zone_path <- read_artifact_path("04_zones", "section_04_cluster_zones")
cluster_zone_summary_path <- read_artifact_path("04_zones", "section_04_cluster_zone_summary")
parcel_root <- resolve_parcel_standardized_root()
parcel_manifest_path <- file.path(parcel_root, "parcel_ingest_manifest.rds")

required_paths <- c(
  cluster_zone_path,
  cluster_zone_summary_path,
  parcel_root
)

missing_paths <- required_paths[!file.exists(required_paths)]
if (length(missing_paths) > 0) {
  stop(
    glue::glue("Section 05 D1 missing required inputs: {paste(missing_paths, collapse = '; ')}"),
    call. = FALSE
  )
}

cluster_zones <- readRDS(cluster_zone_path)
cluster_zone_summary <- readRDS(cluster_zone_summary_path)

cluster_zone_schema_check <- validate_columns(
  cluster_zones,
  c("cluster_id", "cluster_label", "geometry"),
  "section_04_cluster_zones"
)
cluster_zone_summary_schema_check <- validate_columns(
  cluster_zone_summary,
  c("cluster_id", "cluster_label", "mean_tract_score"),
  "section_04_cluster_zone_summary"
)

cluster_zone_geom_check <- validate_sf(
  cluster_zones,
  "section_04_cluster_zones",
  storage_crs_epsg
)

zones_canonical <- cluster_zones %>%
  transmute(
    zone_system = "cluster",
    zone_id = as.character(cluster_id),
    zone_label = as.character(cluster_label),
    geometry = geometry
  ) %>%
  sf::st_make_valid() %>%
  arrange(zone_system, zone_id)

zones_canonical_key_check <- list(
  dataset = "section_05_zones_canonical",
  key = "zone_system + zone_id",
  n_rows = nrow(zones_canonical),
  n_distinct = dplyr::n_distinct(paste(zones_canonical$zone_system, zones_canonical$zone_id, sep = "::")),
  duplicates = nrow(zones_canonical) - dplyr::n_distinct(paste(zones_canonical$zone_system, zones_canonical$zone_id, sep = "::")),
  pass = nrow(zones_canonical) == dplyr::n_distinct(paste(zones_canonical$zone_system, zones_canonical$zone_id, sep = "::"))
)
zones_canonical_geom_check <- validate_sf(
  zones_canonical,
  "section_05_zones_canonical",
  storage_crs_epsg
)

serving_inputs_available <- !is.null(section_05_duckdb_inputs)
parcel_ingest_manifest <- if (file.exists(parcel_manifest_path)) readRDS(parcel_manifest_path) else NULL
geometry_bundle <- build_geometry_lookup(
  parcel_root = parcel_root,
  parcel_join_qa = if (serving_inputs_available) section_05_duckdb_inputs$parcel_join_qa else NULL,
  expected_epsg = storage_crs_epsg
)

if (serving_inputs_available && nrow(section_05_duckdb_inputs$parcels_canonical) > 0) {
  parcels_canonical <- section_05_duckdb_inputs$parcels_canonical %>%
    mutate(
      parcel_uid = as.character(parcel_uid),
      parcel_id = as.character(parcel_id),
      join_key = trimws(as.character(join_key)),
      county = as.character(county_code),
      county_name = as.character(county_name),
      source_county_tag = as.character(source_county_tag),
      land_use_code = as.character(land_use_code),
      owner_name = as.character(owner_name),
      owner_addr = as.character(owner_addr),
      site_addr = as.character(site_addr),
      parcel_area_sqft = NA_real_,
      just_value = safe_numeric(just_value),
      assessed_value = dplyr::coalesce(
        if ("total_value" %in% names(section_05_duckdb_inputs$parcels_canonical)) safe_numeric(.data$total_value) else NA_real_,
        if ("land_value" %in% names(section_05_duckdb_inputs$parcels_canonical)) safe_numeric(.data$land_value) else NA_real_,
        if ("assessed_value" %in% names(section_05_duckdb_inputs$parcels_canonical)) safe_numeric(.data$assessed_value) else NA_real_
      ),
      last_sale_price = safe_numeric(last_sale_price),
      last_sale_date = as.Date(last_sale_date),
      qa_missing_join_key = as.logical(qa_missing_join_key),
      qa_zero_county = as.logical(qa_zero_county),
      source_mode = "duckdb_parcels_canonical"
    ) %>%
    select(
      parcel_uid,
      parcel_id,
      join_key,
      county,
      county_name,
      source_county_tag,
      land_use_code,
      owner_name,
      owner_addr,
      site_addr,
      parcel_area_sqft,
      just_value,
      assessed_value,
      last_sale_date,
      last_sale_price,
      qa_missing_join_key,
      qa_zero_county,
      source_mode
    ) %>%
    filter(!is.na(join_key), join_key != "", !is.na(county), county != "")
} else {
  parcels_canonical <- build_parcels_canonical_from_raw(geometry_bundle$parcels_raw)
}

parcels_canonical_key_check <- validate_unique_key(parcels_canonical, "parcel_uid", "section_05_parcels_canonical")
parcel_null_summary <- null_rate_summary(
  parcels_canonical,
  c("parcel_area_sqft", "assessed_value", "last_sale_date", "last_sale_price", "land_use_code"),
  "section_05_parcels_canonical"
)

readiness_report <- list(
  run_metadata = run_metadata(),
  source_modes = list(
    parcels_canonical = if (nrow(parcels_canonical) > 0) unique(parcels_canonical$source_mode) else character(),
    retail_parcels = if (serving_inputs_available && nrow(section_05_duckdb_inputs$retail_parcels) > 0) "duckdb_retail_parcels" else "mapping_or_canonical_fallback",
    retail_assignment = if (serving_inputs_available && nrow(section_05_duckdb_inputs$retail_parcel_tract_assignment) > 0) "duckdb_serving_assignment" else "spatial_fallback_if_needed",
    retail_intensity = if (serving_inputs_available && nrow(section_05_duckdb_inputs$retail_intensity_by_tract) > 0) "duckdb_serving_intensity" else "derived_in_section",
    parcel_zone_overlay = if (serving_inputs_available && nrow(section_05_duckdb_inputs$parcel_zone_overlay) > 0) "duckdb_serving_overlay" else "derived_in_section",
    parcel_shortlist = if (serving_inputs_available && nrow(section_05_duckdb_inputs$parcel_shortlist) > 0) "duckdb_serving_shortlist" else "derived_in_section"
  ),
  input_files = list(
    cluster_zone_path = cluster_zone_path,
    cluster_zone_summary_path = cluster_zone_summary_path,
    parcel_root = parcel_root,
    parcel_manifest_path = if (file.exists(parcel_manifest_path)) parcel_manifest_path else NA_character_,
    parcel_geometry_files = geometry_bundle$parcel_geometry_paths
  ),
  schema_checks = list(
    cluster_zone_schema_check = cluster_zone_schema_check,
    cluster_zone_summary_schema_check = cluster_zone_summary_schema_check,
    parcel_schema_check = geometry_bundle$parcel_schema_check
  ),
  geometry_checks = list(
    cluster_zone_geom_check = cluster_zone_geom_check,
    zones_canonical_geom_check = zones_canonical_geom_check,
    parcel_geom_check = geometry_bundle$parcel_geom_check
  ),
  key_checks = list(
    zones_canonical_key_check = zones_canonical_key_check,
    parcels_canonical_key_check = parcels_canonical_key_check
  ),
  counts = list(
    cluster_zones = nrow(cluster_zones),
    canonical_zone_rows = nrow(zones_canonical),
    parcel_manifest_rows = if (is.null(parcel_ingest_manifest)) 0L else nrow(parcel_ingest_manifest),
    parcel_county_files = length(geometry_bundle$parcel_geometry_paths),
    parcels_raw_rows = nrow(geometry_bundle$parcels_raw),
    parcels_canonical_rows = nrow(parcels_canonical),
    parcels_loaded_from_duckdb = if (serving_inputs_available) nrow(section_05_duckdb_inputs$parcels_canonical) else 0L
  ),
  null_summary = parcel_null_summary,
  warnings = list(
    parcel_invalid_sample_count_raw = geometry_bundle$parcel_geom_check$invalid_geometries_sample,
    spatial_ops_crs_epsg = analysis_crs_epsg
  ),
  pass = isTRUE(cluster_zone_schema_check$pass) &&
    isTRUE(cluster_zone_summary_schema_check$pass) &&
    isTRUE(cluster_zone_geom_check$pass) &&
    isTRUE(zones_canonical_geom_check$pass) &&
    isTRUE(zones_canonical_key_check$pass) &&
    isTRUE(geometry_bundle$parcel_schema_check$pass) &&
    isTRUE(geometry_bundle$parcel_geom_check$pass) &&
    isTRUE(parcels_canonical_key_check$pass)
)

save_artifact(
  zones_canonical,
  resolve_output_path("05_parcels", "section_05_zones_canonical")
)
save_artifact(
  parcels_canonical,
  resolve_output_path("05_parcels", "section_05_parcels_canonical")
)
save_artifact(
  readiness_report,
  resolve_output_path("05_parcels", "section_05_input_readiness_report")
)

if (!isTRUE(readiness_report$pass)) {
  stop("Section 05 D1 input readiness checks failed. See section_05_input_readiness_report.rds.", call. = FALSE)
}

message(glue::glue(
  "Section 05 D1 complete: {nrow(zones_canonical)} canonical cluster zones and {nrow(parcels_canonical)} canonical parcels."
))

# Step D2: Retail classification and tract-level retail intensity
mapping_path <- read_artifact_path("05_parcels", "section_05_retail_land_use_mapping_candidates_v0_1", ext = "csv")

retail_mapping <- if (serving_inputs_available && nrow(section_05_duckdb_inputs$retail_mapping) > 0) {
  section_05_duckdb_inputs$retail_mapping %>%
    transmute(
      use_code = as.character(land_use_code),
      land_use_code = as.character(land_use_code),
      use_code_definition = as.character(description),
      use_code_type = as.character(category),
      retail_flag = as.logical(retail_flag),
      retail_subtype = as.character(retail_subtype),
      review_note = as.character(review_note)
    ) %>%
    distinct(land_use_code, .keep_all = TRUE)
} else {
  if (!file.exists(mapping_path)) {
    stop(glue::glue("Missing retail mapping file: {mapping_path}"), call. = FALSE)
  }

  readr::read_csv(mapping_path, show_col_types = FALSE) %>%
    transmute(
      land_use_code = as.character(use_code),
      use_code_definition = dplyr::coalesce(
        if ("definition" %in% names(.)) as.character(.data$definition) else NA_character_,
        if ("definition.x" %in% names(.)) as.character(.data$definition.x) else NA_character_,
        if ("property_use_description" %in% names(.)) as.character(.data$property_use_description) else NA_character_
      ),
      use_code_type = dplyr::coalesce(
        if ("type" %in% names(.)) as.character(.data$type) else NA_character_,
        if ("type.x" %in% names(.)) as.character(.data$type.x) else NA_character_
      ),
      retail_flag = as.logical(retail_flag),
      retail_subtype = as.character(retail_subtype),
      review_note = as.character(review_note)
    ) %>%
    distinct(land_use_code, .keep_all = TRUE)
}

readr::write_csv(
  retail_mapping %>%
    transmute(
      use_code = land_use_code,
      definition = use_code_definition,
      type = use_code_type,
      retail_flag = retail_flag,
      retail_subtype = retail_subtype,
      review_note = review_note
    ),
  mapping_path
)

retail_mapping_check <- validate_columns(
  retail_mapping,
  c("land_use_code", "retail_flag", "retail_subtype"),
  "section_05_retail_mapping"
)
if (!isTRUE(retail_mapping_check$pass)) {
  stop("Retail mapping schema check failed.", call. = FALSE)
}

if (serving_inputs_available && nrow(section_05_duckdb_inputs$retail_parcels) > 0) {
  retail_lookup <- section_05_duckdb_inputs$retail_parcels %>%
    transmute(
      parcel_uid = as.character(parcel_uid),
      use_code_definition = as.character(land_use_description),
      use_code_type = as.character(land_use_category),
      retail_flag = as.logical(retail_flag),
      retail_subtype = dplyr::if_else(retail_flag & is.na(retail_subtype), "retail_uncategorized", as.character(retail_subtype)),
      review_note = as.character(review_note),
      parcel_segment = "Retail parcel"
    ) %>%
    distinct(parcel_uid, .keep_all = TRUE)

  retail_classified_parcels_tabular <- parcels_canonical %>%
    left_join(retail_lookup, by = "parcel_uid") %>%
    left_join(
      retail_mapping %>%
        select(land_use_code, mapped_definition = use_code_definition, mapped_type = use_code_type, mapped_review_note = review_note),
      by = "land_use_code"
    ) %>%
    mutate(
      use_code_definition = dplyr::coalesce(use_code_definition, mapped_definition),
      use_code_type = dplyr::coalesce(use_code_type, mapped_type),
      review_note = dplyr::coalesce(review_note, mapped_review_note),
      retail_flag = dplyr::coalesce(retail_flag, FALSE),
      retail_subtype = dplyr::if_else(retail_flag & is.na(retail_subtype), "retail_uncategorized", retail_subtype),
      parcel_segment = dplyr::if_else(retail_flag, "Retail parcel", "Residential/other parcel")
    ) %>%
    select(-mapped_definition, -mapped_type, -mapped_review_note)
} else {
  retail_classified_parcels_tabular <- parcels_canonical %>%
    left_join(retail_mapping, by = "land_use_code") %>%
    mutate(
      retail_flag = dplyr::coalesce(retail_flag, FALSE),
      retail_subtype = dplyr::if_else(retail_flag & is.na(retail_subtype), "retail_uncategorized", retail_subtype),
      parcel_segment = dplyr::if_else(retail_flag, "Retail parcel", "Residential/other parcel")
    )
}

retail_geometry_bundle <- attach_geometry(
  retail_classified_parcels_tabular,
  geometry_bundle$geometry_lookup,
  "section_05_retail_classified_parcels",
  storage_crs_epsg
)
retail_classified_parcels <- retail_geometry_bundle$data

retail_classified_parcels_proj <- normalize_for_spatial_ops(
  retail_classified_parcels,
  "retail_classified_parcels",
  analysis_crs_epsg
)
parcel_area_sqmi_from_geom <- as.numeric(sf::st_area(retail_classified_parcels_proj)) / 2589988.110336
retail_classified_parcels$parcel_area_sqmi <- dplyr::coalesce(
  safe_numeric(retail_classified_parcels$parcel_area_sqft) / 27878400,
  parcel_area_sqmi_from_geom
)

save_artifact(
  retail_classified_parcels,
  resolve_output_path("05_parcels", "section_05_retail_classified_parcels")
)

retail_parcels <- retail_classified_parcels %>%
  filter(retail_flag) %>%
  filter(!sf::st_is_empty(geometry))

if (nrow(retail_parcels) == 0) {
  stop("No retail-flagged parcels available after classification.", call. = FALSE)
}

serving_assignment_available <- serving_inputs_available && nrow(section_05_duckdb_inputs$retail_parcel_tract_assignment) > 0
serving_intensity_available <- serving_inputs_available && nrow(section_05_duckdb_inputs$retail_intensity_by_tract) > 0
serving_overlay_available <- serving_inputs_available && nrow(section_05_duckdb_inputs$parcel_zone_overlay) > 0
serving_shortlist_available <- serving_inputs_available && nrow(section_05_duckdb_inputs$parcel_shortlist) > 0

tract_schema_check <- list(dataset = "section_03_tract_sf", pass = TRUE, mode = "not_required")
tract_geom_check <- list(dataset = "section_03_tract_sf", pass = TRUE, mode = "not_required")

if (serving_assignment_available) {
  retail_assignment <- section_05_duckdb_inputs$retail_parcel_tract_assignment %>%
    filter(assignment_status == "assigned", !is.na(tract_geoid))
} else {
  tract_sf <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_tract_sf")) %>%
    select(tract_geoid, geometry)

  tract_schema_check <- validate_columns(tract_sf, c("tract_geoid", "geometry"), "section_03_tract_sf")
  tract_geom_check <- validate_sf(tract_sf, "section_03_tract_sf", storage_crs_epsg)
  if (!isTRUE(tract_schema_check$pass) || !isTRUE(tract_geom_check$pass)) {
    stop("Tract geometry input validation failed for D2.", call. = FALSE)
  }

  tract_sf_proj <- normalize_for_spatial_ops(tract_sf, "tract_sf", analysis_crs_epsg)
  retail_parcels_proj <- normalize_for_spatial_ops(retail_parcels, "retail_parcels", analysis_crs_epsg)
  retail_point_geom <- sf::st_point_on_surface(sf::st_geometry(retail_parcels_proj))
  retail_points <- sf::st_as_sf(
    sf::st_drop_geometry(retail_parcels_proj),
    geometry = retail_point_geom,
    crs = analysis_crs_epsg
  )

  retail_assignment <- sf::st_join(
    retail_points,
    tract_sf_proj %>% select(tract_geoid),
    join = sf::st_within,
    left = TRUE
  ) %>%
    sf::st_drop_geometry() %>%
    filter(!is.na(tract_geoid)) %>%
    mutate(assignment_status = "assigned")
}

if (serving_intensity_available) {
  retail_intensity <- section_05_duckdb_inputs$retail_intensity_by_tract %>%
    arrange(tract_geoid)
} else {
  if (!exists("tract_sf")) {
    tract_sf <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_tract_sf")) %>%
      select(tract_geoid, geometry)
    tract_schema_check <- validate_columns(tract_sf, c("tract_geoid", "geometry"), "section_03_tract_sf")
    tract_geom_check <- validate_sf(tract_sf, "section_03_tract_sf", storage_crs_epsg)
    if (!isTRUE(tract_schema_check$pass) || !isTRUE(tract_geom_check$pass)) {
      stop("Tract geometry input validation failed for D2.", call. = FALSE)
    }
  }

  tract_land_area <- tract_sf %>%
    normalize_for_spatial_ops("tract_sf_for_area", analysis_crs_epsg) %>%
    mutate(
      tract_land_area_sqmi = as.numeric(sf::st_area(geometry)) / 2589988.110336
    ) %>%
    sf::st_drop_geometry() %>%
    select(tract_geoid, tract_land_area_sqmi)

  retail_intensity <- retail_assignment %>%
    left_join(
      retail_parcels %>%
        sf::st_drop_geometry() %>%
        select(parcel_uid, parcel_area_sqmi),
      by = "parcel_uid"
    ) %>%
    group_by(tract_geoid) %>%
    summarise(
      retail_parcel_count = dplyr::n_distinct(parcel_uid),
      retail_area = sum(parcel_area_sqmi, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    right_join(tract_land_area, by = "tract_geoid") %>%
    mutate(
      retail_parcel_count = dplyr::coalesce(retail_parcel_count, 0L),
      retail_area = dplyr::coalesce(retail_area, 0),
      retail_area_density = dplyr::if_else(
        !is.na(tract_land_area_sqmi) & tract_land_area_sqmi > 0,
        retail_area / tract_land_area_sqmi,
        NA_real_
      ),
      pctl_tract_retail_parcel_count = safe_percent_rank(retail_parcel_count),
      pctl_tract_retail_area_density = safe_percent_rank(retail_area_density),
      local_retail_context_score = 0.5 * pctl_tract_retail_parcel_count + 0.5 * pctl_tract_retail_area_density
    ) %>%
    arrange(tract_geoid)
}

retail_intensity_report <- list(
  run_metadata = run_metadata(),
  source_modes = list(
    retail_assignment = if (serving_assignment_available) "duckdb_serving_assignment" else "spatial_fallback",
    retail_intensity = if (serving_intensity_available) "duckdb_serving_intensity" else "section_derived"
  ),
  checks = list(
    retail_mapping_check = retail_mapping_check,
    tract_schema_check = tract_schema_check,
    tract_geom_check = tract_geom_check,
    retail_classified_geom_check = retail_geometry_bundle$geometry_check
  ),
  counts = list(
    parcels_total = nrow(parcels_canonical),
    parcels_retail_flagged = nrow(retail_parcels),
    parcels_retail_assigned_to_tract = nrow(retail_assignment),
    parcels_retail_unassigned = nrow(retail_parcels) - nrow(retail_assignment),
    tracts_total = nrow(retail_intensity),
    tracts_with_retail = sum(retail_intensity$retail_parcel_count > 0, na.rm = TRUE),
    retail_classified_missing_geometry = retail_geometry_bundle$missing_geometry
  ),
  pass = isTRUE(retail_mapping_check$pass) &&
    isTRUE(tract_schema_check$pass) &&
    isTRUE(tract_geom_check$pass) &&
    isTRUE(retail_geometry_bundle$geometry_check$pass)
)

save_artifact(
  retail_intensity,
  resolve_output_path("05_parcels", "section_05_retail_intensity")
)
save_artifact(
  retail_intensity_report,
  resolve_output_path("05_parcels", "section_05_retail_intensity_report")
)

message(glue::glue(
  "Section 05 D2 complete: {nrow(retail_parcels)} retail parcels classified; {sum(retail_intensity$retail_parcel_count > 0)} tracts with retail signal."
))

# Step D3: Cluster zone overlays and parcel shortlist candidates
cluster_assignments <- readRDS(read_artifact_path("04_zones", "section_04_cluster_assignments"))

cluster_assignments_check <- validate_columns(
  cluster_assignments,
  c("tract_geoid", "cluster_id", "cluster_label"),
  "section_04_cluster_assignments"
)
if (!isTRUE(cluster_assignments_check$pass)) {
  stop("Section 05 D3 cluster mapping inputs failed schema checks.", call. = FALSE)
}

tract_zone_map <- cluster_assignments %>%
  transmute(
    tract_geoid = as.character(tract_geoid),
    zone_system = "cluster",
    zone_id = as.character(cluster_id),
    zone_label = as.character(cluster_label)
  )

tract_zone_map_key_check <- list(
  dataset = "section_05_tract_zone_map",
  key = "zone_system + tract_geoid",
  n_rows = nrow(tract_zone_map),
  n_distinct = dplyr::n_distinct(paste(tract_zone_map$zone_system, tract_zone_map$tract_geoid, sep = "::")),
  duplicates = nrow(tract_zone_map) - dplyr::n_distinct(paste(tract_zone_map$zone_system, tract_zone_map$tract_geoid, sep = "::")),
  pass = nrow(tract_zone_map) == dplyr::n_distinct(paste(tract_zone_map$zone_system, tract_zone_map$tract_geoid, sep = "::"))
)
if (!isTRUE(tract_zone_map_key_check$pass)) {
  stop("Section 05 D3 tract-zone mapping is not unique by zone_system + tract_geoid.", call. = FALSE)
}

if (serving_overlay_available) {
  zone_overlay_cluster <- section_05_duckdb_inputs$parcel_zone_overlay %>%
    filter(zone_system == "cluster") %>%
    arrange(zone_order)
} else {
  retail_intensity_scored <- retail_intensity %>%
    mutate(
      pctl_tract_retail_parcel_count = safe_percent_rank(retail_parcel_count),
      pctl_tract_retail_area_density = safe_percent_rank(retail_area_density),
      local_retail_context_score = 0.5 * pctl_tract_retail_parcel_count + 0.5 * pctl_tract_retail_area_density
    )

  zone_quality <- cluster_zone_summary %>%
    transmute(
      zone_system = "cluster",
      zone_id = as.character(cluster_id),
      zone_label = as.character(cluster_label),
      mean_tract_score = as.numeric(mean_tract_score)
    ) %>%
    mutate(zone_quality_score = safe_percent_rank(mean_tract_score))

  zone_overlay_cluster <- tract_zone_map %>%
    left_join(retail_intensity_scored, by = "tract_geoid") %>%
    group_by(zone_system, zone_id, zone_label) %>%
    summarise(
      tracts = dplyr::n_distinct(tract_geoid),
      retail_parcel_count = sum(retail_parcel_count, na.rm = TRUE),
      retail_area = sum(retail_area, na.rm = TRUE),
      tract_land_area_sqmi = sum(tract_land_area_sqmi, na.rm = TRUE),
      retail_area_density = dplyr::if_else(tract_land_area_sqmi > 0, retail_area / tract_land_area_sqmi, NA_real_),
      local_retail_context_score = mean(local_retail_context_score, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    left_join(
      zone_quality %>% select(zone_system, zone_id, mean_tract_score, zone_quality_score),
      by = c("zone_system", "zone_id")
    ) %>%
    arrange(desc(zone_quality_score), desc(retail_parcel_count))
}

if (serving_shortlist_available) {
  shortlist_geometry_bundle <- attach_geometry(
    section_05_duckdb_inputs$parcel_shortlist %>%
      filter(zone_system == "cluster") %>%
      enrich_shortlist_metrics(),
    geometry_bundle$geometry_lookup,
    "section_05_parcel_shortlist_cluster",
    storage_crs_epsg
  )
  parcel_shortlist_cluster <- shortlist_geometry_bundle$data
} else {
  parcel_tract_map <- retail_assignment %>%
    select(parcel_uid, tract_geoid) %>%
    distinct(parcel_uid, .keep_all = TRUE)

  parcel_zone_cluster <- parcel_tract_map %>%
    inner_join(tract_zone_map, by = "tract_geoid") %>%
    distinct(zone_system, parcel_uid, zone_id, .keep_all = TRUE)

  retail_intensity_scored <- retail_intensity %>%
    mutate(
      pctl_tract_retail_parcel_count = safe_percent_rank(retail_parcel_count),
      pctl_tract_retail_area_density = safe_percent_rank(retail_area_density),
      local_retail_context_score = 0.5 * pctl_tract_retail_parcel_count + 0.5 * pctl_tract_retail_area_density
    )

  zone_quality <- cluster_zone_summary %>%
    transmute(
      zone_system = "cluster",
      zone_id = as.character(cluster_id),
      zone_label = as.character(cluster_label),
      mean_tract_score = as.numeric(mean_tract_score)
    ) %>%
    mutate(zone_quality_score = safe_percent_rank(mean_tract_score))

  parcel_shortlist_candidates <- parcel_zone_cluster %>%
    left_join(parcel_tract_map, by = "parcel_uid") %>%
    left_join(
      retail_classified_parcels %>%
        sf::st_drop_geometry() %>%
        select(
          parcel_uid, parcel_id, county, county_name, land_use_code,
          use_code_definition, use_code_type,
          owner_name, owner_addr, site_addr,
          retail_subtype, review_note,
          parcel_area_sqmi, just_value, assessed_value, last_sale_date, last_sale_price
        ),
      by = "parcel_uid"
    ) %>%
    left_join(
      retail_intensity_scored %>%
        select(tract_geoid, pctl_tract_retail_parcel_count, pctl_tract_retail_area_density, local_retail_context_score),
      by = "tract_geoid"
    ) %>%
    left_join(
      zone_quality %>% select(zone_system, zone_id, zone_label, mean_tract_score, zone_quality_score),
      by = c("zone_system", "zone_id")
    )

  parcel_shortlist_scored <- parcel_shortlist_candidates %>%
    enrich_shortlist_metrics() %>%
    mutate(
      sale_recency_days = as.numeric(difftime(Sys.Date(), last_sale_date, units = "days")),
      pctl_parcel_area = safe_percent_rank(parcel_area_sqmi),
      pctl_sale_recency = safe_percent_rank(-sale_recency_days),
      parcel_characteristics_score = 0.4 * pctl_parcel_area + 0.3 * inv_pctl_assessed_value_psf + 0.3 * pctl_sale_recency,
      shortlist_score = 0.50 * zone_quality_score + 0.25 * local_retail_context_score + 0.25 * parcel_characteristics_score
    ) %>%
    arrange(
      desc(shortlist_score),
      desc(zone_quality_score),
      desc(parcel_area_sqmi),
      parcel_uid
    ) %>%
    mutate(shortlist_rank_system = row_number()) %>%
    group_by(zone_id) %>%
    arrange(desc(shortlist_score), desc(parcel_area_sqmi), parcel_uid, .by_group = TRUE) %>%
    mutate(shortlist_rank_zone = row_number()) %>%
    ungroup()

  shortlist_geometry_bundle <- attach_geometry(
    parcel_shortlist_scored,
    geometry_bundle$geometry_lookup,
    "section_05_parcel_shortlist_cluster",
    storage_crs_epsg
  )
  parcel_shortlist_cluster <- shortlist_geometry_bundle$data
}

save_artifact(
  zone_overlay_cluster,
  resolve_output_path("05_parcels", "section_05_zone_overlay_cluster")
)

save_artifact(
  parcel_shortlist_cluster,
  resolve_output_path("05_parcels", "section_05_parcel_shortlist_cluster")
)

shortlist_report <- list(
  run_metadata = run_metadata(),
  source_modes = list(
    parcel_zone_overlay = if (serving_overlay_available) "duckdb_serving_overlay" else "section_derived_from_tract_zone_map",
    parcel_shortlist = if (serving_shortlist_available) "duckdb_serving_shortlist" else "section_derived_from_tract_zone_map"
  ),
  checks = list(
    cluster_assignments_check = cluster_assignments_check,
    tract_zone_map_key_check = tract_zone_map_key_check,
    shortlist_geom_check = shortlist_geometry_bundle$geometry_check
  ),
  counts = list(
    overlay_cluster_zones = nrow(zone_overlay_cluster),
    parcel_zone_assignments_cluster = nrow(parcel_shortlist_cluster),
    shortlist_cluster_rows = nrow(parcel_shortlist_cluster),
    shortlist_missing_geometry_cluster = shortlist_geometry_bundle$missing_geometry,
    shortlist_zero_or_negative_just_value_count = if ("just_value_clean" %in% names(parcel_shortlist_cluster)) sum(is.na(parcel_shortlist_cluster$just_value_clean)) else sum(is.na(parcel_shortlist_cluster$just_value) | parcel_shortlist_cluster$just_value <= 0, na.rm = TRUE),
    shortlist_small_area_excluded_from_value_psf_count = if ("parcel_area_sqft_clean" %in% names(parcel_shortlist_cluster)) sum(is.na(parcel_shortlist_cluster$parcel_area_sqft_clean)) else NA_integer_,
    shortlist_missing_value_psf_count = if ("assessed_value_psf" %in% names(parcel_shortlist_cluster)) sum(is.na(parcel_shortlist_cluster$assessed_value_psf)) else NA_integer_,
    shortlist_winsorized_low_count = if (all(c("assessed_value_psf", "assessed_value_psf_winsorized") %in% names(parcel_shortlist_cluster))) {
      sum(
        !is.na(parcel_shortlist_cluster$assessed_value_psf) &
          !is.na(parcel_shortlist_cluster$assessed_value_psf_winsorized) &
          parcel_shortlist_cluster$assessed_value_psf_winsorized < parcel_shortlist_cluster$assessed_value_psf
      )
    } else {
      NA_integer_
    },
    shortlist_winsorized_high_count = if (all(c("assessed_value_psf", "assessed_value_psf_winsorized") %in% names(parcel_shortlist_cluster))) {
      sum(
        !is.na(parcel_shortlist_cluster$assessed_value_psf) &
          !is.na(parcel_shortlist_cluster$assessed_value_psf_winsorized) &
          parcel_shortlist_cluster$assessed_value_psf_winsorized > parcel_shortlist_cluster$assessed_value_psf
      )
    } else {
      NA_integer_
    }
  ),
  pass = isTRUE(cluster_assignments_check$pass) &&
    isTRUE(tract_zone_map_key_check$pass) &&
    isTRUE(shortlist_geometry_bundle$geometry_check$pass)
)

save_artifact(
  shortlist_report,
  resolve_output_path("05_parcels", "section_05_shortlist_report")
)

if (!isTRUE(shortlist_report$pass)) {
  stop("Section 05 D3 failed checklist validations. See section_05_shortlist_report.rds.", call. = FALSE)
}

message(glue::glue(
  "Section 05 D3 complete: {nrow(parcel_shortlist_cluster)} cluster parcel candidates."
))
