#!/usr/bin/env Rscript

# Batch runner for all first-pass Costs visuals.
# This gives the section a single rerun path while preserving the simpler
# one-script-per-chart production workflow.

visual_scripts <- c(
  "publisher/content/housing/02_costs/visuals/state_rent_to_income_map.R",
  "publisher/content/housing/02_costs/visuals/cost_index_trends.R",
  "publisher/content/housing/02_costs/visuals/cbsa_vacancy_vs_cost_changes.R",
  "publisher/content/housing/02_costs/visuals/cbsa_cost_correlation_heatmap.R"
)

for (script in visual_scripts) {
  message(sprintf("Running %s", script))
  status <- system2("Rscript", script)
  if (!identical(status, 0L)) {
    stop(sprintf("Render failed for %s", script), call. = FALSE)
  }
}

message("Costs render complete.")
