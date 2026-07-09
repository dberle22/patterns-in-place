# Agent Instructions

Use this workflow before and during section build tasks to reduce rework and catch issues early.

## 1) Preflight Contract Lock
- Define exact input artifacts and expected schemas before coding.
- Define required keys and uniqueness constraints up front.
- Confirm output artifact names/paths before implementation.

## 2) Spatial CRS Policy
- Keep storage CRS checks against `GEOMETRY_ASSUMPTIONS$expected_crs_epsg` (currently `4326`).
- Run all spatial operations (joins, intersections, area, point-on-surface) in `GEOMETRY_ASSUMPTIONS$analysis_crs_epsg` (currently `5070`).
- Normalize all `sf` inputs to analysis CRS before any spatial operation.

## 3) Readiness Checks Before Transforms
- Validate required columns for every upstream artifact.
- Validate key uniqueness for all join keys.
- Validate geometry object type, CRS, and empty geometry policy.
- Fail fast on hard-check failures before downstream computation.

## 4) Build Execution Pattern
- Implement transforms in small, deterministic steps.
- Persist intermediate artifacts at step boundaries.
- Include explicit score component columns before any final composite score.
- Use deterministic ranking/tie-break rules for shortlist outputs.

## 5) Validation and Reporting
- Persist a step-level validation report (`*_report.rds`) with:
  - schema checks
  - key checks
  - geometry checks
  - row/coverage counts
  - pass/fail status
- Treat warnings (for example geometry validity sample counts) as explicit report fields.

## 6) Communication Protocol
- Before coding each step, restate:
  - target step scope
  - required inputs
  - expected outputs
  - blocking assumptions
- After execution, report:
  - produced artifacts
  - key row counts/coverage
  - pass/fail status
  - any warnings and next mitigation action
