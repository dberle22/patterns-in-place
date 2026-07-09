# Section 01 visuals script
# Purpose: generate plots/tables from section outputs.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 01 visuals: 01_setup")

run_meta <- readRDS(read_artifact_path("01_setup", "section_01_run_metadata"))
foundation <- readRDS(read_artifact_path("01_setup", "section_01_foundation"))
validation_report <- readRDS(read_artifact_path("01_setup", "section_01_validation_report"))

kpi_tile <- function(label, value, subtitle = NULL) {
  bslib::card(
    bslib::card_body(
      htmltools::tags$div(style = "font-size: 12px; color: #666;", label),
      htmltools::tags$div(style = "font-size: 26px; font-weight: 700; line-height: 1.1;", value),
      if (!is.null(subtitle)) htmltools::tags$div(style = "font-size: 11px; color: #888; margin-top: 6px;", subtitle)
    ),
    style = "height: 120px;"
  )
}

all_checks_pass <- isTRUE(validation_report$market_profile_check$pass) &&
  all(vapply(validation_report$column_checks, `[[`, logical(1), "pass")) &&
  all(vapply(validation_report$key_checks, `[[`, logical(1), "pass")) &&
  all(vapply(validation_report$geometry_checks, `[[`, logical(1), "pass"))

tiles_layout <- bslib::layout_column_wrap(
  width = 1 / 3,
  kpi_tile("Market", run_meta$market_name, paste0("CBSA ", run_meta$target_cbsa)),
  kpi_tile("Target year", as.character(run_meta$target_year), paste0("Vintage ", run_meta$target_vintage)),
  kpi_tile("Validation status", if (all_checks_pass) "PASS" else "CHECK", paste0("Git ", run_meta$git_hash)),
  kpi_tile("Tracts", scales::comma(validation_report$column_checks$tract_features$n_rows), "Feature rows"),
  kpi_tile("Counties", scales::comma(validation_report$geometry_checks$county$n_rows), "County geometries"),
  kpi_tile("Model weights", scales::number(foundation$model_params_check$weight_sum, accuracy = 0.01), "Expected to sum to 1.00")
)

check_status_tbl <- dplyr::bind_rows(
  tibble::tibble(
    check_group = "Market profile",
    dataset = run_meta$market_key,
    status = validation_report$market_profile_check$pass
  ),
  purrr::imap_dfr(validation_report$column_checks, ~ tibble::tibble(
    check_group = "Columns",
    dataset = .y,
    status = .x$pass
  )),
  purrr::imap_dfr(validation_report$key_checks, ~ tibble::tibble(
    check_group = "Keys",
    dataset = .y,
    status = .x$pass
  )),
  purrr::imap_dfr(validation_report$geometry_checks, ~ tibble::tibble(
    check_group = "Geometry",
    dataset = .y,
    status = .x$pass
  ))
)

check_status_gt <- check_status_tbl %>%
  dplyr::mutate(status = dplyr::if_else(status, "Pass", "Fail")) %>%
  gt::gt(groupname_col = "check_group") %>%
  gt::tab_header(title = "Section 01 setup validation status") %>%
  gt::cols_label(
    dataset = "Dataset / scope",
    status = "Status"
  ) %>%
  gt::data_color(
    columns = "status",
    fn = scales::col_factor(
      palette = c("Pass" = "#D1FADF", "Fail" = "#FEE4E2"),
      domain = c("Pass", "Fail")
    )
  ) %>%
  gt::tab_options(table.font.size = 12, data_row.padding = gt::px(4))

null_checks_gt <- validation_report$null_checks %>%
  dplyr::arrange(dplyr::desc(null_rate), dataset, column) %>%
  gt::gt(groupname_col = "dataset") %>%
  gt::tab_header(title = "Null-rate scan for tracked fields") %>%
  gt::cols_label(
    column = "Column",
    null_rate = "Null rate"
  ) %>%
  gt::fmt_percent(columns = "null_rate", decimals = 2) %>%
  gt::tab_options(table.font.size = 12, data_row.padding = gt::px(4))

null_rate_plot <- ggplot2::ggplot(
  validation_report$null_checks,
  ggplot2::aes(
    x = stats::reorder(column, null_rate),
    y = null_rate,
    fill = dataset
  )
) +
  ggplot2::geom_col(position = "dodge", width = 0.7) +
  ggplot2::coord_flip() +
  ggplot2::scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
  ggplot2::scale_fill_manual(values = c("tract_features" = "#1570EF", "cbsa_features" = "#12B76A")) +
  ggplot2::theme_minimal() +
  ggplot2::theme(
    panel.grid.minor = ggplot2::element_blank(),
    legend.title = ggplot2::element_blank()
  ) +
  ggplot2::labs(
    title = "Tracked null rates across section 01 validation checks",
    x = NULL,
    y = "Null rate"
  )

save_artifact(
  list(
    tiles_layout = tiles_layout,
    check_status_gt = check_status_gt,
    null_checks_gt = null_checks_gt,
    null_rate_plot = null_rate_plot
  ),
  resolve_output_path("01_setup", "section_01_visual_objects")
)

ggplot2::ggsave(
  filename = resolve_output_path("01_setup", "section_01_null_rate_plot", ext = "png"),
  plot = null_rate_plot,
  width = 8,
  height = 4.5,
  dpi = 150
)

message("Section 01 visuals complete.")
