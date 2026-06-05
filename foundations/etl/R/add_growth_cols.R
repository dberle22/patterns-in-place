# Generic helper to add simple % change and CAGR for multiple horizons
# df must contain: id_cols (e.g., GEOID, NAME), a YEAR column (numeric/int), and a value_col
add_growth_cols <- function(df, id_cols, year_col = "YEAR", value_col, horizons = c(1,3,5,10), prefix = "") {
  stopifnot(all(c(id_cols, year_col, value_col) %in% names(df)))
  df %>%
    arrange(across(all_of(c(id_cols, year_col)))) %>%
    group_by(across(all_of(id_cols))) %>%
    mutate(
      across(
        all_of(value_col),
        .fns = list(
          !!!setNames(
            lapply(horizons, function(h) \(x) (x / dplyr::lag(x, h) - 1)),
            paste0(prefix, "chg_", horizons, "y")
          ),
          !!!setNames(
            lapply(horizons, function(h) \(x) (x / dplyr::lag(x, h))^(1 / h) - 1),
            paste0(prefix, "cagr_", horizons, "y")
          )
        ),
        .names = "{fn}"
      )
    ) %>%
    ungroup()
}