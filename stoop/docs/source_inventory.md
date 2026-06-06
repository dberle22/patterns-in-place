# Source Inventory

This is the Sprint 1 source inventory proposal. Paths are local defaults and can
change after review; raw files should remain outside git.

Use `docs/data_model.md` for the compact app-facing contract that maps each
MVP source to its gold table and build entrypoint. This file is the deeper
source notebook for external URLs, selected source decisions, local caveats,
sample coverage, and open source questions.

## MVP Sources

| Source | MVP Role | Proposed Path | Format | Owner | Notes |
| --- | --- | --- | --- | --- | --- |
| Manual property listings | Property facts for map/list/detail | `data/raw/listings_sample.csv` for Sprint 2 sample; `data/raw/property_listings.csv` as default future manual path | CSV | User-maintained | Mixed listings with a rental lean. First manual sources are StreetEasy and Zillow. |
| Address geocoding | Fill missing listing coordinates | `data/interim/geocoding/listing_geocodes.csv` | CSV | Pipeline-generated | Candidate services: NYC GeoSearch or NYC Geoclient/Geoservice. Store quality/source and quarantine unmatched rows. |
| Google Maps saved places | Personal POIs and fit scoring | `data/raw/google_maps/saved_places.kml` or `.json` | KML/JSON | User export | First custom lists: Bookstores, Museums, Restaurants. Preserve saved list name when available. |
| Tract-to-NTA equivalency | Official tract to neighborhood mapping | `data/raw/geography/tract_to_nta_equivalency.csv` | CSV | NYC Open Data/manual download | Preferred over centroid joins. Candidate: 2020 Census Tracts to 2020 NTAs and CDTAs Equivalency. |
| NYC NTA boundaries | Neighborhood UI layer | `data/raw/geography/nta_boundaries.geojson` | GeoJSON | NYC source/manual download | Need NTA ID/name and geometry. |
| Census tract boundaries | Tract feature grain and NTA assignment | `data/raw/geography/census_tracts.geojson` | GeoJSON | Census/NYC source/manual download | Need full tract GEOID and geometry. |
| Subway stops | Transit context and mobility score | `data/raw/transit/gtfs_subway.zip` or normalized `data/raw/transit/subway_stops.csv` | GTFS ZIP/CSV | MTA official static GTFS | Use regular subway GTFS from `https://rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip`; normalize `stops.txt` to stop ID/name/lines/lat/lon. |
| Metro Deep Dive tract features | Neighborhood metrics | `data/raw/metro_deep_dive/tract_features.csv` | CSV or DuckDB export | Existing local DuckDB | Source DB path is local-only in ignored `config/data_sources.yaml`. Source table/view still needs selection. |

## Deferred Sources

| Source | Status | Reason |
| --- | --- | --- |
| StreetEasy scraper | Future adapter | Legal/terms and anti-bot risk; manual CSV is MVP path. |
| RentHop scraper | Future adapter | Same as above. |
| Crime/safety data | Deferred | Needs stronger source and careful product framing. |
| School quality, 311, flood risk | V2+ | Explicitly outside MVP scope. |
| Real-time listing refresh | V2+ | MVP is file-backed and deterministic. |
| Listing image/media ingestion | Post-MVP | MVP links to source listings instead of displaying listing images. |
| POI category override file | Post-MVP | Keyword categories are enough for MVP. |
| Walking-time/network distances | Post-MVP | Straight-line distance is enough for MVP scoring and filtering. |

## Source Expectations

### Reference Links

- NYC Open Data tract/NTA equivalency CSV:
  `https://data.cityofnewyork.us/api/views/hm78-6dwm/rows.csv?accessType=DOWNLOAD`
- NYC Open Data tract/NTA catalog mirror:
  `https://catalog.data.gov/dataset/2020-census-tracts-to-2020-ntas-and-cdtas-equivalency`
- NYC GeoSearch docs:
  `https://geosearch.planninglabs.nyc/docs/`
- NYC Geoclient docs:
  `https://maps.nyc.gov/geoclient/v2/doc`

### Manual Property Listings

- User-owned CSV/JSON input, gathered manually from StreetEasy and Zillow first.
- Sprint 2 starts from `data/raw/listings_sample.csv`, currently about 22
  Manhattan and Brooklyn properties.
- Required fields are enough for map display and listing scoring.
- Rows without coordinates can enter a geocoding queue, but normalized listings
  require coordinates before map display and scoring.
- Approximate coordinates are acceptable when marked with `coordinate_quality`.
- Mixed rentals and sales are allowed with `listing_type`.
- The first mix can lean toward rentals.
- `no_fee` is required for rental rows because fee status materially changes
  affordability.
- `days_on_market` is deferred until scraper/adapter data exists because it is
  hard to maintain by hand.
- Source links should be collected to make every listing inspectable.
- Listing images are deferred; `url` is the MVP path back to source media.

### Google Maps POIs

- Export from Google Maps saved places or Google Takeout when possible.
- KML is acceptable when it includes coordinates; JSON is acceptable if it
  includes name and coordinates.
- Sprint 2 saved-list CSV exports are accepted when they include `Title` and
  `URL`. The MVP resolver uses `Title` plus NYC GeoSearch to create coordinates
  and quarantines misses.
- Google Places API resolution is Post-MVP.
- First expected saved lists are custom Bookstores, Museums, and Restaurants
  lists. Final list names can be decided when this integration starts.
- Saved list names should be preserved as `source_list_name` when available.
- Categories are normalized with `config/poi_categories.yaml`. The canonical
  curated taxonomy lives under `curated_taxonomy`; the legacy
  `keyword_taxonomy_rules` block is only a coarse matcher for older Google Maps
  export normalization. Unknown places become `other`.
- Category overrides are post-MVP.
- Raw files may expose sensitive personal routines and should remain local.

### Geography

- Tract and NTA geometries should use WGS84 coordinates or be reprojected before
  spatial work.
- Prefer NYC Open Data's tract-to-NTA equivalency table before deriving the
  mapping from geometries.
- Sprint 2 selected the NYC Open Data `hm78-6dwm` equivalency as the
  authoritative tract/NTA mapping source.
- Sprint 3 geometry should use NYC DCP/ArcGIS 2020 census tract and NTA boundary
  files, filtered to Manhattan and Brooklyn first if full-city geometry is too
  heavy.
- Manhattan and Brooklyn are the minimum first real coverage target.
- Tract IDs must be compatible with Metro Deep Dive feature IDs.
- NTA names should be human-readable for UI filters and detail panels.

### Transit

- MTA GTFS stops are the preferred durable source.
- Sprint 2 selected source: MTA official regular subway static GTFS at
  `https://rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip`.
- Normalize `stops.txt` parent stations or platform stops into stop/station ID,
  display name, served lines, and coordinates.
- A simpler station CSV remains acceptable as a fallback if GTFS route-to-stop
  line normalization becomes too large for the sprint.
- The MVP uses straight-line distance to the nearest stop as a transparent
  proxy.

### Metro Deep Dive Features

- Start with existing Metro Deep Dive DuckDB features rather than a new Census
  API pull.
- Source database path should be set locally in ignored
  `config/data_sources.yaml`.
- Sprint 2 inspected `foundation.tract_features`, `gold.housing_core_wide`, and
  `gold.population_demographics`. The local source does not currently expose NYC
  tract metric rows, so Sprint 2 materializes Brooklyn/Manhattan tract and NTA
  feature rows with null metric values as an explicit MVP fallback.
- Fields should match `fct_tract_features`: income, rent, home value,
  education, and age.
- Percent fields must use one documented scale.
- Crime/safety fields are excluded from MVP scoring.

### Address Geocoding

- Address geocoding can fill missing listing `lat`/`lon` before normalization.
- In this app, geocoding is only the address-to-coordinate step needed for map
  placement, tract/NTA assignment, nearest subway distance, and nearby POI
  counts.
- Start with a manual/cache CSV plus NYC GeoSearch fallback for forward
  geocoding by address/name.
- NYC Geoclient/Geoservice are post-MVP candidates when official NYC address
  handling, BBL/BIN, or political/geographic attributes become useful.
- The geocoding output should retain original address, matched address,
  coordinates, geocode source, quality/status, and error messages.

## Minimum Viable Sample Coverage

- Geography: Manhattan and Brooklyn tracts/NTAs.
- Listings: 10-30 representative records, mixed but rental-leaning, copied from
  StreetEasy/Zillow first.
- Transit: subway stops covering those listing neighborhoods.
- POIs: at least 20 saved places across Bookstores, Museums, Restaurants, and
  any later custom lists so personal fit scoring is visible.
- Features: enough Metro Deep Dive tract/NTA rows for all sample listings to
  receive neighborhood context where possible.

## Open Questions For You

1. Which borough should be second priority after Manhattan and Brooklyn, if the
   sample expands?
2. What are the exact Google Maps custom list names for Bookstores, Museums,
   and Restaurants?
3. Do you prefer MTA GTFS as the first transit source, or a simpler station CSV
   if it gets us to the demo faster?
4. Which Metro Deep Dive source tables/views should the Sprint 2 tract feature
   SQL query use?
