#' Rebase CBSA metrics from county-level data
#'
#' @param df Tibble with county-level observations including `cbsa_code`, `year`, and metric columns.
#' @param weight_col Column to use for weighting county contributions.
#'
#' @return A tibble summarising CBSA-level metrics.
#' @export
rebase_cbsa_from_counties <- function(df, weight_col = NULL) {
  stopifnot("cbsa_code" %in% names(df))
  stopifnot("year" %in% names(df))
  
  if (!is.null(weight_col)) {
    weight_sym <- rlang::sym(weight_col)
  } else {
    weight_sym <- rlang::sym("weight")
    df <- df |> dplyr::mutate(weight = 1)
  }
  
  numeric_cols <- names(dplyr::select(df, dplyr::where(is.numeric)))
  metric_cols <- setdiff(numeric_cols, rlang::as_string(weight_sym))
  
  df |>
    dplyr::group_by(cbsa_code, year) |>
    dplyr::summarise(
      dplyr::across(
        dplyr::all_of(metric_cols),
        ~stats::weighted.mean(.x, !!weight_sym, na.rm = TRUE)
      ),
      .groups = "drop"
    )
}

## Create smaller, ACS specific functions
# This function sums the totals by CBSA so we can aggregate correctly
sum_pops_by_cbsa <- function(df, pop_pattern = "pop") {
  df %>%
    group_by(cbsa_code, cbsa_name, year) %>%
    summarise(
      across(contains(pop_pattern), ~ sum(.x, na.rm = TRUE)),
      .groups = "drop"
    )
}

# This function allows us to calculate the weighted average of a specific column
weighted_by_cbsa <- function(df, value_col, weight_col) {
  df %>%
    group_by(cbsa_code, cbsa_name, year) %>%
    summarise(
      "{{value_col}}" := stats::weighted.mean(
        .data[[value_col]],
        .data[[weight_col]],
        na.rm = TRUE
      ),
      .groups = "drop"
    )
}

# This function alows us to calculate weighted averages for all columns that follow a specfic pattern
weighted_by_cbsa_pattern <- function(df, value_pattern, weight_col) {
  stopifnot("cbsa_code" %in% names(df))
  stopifnot("year" %in% names(df))
  stopifnot("cbsa_name" %in% names(df))
  stopifnot(weight_col %in% names(df))
  
  # 1) Start with numeric columns
  numeric_cols <- names(dplyr::select(df, dplyr::where(is.numeric)))
  
  # 2) Keep only those whose names match the pattern
  pattern_cols <- numeric_cols[grepl(value_pattern, numeric_cols)]
  
  # 3) Exclude things we never want to average
  exclude_cols <- c("year", "cbsa_code", weight_col)
  value_cols <- setdiff(pattern_cols, exclude_cols)
  
  if (length(value_cols) == 0) {
    stop("No numeric columns found matching pattern: ", value_pattern)
  }
  
  df %>%
    dplyr::group_by(cbsa_code, cbsa_name, year) %>%
    dplyr::summarise(
      dplyr::across(
        dplyr::all_of(value_cols),
        ~ stats::weighted.mean(.x, .data[[weight_col]], na.rm = TRUE)
      ),
      .groups = "drop"
    )
}