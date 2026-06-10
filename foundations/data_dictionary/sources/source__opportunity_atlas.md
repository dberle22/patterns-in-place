# Source Spec: Opportunity Atlas

## 1. Overview

- Source: Opportunity Insights Opportunity Atlas downloadable county datasets
- Upstream host: Opportunity Insights data library
- Access pattern: public downloadable Excel / Stata / README bundles plus some direct CSV assets; no API key required
- Native geographies available: census tract, county, commuting zone, national, plus supporting crosswalk and covariate files
- Foundations scope for Track 14: county-first intergenerational mobility metrics, with careful pruning because the full source catalog is much broader than what Foundations needs
- Documentation goal: review the county-grain options, recommend what is actually worth ingesting, and document why several available files should stay out of the first pass

The Opportunity Atlas family contains both very high-value mobility outcomes and a large amount of supporting covariate material that mostly duplicates sources we already have or plan to ingest elsewhere. The right Track 14 move is selective ingestion, not wholesale ingestion of every county file on the page.

---

## 2. Coverage Matrix

| County dataset on the Opportunity Atlas page | Role for Foundations | Recommendation |
| --- | --- | --- |
| All Outcomes by County, Race, Gender and Parental Income Percentile | Primary county mobility outcome file | Recommended first-pass source |
| Household Income and Incarceration for Children from Low-Income Households by County, Race, and Gender | Smaller, more targeted alternative focused on low-income children | Good fallback or later add-on |
| Neighborhood Characteristics by County | County covariates used in the paper and atlas | Do not ingest in first pass |
| Crosswalk Between Income/Wage Percentiles and 2015 Dollars | Supporting lookup for translating percentile-rank concepts | Optional helper only |

### Why this split matters

- The county all-outcomes file is the uniquely valuable part of the Opportunity Atlas for Foundations because it measures intergenerational outcomes we do not already have elsewhere.
- The county neighborhood covariates file is mostly composed of ACS, Census, HUD-rent, BLS, and SEDA-style variables that overlap with current or planned platform sources.
- The low-income county file is attractive because it is conceptually closer to the editorial question "what happens to children from low-income households here?", but it is narrower than the all-outcomes file.

---

## 3. Source Contract

- Provider: Opportunity Insights
- Main data-library page for the Opportunity Atlas:
  `https://opportunityinsights.org/data/?geographic_level=0&topic=0&paper_id=1652#resource-listing`
- County all-outcomes documentation:
  - page listing: "All Outcomes by County, Race, Gender and Parental Income Percentile"
  - codebook / README PDF: `https://opportunityinsights.org/wp-content/uploads/2019/07/Codebook-for-Table-5.pdf`
- County neighborhood-covariates documentation:
  - page listing: "Neighborhood Characteristics by County"
  - direct CSV observed during research: `https://opportunityinsights.org/wp-content/uploads/2018/12/cty_covariates.csv`
  - codebook / README PDF: `https://opportunityinsights.org/wp-content/uploads/2019/07/Codebook-for-Table-10.pdf`
- Authentication: none
- Cohort note: the county all-outcomes codebook states the estimates cover children born between `1978` and `1983`

### What we confirmed

- The Opportunity Atlas county all-outcomes file is organized one row per county and wide on race, gender, and parental-income percentile.
- The county neighborhood covariates file is a separate county-level table built from public data sources and used as supporting explanatory variables in the paper.
- The Opportunity Atlas data page exposes additional county downloads beyond these two, but the first-pass county mobility use case does not need all of them.

### Important limitation from this research pass

The live data-library page clearly exposes the county all-outcomes download bundle, but the raw asset URL for the county workbook was not directly surfaced by the tooling during this pass. The listing page and the official codebook are confirmed; when we implement `14.2`, we should capture the exact workbook URL in the staging script comments or `SOURCES.md`.

---

## 4. Staging Shape

### Recommended first-pass staging table

`staging.opportunity_insights_opportunity_atlas`

- one row per county FIPS
- source family: county all-outcomes file
- preserve the published wide layout in staging
- keep race / gender / parental-percentile suffixes exactly enough to trace back to the source

### Optional support table

`staging.opportunity_atlas_income_percentile_crosswalk`

- only needed if we choose to translate percentile-rank outputs into approximate 2015-dollar income values

### Not recommended for first-pass staging

`Neighborhood Characteristics by County` should not become a modeled Track 14 staging family unless we explicitly decide we want a staging-only research appendix. It adds width but very little new information relative to existing or planned Foundations sources.

---

## 5. Staging To Silver

### Recommended first-pass Silver scope

First-pass modeled output:
- `silver.opportunity_insights_opportunity_atlas`
- county rows from the all-outcomes county file
- derived CBSA rows built from county staging

### Recommended first-pass keep set

Keep a very small subset from the county all-outcomes file:

| Silver column | Source concept | Why keep it |
| --- | --- | --- |
| `geo_level` | derived | `county` or derived `cbsa` |
| `geo_id` | county / CBSA code | Canonical geography key |
| `geo_name` | county or CBSA name | Display field |
| `adult_household_income_rank_p25_parent` | `kfr_pooled_pooled_p25` | Core "where do children from lower-income families land?" metric |
| `adult_household_income_rank_p75_parent` | `kfr_pooled_pooled_p75` | Contrast point for local mobility slope |
| `upward_mobility_top20_from_p25` | `kfr_top20_pooled_pooled_p25` | Clean, interpretable upward-mobility probability |
| `adult_individual_income_rank_p25_parent` | `kir_pooled_pooled_p25` | Optional companion to household-income rank |
| `children_below_median_count` | `kid_pooled_pooled_blw_p50_n` | Best weighting field named by the codebook for place comparisons |

### Why this is the recommended subset

- These metrics are the distinctive value of the Opportunity Atlas for Foundations.
- They answer the central place-based opportunity question without dragging in hundreds of race/gender/percentile permutations on day one.
- They stay aligned with the completion plan's intended use: intergenerational mobility at county/CBSA grain.

### Additional option if we want a richer first pass

Add a second Silver family later for stratified metrics:
- Black / white pooled-gender mobility
- male / female pooled-race mobility
- selected education and incarceration outcomes for low-income children

That is a legitimate phase-two expansion, but it should not block the simpler first pass.

---

## 6. Transformation Notes

- Treat `state` and `county` as zero-padded text and combine them to a 5-digit county FIPS key.
- The county all-outcomes file is wide and suffix-heavy:
  - `[outcome]_[race]_[gender]_p[pctile]`
  - `[outcome]_[race]_[gender]_mean`
  - `[outcome]_[race]_[gender]_n`
- That argues for source-faithful wide staging and deliberate pruning in Silver rather than trying to pivot everything immediately.
- `kfr_*` variables are household-income-rank outcomes.
- `kir_*` variables are individual-income-rank outcomes.
- `kfr_top20_*` is the most straightforward upward-mobility probability in the file.
- The codebook identifies `kid_[race]_[gender]_blw_p50_n` as the preferred population-weighting variable for cross-place analysis; that is more defensible than using raw county population when rolling to CBSA.

### Why we should not ingest the county neighborhood covariates in Track 14 first pass

The neighborhood-covariates file overlaps heavily with existing or planned platform sources:
- `frac_coll_plus*`, `foreign_share2010`, `poor_share*`, `share_*`, `singleparent_share*`, `traveltime15_2010` overlap with ACS
- `rent_twobed2015` overlaps with HUD / ACS housing measures
- `ann_avg_job_growth_2004_2013` and `emp2000` overlap with BLS / BEA labor-market context
- `gsmn_math_g3_2013` overlaps conceptually with SEDA / K-12 education datasets already on the roadmap

That file is excellent for paper replication, but weak for incremental platform value.

---

## 7. Data Quality Expectations

- The county all-outcomes estimates include privacy-protecting noise, and the published standard errors incorporate both sampling error and the added noise.
- The county all-outcomes file is built around children born from 1978 to 1983, so it is a long-run cohort outcome source, not a current annual mobility feed.
- The county neighborhood covariates file mixes vintages such as 1990, 2000, 2010, 2013, 2015, and 2016. That makes it awkward as a clean ongoing Foundations mart even before considering overlap.
- Race / gender slices can be sparse for some counties. That is another reason to start with pooled metrics rather than carrying the entire stratified surface immediately.

---

## 8. Operational Notes

- The first-pass ingest should use the county all-outcomes file, not the county covariates file.
- Keep the county covariates file documented here as intentionally rejected for first-pass ingestion, because it will come up again and the overlap rationale is worth preserving.
- If we later want dollar-denominated mobility outputs, use the published percentile-to-2015-dollars crosswalk as a helper table rather than baking an opaque conversion into Silver.
- Track 14 should stay county-first. The tract-level Opportunity Atlas release is rich, but it is substantially larger and would push us into a different product surface than the current county/CBSA roadmap.

---

## 9. Known Gaps

- The exact raw workbook URL for the county all-outcomes asset still needs to be captured during implementation, even though the data-library listing and official codebook are confirmed.
- We have not yet chosen whether Track 14 should stay pooled-only in Silver or preserve a second stratified output for race and gender slices.
- The completion-plan shorthand names `p25_household_income` and `p75_household_income` should probably be revised during implementation to make clear that the direct source variables are income ranks, not literal household-income dollars.
- The low-income county file may still be worth a later add-on if we want a more editorially direct "children from low-income households" view rather than percentile-based mobility curves.

---

## 10. Recommended Ingestion Decision

### Recommended now

Ingest only the county all-outcomes file from the Opportunity Atlas family, and keep the first Silver contract intentionally compact:
- `kfr_pooled_pooled_p25`
- `kfr_pooled_pooled_p75`
- `kfr_top20_pooled_pooled_p25`
- optionally `kir_pooled_pooled_p25`
- plus the weighting field `kid_pooled_pooled_blw_p50_n`

### Reasoning

- These are genuinely additive to Foundations. They measure intergenerational mobility directly rather than proxied current conditions.
- They are the cleanest fit for the county/CBSA roadmap.
- They avoid ingesting a very wide research file only to use a tiny portion of it downstream.

### Defer

- `Neighborhood Characteristics by County`
- the tract-level Opportunity Atlas files
- the full race/gender/percentile surface

### Reasoning for deferral

- County covariates mostly duplicate other source families.
- Tract files are valuable but belong to a later neighborhood-focused phase.
- Full stratified county mobility is analytically interesting, but it would add a lot of width and QA work before we know whether products need it.

---

## 11. Source References

- Opportunity Atlas data-library page:
  `https://opportunityinsights.org/data/?geographic_level=0&topic=0&paper_id=1652#resource-listing`
- County all-outcomes codebook:
  `https://opportunityinsights.org/wp-content/uploads/2019/07/Codebook-for-Table-5.pdf`
- County covariates CSV:
  `https://opportunityinsights.org/wp-content/uploads/2018/12/cty_covariates.csv`
- County covariates codebook:
  `https://opportunityinsights.org/wp-content/uploads/2019/07/Codebook-for-Table-10.pdf`
