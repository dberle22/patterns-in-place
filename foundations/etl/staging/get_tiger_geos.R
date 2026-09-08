# Compatibility entry point for callers that still use the former staging path.
# The governed on-demand display builder now lives with other geometry ETL.
source(here::here("foundations", "etl", "geo", "get_tiger_geos.R"))
