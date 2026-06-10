# Data Dictionary: gold.social_fabric_wide

## Overview
- **Table**: `gold.social_fabric_wide`
- **Purpose**: Dedicated static social-fabric baseline mart for Opportunity Insights Social Capital Atlas metrics plus IRS EO BMF nonprofit-density enrichment.
- **KPI applicability**: decision-ready connectedness, cohesion, civic-engagement, and nonprofit-density geography surface for county, state, CBSA, and ZCTA analysis.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id`.
- **Primary key candidate**: (`geo_level`, `geo_id`)
- **Current scope**:
  - `geo_level = county`, `state`, `cbsa`, `zcta`
  - static baseline, not a recurring annual panel

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`
- **Context fields**: `population_total`, `children_below_p50`
- **Connectedness**: `economic_connectedness`, `childhood_economic_connectedness`, `neighborhood_economic_connectedness`
- **Connectedness decomposition**: `economic_exposure`, `childhood_economic_exposure`, `neighborhood_economic_exposure`, `friending_bias`, `childhood_friending_bias`, `neighborhood_friending_bias`
- **Cohesion**: `cohesion_clustering`, `cohesion_support_ratio`
- **Civic engagement**: `civic_engagement_volunteering_rate`, `civic_organizations_per_1000`
- **IRS nonprofit density**: `irs_bmf_snapshot_date`, `irs_bmf_population_year`, `nonprofit_org_count_est`, `nonprofit_org_count_nonreligious_est`, `nonprofits_per_100k`, `nonprofits_total_per_100k`, `nonprofit_source_zip5_count`, `nonprofit_weight_method`

## Data Quality Notes
- This table is intentionally separate from the recurring fact marts because the Social Capital Atlas is a static snapshot source.
- County, state, and CBSA rows all come from the county metric family.
- ZCTA rows come from the ZIP metric family and therefore carry the neighborhood-only fields that do not exist on county-based rows.
- State and CBSA values are population-weighted county rollups from Silver.
- IRS EO BMF enriches only county and CBSA rows.
  - State and ZCTA rows intentionally remain null for the nonprofit-density columns.
  - The nonprofit counts are modeled from ZIP5 first, then allocated to county using the HUD ZIP-county relationship file.

## Lineage
1. `foundations/etl/staging/get_opportunity_insights_social_capital.R` downloads the public county and ZIP Social Capital Atlas files.
2. `foundations/etl/silver/opportunity_insights_social_capital_silver.R` standardizes source-native rows and derives state and CBSA rollups.
3. `foundations/etl/staging/get_irs_bmf.R` downloads the latest IRS EO BMF regional files and lands the active U.S. staging snapshot.
4. `foundations/etl/silver/irs_bmf_silver.R` aggregates EO BMF organizations to ZIP5, allocates ZIP counts to county, and derives county / CBSA nonprofit-density metrics.
5. `foundations/etl/gold/gold_social_fabric_wide.sql` promotes the curated static social-fabric metric set and left-joins the IRS nonprofit-density enrichment into `gold.social_fabric_wide`.

## Known Gaps / To-Dos
- Opportunity Atlas is still pending and is not yet part of this Gold theme.
- If a future product needs a stricter county/CBSA/state-only surface, this table can be subset further without changing the underlying Silver contract.
- IRS EO BMF remains a latest-snapshot enrichment, not a historical panel inside this Gold mart.
