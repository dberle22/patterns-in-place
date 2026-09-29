-- Set this once to the canonical directory recorded in the published v2026.1 manifest.
-- Example: SET VARIABLE panel_base_url = 'https://data.source.coop/<publisher>/pip-metro-micro-panel/v2026.1';
INSTALL httpfs;
LOAD httpfs;

SELECT geo_name, annualized_median_rent, rent_to_income
FROM read_parquet(getvariable('panel_base_url') || '/affordability_wide.parquet')
WHERE year = 2024
ORDER BY rent_to_income DESC
LIMIT 10;
