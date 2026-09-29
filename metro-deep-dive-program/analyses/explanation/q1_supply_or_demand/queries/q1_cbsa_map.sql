-- Geometry remains source-faithful here because the read-only consumer does not
-- assume DuckDB's optional spatial extension is loaded.
select cbsa_code, cbsa_name, geom_wkb
from geo.cbsas;
