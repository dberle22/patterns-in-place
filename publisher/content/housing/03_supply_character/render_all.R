#!/usr/bin/env Rscript

# Batch runner for all first-pass Supply Character visuals.
# This gives the section a single rerun path while preserving the simpler
# one-script-per-chart production workflow.

visual_scripts <- c(
  "publisher/content/housing/03_supply_character/visuals/cbsa_permit_intensity_map.R",
  "publisher/content/housing/03_supply_character/visuals/cbsa_supply_mix_top_markets.R",
  "publisher/content/housing/03_supply_character/visuals/cbsa_supply_vs_growth.R"
)

for (script in visual_scripts) {
  message(sprintf("Running %s", script))
  status <- system2("Rscript", script)
  if (!identical(status, 0L)) {
    stop(sprintf("Render failed for %s", script), call. = FALSE)
  }
}

message("Supply Character render complete.")
