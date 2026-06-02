# Highlight + Context Map Decisions

## Decision HM-001: Default context rule
- Question: What should the default context set be when adjacency logic is not yet available?
- Answer: Default to the full filtered geography universe with a single highlighted target, and add explicit neighbor-ring logic when geometry support is available.
- Status: Decided
- Date: 2026-04-14

## Decision HM-002: Local outlier proxy geography
- Question: What geography should the first highlight-plus-local-outlier implementation use before a reviewable ZCTA geometry layer is available?
- Answer: Use tract geometry as the local proxy for the Atlanta affordability outlier sample and keep the proxy explicit in the sample runner, captions, and review notes until ZCTA geometry is added.
- Status: Decided
- Date: 2026-04-15
