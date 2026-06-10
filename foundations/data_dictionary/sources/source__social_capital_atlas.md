# Source Spec: Social Capital Atlas

## 1. Overview

- Source: Opportunity Insights Social Capital Atlas public release
- Upstream host: Opportunity Insights data library, with public CSVs hosted via HDX / Humdata
- Access pattern: public bulk CSV download plus a published PDF codebook; no API key required
- Native geographies available: county, ZIP code, high school, college, plus a separate SES friending matrix
- Foundations scope for Track 14: county and ZIP/ZCTA ingest for national social capital coverage, with county-derived state and CBSA rollups in Silver
- Documentation goal: pin the county and ZIP file layouts, identify the approved modeled keep set, and document why the county and ZIP slices should land as separate source-faithful staging tables

This source replaces the older JEC social capital concept in the completion plan. It is materially better aligned to the platform because it offers decomposed measures rather than a single composite score: economic connectedness, cohesiveness, and civic engagement, with exposure and friending-bias helpers available in the same release.

---

## 2. Coverage Matrix

| Release slice | Native grain | Recommended staging contract | Recommended Silver path | Status |
| --- | --- | --- | --- | --- |
| Social Capital Data by County | County | `staging.opportunity_insights_social_capital_county` | `silver.opportunity_insights_social_capital` | In scope |
| Social Capital Data by ZIP Code | ZIP code / ZCTA-style 5-digit geography | `staging.opportunity_insights_social_capital_zip` | `silver.opportunity_insights_social_capital` | In scope |
| Social Capital Data by High School | High school | None for Track 14 | None | Out of scope |
| Social Capital Data by College | College | None for Track 14 | None | Out of scope |
| 100 by 100 Matrix of Friending Rates by SES | SES-pair matrix | None for Track 14 | None | Out of scope |

County remains the canonical rollup surface for Track 14 because:
- it matches the current state and CBSA rollup pattern
- the county file includes the childhood-place measures that do not exist in the ZIP release
- county-to-state and county-to-CBSA rollups are straightforward
- ZIP coverage is intentionally incomplete because small cells are suppressed for privacy, so ZIP is modeled as a source-native companion slice rather than the rollup backbone

---

## 3. Source Contract

- Provider: Opportunity Insights
- Research pages:
  - `https://opportunityinsights.org/data/?geographic_level=0&paper_id=3978&topic=0`
  - `https://socialcapital.org/`
- County CSV:
  - `https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/ec896b64-c922-4737-b759-e4bd7f73b8cc/download/social_capital_county.csv`
- ZIP CSV:
  - `https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/ab878625-279b-4bef-a2b3-c132168d536e/download/social_capital_zip.csv`
- Public codebook / README:
  - `https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/fbe5b0b9-e81c-41c7-a9f2-3ebf8212cf64/download/data_release_readme_31_07_2022_nomatrix.pdf`
- Authentication: none
- Release vintage: public data release dated `July 2022`
- Source population note: measures are derived from Facebook social-network data with privacy protection and small-cell suppression; `pop2018` and `num_below_p50` are external context variables, not Facebook-native counts

### County columns confirmed from the public CSV and codebook

| Column | Meaning |
| --- | --- |
| `county` | 5-digit county FIPS |
| `county_name` | County and state display name |
| `num_below_p50` | Number of children with below-national-median parental income |
| `pop2018` | 2018 ACS population |
| `ec_county` | Baseline economic connectedness |
| `ec_se_county` | Standard error for economic connectedness |
| `child_ec_county` | Childhood economic connectedness, assigned by high-school county |
| `child_ec_se_county` | Standard error for childhood economic connectedness |
| `ec_grp_mem_county` | Economic connectedness restricted to allocable group-member friendships |
| `ec_high_county` | Economic connectedness among high-SES individuals |
| `ec_high_se_county` | Standard error for `ec_high_county` |
| `child_high_ec_county` | Childhood high-SES economic connectedness |
| `child_high_ec_se_county` | Standard error for `child_high_ec_county` |
| `ec_grp_mem_high_county` | Group-member connectedness among high-SES individuals |
| `exposure_grp_mem_county` | Exposure to high-SES peers in groups, low-SES focus |
| `exposure_grp_mem_high_county` | Exposure to high-SES peers in groups, high-SES focus |
| `child_exposure_county` | Childhood exposure to high-parental-SES peers |
| `child_high_exposure_county` | Childhood exposure for high-parental-SES children |
| `bias_grp_mem_county` | Friending bias estimate for low-SES individuals |
| `bias_grp_mem_high_county` | Friending bias estimate for high-SES individuals |
| `child_bias_county` | Childhood friending bias |
| `child_high_bias_county` | Childhood high-SES friending bias |
| `clustering_county` | Social-network clustering / clique density |
| `support_ratio_county` | Share of within-county friendships supported by a mutual friend |
| `volunteering_rate_county` | Share of Facebook users in volunteering/activism groups |
| `civic_organizations_county` | Public-good Facebook pages per 1,000 users |

### ZIP columns confirmed from the public CSV and codebook

The ZIP release mirrors the county file conceptually but uses ZIP-specific fields such as `nbhd_ec_zip`, `nbhd_exposure_zip`, `nbhd_bias_zip`, and `nbhd_bias_high_zip`. Those neighborhood-only fields are useful, but they make the ZIP schema materially different from the county schema. That is the main reason to keep county and ZIP as separate staging families if we ingest both.

---

## 4. Staging Shape

### County staging table

`staging.opportunity_insights_social_capital_county`

- one row per county FIPS
- keep the published county columns with light normalization only:
  - snake_case stays aligned to source names
  - `county` is zero-padded text
  - numeric metrics stay numeric
- no attempt to recompute or denoise provider statistics

### ZIP staging table

`staging.opportunity_insights_social_capital_zip`

- one row per ZIP / ZCTA-style 5-digit code published by Opportunity Insights
- should remain a separate staging table because ZIP includes `nbhd_*` fields that do not exist in the county file

### Why keep the staging layer source-faithful

- The county file is already compact, so the simplest safe choice is to preserve all published columns.
- Several fields that are probably staging-only for Silver, such as `child_*`, `*_se_*`, and `*_high_*`, are still valuable QA and future-modeling context.
- The provider applies privacy noise and minimum-cell suppression upstream; staging should preserve those released values rather than trying to smooth or fill them.

---

## 5. Staging To Silver

### Recommended first-pass Silver scope

First-pass modeled output:
- `silver.opportunity_insights_social_capital`
- county rows from the county release
- derived state and CBSA rows built from county staging
- source-native ZCTA rows from the ZIP release

### Recommended first-pass keep set

| Silver column | Source column | Why keep it |
| --- | --- | --- |
| `geo_level` | derived | `county`, `state`, `cbsa`, or `zcta` |
| `geo_id` | canonical geo key | County FIPS, state FIPS, CBSA code, or ZCTA code |
| `geo_name` | geography display name | Display field |
| `economic_connectedness` | `ec_county` | Primary social-capital headline metric |
| `economic_connectedness_se` | `ec_se_county` | Keep on source-native county and ZCTA rows; null on derived rollups |
| `childhood_economic_connectedness` | `child_ec_county` | Useful county-based childhood-place companion metric |
| `neighborhood_economic_connectedness` | `nbhd_ec_zip` | Useful ZIP/ZCTA neighborhood-place companion metric |
| `economic_exposure` | `exposure_grp_mem_county` / `exposure_grp_mem_zip` | Main connectedness decomposition helper |
| `childhood_economic_exposure` | `child_exposure_county` | Childhood decomposition companion metric |
| `neighborhood_economic_exposure` | `nbhd_exposure_zip` | ZIP/ZCTA neighborhood decomposition metric |
| `friending_bias` | `bias_grp_mem_county` / `bias_grp_mem_zip` | Main connectedness decomposition helper |
| `childhood_friending_bias` | `child_bias_county` | Childhood decomposition companion metric |
| `neighborhood_friending_bias` | `nbhd_bias_zip` | ZIP/ZCTA neighborhood decomposition metric |
| `cohesion_clustering` | `clustering_county` | Core cohesiveness measure |
| `cohesion_support_ratio` | `support_ratio_county` | Second cohesiveness measure with different interpretation |
| `civic_engagement_volunteering_rate` | `volunteering_rate_county` | Civic engagement participation signal |
| `civic_organizations_per_1000` | `civic_organizations_county` | Civic infrastructure density signal |
| `population` | `pop2018` | Rollup weight and QA denominator |
| `children_below_p50` | `num_below_p50` | Helpful weighting / context field |

### Staging-only in the first pass

These fields are useful, but they should stay in staging unless we explicitly decide we need them in Silver:
- high-SES variants: `ec_high_*`, `child_high_*`, `nbhd_ec_high_zip`
- high-SES decomposition helpers: `exposure_grp_mem_high_*`, `bias_grp_mem_high_*`, `nbhd_bias_high_zip`

The reason is simplicity: the first modeled contract should normalize the main connectedness, decomposition, cohesion, and civic-engagement fields without turning Silver into a full research replication package.

---

## 6. Transformation Notes

- Treat county FIPS and ZIP codes as text immediately to preserve leading zeros.
- The county file and ZIP file should not be forced into one shared staging schema; the ZIP release adds neighborhood-only variables that are absent at county level.
- The codebook makes a key semantic distinction between:
  - current-place measures such as `ec_county`
  - childhood-place measures such as `child_ec_county`, which are assigned using high-school county
- That distinction matters for Foundations. The current plan wants place-level social-fabric indicators, so the current-place measures are the cleanest first-pass Silver contract.
- County-to-state and county-to-CBSA rollups should use `pop2018` as the default weight for rate-like or mean-like measures.
- `civic_organizations_county` is already standardized per 1,000 users, so CBSA rollups should be weighted means rather than summed counts.
- Provider-published standard errors should not be recomputed for derived state and CBSA rows. Keep them on source-native rows and leave them null on rollups.

---

## 6.1 Gold Placement Decision

- Gold destination: `gold.social_fabric_wide`
- Reasoning: this source is a static research baseline, not a recurring annual panel, so it should live in its own dedicated Gold mart instead of extending the general time-series fact tables such as `gold.health_wide`.
- Gold shape: one row per `geo_level + geo_id`, carrying the curated connectedness, cohesion, and civic-engagement fields for county, state, CBSA, and ZCTA analysis.

---

## 7. Data Quality Expectations

- The provider adds privacy-protecting noise and suppresses small cells. The public release is intentionally not an exact replication of the paper tables.
- County coverage is nearly complete, but the public codebook notes that 7 counties are excluded because of release restrictions.
- ZIP coverage is much more incomplete. The codebook notes that 6,034 ZIPs are excluded from the public release because of privacy thresholds.
- `volunteering_rate_*` and `civic_organizations_*` reflect Facebook-group and Facebook-page proxies, not direct IRS nonprofit registrations or government administrative counts.
- `pop2018` and `num_below_p50` come from external public data and may not line up exactly with other Foundations denominator choices.

---

## 8. Operational Notes

- Prefer the bulk CSVs over any programmatic API path. The CSV + PDF codebook path is simpler, public, and stable enough for Foundations.
- The live Track 14 implementation now carries both county and ZIP releases.
  - County remains the rollup backbone for state and CBSA.
  - ZIP/ZCTA remains a source-native geography slice with neighborhood-only metrics.
- The published README PDF is important enough to keep linked in the source spec because field names like `support_ratio_county` and `bias_grp_mem_county` are not self-explanatory from headers alone.
- This source has no annual refresh cadence in the way ACS or BLS do. It should be treated as a static research release unless Opportunity Insights publishes a new version.

---

## 9. Known Gaps

- We have not yet confirmed a newer public release after the July 2022 public data package.
- High school and college remain intentionally deferred.
- The source is a proxy for social capital based on one platform’s social graph. It is analytically valuable, but it should not be described as a direct administrative measure of civic life.
- The current Silver contract already keeps ZIP/ZCTA in the same table as county/state/CBSA rows, with the neighborhood-only ZIP fields left null outside the ZCTA slice.

---

## 10. Source References

- Opportunity Insights data library listing for Social Capital I:
  `https://opportunityinsights.org/data/?geographic_level=0&paper_id=3978&topic=0`
- Social Capital Atlas site:
  `https://socialcapital.org/`
- County CSV:
  `https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/ec896b64-c922-4737-b759-e4bd7f73b8cc/download/social_capital_county.csv`
- ZIP CSV:
  `https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/ab878625-279b-4bef-a2b3-c132168d536e/download/social_capital_zip.csv`
- Public codebook:
  `https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/fbe5b0b9-e81c-41c7-a9f2-3ebf8212cf64/download/data_release_readme_31_07_2022_nomatrix.pdf`
