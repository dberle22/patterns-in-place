suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q015")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_bar.R")
source("visual_library/shared/render/render_bar.R")

result_df <- readr::read_csv(result_path, show_col_types = FALSE)
side_note <- unique(stats::na.omit(result_df$note))[[1]]

bar_df <- prep_bar(
  result_df,
  config = list(
    question_id = "q015",
    time_window = "2023_snapshot",
    metric_id = "diversity_index",
    sort_desc = TRUE,
    top_n = 15
  )
)

bar_plot <- render_bar(
  bar_df,
  config = list(
    output_mode = "presentation",
    title = "Which metros are the most racially and ethnically diverse in 2023?",
    subtitle = "Top 15 CBSAs by diversity index | Population filter: 500k+",
    y_label = "Diversity index",
    label_style = "number",
    label_accuracy = 0.001,
    show_labels = TRUE,
    show_axis_labels = TRUE,
    caption_side_note = side_note,
    caption_methodology_note = "Metric from gold.population_demographics; geography labels from gold.dim_geo.",
    right_margin_pt = 84
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = bar_plot,
  width = 12,
  height = 8,
  dpi = 300,
  bg = "white"
)
