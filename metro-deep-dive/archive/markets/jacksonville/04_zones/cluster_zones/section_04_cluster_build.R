# Section 04 cluster build script
# Purpose: generate cluster-based zones from eligible tract candidates.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()
source("notebooks/retail_opportunity_finder/data_platform/layers/03_zone_build/zone_build_workflow.R")

message("Running section 04 cluster build")

zone_inputs <- readRDS(read_artifact_path("04_zones", "section_04_zone_input_candidates"))
cluster_products <- build_cluster_zone_products(zone_inputs)
cluster_assignments <- cluster_products$cluster_assignments
cluster_zones <- cluster_products$cluster_zones
cluster_zone_summary <- cluster_products$cluster_zone_summary
cluster_params <- cluster_products$cluster_params

save_artifact(
  cluster_assignments,
  resolve_output_path("04_zones", "section_04_cluster_assignments")
)
save_artifact(
  cluster_zones,
  resolve_output_path("04_zones", "section_04_cluster_zones")
)
save_artifact(
  cluster_zone_summary,
  resolve_output_path("04_zones", "section_04_cluster_zone_summary")
)
save_artifact(
  cluster_params,
  resolve_output_path("04_zones", "section_04_cluster_params")
)

message(glue::glue(
  "Cluster build complete: {nrow(cluster_zone_summary)} cluster zones generated from {nrow(cluster_assignments)} tracts."
))
