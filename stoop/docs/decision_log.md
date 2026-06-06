# Decision Log

This log separates confirmed Sprint 1 decisions from proposed choices and open
questions. Dates use the local project date.

## Confirmed

| Date | Decision | Rationale | Owner |
| --- | --- | --- | --- |
| 2026-04-17 | MVP is file-backed first. | Avoid fragile scraping as a dependency for the demo. | Project |
| 2026-04-17 | MVP supports rentals and sales. | Product should evaluate both rental and purchase options. | Project |
| 2026-04-17 | First geography target is Manhattan and Brooklyn. | Enough coverage for a credible NYC demo without full-city scope. | Project |
| 2026-04-17 | NTA is the primary neighborhood UI language. | NTAs are more legible than tracts for app users. | Project |
| 2026-04-17 | Google Maps saved places are core MVP data. | Personal POIs make ranking and context user-specific. | Project |
| 2026-04-17 | Shortlists persist in DuckDB. | Saved listings should survive Streamlit sessions. | Project |
| 2026-04-17 | Crime/safety is deferred. | Needs stronger source choice and careful framing. | Project |
| 2026-04-17 | First listing set will be mixed, leaning rental. | Reflects expected user collection pattern. | User |
| 2026-04-17 | StreetEasy and Zillow are the first manual listing sources. | These are the sources the user expects to gather from first. | User |
| 2026-04-17 | Listing images are post-MVP. | MVP can link back to the source URL for images and full listing media. | User |
| 2026-04-17 | Approximate listing coordinates are acceptable when marked. | Exact addresses are preferred, but some listings may hide precise location. | User |
| 2026-04-17 | First Google Maps POI lists are custom Bookstores, Museums, and Restaurants lists. | These categories match the user's personal context and are easy to demo. | User |
| 2026-04-17 | Keyword-based POI categorization is enough for MVP. | Category overrides can wait until the first POI integration shows a need. | User |
| 2026-04-17 | Straight-line distance is the MVP proximity method. | Easier to implement and explain than walking-time/network distance. | User |
| 2026-04-17 | Tract-to-NTA mapping should prefer an online/source equivalency table. | Reduces geospatial derivation risk and follows the user's preference. | User |
| 2026-04-17 | Metro Deep Dive DuckDB-derived features are the first neighborhood feature source. | Reuses existing local feature work instead of starting with a new Census API pull. | User |
| 2026-04-17 | Metro Deep Dive source database path is local-only in ignored `config/data_sources.yaml`. | Avoids publishing machine-specific absolute paths while keeping Sprint 2 configurable. | User |
| 2026-04-17 | Shortlist user ID should come from `config/settings.yaml`. | Keeps MVP local-user behavior configurable with little complexity. | User |
| 2026-04-17 | `no_fee` belongs in the rental CSV contract. | Broker fee status materially affects rental affordability. | User |
| 2026-04-17 | `days_on_market` is deferred until scraper/adapter data exists. | It is hard to maintain accurately by hand. | User |
| 2026-04-17 | Metro Deep Dive feature selection requires a Sprint 2 SQL build query. | The needed tract feature dataset is likely assembled from multiple source tables. | User |
| 2026-04-17 | Geocoding should start with a manual/cache CSV plus NYC GeoSearch fallback. | Keeps credentials and rate-limit complexity low while supporting address-only listings. | User |
| 2026-04-17 | Missing POI data should default `personal_fit_score` to null. | Avoids pretending personal-fit scoring is available before POIs are loaded. | User |
| 2026-04-17 | `active` stays on `dim_property_listing`; full snapshot/history is deferred. | Gives MVP current-listing behavior without a heavier history model. | User |
| 2026-04-17 | Project naming should use Property Explorer going forward. | Better reflects the product as an exploratory decision tool, not only a finder. | User |
| 2026-04-17 | App-facing DuckDB tables should use the `property_explorer_gold` schema. | Aligns data-layer naming with the Property Explorer product direction. | User |
| 2026-04-17 | Listing geocoding should use NYC GeoSearch first. | The Sprint 2 listing sample currently lacks latitude/longitude, and NYC GeoSearch avoids Google geocoding credentials for the MVP path. | User |
| 2026-04-17 | Codex should select the subway stop source from public web sources. | Keeps the transit foundation moving without requiring user-provided files. | User |
| 2026-04-17 | Google Maps saved-list CSVs should be resolved with NYC GeoSearch for MVP. | Good enough for local demo data without adding Google API credentials and billing to the MVP path. | User |
| 2026-04-17 | Google Places API is Post-MVP. | Official Google place resolution is better long-term but not needed for the first MVP. | User |
| 2026-04-17 | Sprint 3 should build `property_explorer_gold.fct_property_context` from the completed Sprint 2 foundation tables. | Keeps Sprint 3 focused on app-ready context and scoring rather than new source acquisition. | User/Codex |
| 2026-04-17 | Sprint 3 scoring must treat null neighborhood metrics as missing source coverage, not real zero values. | Metro Deep Dive NYC tract metrics are currently null, so zero-filled scoring would pretend precision. | User/Codex |
| 2026-04-17 | Sprint 3 should use nearest-stop straight-line subway distance and straight-line POI radius counts. | Matches MVP proximity decisions and avoids walking-time/routing complexity. | User/Codex |
| 2026-04-17 | Sprint 3 context DDL includes `nta_name`, `poi_count_nearby`, POI availability, and score status fields. | Makes Sprint 4 map/list/detail UI able to explain context and missing data directly from one table. | Codex |
| 2026-04-17 | Sprint 3 total score reweights available components and marks missing-component behavior. | Preserves a sortable score without hiding that neighborhood or POI inputs may be missing. | Codex |
| 2026-04-17 | Sprint 4 should use `property_explorer_gold.fct_property_context` as the primary app table. | Sprint 3 already materializes listing facts, geography assignment, transit context, POI context, scores, and missing-data statuses needed for map/list/detail workflows. | Codex |
| 2026-04-17 | Sprint 4 should implement the actual explorer as the first screen, not a marketing landing page. | The MVP value is reviewing properties immediately through filters, map, listing cards, and detail. | Codex |
| 2026-04-17 | Sprint 4 should display neighborhood score/status as unavailable with current data. | Metro Deep Dive NYC tract metrics are currently null, so the app must not present a false neighborhood score. | Codex |
| 2026-04-17 | Next major workstreams should be ACS neighborhood context, scoring redesign, Google Places cached POI enrichment, and StreetEasy scraping. | These address the largest remaining data quality, ranking credibility, personalization, and listing supply gaps after Sprint 4. | User/Codex |
| 2026-05-08 | Stoop Explore and Stoop Search intelligence outputs should be pre-computed and stored in DuckDB. | Pipeline-time materialization gives the apps fast reads, a stable contract, reproducible validation, and simpler testing; richer runtime flexibility can wait until the metrics and label system are more mature. | User/Codex |
| 2026-05-08 | Stoop Explore Character should use "known for" as the dominant MVP framing. | This keeps the product descriptive and evidence-led while still leaving room for more playful editorial copy on the surface. | User/Codex |
| 2026-05-08 | Stoop Explore v1 should keep six initial story types, including quiet residential enclave. | The full set gives Explore a complete narrative frame, while quiet residential enclave can later lean more heavily on Search/Livability inputs. | User/Codex |
| 2026-05-08 | Stoop Explore v1 category ranking should break ties using subcategory diversity after raw count. | Restaurant and other high-volume categories need a way to reward depth, not just mass. | User/Codex |
| 2026-05-08 | Stoop Explore evidence thresholds should remain tunable during Sprint 2 validation. | Current category coverage is still uneven, so the minimum threshold should not be treated as fixed yet. | User/Codex |
| 2026-05-08 | `music_venues` should stay hidden in the first public Explore category set. | It can remain a background signal, but it is not the right front-door neighborhood recommendation category for v1. | User/Codex |
| 2026-05-08 | `museums` should stay live in Explore, and `art_galleries` should be a future separate category. | This keeps a useful cultural category live now while leaving room for better Chelsea-style arts coverage later. | User/Codex |
| 2026-05-08 | Sprint 2 Explore intelligence is approved as good enough to ship with known blind spots. | The right next move is Sprint 3 surface build plus targeted source expansion, not another round of design-only refinement. | User/Codex |
| 2026-05-12 | Sprint 3 bars expansion should treat blank article-level bar subcategories as `bars` and use article theme in `detail_level_3` when obvious. | The current classification mart only reclassifies `mixed_restaurants`, so keeping null bar inputs as generic bars avoids speculative bar inference while still preserving useful themes like `outdoor`. | User/Codex |

## Proposed For Review

| Decision | Proposal | Target Sprint | Owner |
| --- | --- | --- | --- |
| Manual listing source | Use `data/raw/listings_sample.csv` as the Sprint 2 sample input; keep `data/raw/property_listings.csv` as the default future manual path unless renamed. Source values can distinguish `streeteasy_saved`, `zillow_saved`, and later sources. | Sprint 2 | User/Codex |
| Listing card fields | Price, beds/baths, address, NTA, nearest subway, top POI signal, listing type, source, no-fee badge for rentals, mobility score, and personal score. | Sprint 1 | User |
| Metro Deep Dive feature query | Write a Sprint 2 SQL query that assembles the tract-level feature export from the needed Metro Deep Dive tables/views. | Sprint 2 | Codex |
| Listing geocoding | Allow raw address-only rows, use a manual/cache CSV plus NYC GeoSearch fallback, geocode before `property_explorer_gold` load/scoring, and quarantine unmatched rows. | Sprint 2 | User/Codex |
| Subway stop source | Use MTA official static subway GTFS regular feed from `https://rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip`, normalizing `stops.txt` into `property_explorer_gold.dim_subway_stop`. | Sprint 2 | Codex |
| Tract/NTA source alignment | Use NYC Open Data `hm78-6dwm` for tract-to-NTA equivalency; align on NYC DCP 2020 tract and NTA geometry files before implementation. | Sprint 2 | User/Codex |
| Tract-to-NTA fallback | Use centroid assignment only as fallback if the equivalency source is unavailable or incomplete. | Sprint 2 | User/Codex |
| Shortlist user ID | Read a configurable local default user ID from `config/settings.yaml`, with app-entered user names as the scale-up path. | Sprint 4 | User |
| Shortlist facts | Join to current listing/context tables rather than denormalizing listing facts into shortlist rows. | Sprint 4 | User/Codex |
| Sprint 3 POI radius | Use `0.5` straight-line miles for nearby personal POI counts. | Sprint 3 | User/Codex |
| Sprint 4 shortlist write scope | Implement read/join first, then add save/archive/reject and notes if low-risk after map/list/detail is stable. | Sprint 4 | User/Codex |
| Sprint 4 default sort | Default to `property_fit_score` descending, nulls last, with clear status labels for reweighted totals. | Sprint 4 | User/Codex |
| Sprint 4 map layers | Use property markers by default, with toggleable Google Maps POI and subway stop layers. | Sprint 4 | User/Codex |
| Score handling before redesign | De-emphasize or clearly label the current MVP total score until ACS and POI inputs are stronger. | Next workstreams | User/Codex |
| Google Places cost control | Use API calls only for unresolved places, persist cache results locally, and default future runs to cache-only. | Next workstreams | User/Codex |
| StreetEasy source strategy | Build StreetEasy as an optional adapter into the manual listing contract, with fixture-first parser tests and manual CSV fallback. | Next workstreams | User/Codex |

## Open Questions

| Question | Why It Matters | Target Sprint | Owner |
| --- | --- | --- | --- |
| What are the exact exported Google Maps custom list names? | Determines filtering and source-list handling in the POI parser. | Sprint 2 | User |
| What are the exact Metro Deep Dive source tables/views needed by the Sprint 2 tract feature SQL query? | Determines the implementation details of the feature export. | Sprint 2 | User/Codex |
| Should Sprint 4 default to showing rentals and sales together, or rentals only? | Mixed listing types are supported, but affordability and ranking semantics differ between rentals and sales. | Sprint 4 | User |
| Should Sprint 4 implement save/archive only, or also rejected status and notes? | This determines how much write-state complexity belongs in the first UI sprint. | Sprint 4 | User |
