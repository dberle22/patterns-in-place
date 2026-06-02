# Scatter Chart Decisions

## Decision S-001: Primary reference baseline
- Question: Which prior sample should be the primary reference for Scatter implementation?
- Answer: Use National CBSA scatter with labels, bubble size, and reference line as the main reference.
- Status: Decided
- Date: 2026-03-04

## Decision S-002: Feature defaults
- Question: Which scatter features should be included by default vs optional?
- Answer: Keep size encoding in base. Make both highlight modes optional (label overlay and color-highlight subset). Keep trend/reference line optional. Keep density/hexbin as a separate variant.
- Status: Decided
- Date: 2026-03-04

## Decision S-003: Sample SQL organization
- Question: Should scatter sample data be built as tables or as isolated per-question SQL queries?
- Answer: Use one SQL file per business question in `sample_sql/` and execute queries directly from R (no persistent sample tables).
- Status: Decided
- Date: 2026-03-04

## Decision S-004: SQL parameterization style
- Question: Where should test parameters live and how should they be updated?
- Answer: Keep constants in a `params` CTE at the top of each SQL file with comments describing what to edit for geography/time-window changes.
- Status: Decided
- Date: 2026-03-04
