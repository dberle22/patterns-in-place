# Stoop Place Classification Execution

## Purpose

This document is the ordered runbook for rebuilding the restaurant classification mart in DuckDB.

Use it when you want to:

- rebuild the classification mart from source curated POIs
- refresh keyword matches, scores, recommendations, and review queue outputs
- inspect the main QA summaries after a run

This runbook assumes:

- `property_explorer_gold.dim_user_poi_v2` already exists
- the DuckDB file is not locked by another process
- the SQL files under `sql/marts/place_classification/` are the current source of truth

---

## Ordered Build Sequence

The runner executes files in this order:

1. [sql/ddl/003_property_classification_mart.sql]
2. [sql/marts/place_classification/place_classification_text.sql]
3. [sql/marts/place_classification/place_word_profile.sql]
4. [sql/marts/place_classification/place_phrase_profile.sql]
5. [sql/marts/place_classification/place_keyword_mapping_seed.sql]
6. [sql/marts/place_classification/place_keyword_matches.sql]
7. [sql/marts/place_classification/place_matched_keywords.sql]
8. [sql/marts/place_classification/place_classification_scores.sql]
9. [sql/marts/place_classification/place_classification_recommendations.sql]
10. [sql/marts/place_classification/place_classification_review_queue.sql]
11. [sql/marts/place_classification/curated_places_classified.sql]

This order matters because the downstream outputs depend on the upstream tables being rebuilt first.

---

## Runner Command

Run the pipeline with:

```bash
PYTHONPATH=src python3 -m nyc_property_finder.pipelines.build_place_classification_mart
```

Optional database override:

```bash
PYTHONPATH=src python3 -m nyc_property_finder.pipelines.build_place_classification_mart --database /path/to/file.duckdb
```

---

## What The Runner Prints

The runner prints:

- each executed SQL file
- key summary counts
- top recommendation counts for `mixed_restaurants`
- confidence distribution
- review queue reasons

This makes it easy to see whether a run materially improved restaurant classification coverage.

---

## Recommended Post-Run QA

After the runner finishes, review:

- [sql/qa/curated_categories.sql/category_qa.sql]
- [sql/qa/curated_categories.sql/category_retaurant_update.sql]

Focus especially on:

- how many places remain `mixed_restaurants`
- which recommended subcategories appear most often
- which cases were routed into review
- whether any recommendations look obviously wrong because of noisy list-name language

---

## Expected Analyst Workflow

1. Run the mart rebuild.
2. Inspect `mixed_restaurants` recommendations.
3. Review low-confidence and changed cases.
4. Add manual overrides where needed.
5. Rerun the mart after mapping or override updates.

This should become the standard loop for restaurant reclassification work.
