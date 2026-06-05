# Build ACS variable dictionary from staging ingest scripts and ACS 2024 metadata.
#
# Output table:
#   silver.acs_variable_dictionary
#
# This table is intended to support data-dictionary definition fill workflows
# for Silver and Gold tables.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")
db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

extract_block <- function(lines, start_idx) {
  # Capture from `... <- c(` until a standalone closing `)` line.
  # This avoids false balance breaks caused by comments containing parentheses.
  buf <- character()
  i <- start_idx
  while (i <= length(lines)) {
    ln <- lines[[i]]
    buf <- c(buf, ln)
    if (i > start_idx && stringr::str_detect(ln, "^\\s*\\)\\s*$")) break
    i <- i + 1L
  }

  list(text = paste(buf, collapse = "\n"), end_idx = i)
}

extract_vars_from_script <- function(path) {
  lines <- readLines(path, warn = FALSE)
  out <- list()
  i <- 1L

  topic <- basename(path) |>
    stringr::str_remove("^get_acs_") |>
    stringr::str_remove("\\.R$")

  script_text <- paste(lines, collapse = "\n")

  while (i <= length(lines)) {
    ln <- lines[[i]]
    m <- stringr::str_match(ln, "^\\s*([A-Za-z][A-Za-z0-9_]*)\\s*<-\\s*c\\s*\\(")
    if (is.na(m[[1, 1]])) {
      i <- i + 1L
      next
    }

    var_set <- m[[1, 2]]
    # Keep only vectors actually used as ACS variable maps in this script.
    in_use <- stringr::str_detect(
      script_text,
      paste0("variables\\s*=\\s*", var_set, "\\b")
    )
    if (!in_use) {
      i <- i + 1L
      next
    }
    blk <- extract_block(lines, i)

    pairs <- stringr::str_match_all(
      blk$text,
      "([A-Za-z0-9_\\.]+)\\s*=\\s*\"([A-Za-z0-9_]+)\""
    )[[1]]

    if (nrow(pairs) > 0) {
      df <- tibble::tibble(
      source_script = sub("^.*/foundations/etl/", "foundations/etl/", path),
        topic = topic,
        var_set = var_set,
        metric_key_raw = pairs[, 2],
        acs_variable = pairs[, 3]
      ) |>
        dplyr::mutate(
          # Some script keys include trailing dots (e.g. median_age.)
          metric_key = stringr::str_remove(metric_key_raw, "\\.$"),
          silver_estimate_column = paste0(metric_key, "E"),
          silver_moe_column = paste0(metric_key, "M")
        )
      out[[length(out) + 1L]] <- df
    }

    i <- blk$end_idx + 1L
  }

  if (length(out) == 0) {
    return(tibble::tibble(
      source_script = character(),
      topic = character(),
      var_set = character(),
      metric_key_raw = character(),
      acs_variable = character(),
      metric_key = character(),
      silver_estimate_column = character(),
      silver_moe_column = character()
    ))
  }

  dplyr::bind_rows(out)
}

staging_dir <- here::here("foundations", "etl", "staging")
acs_scripts <- list.files(
  staging_dir,
  pattern = "^get_acs_.*\\.R$",
  full.names = TRUE
)

if (length(acs_scripts) == 0) {
  stop("No ACS staging scripts found under foundations/etl/staging.", call. = FALSE)
}

acs_map <- purrr::map_dfr(acs_scripts, extract_vars_from_script) |>
  dplyr::distinct()

if (nrow(acs_map) == 0) {
  stop("No ACS variable mappings were parsed from staging scripts.", call. = FALSE)
}

# Pull ACS variable metadata for 2024 ACS5.
acs_2024_vars <- tidycensus::load_variables(
  year = 2024,
  dataset = "acs5",
  cache = TRUE
) |>
  dplyr::transmute(
    acs_variable = name,
    acs_label_2024 = label,
    acs_concept_2024 = concept
  )

acs_dictionary <- acs_map |>
  dplyr::left_join(acs_2024_vars, by = "acs_variable") |>
  dplyr::mutate(
    acs_label_clean = dplyr::if_else(
      is.na(acs_label_2024),
      NA_character_,
      stringr::str_replace(acs_label_2024, "^Estimate!!", "")
    ),
    label_match_status = dplyr::if_else(is.na(acs_label_2024), "missing_in_2024_lookup", "matched"),
    lookup_year = 2024L,
    lookup_dataset = "acs5"
  ) |>
  dplyr::arrange(topic, var_set, metric_key)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "acs_variable_dictionary"),
  acs_dictionary,
  overwrite = TRUE
)

message("Wrote silver.acs_variable_dictionary")
message("Rows: ", nrow(acs_dictionary))
message("Distinct ACS variables: ", dplyr::n_distinct(acs_dictionary$acs_variable))
message(
  "Matched labels: ",
  sum(acs_dictionary$label_match_status == "matched"),
  " / ",
  nrow(acs_dictionary)
)

DBI::dbExecute(con, "CHECKPOINT")
DBI::dbDisconnect(con, shutdown = TRUE)
