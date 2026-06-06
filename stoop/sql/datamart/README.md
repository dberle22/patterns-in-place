# sql/datamart - Stoop Datamart

Stoop-specific SQL views and mart tables. This is the permanent home for
SQL that shapes data for Stoop Explore and Stoop Search product surfaces.

## Current marts

### neighborhood_character/
Pre-computed NTA-level character scores and POI density summaries.
Powers the character profile panel and category density overlays in Stoop Explore.

- `nta_category_controls` - UI control metadata for POI categories
- `nta_category_density` - POI density per NTA per category
- `nta_character_profile` - composite NTA character score and explanation
- `nta_curated_poi_counts` - curated (Google + scrape) POI counts per NTA
- `nta_public_poi_counts` - public (OSM) POI counts per NTA

### place_classification/
Classification pipeline for curated POIs - assigns type labels, scores,
keyword matches, and phrase profiles used in character scoring.

- `place_keyword_mapping_seed` - seed keyword-to-category mappings
- `place_keyword_matches` - keyword match results per place
- `place_matched_keywords` - matched keyword lookup
- `place_word_profile` - word frequency profile per place
- `place_phrase_profile` - phrase-level profile per place
- `place_classification_scores` - composite classification scores
- `place_classification_text` - text representations for review
- `place_classification_review_queue` - places needing manual review
- `place_classification_recommendations` - final classification output
- `curated_places_classified` - full classified curated POI table

## Planned datamart tables (Phase 1 and beyond)

These tables will be added when the corresponding product phases are built.
SQL does not exist yet - this is a forward declaration only.

| Table | Description | Depends on |
|---|---|---|
| `stoop_nta_intelligence` | Pre-joined NTA Character + Livability + Opportunity scores for app consumption | Intelligence Framework (F3) |
| `stoop_poi_summary` | Aggregated POI density and category counts per NTA, across all source types | Current neighborhood_character mart |
| `stoop_listing_scores` | Zillow/StreetEasy listing enrichment - NTA scores, proximity, composite listing score | Stoop Search Phase 1 |
