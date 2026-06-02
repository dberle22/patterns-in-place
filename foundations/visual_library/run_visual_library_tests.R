#!/usr/bin/env Rscript

if (file.exists(".Renviron")) readRenviron(".Renviron")

get_script_path <- function() {
  file_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
  if (length(file_arg) == 0) {
    return(normalizePath("visual_library/run_visual_library_tests.R", mustWork = FALSE))
  }
  normalizePath(sub("^--file=", "", file_arg[1]), mustWork = FALSE)
}

script_path <- get_script_path()
repo_root <- dirname(dirname(script_path))
repo_path <- function(...) file.path(repo_root, ...)
relative_repo_path <- function(path) sub(paste0("^", repo_root, "/?"), "", path)

source(repo_path("visual_library", "shared", "standards.R"))
source(repo_path("visual_library", "shared", "chart_utils.R"))
source(repo_path("visual_library", "shared", "data_contracts.R"))
source(repo_path("visual_library", "shared", "prep", "prep_line.R"))
source(repo_path("visual_library", "shared", "render", "render_line.R"))
source(repo_path("visual_library", "shared", "prep", "prep_scatter.R"))
source(repo_path("visual_library", "shared", "render", "render_scatter.R"))
source(repo_path("visual_library", "shared", "prep", "prep_bar.R"))
source(repo_path("visual_library", "shared", "render", "render_bar.R"))
source(repo_path("visual_library", "shared", "prep", "prep_choropleth.R"))
source(repo_path("visual_library", "shared", "render", "render_choropleth.R"))
source(repo_path("visual_library", "shared", "prep", "prep_boxplot.R"))
source(repo_path("visual_library", "shared", "render", "render_boxplot.R"))
source(repo_path("visual_library", "shared", "prep", "prep_hexbin.R"))
source(repo_path("visual_library", "shared", "render", "render_hexbin.R"))
source(repo_path("visual_library", "shared", "prep", "prep_strength_strip.R"))
source(repo_path("visual_library", "shared", "render", "render_strength_strip.R"))
source(repo_path("visual_library", "shared", "prep", "prep_correlation_heatmap.R"))
source(repo_path("visual_library", "shared", "render", "render_correlation_heatmap.R"))
source(repo_path("visual_library", "shared", "prep", "prep_highlight_context_map.R"))
source(repo_path("visual_library", "shared", "render", "render_highlight_context_map.R"))
source(repo_path("visual_library", "shared", "prep", "prep_slopegraph.R"))
source(repo_path("visual_library", "shared", "render", "render_slopegraph.R"))
source(repo_path("visual_library", "shared", "prep", "prep_heatmap_table.R"))
source(repo_path("visual_library", "shared", "render", "render_heatmap_table.R"))
source(repo_path("visual_library", "shared", "prep", "prep_age_pyramid.R"))
source(repo_path("visual_library", "shared", "render", "render_age_pyramid.R"))
source(repo_path("visual_library", "shared", "prep", "prep_bump_chart.R"))
source(repo_path("visual_library", "shared", "render", "render_bump_chart.R"))
source(repo_path("visual_library", "shared", "prep", "prep_waterfall.R"))
source(repo_path("visual_library", "shared", "render", "render_waterfall.R"))
source(repo_path("visual_library", "shared", "prep", "prep_bivariate_choropleth.R"))
source(repo_path("visual_library", "shared", "render", "render_bivariate_choropleth.R"))
source(repo_path("visual_library", "shared", "prep", "prep_proportional_symbol_map.R"))
source(repo_path("visual_library", "shared", "render", "render_proportional_symbol_map.R"))

output_dir <- repo_path("outputs", "visual_library")
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

registry_path <- repo_path("visual_library", "config", "visual_registry.yml")
if (!requireNamespace("yaml", quietly = TRUE)) {
  stop("Package 'yaml' is required to run the visual library test harness.")
}

registry <- yaml::read_yaml(registry_path)
charts <- registry$charts

file_exists <- function(path) {
  !is.null(path) && file.exists(path)
}

readable_chart_label <- function(chart_type) {
  tools::toTitleCase(gsub("_", " ", chart_type))
}

build_scaffold_fixture <- function(chart_type) {
  switch(
    chart_type,
    bar = data.frame(
      geo_level = "cbsa",
      geo_id = c("1", "2", "3"),
      geo_name = c("Alpha", "Beta", "Gamma"),
      time_window = "2023",
      metric_id = "income_growth",
      metric_label = "Income Growth",
      metric_value = c(9.2, 6.4, 4.8),
      source = "visual_library_fixture",
      vintage = "2026-04-14",
      highlight_flag = c(TRUE, FALSE, FALSE),
      stringsAsFactors = FALSE
    ),
    choropleth = data.frame(
      geo_level = "county",
      geo_id = c("1", "2", "3"),
      geo_name = c("Alpha County", "Beta County", "Gamma County"),
      time_window = "2023",
      metric_value = c(0.22, 0.31, 0.27),
      metric_label = "Rent Burden",
      source = "visual_library_fixture",
      vintage = "2026-04-14",
      stringsAsFactors = FALSE
    ),
    boxplot = data.frame(
      geo_level = "cbsa",
      geo_id = as.character(seq_len(24)),
      geo_name = paste("Metro", seq_len(24)),
      time_window = "2023",
      metric_id = "rent_burden",
      metric_label = "Rent Burden",
      metric_value = c(
        0.31, 0.34, 0.36, 0.38, 0.40, 0.42,
        0.35, 0.37, 0.39, 0.41, 0.43, 0.45,
        0.29, 0.32, 0.34, 0.36, 0.37, 0.39,
        0.44, 0.46, 0.49, 0.51, 0.53, 0.57
      ),
      group = rep(c("Midwest", "Northeast", "South", "West"), each = 6),
      highlight_flag = c(TRUE, rep(FALSE, 23)),
      source = "visual_library_fixture",
      vintage = "2026-04-16",
      stringsAsFactors = FALSE
    ),
    hexbin = data.frame(
      geo_level = "zcta",
      geo_id = as.character(seq_len(100)),
      geo_name = paste("ZCTA", seq_len(100)),
      time_window = "2023",
      x_value = rnorm(100, 60000, 12000),
      y_value = rnorm(100, 0.28, 0.05),
      x_label = "Income",
      y_label = "Rent Burden",
      source = "visual_library_fixture",
      vintage = "2026-04-14",
      stringsAsFactors = FALSE
    ),
    strength_strip = data.frame(
      geo_level = "cbsa",
      geo_id = rep("48900", 4),
      geo_name = rep("Wilmington, NC", 4),
      time_window = "2023",
      metric_id = c("population", "income", "permits", "rent_burden"),
      metric_label = c("Population Growth", "Income Growth", "Permits Tailwind", "Rent Burden"),
      metric_value = c(72, 61, 58, 43),
      normalized_value = c(72, 61, 58, 57),
      direction = c("higher_is_better", "higher_is_better", "higher_is_better", "lower_is_better"),
      source = "visual_library_fixture",
      vintage = "2026-04-14",
      stringsAsFactors = FALSE
    ),
    correlation_heatmap = data.frame(
      geo_level = rep("cbsa", 12),
      geo_id = rep(c("1", "2", "3", "4"), each = 3),
      geo_name = rep(c("Alpha", "Beta", "Gamma", "Delta"), each = 3),
      time_window = "2023",
      metric_id = rep(c("income", "rent_burden", "permits"), 4),
      metric_label = rep(c("Income", "Rent Burden", "Permits"), 4),
      metric_value = c(70, 28, 14, 64, 31, 11, 59, 34, 9, 77, 24, 16),
      source = "visual_library_fixture",
      vintage = "2026-04-14",
      stringsAsFactors = FALSE
    ),
    highlight_context_map = data.frame(
      geo_level = "county",
      geo_id = c("1", "2", "3"),
      geo_name = c("Alpha", "Beta", "Gamma"),
      time_window = "2023",
      source = "visual_library_fixture",
      vintage = "2026-04-14",
      highlight_flag = c(TRUE, FALSE, FALSE),
      stringsAsFactors = FALSE
    ),
    slopegraph = data.frame(
      geo_level = "cbsa",
      geo_id = rep(c("1", "2", "3"), each = 2),
      geo_name = rep(c("Alpha", "Beta", "Gamma"), each = 2),
      period = rep(c(2018, 2023), 3),
      metric_id = "income_pc",
      metric_label = "Per Capita Income",
      metric_value = c(42000, 52000, 45000, 50000, 47000, 54000),
      source = "visual_library_fixture",
      vintage = "2026-04-14",
      stringsAsFactors = FALSE
    ),
    heatmap_table = data.frame(
      geo_level = rep("cbsa", 9),
      geo_id = rep(c("1", "2", "3"), each = 3),
      geo_name = rep(c("Alpha", "Beta", "Gamma"), each = 3),
      time_window = "2023",
      metric_id = rep(c("growth", "affordability", "permits"), 3),
      metric_label = rep(c("Growth", "Affordability", "Permits"), 3),
      metric_value = c(71, 44, 63, 58, 62, 49, 47, 55, 72),
      source = "visual_library_fixture",
      vintage = "2026-04-14",
      stringsAsFactors = FALSE
    ),
    age_pyramid = expand.grid(
      geo_level = "cbsa",
      geo_id = "48900",
      geo_name = "Wilmington, NC",
      period = 2023,
      age_bin = c("0-17", "18-34", "35-54", "55-64", "65+"),
      sex = c("Male", "Female"),
      stringsAsFactors = FALSE
    ) |>
      transform(
        pop_value = c(9000, 11000, 13000, 8000, 7000, 8500, 10800, 12800, 8400, 8600),
        source = "visual_library_fixture",
        vintage = "2026-04-14"
      ),
    bump_chart = data.frame(
      geo_level = rep("cbsa", 9),
      geo_id = rep(c("1", "2", "3"), each = 3),
      geo_name = rep(c("Alpha", "Beta", "Gamma"), each = 3),
      period = rep(c(2019, 2021, 2023), times = 3),
      metric_id = "growth_rank",
      metric_label = "Population Growth Rank",
      metric_value = c(4.2, 4.4, 4.8, 5.1, 4.6, 4.0, 3.8, 4.1, 4.7),
      source = "visual_library_fixture",
      vintage = "2026-04-14",
      stringsAsFactors = FALSE
    ),
    waterfall = data.frame(
      geo_level = "cbsa",
      geo_id = "48900",
      geo_name = "Wilmington, NC",
      time_window = "2013_to_2023",
      total_label = "Income Change",
      component_id = c("wages", "dividends", "transfers", "other"),
      component_label = c("Wages", "Dividends", "Transfers", "Other"),
      component_value = c(12, 5, 7, -2),
      component_delta = c(12, 5, 7, -2),
      sort_order = 1:4,
      source = "visual_library_fixture",
      vintage = "2026-04-14",
      stringsAsFactors = FALSE
    ),
    bivariate_choropleth = data.frame(
      geo_level = "county",
      geo_id = c("1", "2", "3"),
      geo_name = c("Alpha", "Beta", "Gamma"),
      time_window = "2023",
      x_value = c(0.75, 0.40, 0.20),
      y_value = c(0.80, 0.35, 0.25),
      x_label = "Growth",
      y_label = "Affordability",
      source = "visual_library_fixture",
      vintage = "2026-04-14",
      stringsAsFactors = FALSE
    ),
    proportional_symbol_map = data.frame(
      geo_level = "county",
      geo_id = c("1", "2", "3"),
      geo_name = c("Alpha", "Beta", "Gamma"),
      time_window = "2023",
      size_value = c(120000, 80000, 50000),
      size_label = "Population",
      lon = c(-78.0, -79.5, -77.4),
      lat = c(34.2, 35.1, 36.0),
      source = "visual_library_fixture",
      vintage = "2026-04-14",
      stringsAsFactors = FALSE
    ),
    NULL
  )
}

run_scaffold_chart <- function(chart_type) {
  fixture <- build_scaffold_fixture(chart_type)
  if (is.null(fixture)) {
    return(list(status = "skipped", output = NA_character_, source_type = "none"))
  }

  prep_fn <- get(paste0("prep_", chart_type), mode = "function")
  render_fn <- get(paste0("render_", chart_type), mode = "function")

  prepared <- prep_fn(fixture, config = list())
  rendered <- render_fn(
    prepared,
    config = list(
      title = paste(readable_chart_label(chart_type), "Smoke Test"),
      subtitle = "Registry scaffold fixture"
    )
  )

  out_path <- file.path(output_dir, paste0(chart_type, "_scaffold.png"))
  ggplot2::ggsave(out_path, plot = rendered, width = 10, height = 6, dpi = 300, bg = "white")
  list(
    status = "rendered",
    output = relative_repo_path(out_path),
    source_type = "synthetic_smoke_fixture"
  )
}

run_external_script <- function(path) {
  if (!nzchar(Sys.getenv("DATA", unset = ""))) {
    return(list(
      status = "skipped: DATA environment variable is not set",
      output = path,
      source_type = "gold_query"
    ))
  }

  result <- tryCatch(
    {
      resolved_path <- repo_path(path)
      source(resolved_path, local = new.env(parent = globalenv()))
      list(status = "rendered", output = path, source_type = "gold_query")
    },
    error = function(e) {
      list(status = paste("error:", conditionMessage(e)), output = path, source_type = "gold_query")
    }
  )
  result
}

results <- lapply(charts, function(chart) {
  chart_type <- chart$chart_type
  coverage_exists <- file_exists(chart$question_coverage_file)

  if (identical(chart_type, "line")) {
    run_result <- run_external_script("visual_library/charts/line/test_line_render.R")
  } else if (identical(chart_type, "scatter")) {
    run_result <- run_external_script("visual_library/charts/scatter/test_scatter_render.R")
  } else if (identical(chart_type, "bar")) {
    run_result <- run_external_script("visual_library/charts/bar/sample_output/test_bar_render.R")
  } else {
    run_result <- run_scaffold_chart(chart_type)
  }

  data.frame(
    chart_id = chart$chart_id,
    chart_type = chart_type,
    family = chart$family,
    registry_status = chart$status,
    question_coverage_exists = coverage_exists,
    run_status = run_result$status,
    source_type = run_result$source_type,
    output_ref = run_result$output,
    stringsAsFactors = FALSE
  )
})

manifest <- do.call(rbind, results)
manifest_path <- file.path(output_dir, "visual_library_test_manifest.csv")
utils::write.csv(manifest, manifest_path, row.names = FALSE)

coverage_failures <- manifest$chart_id[!manifest$question_coverage_exists]
if (length(coverage_failures) > 0) {
  stop(sprintf("Question coverage missing for: %s", paste(coverage_failures, collapse = ", ")))
}

print(manifest)
cat(sprintf("\nManifest written to %s\n", relative_repo_path(manifest_path)))
