# Stage one versioned HUD-USPS ZIP crosswalk release without conflating ZIPs
# with Census ZCTAs. Silver owns the normalized allocation tables.
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

library(DBI)
library(duckdb)
library(readxl)
library(dplyr)
library(stringr)

db_path <- get_env_path("DB_PATH")
raw_root <- Sys.getenv("GEOGRAPHY_RAW_DIR", unset = file.path(get_env_path("DATA"), "geography", "raw"))
release_code <- Sys.getenv("HUD_USPS_RELEASE_CODE", unset = "062025")
release_label <- Sys.getenv("HUD_USPS_RELEASE_LABEL", unset = "2025Q1")
release_year <- as.integer(str_sub(release_label, 1, 4))

dir.create(file.path(raw_root, "hud_usps", release_label), recursive = TRUE, showWarnings = FALSE)

# HUD publishes a separate workbook for each target geography. Cache the exact
# release so a later quarter cannot silently replace the allocation basis.
download_hud_workbook <- function(kind) {
  filename <- paste0("ZIP_", kind, "_", release_code, ".xlsx")
  destination <- file.path(raw_root, "hud_usps", release_label, filename)
  legacy_cache <- file.path(get_env_path("DATA"), "demographics", "raw", "crosswalks", filename)
  if (!file.exists(destination)) {
    # Preserve an already-downloaded release when HUD retires older URLs. New
    # releases still use the provider URL and land in the versioned cache.
    if (file.exists(legacy_cache)) {
      file.copy(legacy_cache, destination)
    } else {
      download.file(
        url = paste0("https://www.huduser.gov/portal/datasets/", filename),
        destfile = destination,
        mode = "wb",
        quiet = FALSE
      )
    }
  }
  if (!file.exists(destination)) stop("HUD-USPS workbook was not acquired: ", filename)
  destination
}

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)
dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging")

for (kind in c("COUNTY", "CBSA", "TRACT")) {
  workbook <- download_hud_workbook(kind)
  raw <- readxl::read_excel(workbook)
  dbWriteTable(
    con,
    Id(schema = "staging", table = paste0("hud_usps_zip_", tolower(kind))),
    raw %>% mutate(source_release_year = release_year, source_release = release_label),
    overwrite = TRUE
  )
}

message("Staged HUD-USPS ZIP crosswalk release ", release_label, ".")
