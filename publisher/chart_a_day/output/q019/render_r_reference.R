suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q019")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_heatmap_table.R")
source("visual_library/shared/render/render_heatmap_table.R")

short_names <- c(
  "Austin-Round Rock-San Marcos, TX" = "Austin",
  "Dallas-Fort Worth-Arlington, TX" = "Dallas-Fort Worth",
  "Phoenix-Mesa-Chandler, AZ" = "Phoenix",
  "Nashville-Davidson--Murfreesboro--Franklin, TN" = "Nashville",
  "Charlotte-Concord-Gastonia, NC-SC" = "Charlotte",
  "Atlanta-Sandy Springs-Roswell, GA" = "Atlanta",
  "Tampa-St. Petersburg-Clearwater, FL" = "Tampa",
  "Orlando-Kissimmee-Sanford, FL" = "Orlando"
)

result_df <- as.data.frame(readr::read_csv(result_path, show_col_types = FALSE))
result_df$geo_name <- ifelse(
  result_df$geo_name %in% names(short_names),
  unname(short_names[result_df$geo_name]),
  result_df$geo_name
)
side_note <- unique(stats::na.omit(result_df$note))[[1]]

heatmap_df <- prep_heatmap_table(
  result_df,
  config = list(
    normalize = FALSE,
    fill_value_field = "normalized_value",
    label_value_field = "metric_value",
    row_order = c("Austin", "Dallas-Fort Worth", "Phoenix", "Nashville", "Charlotte", "Atlanta", "Tampa", "Orlando"),
    column_order = c("Rent-to-income ratio", "Vacancy rate", "5-year population growth"),
    keep_missing = TRUE
  )
)

heatmap_plot <- render_heatmap_table(
  heatmap_df,
  config = list(
    title = "How do rent burden, vacancy rate, and population growth compare across Sun Belt metros in 2023?",
    subtitle = "Austin plus 7 Sun Belt peers | Fill shows a metric-specific housing-stress percentile within major metros",
    fill_value_field = "normalized_value",
    legend_title = "Stress percentile",
    show_cell_labels = TRUE,
    x_text_angle = 0,
    side_note = side_note,
    right_margin_pt = 40
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = heatmap_plot,
  width = 12,
  height = 7,
  dpi = 300,
  bg = "white"
)
