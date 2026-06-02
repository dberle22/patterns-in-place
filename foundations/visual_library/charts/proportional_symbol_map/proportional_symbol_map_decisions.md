# Proportional Symbol Map Decisions

## Decision PS-001: Size scaling rule
- Question: What size-scaling strategy should the shared implementation use by default?
- Answer: Map symbol radius using a perceptual square-root size relationship and keep Top N filtering as the default clutter-control option for broad views.
- Status: Decided
- Date: 2026-04-14

## Decision PS-002: ZCTA coordinates before ZCTA geometry
- Question: How should the largest-ZCTA local sample render before a dedicated ZCTA geometry layer is available?
- Answer: Use tract-weighted ZCTA coordinates from `silver.xwalk_zcta_tract` and `foundation.market_tract_geometry`, and disclose the approximation in the caption and review notes.
- Status: Decided
- Date: 2026-04-16

## Decision PS-003: Retail parcel cluster sample before parcel clusters are DuckDB-backed
- Question: How should the retail parcel cluster canonical question be represented while parcel-level retail clusters are not materialized in DuckDB?
- Answer: Use high-scoring Jacksonville target-zone tracts from `foundation.tract_features` as a reviewable proxy and label the output as a proxy in the title, caption, and QA notes.
- Status: Decided
- Date: 2026-04-16

## Decision PS-004: Label policy for bubble maps
- Question: How should labels behave when highlighted bubbles are numerous?
- Answer: Shared prep supports a `label_strategy`; broad or dense maps should use top-ranked labels only, while highlights can remain a color/outline treatment without forcing every highlighted bubble to label.
- Status: Decided
- Date: 2026-04-16
