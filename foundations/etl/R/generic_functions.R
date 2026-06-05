# Easily convert to PCT
pct <- function(x, acc = 0.1) scales::percent(x, accuracy = acc)

# Safe col pick by regex (first match), returns sym or NULL
pick_col <- function(df, patterns){
  cols <- names(df)
  hit <- map_chr(patterns, function(p) {
    m <- cols[str_detect(cols, regex(p, ignore_case = TRUE))]
    if(length(m)) m[1] else NA_character_
  }) %>% discard(is.na)
  if(length(hit)) sym(hit[1]) else NULL
}


# Keep only intersecting years across sources for fair comparisons
intersect_years <- function(...){
  ys <- list(...)
  reduce(ys, intersect)
}

# Simple state abbrev extractor from CBSA title "Wilmington, NC (MSA)"
extract_state_abbrev <- function(title){
  m <- str_match(title, ",\\s*([A-Z]{2})")[,2]
  m
}

# Get and expand env var path, return NA if unset or empty
get_env_path <- function(key) {
  val <- Sys.getenv(key, unset = "")
  if (!nzchar(val)) return(NA_character_)
  path.expand(val)
}