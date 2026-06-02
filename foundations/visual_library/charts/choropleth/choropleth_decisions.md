# Choropleth Decisions

## Decision C-001: Smoke-test rendering
- Question: How should map smoke tests behave before production geometry inputs are wired into gold-backed builds?
- Answer: Allow placeholder diagnostic renders in smoke-test mode and document the geometry dependency explicitly in chart QA notes.
- Status: Decided
- Date: 2026-04-14

## Decision C-002: First-pass local outlier geography
- Question: What geography should the first choropleth implementation use for the within-market affordability outlier question before ZCTA geometry is added?
- Answer: Use tract geometry for the first validated render set, then swap the local outlier sample to ZCTA once a reviewable ZCTA geometry layer exists.
- Status: Decided
- Date: 2026-04-15
