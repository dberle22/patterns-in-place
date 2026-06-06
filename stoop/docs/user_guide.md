# User Guide

Short overview of common curated POI workflows in the repo.

## Curated POI Overview

Curated POIs currently have one active ingestion path:

- Google Takeout saved lists under `data/raw/google_maps/poi_nyc/`

One additional curated path is now designed but not implemented yet:

- Editorial article scraping under `data/raw/scraped/`

The active implementation now lives under:

```text
src/nyc_property_finder/curated_poi/google_takeout/
```

The planned scraping implementation will live under:

```text
src/nyc_property_finder/curated_poi/web_scraping/
```

The preferred CLI entry point is:

```text
nyc_property_finder.pipelines.ingest_curated_poi_google_takeout
```

These pipelines write:

```text
property_explorer_gold.dim_user_poi_v2
```

The shared Google Places enrichment layer now requests a richer default Place
Details payload, including rating, review count, business status, editorial
summary, editorial summary language code, price level, and website URI.

## One-Time Setup

Create a local `.env` file in the repo root:

```bash
printf 'GOOGLE_MAPS_API_KEY=your_google_maps_key_here\n' > .env
chmod 600 .env
```

Enable **Places API (New)** in the Google Cloud project for that key.

The key is read from `.env`, and `.env` is ignored by git.

## Update POI Categories

Use this workflow whenever you want to add or adjust curated taxonomy.

### Where taxonomy lives

- Config rules: `config/poi_categories.yaml`
- Scraped article inventory and status tracker: `config/curated_scrape_articles.yaml`
- Reference documentation: `docs/poi_categories.md`

Within `config/poi_categories.yaml`:

- `curated_taxonomy` is the canonical curated taxonomy contract.
- `keyword_taxonomy_rules` is a legacy matcher used for coarse Google Maps
  export normalization and should not be treated as the source of truth.

### What to update

1. Update `config/poi_categories.yaml`.
2. Update `config/curated_scrape_articles.yaml` when scraped article status, parser investment, or article-level taxonomy changes.
3. Add or revise the file-level rule under `curated_taxonomy.files`.
4. If needed, add or revise `tag_aliases` used to derive subcategory or level-3 descriptors.
5. Only update `keyword_taxonomy_rules` when the legacy coarse matcher needs better fallback behavior.
6. Update `docs/poi_categories.md` so the documented taxonomy and scrape inventory match the config.

### Taxonomy model

- `category`: top-level group such as `restaurants`, `bars`, `music_venues`
- `subcategory`: one stable, primary filter bucket
- `detail_level_3`: flexible descriptor layer that can hold one or many tags

Examples:

- `restaurants / japanese / ramen|sushi|izakaya`
- `restaurants / sandwiches / deli|italian`
- `bars / irish_pub /`

## Export Google Takeout

Use this flow when your places are saved as Google Maps lists.

1. Go to Google Takeout: https://takeout.google.com/
2. Deselect all products.
3. Select Saved.
4. Create a one-time export.
5. Download the zip when the email arrives.
6. Put the CSVs you want to ingest under `data/raw/google_maps/poi_nyc/`.

## Scrape Editorial Articles

Use this flow when your places come from Eater, Time Out, Vogue, or similar
articles.

### Locked approach

- Scraping is file-first, not database-first.
- Each publication gets its own scraper module.
- Low-volume or awkward one-off articles can use a semi-manual or manual-seed path.
- Multi-address mentions must be split into distinct rows before Places resolution.

### Planned package shape

```text
src/nyc_property_finder/curated_poi/web_scraping/
  base.py
  normalize.py
  registry.py
  publications/
    eater.py
```

### Current first implementation

The parser-backed scraper scaffold now covers Eater and Time Out. It supports:

- a locked Eater article registry
- a locked Time Out article registry
- a config-backed article inventory and status tracker
- listing registered article slugs
- parsing a saved local HTML file
- optionally fetching a live article URL
- writing one normalized CSV for QA review

Preferred generic export entry point:

```text
nyc_property_finder.pipelines.export_curated_poi_article
```

Compatibility alias kept for Eater:

```text
nyc_property_finder.pipelines.export_curated_poi_eater_article
```

Preferred semi-manual export entry point:

```text
nyc_property_finder.pipelines.export_curated_poi_semi_manual_article
```

### File flow

```text
article html/text
  -> data/raw/scraped/raw/<publication>/<slug>_<date>.{html,txt,json}
  -> data/raw/scraped/normalized/<category>_<publication>_<slug>_<date>.csv
  -> property_explorer_gold.stg_user_poi_web_scrape
  -> property_explorer_gold.dim_user_poi_v2
```

### Shared normalized scrape contract

Every publication-specific scraper should normalize into the same row shape
before Places resolution. Keep these fields at minimum:

- `publisher`
- `article_title`
- `article_url`
- `source_list_name`
- `item_rank`
- `item_name`
- `item_url`
- `raw_address`
- `raw_description`
- `raw_neighborhood`
- `raw_borough`
- `category`
- `subcategory`
- `detail_level_3`
- `scraped_at`

During normalization, these fields should then map into the curated POI
resolve contract used downstream:

- `input_title` = `item_name`
- `note` = `raw_address`
- `comment` = `raw_description`
- `source_url` = `article_url` or `item_url`
- `search_query` = `item_name + raw_address + NYC context`
  and when address is blank, append `raw_neighborhood` before the NYC context

### Taxonomy rules for scraped inputs

- Set `category` and `subcategory` from the article or list identity first.
- Use publication-specific parser hints second when needed.
- Use description keyword extraction only as a fallback.
- Use Google Places metadata later for enrichment, not as the primary source of taxonomy.

### QA before Places resolution

Review each normalized scrape file before a live resolve run:

- row count
- missing names
- missing addresses
- duplicate `item_name + raw_address`
- multi-address mentions split correctly
- obvious non-places removed

### Reusable Eater workflow

1. List the registered Eater articles:

```bash
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.export_curated_poi_article \
  --publisher-filter Eater \
  --list-articles
```

2. Save the raw article HTML under `data/raw/scraped/raw/eater/`.

Recommended filename shape:

```text
data/raw/scraped/raw/eater/<article_slug>_<date>.html
```

3. Export one normalized review CSV from the saved HTML:

```bash
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.export_curated_poi_article \
  --article-slug best-bakeries-nyc \
  --html data/raw/scraped/raw/eater/best-bakeries-nyc_2026-04-28.html
```

4. Review the normalized CSV written under `data/raw/scraped/normalized/`.

The command prints:

- total rows written
- rows with addresses
- duplicate `item_name + raw_address` count

The article listing also includes each article's current scrape `status`.

5. Spot-check the file before any Places resolution work:

- verify article-level taxonomy is correct
- verify multi-address mentions became separate rows
- verify `raw_address` and `raw_description` are clean
- remove or correct obvious non-places if needed

Optional live-fetch mode:

```bash
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.export_curated_poi_article \
  --article-slug best-bakeries-nyc \
  --url https://ny.eater.com/maps/best-bakeries-nyc
```

Use saved HTML by default when iterating so parser QA is reproducible.

### Resolve One Normalized Scrape

Once the normalized CSV looks correct, run it through the shared Google Places
resolve/enrich path and merge it into curated staging plus canonical output:

```bash
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.ingest_curated_poi_web_scrape \
  --csv data/raw/scraped/normalized/bakeries_eater_best-bakeries-nyc_2026-04-28.csv
```

## Dry Run A Batch

Use dry run before any live ingestion. It does not hit the API and does not
write DuckDB.

```bash
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.ingest_curated_poi_google_takeout \
  --input-dir data/raw/google_maps/poi_nyc \
  --dry-run
```

Dry-run reports:

- per-file row counts
- category assignments
- subcategory assignments
- level-3 descriptor values
- estimated Text Search calls
- estimated Place Details calls

## Run A Batch

Use this to process the full curated Google Takeout directory.

```bash
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.ingest_curated_poi_google_takeout \
  --input-dir data/raw/google_maps/poi_nyc
```

This flow:

1. Parses every CSV in `data/raw/google_maps/poi_nyc/`
2. Resolves rows to Google `place_id`s
3. Fetches cached or current-version Place Details for unique places
4. Writes the current batch into `property_explorer_gold.stg_user_poi_google_takeout`
5. Promotes that staged batch into canonical `property_explorer_gold.dim_user_poi_v2`

The API calls are cache-first. Re-running the same inputs should make zero new
API calls unless the inputs changed or an older cached details payload needs a
versioned refresh.

## Run One CSV

Use this while iterating on one curated file.

```bash
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.ingest_curated_poi_google_takeout \
  data/raw/google_maps/poi_nyc/poi_bookstores_nyc.csv
```

## Guardrails

Defaults:

```text
max Text Search calls: 50
max Place Details calls: 50
```

If a run would exceed those caps, it stops before making the extra calls.

Override when needed:

```bash
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.ingest_curated_poi_google_takeout \
  --input-dir data/raw/google_maps/poi_nyc \
  --max-text-search-calls 100 \
  --max-details-calls 100
```

## Outputs

Intermediate caches:

```text
data/interim/google_places/place_resolution_cache.csv
data/interim/google_places/place_details_cache.jsonl
```

Run summary and quick QA:

```text
data/interim/google_places/place_pipeline_summary.json
data/interim/google_places/place_pipeline_qa.csv
```

DuckDB table:

```text
data/processed/nyc_property_finder.duckdb
property_explorer_gold.stg_user_poi_google_takeout
property_explorer_gold.stg_user_poi_web_scrape
property_explorer_gold.dim_user_poi_v2
```

## Check The Result

Open the summary:

```bash
cat data/interim/google_places/place_pipeline_summary.json
```

Review duplicate or missing-coordinate warnings:

```bash
cat data/interim/google_places/place_pipeline_qa.csv
```

Quick row count:

```bash
PYTHONPATH=src .venv/bin/python - <<'PY'
from nyc_property_finder.services.duckdb_service import DuckDBService

with DuckDBService("data/processed/nyc_property_finder.duckdb", read_only=True) as db:
    print(db.query_df("""
        SELECT
            COUNT(*) AS rows,
            COUNT(*) FILTER (WHERE lat IS NOT NULL AND lon IS NOT NULL) AS rows_with_coordinates
        FROM property_explorer_gold.dim_user_poi_v2
    """))
PY
```

## Compatibility Note

The older CLI path still exists:

```text
nyc_property_finder.pipelines.ingest_google_places_poi
```

But new documentation should use:

```text
nyc_property_finder.pipelines.ingest_curated_poi_google_takeout
```
