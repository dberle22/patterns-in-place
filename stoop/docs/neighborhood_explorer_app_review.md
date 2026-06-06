# Neighborhood Explorer App Review

Review date: 2026-04-21

## Executive Summary

`app/streamlit_app_v2.py` is in a strong place for a local decision-support
app. It has moved beyond a simple proof-of-concept map into a credible
neighborhood review surface: tract and neighborhood geography render from the
gold data model, demographic metrics are selectable, POIs can be overlaid and
filtered by saved-list source, and the data-loading logic is reusable and
covered by focused tests.

The biggest opportunity now is not a single code cleanup. It is to turn the app
from a foundation viewer into a neighborhood intelligence tool. That means
finishing POI coverage across the saved lists already sitting in
`data/raw/google_maps`, broadening demographic and neighborhood context,
building richer spatial analysis around listings and places, and tightening the
build/run path so the app can be refreshed confidently.

Current local data snapshot:

| Artifact | Current local state |
| --- | --- |
| `property_explorer_gold.fct_tract_features` | 1,115 rows. Metric coverage is high but not complete: income 1,067, rent 1,069, home value 955, bachelor's-plus 1,083, median age 1,082. |
| `property_explorer_gold.fct_nta_features` | 108 rows. Metric coverage is moderate: income 87, rent 87, home value 85, bachelor's-plus 90, median age 89. |
| `property_explorer_gold.fct_property_context` | 22 listing-context rows. |
| `property_explorer_gold.dim_user_poi_v2` | 91 Google Places-backed POIs, all with coordinates. Current v2 categories are Bookstores, Record Stores, and Museums. |
| Google Places cache | 97 source rows resolved to 91 unique Google Place IDs, with 5 duplicate-place groups flagged for review. |
| Raw Google Maps CSVs | Additional saved-list files exist for bars, museums, bookstores, record stores, pastry shops, pizza, restaurants, and shopping. The v2 app table does not yet cover all of them. |

## What Is Working Well

### App Shape And Separation

The Streamlit entry point is nicely thin. `app/streamlit_app_v2.py` handles
page layout, widgets, cache wrappers, and display composition. The heavier
logic lives in `src/nyc_property_finder/app/base_map.py`, including:

- DuckDB table loading.
- tract geometry loading and borough filtering.
- tract-to-NTA attribute joins.
- NTA dissolve/aggregation geometry.
- demographic display formatting.
- color ramp generation.
- POI normalization and filtering.
- PyDeck layer construction.

That split is exactly what makes the app testable and easier to evolve. The
tests in `tests/test_base_map_app.py` validate the important contracts without
needing a running Streamlit process.

### The App Handles Missing Data Honestly

The app does not pretend missing demographics are zeros. Missing values get
explicit "Unavailable" labels and muted map colors. This is a very good product
instinct because neighborhood metrics can otherwise look more precise than they
are.

The companion `app/neighborhood_qa_app.py` is also a good move. It keeps
coverage and readiness review out of the exploration flow while still making
data gaps visible.

### Geography Foundation Is Solid

The app uses Brooklyn and Manhattan tract geometry, joins to
`dim_tract_to_nta`, and can display either tract-level or dissolved
neighborhood-level geography. The current design supports both fine-grained
inspection and broader neighborhood comparison.

The test fixtures confirm important geography behavior:

- Queens tracts are excluded from the current target geography.
- tract metrics join by normalized tract IDs.
- NTA geometries can be built from tract geometries.
- boundaries still render when demographic fill is disabled.

### POI Integration Is Meaningfully Better Now

The Google Places v2 workflow is a major improvement over plain exported saved
places. The current pipeline resolves saved-list rows to Google Place IDs,
fetches minimal details, caches both resolution and details, writes
`dim_user_poi_v2`, and produces summary/QA artifacts.

Good pieces already present:

- API call caps.
- cache-first reruns.
- one row per unique Google Place ID.
- preservation of source list names.
- JSON arrays for multi-list membership and source metadata.
- QA for duplicate Google Place IDs.
- app fallback order that prefers `dim_user_poi_v2` but can still use legacy
  `dim_user_poi` or caches.

The v2 table is currently clean in the most important basic way: 91 rows and 91
rows with coordinates.

### Documentation Has Good Canonical Structure

The docs folder has a healthy shape:

- `docs/README.md` tells readers where project truth belongs.
- `docs/data_model.md` owns table contracts.
- `docs/pipeline_plan.md` owns build order.
- `docs/source_inventory.md` owns source caveats.
- `docs/app/neighborhood_explorer_app.md` owns app behavior.
- `docs/planning/next_workstreams_plan.md` captures strategic follow-on work.

This structure will save you pain as the app grows. The project already has
enough moving parts that unwritten decisions would become expensive quickly.

## What Can Be Improved

### Expand POI Coverage Beyond The First Three Lists

The largest immediate product gap is POI coverage. The v2 table currently
contains:

| Category | Rows |
| --- | ---: |
| Bookstores | 37 |
| Record Stores | 29 |
| Museums | 25 |

But raw saved-list CSVs also exist for:

- Bars.
- Bars - NYC.
- Pastry Shops.
- Pizza.
- Restaurants.
- Shopping.
- Museums and New York - Museums, which may partially overlap.

Those categories matter a lot for rental-area search. Restaurants, bars, pizza,
coffee/pastry, shopping, and errand places are closer to everyday livability
than museums and bookstores alone. The current POI layer proves the workflow,
but the lifestyle picture is still narrow.

Recommended next step: add directory-wide or multi-file Google Places ingestion
so all curated lists can flow into `dim_user_poi_v2` in one run. Then review
duplicates and category labels before wiring those categories into scoring or
summary panels.

### Review Duplicate Place Resolutions

`place_pipeline_qa.csv` flags 5 duplicate-place groups from 11 duplicate source
rows. Some are likely valid duplicates, such as alternate names for the same
bookstore. One looks suspicious:

`Book Club` and `Bluestockings Bookstore, Cafe & Activist Center` resolved to
the same Google Place ID.

That could be a bad top-candidate match. Before scaling POI analysis, add a
small manual review workflow:

- source title.
- resolved Google display name.
- formatted address.
- Google Place ID.
- source list.
- accept/reject/override status.

This does not need to be elaborate. A CSV override file would be enough.

### Decouple App Runtime From Pipeline Building

`load_poi_map_data()` can build `dim_user_poi_v2` directly from caches when the
DuckDB table is empty. That fallback is useful during development, but it makes
the app do pipeline-ish work at display time.

Near term, keep the fallback, but make the behavior more visible:

- expose the POI source in the sidebar, already partly done with
  `poi_data.source`;
- show whether POIs came from DuckDB, legacy table, or cache fallback;
- consider warning when the app is reading directly from cache instead of a
  built gold table.

Longer term, the app should mostly read app-ready tables. Cache-to-table builds
should happen in an explicit pipeline command.

### Use Configured Geography Targets

`config/settings.yaml` has:

```yaml
target_boroughs:
  - Brooklyn
  - Manhattan
```

But `base_map.py` currently hard-codes county GEOIDs with
`TARGET_COUNTY_GEOIDS = ("36047", "36061")`. That is fine for the current app,
but the settings and implementation should converge before expanding coverage.

Recommended improvement: derive target county GEOIDs or borough filters from
config. At minimum, document that the setting is currently descriptive while
the app helper uses constants.

### Improve NTA Metric Coverage And Aggregation

Tract metric coverage is fairly strong, but NTA coverage has more holes. Only
87 of 108 NTA rows currently have median income and median rent, and 85 have
median home value.

This raises two questions:

1. Are missing NTA values caused by tract source coverage gaps, aggregation
   rules, or NTA membership mismatches?
2. Are the aggregation methods appropriate for each metric?

The app can render these gaps correctly, but the product story becomes stronger
if the docs and QA app explain why each missing value is missing. For percent
and count-like metrics, weighted aggregation should be preferred when
denominators are available. For medians, median-of-tract-medians is often only
an approximation and should be labeled that way if used.

### Update Docs That Still Say Google Places Is Post-MVP

Several docs were accurate when written but are now behind the implementation.
For example, `docs/source_inventory.md` still says Google Places API resolution
is post-MVP, while the repo now has a working Google Places v2 pipeline and
user guide.

Recommended cleanup:

- Update `docs/source_inventory.md` to say Google Places v2 exists as an
  optional cache-first enrichment path.
- Update `docs/planning/post_mvp_improvements.md` so Google Places enrichment is
  no longer framed as wholly future work.
- Update `docs/app/neighborhood_explorer_app.md` to mention POI overlays and
  source-list filtering, not just demographic geography.
- Update `docs/pipeline_plan.md` to include the v2 entry point
  `nyc_property_finder.pipelines.ingest_google_places_poi`.

### Add App-Level Data Freshness Signals

The app is now mixing multiple refresh cadences:

- tract features.
- NTA features.
- Google Places caches.
- raw Google Takeout lists.
- listings and property context.
- subway data.

The app should eventually show build timestamps or cache ages. That matters
because stale POIs or listings can lead to wrong conclusions even when the map
works perfectly.

Candidate table: `property_explorer_gold.fct_build_run`, with source name,
run timestamp, row counts, warning counts, and artifact paths.

## Missing Data And Analysis Opportunities

### Everyday Amenities

The current v2 POI coverage leans cultural and preference-driven. That is
valuable, but rental-area decisions also need everyday context:

- grocery stores.
- pharmacies.
- laundromats.
- gyms.
- coffee shops.
- parks and dog runs.
- urgent care and hospitals.
- hardware stores.
- coworking or libraries.
- late-night food.

Some of this can come from personal Google Maps lists. Some should probably
come from public or commercial place sources so the app has baseline coverage
even where the user has not saved places.

### Commute And Mobility

Nearest subway distance is a good MVP measure, but the next level of usefulness
is commute-specific:

- travel time to work anchors.
- travel time to frequent places.
- number of transfers.
- late-night service assumptions.
- bike/transit/walking mode toggles.
- Citi Bike station access.
- ferry access where relevant.

Even before full routing, the app could support user-defined anchors and show
straight-line or nearest-station proxy distance to those anchors.

### Housing Affordability Context

The app has listing price and neighborhood rent/home-value metrics, but it
could do more to frame affordability:

- price per bedroom.
- price per square foot when available.
- rent vs NTA median rent.
- sale price vs NTA median home value.
- no-fee and broker-fee adjusted move-in cash.
- estimated monthly carrying cost for sales.
- rent burden context by income bands, if ACS variables are added.

This should probably be split by rental mode and sale mode. Mixed rental/sale
sorting can become misleading quickly.

### Neighborhood Demographics

The current metrics are a good first set:

- median household income.
- median gross rent.
- median home value.
- bachelor's-plus share.
- median age.

Useful next metrics:

- renter-occupied share.
- vacancy rate.
- household size.
- population density.
- age bands.
- transit commute share.
- car-free household share.
- rent-burden share.
- recent move-in share.
- language or nativity metrics, if product framing stays careful.

Crime/safety remains worth deferring until the source and framing are strong.
It is easy to make that feature feel precise and objective when it is neither.

### Listing Supply And Freshness

The product will feel much more useful with more listing coverage and a sense of
freshness. The current 22 property-context rows are enough for app validation,
but not enough for robust neighborhood comparison.

Good expansion paths:

- richer manual listing CSVs for near-term control.
- StreetEasy saved HTML parser with no live network dependency at first.
- explicit stale/active listing status.
- source update timestamp.
- listing snapshot history for price changes and disappeared listings.

### Comparative Analysis

Once the app has more listings and POIs, it should help answer comparative
questions:

- Which neighborhoods have the highest density of personally relevant places?
- Which listings are near multiple categories, not just many places in one
  category?
- Which areas have good subway access but lower median rent?
- Which neighborhoods are strong on lifestyle fit but weak on commute?
- Which shortlist items dominate others on price, space, transit, and POIs?

That points toward a future shortlist comparison view and neighborhood summary
cards.

## Product Expansion Ideas

### 1. Neighborhood Profile Panel

When a user selects or hovers a neighborhood, show a compact profile:

- demographics.
- number of current listings.
- median listing price in current sample.
- POI counts by selected source lists.
- nearest major subway lines or station density.
- notes about missing data.

This would make the app feel less like a map and more like a research cockpit.

### 2. POI Category Summary

Add a sidebar or below-map summary for selected POI filters:

- total POIs shown.
- counts by source list/category.
- top neighborhoods by POI count.
- duplicate or unresolved POI warnings.

This is especially useful once all saved lists are ingested.

### 3. Listing Overlay In Neighborhood Explorer

Neighborhood Explorer and Property Explorer are separate right now, which is
clean. But the Neighborhood Explorer could optionally show listing points or
listing counts by NTA.

This would answer: "Which neighborhoods have both good context and actual
inventory?"

### 4. Saved Areas Or Neighborhood Shortlist

The app has property shortlist persistence. A parallel neighborhood shortlist
could be useful:

- save an NTA as promising.
- add notes.
- compare saved neighborhoods.
- filter listings to saved neighborhoods.

This would fit the real search process, where areas are often shortlisted
before specific units.

### 5. Data QA Drilldowns

The QA app is useful. A next step would be drilldowns:

- show tracts or NTAs missing each metric.
- show map layer for missing data.
- show POIs without coordinates or with duplicate matches.
- show listings without tract/NTA assignment.
- show source files and last modified timestamps.

### 6. Preference Profiles

For personal fit, support multiple preference profiles:

- culture-heavy.
- food/nightlife.
- quiet/parks.
- commute-first.
- budget-first.

This should come after more baseline POI and demographic coverage, but the data
model is already moving in a direction that can support it.

## Code And Architecture Recommendations

### Near-Term Code Improvements

1. Add directory-wide Google Places ingestion.
   The current CLI accepts one CSV. Add a mode that accepts a directory or a
   list of CSVs and merges all source rows before resolution/enrichment.

2. Add POI manual override support.
   Start with a local CSV for rejected matches, forced Google Place IDs, and
   category overrides.

3. Move target geography into config.
   Use `target_boroughs` or a `target_county_geoids` setting instead of
   hard-coded constants only.

4. Add source/build freshness metadata.
   Even a JSON summary read by Streamlit would be useful before creating a gold
   table.

5. Add focused tests for cache fallback behavior.
   The current tests cover v2 DuckDB preference. Add tests for cache-only
   fallback and duplicate source-list parsing if that path remains app-visible.

6. Add a lightweight Streamlit import/smoke test.
   Current helper tests are good. A minimal app smoke test can catch missing
   imports or config regressions.

### Documentation Improvements

1. Bring Google Places docs up to current implementation.
2. Document the current POI v2 table as an app-consumed table, not just a future
   artifact.
3. Add an explicit "current coverage" section to `docs/app/neighborhood_explorer_app.md`.
4. Add rebuild commands for all current v2 POI lists.
5. Clarify the difference between legacy `dim_user_poi` and v2
   `dim_user_poi_v2`.
6. Document NTA aggregation rules and known metric gaps.

## Suggested Priority Order

### Priority 1: Complete Current POI Coverage

Process all raw Google Maps CSVs into `dim_user_poi_v2`, review duplicate
matches, and update the app/docs to reflect v2 as the preferred POI source.

Why this first: the app already has the pipeline and UI hooks. This is the
fastest path to making the map feel substantially richer.

### Priority 2: Tighten Demographic Coverage And NTA QA

Investigate missing NTA metrics, document aggregation rules, and add QA
drilldowns for missing metric geography.

Why this second: the demographic map is the app's core foundation, and missing
NTA metrics affect neighborhood-level interpretation.

### Priority 3: Add Neighborhood And POI Summary Panels

Add summary tables or panels that rank neighborhoods by selected metric, POI
counts, and possibly listing counts.

Why this third: maps are good for exploration, but decision-making needs
ranked/scannable comparisons.

### Priority 4: Expand Listings And Add Freshness

Increase listing coverage beyond the 22 current property-context rows and show
when listing/property-context data was built.

Why this fourth: once neighborhoods and POIs are richer, listing supply becomes
the limiting factor.

### Priority 5: Redesign Scoring Around Transparent Choices

Do not over-invest in total scoring until the data inputs are broader. In the
meantime, emphasize transparent sortable facts: price, beds, subway distance,
selected POI count, NTA, and core demographics.

Why this fifth: a score is only useful once the underlying context is robust and
the user can understand why one area wins.

## Bottom Line

The current app is working well as a foundation. The code is modular, the map
behavior is covered by tests, the docs have a clear ownership model, and the
Google Places v2 work gives the project a much better personalization layer.

The most valuable next move is to feed the app more of the data it is now ready
to display. Expand saved-list coverage, review Google Places match quality,
tighten NTA metric QA, and add comparison surfaces that summarize what the map
is showing. That will shift Neighborhood Explorer from "technically solid" to
"genuinely useful for choosing where to search."
