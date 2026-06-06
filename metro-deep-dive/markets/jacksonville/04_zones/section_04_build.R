# Section 04 build script
# Purpose: data prep and core transformations for section 04_zones.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()
source("notebooks/retail_opportunity_finder/data_platform/layers/03_zone_build/zone_build_workflow.R")

message("Running section 04 build: 04_zones")

scored_tracts <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_scored_tracts"))
tract_sf <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_tract_sf"))
tract_component_scores <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_tract_component_scores"))
cluster_seed_tracts <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_cluster_seed_tracts"))

zone_input_bundle <- build_zone_input_candidates(
  scored_tracts = scored_tracts,
  tract_sf = tract_sf,
  tract_component_scores = tract_component_scores,
  cluster_seed_tracts = cluster_seed_tracts
)
eligible_zone_inputs <- zone_input_bundle$eligible_zone_inputs
zone_candidate_tracts <- zone_input_bundle$zone_candidate_tracts
readiness_report <- zone_input_bundle$readiness_report

save_artifact(
  eligible_zone_inputs,
  resolve_output_path("04_zones", "section_04_zone_input_candidates")
)

save_artifact(
  readiness_report,
  resolve_output_path("04_zones", "section_04_input_readiness_report")
)

if (!isTRUE(readiness_report$pass)) {
  stop("Section 04 input readiness checks failed. See section_04_input_readiness_report.rds.", call. = FALSE)
}

message("Section 04 build step 1 complete: inputs loaded and validated.")

if (nrow(zone_candidate_tracts) == 0) {
  stop("No cluster seed tracts available for zone candidate universe.", call. = FALSE)
}

save_artifact(
  zone_candidate_tracts,
  resolve_output_path("04_zones", "section_04_zone_candidate_tracts")
)

message(glue::glue("Section 04 build step 2 complete: {nrow(zone_candidate_tracts)} cluster seed tracts selected as zone candidates."))

contiguity_products <- build_contiguity_zone_products(eligible_zone_inputs)
adjacency_edges <- contiguity_products$adjacency_edges
zone_components <- contiguity_products$zone_components
component_summary <- contiguity_products$component_summary

save_artifact(
  adjacency_edges,
  resolve_output_path("04_zones", "section_04_adjacency_edges")
)
save_artifact(
  zone_components,
  resolve_output_path("04_zones", "section_04_zone_components")
)
save_artifact(
  component_summary,
  resolve_output_path("04_zones", "section_04_component_summary")
)

message(glue::glue(
  "Section 04 build step 3 complete: {nrow(component_summary)} connected components across {nrow(zone_components)} tracts."
))

zones <- contiguity_products$zones
zone_order <- contiguity_products$zone_labels

save_artifact(
  zones,
  resolve_output_path("04_zones", "section_04_zones")
)

save_artifact(
  zone_order,
  resolve_output_path("04_zones", "section_04_zone_labels")
)

message(glue::glue(
  "Section 04 build step 4 complete: {nrow(zones)} zone geometries generated."
))

zone_summary <- contiguity_products$zone_summary

save_artifact(
  zone_summary,
  resolve_output_path("04_zones", "section_04_zone_summary")
)

con <- connect_project_duckdb(read_only = FALSE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
cluster_products <- build_cluster_zone_products(eligible_zone_inputs)
publish_zone_build_products(
  con,
  eligible_zone_inputs,
  contiguity_products,
  cluster_products
)

message(glue::glue(
  "Section 04 build step 5 complete: zone summary generated for {nrow(zone_summary)} zones."
))
