# County-first GDP aggregation helpers ---------------------------------------
#
# These functions implement the public BEA geographic-aggregator method for a
# fixed county-to-CBSA membership: sum nominal county GDP, deflate each county
# industry cell with BEA's national value-added price index, and chain adjacent
# Fisher quantity relatives around the published reference year.  Missing or
# non-positive inputs intentionally propagate to the result; replacing them
# with zero would turn a suppression into a fabricated CBSA estimate.

bea_fisher_chain <- function(cells, ref_year = 2017L) {
  required <- c("cbsa_code", "period", "line_code", "nominal_gdp", "price_index")
  stopifnot(all(required %in% names(cells)))

  cells <- cells %>%
    dplyr::arrange(.data$cbsa_code, .data$line_code, .data$period) %>%
    dplyr::mutate(
      fixed_dollars = dplyr::if_else(
        !is.na(.data$nominal_gdp) & !is.na(.data$price_index) & .data$price_index > 0,
        .data$nominal_gdp / .data$price_index,
        NA_real_
      )
    )

  # Summarise with `sum()` only when every component is present. This is the
  # conservative suppression rule described in BEA's 2026 technical document.
  aggregate_year <- function(x) {
    dplyr::tibble(
      nominal_gdp = if (all(!is.na(x$nominal_gdp))) sum(x$nominal_gdp) else NA_real_,
      p1q1 = if (all(!is.na(x$nominal_gdp))) sum(x$nominal_gdp) else NA_real_,
      p1q0 = if (all(!is.na(x$fixed_dollars) & !is.na(x$price_index))) sum(x$price_index * dplyr::lag(x$fixed_dollars), na.rm = FALSE) else NA_real_
    )
  }

  # Build the four Fisher terms at the county-industry cell before aggregating.
  terms <- cells %>%
    dplyr::group_by(.data$cbsa_code, .data$line_code, .data$county_geoid) %>%
    dplyr::arrange(.data$period, .by_group = TRUE) %>%
    dplyr::mutate(
      p1q1 = .data$price_index * .data$fixed_dollars,
      p1q0 = .data$price_index * dplyr::lag(.data$fixed_dollars),
      p0q1 = dplyr::lag(.data$price_index) * .data$fixed_dollars,
      p0q0 = dplyr::lag(.data$price_index) * dplyr::lag(.data$fixed_dollars)
    ) %>%
    dplyr::ungroup()

  totals <- terms %>%
    dplyr::group_by(.data$cbsa_code, .data$line_code, .data$period) %>%
    dplyr::summarise(
      nominal_gdp = if (all(!is.na(.data$nominal_gdp))) sum(.data$nominal_gdp) else NA_real_,
      p1q1 = if (all(!is.na(.data$p1q1))) sum(.data$p1q1) else NA_real_,
      p1q0 = if (all(!is.na(.data$p1q0))) sum(.data$p1q0) else NA_real_,
      p0q1 = if (all(!is.na(.data$p0q1))) sum(.data$p0q1) else NA_real_,
      p0q0 = if (all(!is.na(.data$p0q0))) sum(.data$p0q0) else NA_real_,
      missing_county_inputs = sum(is.na(.data$nominal_gdp)),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      fisher_quantity_relative = sqrt((.data$p1q1 / .data$p1q0) * (.data$p0q1 / .data$p0q0))
    ) %>%
    dplyr::arrange(.data$cbsa_code, .data$line_code, .data$period) %>%
    dplyr::group_by(.data$cbsa_code, .data$line_code) %>%
    dplyr::group_modify(function(.x, .y) {
      .x$chain_type_quantity_index <- NA_real_
      reference <- which(.x$period == ref_year)
      if (length(reference) != 1L || is.na(.x$nominal_gdp[reference]) || .x$nominal_gdp[reference] <= 0) return(.x)
      .x$chain_type_quantity_index[reference] <- 100
      if (reference < nrow(.x)) for (i in seq.int(reference + 1L, nrow(.x))) {
        .x$chain_type_quantity_index[i] <- .x$chain_type_quantity_index[i - 1L] * .x$fisher_quantity_relative[i]
      }
      if (reference > 1L) for (i in seq.int(reference - 1L, 1L)) {
        .x$chain_type_quantity_index[i] <- .x$chain_type_quantity_index[i + 1L] / .x$fisher_quantity_relative[i + 1L]
      }
      .x
    }) %>%
    dplyr::ungroup() %>%
    dplyr::group_by(.data$cbsa_code, .data$line_code) %>%
    dplyr::mutate(
      reference_nominal_gdp = .data$nominal_gdp[.data$period == ref_year][1],
      real_gdp = (.data$chain_type_quantity_index / 100) * .data$reference_nominal_gdp
    ) %>%
    dplyr::ungroup()

  totals
}
