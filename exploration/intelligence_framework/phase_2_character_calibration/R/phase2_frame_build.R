phase2_has_year_column <- function(con, source_table) {
  sql <- sprintf(
    "select count(*) as n
     from information_schema.columns
     where table_schema = 'gold'
       and table_name = '%s'
       and column_name = 'year'",
    source_table
  )

  DBI::dbGetQuery(con, sql)$n[[1]] > 0
}

phase2_pull_metric <- function(con, metric_id, source_table, source_column) {
  if (phase2_has_year_column(con, source_table)) {
    sql <- sprintf(
      "with ranked as (
         select
           geo_id,
           cast(%s as double) as metric_value,
           year as source_year,
           row_number() over (
             partition by geo_id
             order by case when %s is not null then 0 else 1 end, year desc
           ) as rn
         from gold.%s
         where geo_level = 'cbsa'
       )
       select
         geo_id,
         metric_value,
         source_year
       from ranked
       where rn = 1",
      source_column,
      source_column,
      source_table
    )
  } else {
    sql <- sprintf(
      "select
         geo_id,
         cast(%s as double) as metric_value,
         cast(null as integer) as source_year
       from gold.%s
       where geo_level = 'cbsa'",
      source_column,
      source_table
    )
  }

  DBI::dbGetQuery(con, sql) |>
    dplyr::rename(
      cbsa_code = geo_id,
      !!metric_id := metric_value,
      !!paste0(metric_id, "_source_year") := source_year
    )
}

build_phase2_character_frame <- function(con, catalog_check) {
  spine <- DBI::dbGetQuery(con, "
    select
      geo_id as cbsa_code,
      geo_name as cbsa_name,
      pop_total,
      year as spine_year
    from gold.population_demographics
    where geo_level = 'cbsa'
      and year = 2024
      and pop_total >= 100000
      and geo_name not like '%, PR'
    order by pop_total desc
  ")

  metric_specs <- catalog_check |>
    dplyr::select(metric_id, source_table, expected_source_column) |>
    dplyr::distinct()

  metric_frame <- purrr::pmap(
    metric_specs,
    \(metric_id, source_table, expected_source_column) {
      phase2_pull_metric(
        con = con,
        metric_id = metric_id,
        source_table = source_table,
        source_column = expected_source_column
      )
    }
  ) |>
    purrr::reduce(\(x, y) dplyr::full_join(x, y, by = "cbsa_code"))

  character_frame <- spine |>
    dplyr::left_join(metric_frame, by = "cbsa_code")

  stopifnot(nrow(character_frame) == 396)
  character_frame
}
