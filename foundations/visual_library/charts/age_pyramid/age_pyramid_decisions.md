# Age Pyramid Decisions

## Decision AP-001: Comparison metric
- Question: What should be the default measure for cross-geo pyramid comparisons?
- Answer: Use percent-of-total as the default display metric and keep count-based pyramids as an opt-in descriptive variant.
- Status: Decided
- Date: 2026-04-14

## Decision AP-002: Repeated benchmark rows in small multiples
- Question: How should benchmark context work when one benchmark is compared against multiple selected geographies or periods?
- Answer: Repeat benchmark rows per `facet_label` so each facet has its own outline context. Treat `facet_label` as part of the age pyramid grain alongside `geo_id`, `period`, `age_bin`, `sex`, and `benchmark_label`.
- Status: Decided
- Date: 2026-04-16

## Decision AP-003: Chart-local SQL helper for age-sex binning
- Question: Where should the ACS wide age-by-sex unpivot and simplified age-bin mapping live?
- Answer: Keep the reusable CTE fragment in `sample_sql/age_pyramid_age_sex_helper.sql` and have chart-local sample runners substitute it into canonical SQL queries. This avoids a new DuckDB table while keeping age-bin logic consistent across age pyramid samples.
- Status: Decided
- Date: 2026-04-16
