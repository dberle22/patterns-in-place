# Section Output Contracts

This file defines expected outputs from each section module so `.qmd` integration can remain stable.

## General conventions
- Persist reusable objects as `.rds` under each section's `outputs/` folder.
- Active Sprint 3 behavior is market-partitioned by default:
  `sections/<section_id>/outputs/<market_key>/section_<xx>_<artifact>.rds`
- Readers should use shared artifact resolvers so older legacy root-level outputs can still be read during transition.
- File naming pattern: `section_<xx>_<artifact_name>.rds`.
- Include a `generated_at` timestamp column/field where practical.
- Geospatial outputs should include explicit CRS metadata.

## Section contracts

### 01_setup
- `outputs/section_01_run_metadata.rds`
  - List with run metadata and selected parameters.
- `outputs/section_01_foundation.rds`
  - Shared foundations payload (KPI dictionary, model params, model parameter validation).
- `outputs/section_01_validation_report.rds`
  - Column/key/null/geometry validation report for primary notebook inputs.

### 02_market_overview
- `outputs/section_02_kpi_tiles.rds`
  - One-row data frame with metro KPI tile values.
- `outputs/section_02_peer_table.rds`
  - Data frame for peer ranking table.
- `outputs/section_02_benchmark_table.rds`
  - Data frame for JAX vs region vs US comparison.
- `outputs/section_02_pop_trend_indexed.rds`
  - Indexed population trend data for Jacksonville, South Atlantic, and U.S. CBSAs.
- `outputs/section_02_distribution_long.rds`
  - Long-format all-metro distribution dataset used for boxplot facets.
- `outputs/section_02_visual_objects.rds`
  - Render-ready UI/table/plot objects (tiles layout, gt tables, ggplots).
- `outputs/section_02_validation_report.rds`
  - Schema and logic checks for all Section 02 artifacts.

### 03_eligibility_scoring
- `outputs/section_03_funnel_counts.rds`
  - Funnel step counts through growth, price, density, and final eligibility gates.
- `outputs/section_03_eligible_tracts.rds`
  - Tract-level filtered set with eligibility flags.
- `outputs/section_03_scored_tracts.rds`
  - Tract-level scored set with component z-scores and weighted contributions.
- `outputs/section_03_top_tracts.rds`
  - Top-N tract table with rank and why-tags.
- `outputs/section_03_tract_component_scores.rds`
  - Full tract-level table with raw components, z-scores, weighted contributions, and final score/rank.
- `outputs/section_03_tract_component_scores.csv`
  - CSV export of tract-level component and score table for external review.
- `outputs/section_03_visual_objects.rds`
  - Render-ready Section 03 gt/ggplot objects.
- `outputs/section_03_validation_report.rds`
  - Section 03 schema, logic, and geometry validation report.

### 04_zones
- `outputs/section_04_zone_input_candidates.rds`
  - Eligible tract-level `sf` input dataset validated for zone construction.
- `outputs/section_04_input_readiness_report.rds`
  - Input readiness checks for Sprint B dependencies (schema, keys, geometry, set consistency).
- `outputs/section_04_zone_candidate_tracts.rds`
  - Eligible tract list used as the candidate universe for zoning.
- `outputs/section_04_adjacency_edges.rds`
  - Undirected tract adjacency edge list among zone candidates.
- `outputs/section_04_zone_components.rds`
  - Tract-to-component assignments from connected-components analysis.
- `outputs/section_04_component_summary.rds`
  - Component-level tract counts and draft zone labels.
- `outputs/section_04_zones.rds`
  - Zone geometry/object with zone IDs and labels.
- `outputs/section_04_zone_labels.rds`
  - Deterministic zone label mapping and ordering metadata.
- `outputs/section_04_zone_summary.rds`
  - Zone-level KPI summary table.
- `outputs/section_04_visual_objects.rds`
  - Render-ready Section 04 visual objects (zone map plot + summary gt table).
- `outputs/section_04_zone_map.png`
  - Exported zone map image for quick review.
- `outputs/section_04_validation_report.rds`
  - Section 04 schema/key/geometry/assignment validation report.
- `outputs/section_04_cluster_assignments.rds`
  - Tract-level assignment table for proximity-based cluster zones.
- `outputs/section_04_cluster_zones.rds`
  - Cluster-zone geometries with deterministic labels and geometry attributes.
- `outputs/section_04_cluster_zone_summary.rds`
  - Cluster-zone KPI summary metrics.
- `outputs/section_04_cluster_vs_contiguity_comparison.rds`
  - Side-by-side summary stats comparing contiguity and cluster zone systems.
- `outputs/section_04_cluster_params.rds`
  - Parameter record for cluster generation (eps/min_pts/noise policy).
- `outputs/section_04_cluster_visual_objects.rds`
  - Render-ready cluster map and summary table objects.
- `outputs/section_04_cluster_zone_map.png`
  - Exported cluster-zone map image.
- `outputs/section_04_cluster_validation_report.rds`
  - Cluster-zone schema/key/geometry/assignment validation report.

### 05_parcels
- `outputs/section_05_zones_canonical.rds`
  - Canonicalized zone geometry table used by the active cluster-first Section 05 flow (`zone_system`, `zone_id`, `zone_label`, `geometry`).
- `outputs/section_05_parcels_canonical.rds`
  - Canonical parcel table with normalized parcel attributes sourced from prepared parcel-serving products; geometry is attached later only for geometry-bearing outputs.
- `outputs/section_05_input_readiness_report.rds`
  - Input schema/key/geometry readiness report for Section 05 prerequisites.
- `outputs/section_05_retail_land_use_mapping_candidates_v0_1.csv`
  - Required manual retail use-code mapping file consumed by the retail classification step.
- `outputs/section_05_retail_classified_parcels.rds`
  - Geometry-bearing parcel table with retail classification (`retail_flag`, `retail_subtype`) and area fields for map-serving outputs.
- `outputs/section_05_retail_intensity.rds`
  - Tract-level retail intensity metrics (`retail_parcel_count`, `retail_area`, `retail_area_density`).
- `outputs/section_05_retail_intensity_report.rds`
  - Validation summary for retail classification and tract-assignment workflow, including consumer-vs-fallback source modes.
- `outputs/section_05_zone_overlay_contiguity.rds`
  - Contiguity-zone overlay summary with retail context and zone quality fields.
- `outputs/section_05_zone_overlay_cluster.rds`
  - Cluster-zone overlay summary with retail context and zone quality fields.
- `outputs/section_05_parcel_shortlist_contiguity.rds`
  - Contiguity-system parcel shortlist `sf` output with score components and ranks.
- `outputs/section_05_parcel_shortlist_cluster.rds`
  - Cluster-system parcel shortlist `sf` output with score components and ranks.
- `outputs/section_05_shortlist_report.rds`
  - Shortlist build validation summary and row-count checks.
- `outputs/section_05_visual_objects.rds`
  - Render-ready Section 05 map/table objects for both zone systems.
- `outputs/section_05_validation_report.rds`
  - Section 05 schema/key/geometry/logic validation report.
- `outputs/section_05_overlay_map_contiguity.png`
  - Exported contiguity overlay map.
- `outputs/section_05_overlay_map_cluster.png`
  - Exported cluster overlay map.
- `outputs/section_05_market_parcel_context_map.png`
  - Exported parcel market context map for the active cluster-first workflow.
- `outputs/section_05_cluster_parcel_overlay_map.png`
  - Exported cluster parcel overlay map used for shortlist framing.
- `outputs/section_05_shortlist_map_contiguity.png`
  - Exported contiguity shortlist map.
- `outputs/section_05_shortlist_map_cluster.png`
  - Exported cluster shortlist map.

### Section 05 external input contract
- `ROF_PARCEL_STANDARDIZED_ROOT` may override the default parcel standardized root used by Section 05.
- The configured parcel standardized root must contain `parcel_ingest_manifest.rds` when a manifest-driven load is expected.
- Section 05 will read county analysis geometry artifacts from either:
  - manifest `analysis_path` entries, or
  - `county_outputs/<county_tag>/parcel_geometries_analysis.rds`
- The minimum required parcel geometry columns for Section 05 consumption are:
  - `join_key`
  - `parcel_id`
  - `county`
  - `county_name`
  - `use_code`
  - `land_value`
  - `total_value`
  - `sale_price1`
  - `sale_yr1`
  - `sale_mo1`
  - `qa_missing_join_key`
  - `qa_zero_county`
  - `geometry`
- County analysis geometry must be stored in EPSG:4326 for handoff into Section 05.

### 06_conclusion_appendix
- `outputs/section_06_conclusion_payload.rds`
  - Conclusion payload containing highlights and recommended next actions.
- `outputs/section_06_appendix_payload.rds`
  - Appendix payload containing KPI dictionary snapshot, assumptions/caveats, and QA rollup.
- `outputs/section_06_visual_objects.rds`
  - Render-ready Section 06 summary/QA/assumptions tables.
- `outputs/section_06_validation_report.rds`
  - Section 06 schema/reference/narrative validation report.
