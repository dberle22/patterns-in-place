# Data Dictionary: silver.opportunity_insights_social_capital

## Overview
- **Table**: `silver.opportunity_insights_social_capital`
- **Purpose**: Canonical static Social Capital Atlas table covering source-native county and ZCTA rows plus derived state and CBSA rollups.
- **KPI applicability**: reusable social-fabric baseline for connectedness, cohesiveness, and civic-engagement analysis.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id`.
- **Primary key candidate**: (`geo_level`, `geo_id`)
- **Current scope**:
  - `geo_level = county`, `state`, `cbsa`, `zcta`
  - static 2022 public-release snapshot

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`
- **Context fields**: `population_total`, `children_below_p50`
- **Current-place connectedness**: `economic_connectedness`, `economic_connectedness_se`
- **Childhood connectedness**: `childhood_economic_connectedness`, `childhood_economic_connectedness_se`
- **Neighborhood connectedness**: `neighborhood_economic_connectedness`
- **Connectedness decomposition**: `economic_exposure`, `childhood_economic_exposure`, `neighborhood_economic_exposure`, `friending_bias`, `childhood_friending_bias`, `neighborhood_friending_bias`
- **Cohesion**: `cohesion_clustering`, `cohesion_support_ratio`
- **Civic engagement**: `civic_engagement_volunteering_rate`, `civic_organizations_per_1000`

## Data Quality Notes
- County rows come directly from the county release and ZCTA rows come directly from the ZIP release.
- State and CBSA rows are derived only from county rows, which avoids forcing ZIP geography onto non-unique county and CBSA relationships.
- Provider-published standard errors are preserved only on source-native rows.
  - They are intentionally null on state and CBSA rollups because those do not aggregate cleanly.
- ZCTA rows do not carry the childhood-place measures because the ZIP release does not publish them.
- Three ZIP rows in staging have null county identifiers in the public source, but that does not block this Silver contract because ZCTA rows stay source-native and state / CBSA rollups are derived from counties instead.

## Lineage
1. `foundations/etl/staging/get_opportunity_insights_social_capital.R` downloads the public county and ZIP CSVs and writes the separate staging tables.
2. `foundations/etl/silver/opportunity_insights_social_capital_silver.R` standardizes the source-native rows, derives state and CBSA rollups from counties with population-weighted averages, and writes `silver.opportunity_insights_social_capital`.

## Known Gaps / To-Dos
- This first Silver contract intentionally excludes the high-SES helper variants from the public release.
- If Opportunity Insights publishes a newer release later, this table should be refreshed as a new static snapshot rather than assumed to be part of an annual panel.
- Opportunity Atlas remains a separate Track 14 source family and is not yet modeled in Silver.
