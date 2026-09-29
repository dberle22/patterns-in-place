# Monorepo and a single warehouse

**Date:** 2026-05
**Source:** `PLATFORM_ROADMAP.md` (Track A, Done)

## Decision

All Patterns in Place work lives in one monorepo, and every product reads from one DuckDB warehouse (`patterns_in_place.duckdb`) built with a staging → Silver → Gold pattern.

## Why

The work had grown across separate repos (`metro_deep_dive`, `metro_deep_dive_chatbot`, `rental_area_search`), each with its own copy of data and logic. One warehouse keeps numbers consistent across products.

## What it means

- `foundations/` is a dependency, not a product. Products never keep their own copies of its assets.
- New sources go through staging → Silver → Gold in order.
- Exception still open: Stoop uses its own database (see [ARCHITECTURE.md](../ARCHITECTURE.md)).
