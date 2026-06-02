# Bivariate Choropleth Decisions

## Decision BV-001: Default bin scheme
- Question: Which bivariate grid should be the default library standard?
- Answer: Use a 3x3 quantile scheme by default because it balances interpretability and signal.
- Status: Decided
- Date: 2026-04-14

## Decision BV-002: First-pass small-area stress geography
- Question: What geography should the first bivariate implementation use for the ZCTA stress-zone question before ZCTA geometry is available?
- Answer: Use Atlanta tract geometry as the reviewable small-area proxy, following the choropleth local-outlier precedent, then swap the sample query to ZCTA once a ZCTA geometry layer is materialized.
- Status: Decided
- Date: 2026-04-16
