#!/usr/bin/env Rscript

# Batch runner for all first-pass Overheating visuals.
# This gives the section a single rerun path while preserving the simpler
# one-script-per-chart production workflow.

visual_scripts <- c(
  "publisher/content/housing/04_overheating/visuals/cbsa_overheating_hottest.R",
  "publisher/content/housing/04_overheating/visuals/cbsa_overheating_still_affordable.R",
  "publisher/content/housing/04_overheating/visuals/cbsa_overheating_scatter.R",
  "publisher/content/housing/04_overheating/visuals/cbsa_overheating_bivariate_map.R",
  "publisher/content/housing/04_overheating/visuals/cbsa_overheating_component_heatmap.R"
)

for (script in visual_scripts) {
  message(sprintf("Running %s", script))
  status <- system2("Rscript", script)
  if (!identical(status, 0L)) {
    stop(sprintf("Render failed for %s", script), call. = FALSE)
  }
}

message("Overheating render complete.")
