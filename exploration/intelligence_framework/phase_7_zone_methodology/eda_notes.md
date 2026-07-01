# EDA Notes

This doc stores notes on our EDA. These notes come from analyzing and reviewing our EDA app.

## Table Structure

### Benchmarks and examples

- Intended contract in Phase 7 docs: all tracts in the `396` non-Puerto-Rico CBSAs
- Current live table: `78,199` tracts across `925` CBSAs
- Current `silver.xwalk_cbsa_county` breadth: `935` distinct CBSAs

Example read:

- If the tract frame were truly limited to the Phase 7 modeling universe, we would expect the CBSA count to line up with the repeated `396`-CBSA language in the methodology docs.
- Instead, the current table is much closer to "all tracts whose counties map to any CBSA in the crosswalk."

We've created a single table to load with all tracts. We have confirmed that it is tracts from all CBSAs, which is the correct behavior.

### Response

We now have a concrete answer:

- the current app table is not all U.S. tracts
- it is also not currently limited to the intended `396`-CBSA Phase 7 universe
- it is pulling tracts whose counties map into the broader `silver.xwalk_cbsa_county` surface, which currently contains `935` CBSAs, and the resulting table materializes `925` CBSAs

The important distinction is:

- the docs say one thing
- the current SQL implementation does another

### Where the docs say `396`

The `396`-CBSA limit is written in multiple Phase 7 docs:

- [exploration/intelligence_framework/docs/zone_methodology_notes.md](exploration/intelligence_framework/docs/zone_methodology_notes.md): "a consistent label set assigned to every tract in the 396-CBSA universe" and "Universe: all tracts in the 396 non-Puerto-Rico CBSAs"
- [exploration/intelligence_framework/docs/phase7_eda_plan.md](exploration/intelligence_framework/docs/phase7_eda_plan.md): "filtered to the 396-CBSA universe via `silver.xwalk_tract_county` → `silver.xwalk_cbsa_county`"
- [exploration/intelligence_framework/phase_7_zone_methodology/PHASE7_PLAN.md](exploration/intelligence_framework/phase_7_zone_methodology/PHASE7_PLAN.md): "every tract in the 396-CBSA universe gets a nationally consistent label" and "Filter to tracts in the 396 non-PR CBSAs"

### What the current SQL actually does

[foundations/etl/gold/gold_intelligence_zone_inputs.sql](foundations/etl/gold/gold_intelligence_zone_inputs.sql) does this in the `base` CTE:

- joins `silver.xwalk_tract_county` to `silver.xwalk_cbsa_county`
- keeps every tract whose county appears in the CBSA crosswalk
- does not apply any additional filter to reduce the universe to the intended `396`

So this is not a UI misunderstanding. It is a real contract mismatch between the docs and the current Gold build.

---

## Data Quality

### Benchmarks and examples

Coverage benchmark I would use for first-pass KPI triage:

- `0–1% missing`: effectively full coverage
- `1–5% missing`: mild gap, probably usable if the missingness pattern is explainable
- `5–20% missing`: caution zone, needs investigation before we trust the KPI for clustering
- `>20% missing`: likely exclusion, remap, or source redesign candidate
- `100% missing`: treat as broken, not merely sparse

Examples from the current live table after the latest fixes:

- effectively full: `fema_risk_score 0.03% missing`
- effectively full after year-slice fix: `ejs_pm25 0.71% missing`
- effectively full after tract overlap audit: `walkability_index 1.45% missing`, `jobs_access_45min_transit 1.45% missing`
- mild gap: `jobs_per_resident 3.85% missing`
- caution zone: `median_gross_rent 5.77% missing`
- severe before fallback: `pct_ba_plus_change_5yr 28.85% missing`
- broken before fixes: `ejs_pm25 100% missing`, `pov_rate_change_5yr 100% missing`
- current fallback direction: use tract-safe `3yr` change fields in Phase 7 now; keep `5yr` as the longer-term harmonization target

We've removed fixed issues.

### Root cause 3: `pct_ba_plus_change_5yr` is partially missing because of the real tract continuity gap

What we found in `gold.population_demographics` tract rows for `2024`:

- `60,177` non-null
- `24,224` null in the full tract table
- the app's current Phase 7 universe reports `22,561` missing because it is looking at the smaller app frame, not all `84k+` tract rows in the source table

Interpretation:

- this KPI uses the same basic five-year lag idea
- its implementation in `gold_population_wide.sql` partitions only by `geo_level, geo_id`
- it does **not** include `geo_name` in the lag partition

That implementation difference is the key reason it survives while `pov_rate_change_5yr` collapses.

What happens in practice:

- `silver.education_kpi` has the same `2019` to `2024` `geo_id` overlap count as income: `60,853`
- because the lag is partitioned only by `geo_id`, those overlapping tracts successfully recover a 5-year lag
- the remaining missing share is then mostly the genuine continuity gap for tracts that do not have a usable `2019` row under the same `geo_id`

So the diagnosis is:

- **not the same failure as poverty change**
- **works better because the lag partition ignores `geo_name`**
- **remaining missingness is the true tract-continuity problem**

### Root cause 5: the repeated `503`, `736`, `714`, and `637` patterns are mostly `NaN` values from zero denominators, not join failures

This was the most useful thing the deep dive surfaced.

For example:

- `diversity_index` missing in the app = `503`
  - only `14` are SQL `NULL`
  - `489` are `NaN`
- `owner_occ_rate` missing = `736`
  - `14` are SQL `NULL`
  - `722` are `NaN`
- `vacancy_rate` missing = `714`
  - `14` are SQL `NULL`
  - `700` are `NaN`
- `pct_commute_transit` missing = `637`
  - `14` are SQL `NULL`
  - `623` are `NaN`

And the denominator matches are strong:

- `489` `diversity_index` NaNs line up with `2024` tract rows where `pop_total = 0`
- `722` `owner_occ_rate` NaNs line up with `2024` tract rows where `tenure_total = 0`
- `623` transit-share NaNs line up with `2024` tract rows where `commute_workers_total = 0`

Interpretation:

- these are mostly structurally undefined ratios
- the app is correctly showing them as missing because Pandas treats `NaN` as missing
- SQL-only checks understate the problem because they catch `NULL` but not `NaN`

So the diagnosis is:

- **mostly zero-denominator `NaN` values**
- **not primarily broken joins**

### Root cause 6: the shared `14` null-join tracts are real and concentrated in one county

Across multiple Gold sources, the true join-miss count is `14` tracts.

Those `14` tracts are concentrated in:

- county `36103`
- CBSA `35620`

That means:

- there is a small but real geography-alignment problem affecting a narrow tract subset
- it is separate from the much larger `NaN` patterns above

So the diagnosis is:

- **small real tract-join miss in one county**

### Root cause 7: `median_gross_rent` is mostly a tract-level ACS sparsity issue, not a Phase 7 assembly bug

Current app missingness:

- `median_gross_rent`: `4,511` missing out of `78,199` tracts, or `5.77%`

What the live table shows:

- the nulls already exist upstream in `gold.housing_core_wide`
- at full tract source level for `2024`, `gold.housing_core_wide` has `84,401` tract rows and `5,116` null `median_gross_rent` values
- so Phase 7 is not creating this problem; it is inheriting a source-side tract gap

The most important breakdown is by renter presence:

- `932` missing tracts have `0` renter-occupied units
- the other `3,579` missing tracts still have positive renter counts

That second bucket is the one worth interpreting carefully. For those `3,579` tracts with renters but no median rent:

- `3,579` have positive `rent_burden_total`
- `3,423` still have a non-null `pct_rent_burden_30plus`
- `3,432` still have a non-null `median_home_value`
- median renter count is only `53`

And the null rate falls sharply as renter counts rise:

- `1–4` renters: `100%` null
- `5–9` renters: `98.7%` null
- `10–19` renters: `91.8%` null
- `20–49` renters: `51.5%` null
- `50–99` renters: `17.1%` null
- `100–249` renters: `4.8%` null
- `250+` renters: `0.7%` null

Interpretation:

- this does not behave like a broken join
- it also does not behave like "there are no renters here" except for the smaller `932`-tract subset
- it behaves like tract-level ACS median-rent coverage getting weak in small-renter tracts

So the diagnosis is:

- **mostly a real tract-source limitation for the ACS median-rent field**
- **especially concentrated in low-renter tracts**
- **less concerning than a broken KPI, but still a real caution flag if we want median rent in the clustering vector**

Decision note for Phase 7:

- **Treat `median_gross_rent` as a cut candidate unless we decide it adds something we cannot get from the more stable affordability KPIs**

CBSA concentration check:

- the worst percentage-missing CBSAs are mostly very small metros, which makes those rates noisy
- examples: `Cañon City, CO 46.7%`, `Wildwood-The Villages, FL 39.3%`, `Hemlock Farms, PA 36.0%`
- the highest absolute null counts are in large metros, but that looks like a scale effect more than a one-market failure
- examples: `New York 415`, `Detroit 200`, `Chicago 140`, `Philadelphia 134`, `Atlanta 118`
- the top `10` CBSAs by null count account for only `1,474` of `4,511` missing tracts, or about `32.7%`

Interpretation:

- this does **not** look like the missing data is being driven by one specific broken CBSA
- it looks more like a broad tract-level sparsity pattern that shows up nationally, with extra fragility in small-renter tracts

### Tract SLD follow-up: the live overlap is much better than the old Phase 7 docs implied

What we found:

- `gold.transport_built_form_sld` now has `83,220` tract rows for `2021`
- backbone overlap is `83,220 / 84,121`, with `0` SLD tracts outside the backbone
- Phase 7 overlap is `77,300 / 78,199`
- non-null coverage on the current Phase 7 tract frame is `77,064 / 78,199` for both `walkability_index` and `jobs_access_45min_transit`

Missingness pattern:

- only `899` current Phase 7 tracts fail to join any tract SLD row
- `879` of those `899` misses are concentrated in Connecticut CBSAs
- top missing metros: Hartford `293`, Bridgeport `223`, New Haven `135`, Waterbury `98`, Norwich `67`

Interpretation:

- tract SLD is no longer a broad national tract-relationship problem
- it behaves more like a mostly solved tract baseline with one concentrated Connecticut geography issue
- that makes both SLD KPIs reasonable to add back into the exploratory Phase 7 KPI surface now, while still keeping Connecticut visible in the audit notes
- **large apparent gaps elsewhere are mostly source-value problems, not join absence**

### Additional note: `median_gross_rent` is a true source-null problem, not a `NaN` problem

What we found:

- `median_gross_rent` missing in the app: `4,511`
- those are SQL `NULL`s, not `NaN`s
- `silver.housing_kpi` itself has `5,116` tract rows in `2024` with null `median_gross_rent`

Interpretation:

- this gap is already present in the tract housing source
- it is not introduced by the Phase 7 Gold join

So the diagnosis is:

- **source-level tract rent estimate gap**

### What can vs cannot be resolved

#### Current Phase 7 direction

- Use `pov_rate_change_3yr` now
- Use `pct_ba_plus_change_3yr` now
- Keep a note that the longer-term fix is a harmonized `5yr` window on a common tract backbone

#### Summary triage

- **Fixed now:** `ejs_pm25`, tract momentum fallback to `3yr`, poverty partition bug
- **Still worth auditing:** the `14`-tract join miss
- **Fixed now for Phase 7 via fallback:** move both tract momentum fields to `3yr`, plus remove the poverty `geo_name` partition bug
- **Fixable but larger methodology work:** harmonized `5yr` tract momentum fields
- **Mostly treatment decisions rather than bugs:** `NaN` families from zero denominators, `median_gross_rent`
- **Mostly natural source limitation:** LODES trio

#### Completeness refresh after the current fixes

Current national tract frame: `78,199` rows across `925` CBSAs.

Best current coverage:

- `14` missing or fewer: most Character KPIs, `vacancy_rate`, `pct_hh_0_vehicles`, `pct_commute_walk`, `pct_commute_transit`, `pov_rate`
- `fema_risk_score`: `27` missing
- `ejs_pm25`: `554` missing after the year-selection fix

Still mild but acceptable for Phase 7 EDA:

- `pct_unemployment_rate`: `629` missing (`0.8%`)
- `pct_no_internet_access`: `736` missing (`0.9%`)
- `pct_rent_burden_30plus`: `1,088` missing (`1.4%`)
- `median_hh_income`: `1,160` missing (`1.5%`)
- `pct_ba_plus_change_3yr`: `1,445` missing (`1.8%`)
- `pov_rate_change_3yr`: `1,609` missing (`2.1%`)
- LODES trio: `3,013` missing each (`3.9%`)

Main caution item still visible:

- `median_gross_rent`: `4,511` missing (`5.8%`)

Interpretation:

- the two truly broken fields we were worried about are no longer broken in the live app table
- the remaining gaps are now mostly ordinary source sparsity, denominator suppression, or tract continuity limits rather than Phase 7 assembly bugs

---

## Distribution

### Benchmarks and examples

Useful first-pass histogram rules:

- `|skewness| < 0.5`: roughly symmetric
- `0.5–1.0`: moderate skew
- `1.0–1.5`: strong skew
- `> 1.5`: very strong skew, usually worth checking a log transform

Useful excess kurtosis rules:

- around `0`: tails roughly normal
- `1–3`: noticeably heavy-tailed
- `> 3`: strong outlier / extreme-tail behavior

Examples to expect in this app:

- likely high skew: `pop_weighted_density_sqmi`, `median_home_value`, `jobs_per_resident`
- likely lower skew: percentages with tighter natural bounds, like some commute shares or poverty-related rates

Let's define Skewness and Excess Kurtosis.

For the overlay single CBSA we should show the CBSA name, not the number. This will make it more readable for me.

When we select a CBSA we should also show the count of CBSAs there so we can easily understand that skew is due to a small amount of Tracts instead of a data problem.

### Notes:
- Racial KPIs are heavily skewed and have very high excess kurtosis.
- % Age 65+ has a very long right leaning tail.
- Pop Weighted Density has very high skew.
- Home Values and Vacancy Rates have a long right tail.
- % Commute by Walk and Public Transit is basically all grouped at a low end with a few outliers.
- We have a weird error on Median HH Income. It says we have duplicate columns, we will need to double check this.
- There are some bizarre negative values for Unemployment Rate that need to be fixed
- Jobs to Workers Ratio really doesn't have much, there are some extreme outliers.

There's a lot of KPIs with high skewness, I'm not sure how many of them will really have such a big impact. We for sure see some big issues with the Commuting rates being almost all 0 and then Unemployment Rates having strange negative values.


### Better explanation: skewness

Skewness tells us whether a distribution has a longer tail on one side than the other.

- Positive skew means a long right tail.
  Real-world example: home values. Most tracts may sit in a moderate range, but a smaller number of very expensive tracts pull the right tail out.
- Negative skew means a long left tail.
  Real-world example: a score where most tracts do fairly well but a smaller number of tracts do dramatically worse.
- Near-zero skew means the distribution is roughly balanced left vs right.
  Real-world example: a KPI where low and high deviations from the middle are about equally common.

How to think about it in this app:

- high positive skew often means a few tracts are much higher than the rest
- that is why variables like density, rent, home value, or jobs-per-resident often benefit from a log transform

Brief reminder text for the report:

> **Skewness:** shows whether the distribution leans left or right. Positive values mean a long right tail; negative values mean a long left tail.

### Better explanation: excess kurtosis

Excess kurtosis tells us how heavy the tails are compared with a normal distribution. In practice, it is mostly a clue about outliers and extreme values.

- Positive excess kurtosis means heavier tails than normal.
  Real-world example: a KPI where most tracts are ordinary, but a handful are extremely unusual, like a few tracts with exceptionally high job concentration or exceptionally high risk.
- Near-zero excess kurtosis means tail behavior is fairly normal.
- Negative excess kurtosis means lighter tails than normal.
  Real-world example: a KPI where values are tightly bounded and extreme outliers are rare.

How to think about it in this app:

- high excess kurtosis means "watch out, a few tracts may be dominating the visual story"
- it is less about the middle of the histogram and more about whether the distribution contains unusually extreme observations

Brief reminder text for the report:

> **Excess kurtosis:** shows how extreme the tails are relative to a normal distribution. Higher values mean more outliers or more extreme tract values.

### External links for learning

- NIST EDA Handbook, Measures of Skewness and Kurtosis: https://www.itl.nist.gov/div898/handbook/eda/section3/eda35b.htm
- Statistics By Jim, Spearman's Rank Correlation Coefficient: https://statisticsbyjim.com/glossary/spearmans-rank-correlation-coefficient/
- Wikipedia, Pearson correlation coefficient: https://en.wikipedia.org/wiki/Pearson_correlation_coefficient

These are useful for different purposes:

- NIST is the best practical reference for skewness and kurtosis definitions
- Statistics By Jim is the clearest plain-English explanation of Spearman for dashboard users
- The Pearson page is a solid refresher on what "linear relationship" means

---

## Correlation

### Benchmarks and examples

Practical first-pass correlation thresholds:

- `|r| < 0.30`: weak relationship
- `0.30–0.50`: moderate
- `0.50–0.75`: strong
- `> 0.75`: likely redundancy candidate

Example pairs worth checking:

- `pct_ba_plus` vs `median_hh_income`
- `pov_rate` vs `pct_rent_burden_30plus`
- `pct_commute_walk` vs `pct_commute_transit`

What's the difference between Pearson and Spearman?

### Notes:
**Pearson**
- Owner Occupancy Rate & % Multifamily Structures is too highly correlated.
- We should drop commute by transit since it's strogly correlated with % HH Zero Vehicles and Pop-Weighted Density
- We can drop Median Gross Rent because of it's relationship with Median Home Value and it having worse coverage

**Spearman**
- Median HH Income and Poverty Rate are highy inversely correlated.
- Rent and Home Values are strongly correlated
- Education and HH Income are highly correlated

There's a lot of pairs with strong to very strong correlation. We should review and knock off some.

### Response

Pearson and Spearman both measure association between two variables, but they answer slightly different questions.

### Pearson

Pearson asks: do these two KPIs move together in a linear way?

Real-world example:

- `pct_ba_plus` and `median_hh_income` might rise together in a roughly straight-line way across tracts
- if doubling one tends to line up with a fairly steady change in the other, Pearson is the natural read

Use Pearson when:

- you care about linear relationships
- you want the familiar straight-line correlation reading
- you are screening for tract KPIs that may be redundant in a linear modeling sense

### Spearman

Spearman asks: as one KPI gets higher, does the other generally get higher too, even if the relationship is curved or uneven?

Real-world example:

- `pop_weighted_density_sqmi` and `pct_commute_transit` may rise together in rank order, but not in a clean straight line
- dense tracts may generally have more transit commuting, even if the increase is nonlinear and noisy

Use Spearman when:

- you care about rank-order relationships
- the scatterplot may be curved rather than straight
- you want something less sensitive to extreme outliers

Brief reminder text for the report:

> **Pearson:** measures straight-line correlation between raw values.  
> **Spearman:** measures whether higher values of one KPI tend to line up with higher values of the other, even when the pattern is curved.

Practical read for this app:

- if Pearson and Spearman are both high, the relationship is strong and fairly clean
- if Spearman is high but Pearson is lower, the relationship is probably real but nonlinear
- if both are low, the KPI pair is probably not moving together much at tract grain

---

## Scatter

### Benchmarks and examples

Diagnostic examples for the scatter tab:

- expected positive: `pct_ba_plus` vs `median_hh_income`
- expected positive: `jobs_per_resident` vs `pct_commute_walk`
- expected positive: `pov_rate` vs `vacancy_rate`
- expected negative: `ejs_pm25` vs `median_home_value`

Interpretation benchmark:

- if the sign is opposite of expectation, check ETL, polarity assumptions, or whether the KPI behaves differently at tract grain than it did at CBSA grain
- if Pearson is low but Spearman is clearly positive or negative, the relationship may still be real but nonlinear

We should have an option to color by the CBSA's Cross Frame Cluster, at least for Tracts that are part of one of those CBSAs.

### Notes:
- These are interesting charts but since we're using Correlation to find tight pairs is it really necessary as anything more than visuals?

### Are the cluster names easily queryable?

Yes, at CBSA grain.

We already have cross-frame cluster labels available in the repo. The easiest path appears to be the same one the `area-explorer` app uses:

- `mart_intelligence.intelligence_cross_frame` when the datamart is present
- otherwise the Phase 5 parquet fallback at `exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/cross_frame_scores.parquet`

The field is already normalized as `combined_cluster` in `area-explorer/shared/db.py`, with the parquet fallback mapping `cross_frame_cluster_name AS combined_cluster`.

So the main answer is:

- yes, the cluster names are already accessible
- conceptually this is a clean enrichment because the join key is the tract's `cbsa_code`
- analytically this is a much stronger lens than coloring by the old Theme option

What this adds:

- a tract point still represents tract-level KPI values
- color represents inherited CBSA context
- that gives us a local-neighborhood-inside-known-metro-archetype lens, which is much closer to the actual Intelligence workflow than starting from scratch every time

---

## Within-CBSA Variance

### Benchmarks and examples

Current live benchmark distribution for `Within/National ratio` across usable KPIs:

- `p25 = 0.476`
- `median = 0.628`
- `p75 = 0.866`
- `max = 1.026`

Practical interpretation scale:

- `> 0.85`: strong within-metro signal
- `0.60–0.85`: solid neighborhood signal
- `0.40–0.60`: mixed / moderate signal
- `< 0.40`: weak within-metro signal, mostly between-metro

Examples from the current table:

- strong: `vacancy_rate 1.03`, `pct_commute_walk 0.97`, `jobs_per_resident 0.94`, `pct_unemployment_rate 0.90`
- middle: `pct_jobs_professional_services 0.63`, `diversity_index 0.57`, `median_hh_income 0.54`
- weak: `pct_commute_transit 0.27`, `pct_foreign_born 0.31`, `pop_weighted_density_sqmi 0.34`, `median_home_value 0.34`

How does this one work? Do we need to select certain CBSAs?

### Response

This tab is conceptually good, but it is the hardest one to read quickly because the chart is doing two jobs at once:

1. showing tract spread inside each CBSA
2. helping us judge whether the KPI has real neighborhood-level signal

### What the chart is actually plotting

For one selected KPI:

- each box represents one CBSA
- the y-axis is the KPI value
- the x-axis is a set of CBSAs
- within each CBSA, the boxplot summarizes the tract distribution for that KPI

So you are not looking at one number per CBSA. You are looking at the spread of tract values inside each CBSA.

### How to read one box

For a single CBSA boxplot:

- the center line is the median tract in that CBSA
- the box is the middle 50% of tracts in that CBSA
- taller box = more tract-to-tract variation inside that metro
- shorter box = less tract-to-tract variation inside that metro
- long whiskers or many outliers = a few tracts are very different from the rest

### What the whole chart is trying to tell us

The chart is asking:

- does this KPI vary meaningfully within metros?
- or is it mostly a between-metro KPI?

How to interpret the visual:

- if many CBSAs have tall boxes, the KPI varies a lot across neighborhoods inside metros
- if most CBSAs have very short boxes, the KPI may mostly separate metros from one another and do less work for tract clustering
- if some CBSAs are tall and others are compressed, the KPI may be useful in some markets and weak in others

### How to interpret the summary metrics below the chart

The app gives three summary numbers:

- `National IQR`
  This is the middle-50% spread across all tracts nationally.
- `Avg Within-CBSA IQR`
  This is the average middle-50% tract spread computed inside each CBSA separately.
- `Within/National ratio`
  This compares the average within-metro spread to the national spread.

How to read the ratio:

- high ratio, closer to `1`
  The KPI varies almost as much within metros as it does nationally. Good sign for zone-level clustering.
- low ratio, closer to `0`
  The KPI is doing more between-metro work than within-metro work. We should be more skeptical of its tract-clustering value.

### Do we need to select certain CBSAs?

Not strictly, but sometimes yes for interpretation.

- If left national, the tab shows many metros at once, which is useful for broad pattern detection.
- If filtered to a smaller set of CBSAs, the chart becomes much easier to read and compare visually.

So the practical answer is:

- no, filtering is not required for the chart to function
- yes, filtering can make it much easier to interpret

### Best way to read the chart in practice

1. Start with the ratio at the bottom.
   If it is very low, the KPI is probably not doing much neighborhood-level work.
2. Then scan the box heights.
   Are most metros tall, compressed, or mixed?
3. Then compare medians.
   Are metros simply shifted up and down, or do they also have big internal spread?
4. Then check whether the pattern changes when you filter to a few known CBSAs.
   That helps separate a national story from a market-specific one.

Brief reminder text for the report:

> **Within-CBSA variance chart:** each box shows how much tracts vary inside one metro on the selected KPI. Taller boxes mean more neighborhood-level variation; short boxes mean the KPI mostly separates metros, not neighborhoods.

---

## PCA

### Why run PCA here

The earlier EDA tabs helped us identify obvious coverage problems, suspicious distributions, and a few high-correlation pairs. But even after that, the KPI list still felt too long for a tract clustering model.

PCA gives us a cleaner answer to a different question:

- which KPIs are mostly repeating the same latent structure
- which KPIs still carry their own distinct signal
- how much dimensionality really remains after the obvious cleanup cuts

### PCA setup

I ran two PCA passes on the live `gold.intelligence_zone_inputs` tract frame:

1. **Full current app KPI list** — `31` KPIs
2. **Post-EDA trimmed list** — `26` KPIs after removing the five fields already flagged as weak earlier in these notes:
   - `median_gross_rent`
   - `pct_commute_transit`
   - `pct_struct_multifam`
   - `median_home_value`
   - `pct_foreign_born`

Method:

- source frame: `78,199` tracts from the current live Phase 7 table
- missing-data treatment: median imputation per KPI
- scaling: z-score standardization
- PCA basis: correlation matrix
- retained-component rule for interpretation: eigenvalue `> 1`

This is not the final production imputation design. It is a tractable screening pass to understand redundancy structure before clustering.

### PCA pass 1: full `31`-KPI list

High-level result:

- the full KPI surface still resolves into **`9` components with eigenvalue > 1**
- those `9` components explain about **`65.4%`** of total standardized variance
- the first two components explain only about **`33.6%`**, which means the tract frame is genuinely multi-dimensional and should not be collapsed too aggressively

Variance explained by the first components:

- `PC1 = 18.75%`
- `PC2 = 14.88%`
- `PC3 = 7.05%`
- `PC4 = 5.97%`
- `PC5 = 4.62%`
- `PC6 = 3.87%`
- `PC7 = 3.65%`
- `PC8 = 3.38%`
- `PC9 = 3.25%`

What the first pass surfaced:

- the only pair above `|r| >= 0.75` was:
  - `owner_occ_rate` vs `pct_struct_multifam` at about `-0.84`
- the densest redundancy bundle was the **urban form / accessibility / transit mode** cluster:
  - `pop_weighted_density_sqmi`
  - `pct_hh_0_vehicles`
  - `walkability_index`
  - `jobs_access_45min_transit`
  - `pct_commute_transit`
- the second biggest redundancy bundle was the **socioeconomic level** cluster:
  - `median_hh_income`
  - `pct_ba_plus`
  - `median_gross_rent`
  - `median_home_value`
  - `pov_rate`
- LODES did **not** collapse into one trivial factor:
  - `jobs_per_resident`
  - `pct_jobs_high_wage`
  - `pct_jobs_professional_services`
  still carry somewhat distinct signal

Lowest-uniqueness fields in the full pass:

- `pct_unemployment_rate 0.086`
- `median_hh_income 0.168`
- `owner_occ_rate 0.173`
- `pct_hh_0_vehicles 0.180`
- `pct_commute_transit 0.188`
- `pct_ba_plus 0.195`
- `pop_weighted_density_sqmi 0.235`
- `pct_struct_multifam 0.236`
- `jobs_access_45min_transit 0.245`

Interpretation:

- low uniqueness here means the KPI is largely explained by the shared component structure
- for dimensionality reduction, these are the first places to look for pruning
- this does **not** automatically mean the variable is bad; it means it may not deserve its own seat in the clustering vector if a nearby KPI tells the same story more cleanly

Highest-uniqueness fields in the full pass:

- `pct_jobs_professional_services 0.641`
- `pct_rent_burden_30plus 0.557`
- `ejs_pm25 0.539`
- `pct_ba_plus_change_3yr 0.534`
- `pct_asian_nh 0.527`
- `jobs_per_resident 0.510`

Interpretation:

- these are the fields least replaceable by the rest of the matrix
- if we want to preserve conceptual breadth while trimming count, these are exactly the kinds of KPIs we should try to keep

### PCA pass 2: post-EDA trimmed `26`-KPI list

After removing the five already-flagged weak fields (`median_gross_rent`, `pct_commute_transit`, `pct_struct_multifam`, `median_home_value`, `pct_foreign_born`), I reran PCA.

High-level result:

- the trimmed list still resolves into **`8` components with eigenvalue > 1**
- those `8` components explain about **`61.1%`** of total variance
- importantly, there were **no remaining pairwise correlations above `|r| >= 0.75`**

Variance explained by the first components:

- `PC1 = 16.79%`
- `PC2 = 12.97%`
- `PC3 = 7.39%`
- `PC4 = 6.04%`
- `PC5 = 5.07%`
- `PC6 = 4.54%`
- `PC7 = 4.26%`
- `PC8 = 4.01%`

This is the key conclusion from the rerun:

- the PCA **does support trimming**
- the PCA **does not support pretending the tract frame is only 3–4 dimensional**
- even after reasonable cuts, the live Phase 7 tract surface still contains about **8 meaningful latent dimensions**

### What the retained components look like

#### PC1 — urban form / accessibility / tenure / distress

Largest loadings:

- `owner_occ_rate`
- `pct_hh_0_vehicles`
- `pov_rate`
- `pop_weighted_density_sqmi`
- `walkability_index`
- `jobs_access_45min_transit`

Interpretation:

- this is the main tract urbanity-versus-stability bundle
- it is exactly where we should avoid carrying too many near-substitutes

#### PC2 — education / affluence / digital access / knowledge economy

Largest loadings:

- `pct_ba_plus`
- `median_hh_income`
- `pct_no_internet_access`
- `pct_asian_nh`
- `pct_jobs_professional_services`

Interpretation:

- this is the cleanest Knowledge Corridor / socioeconomic status axis
- we probably do not need every single KPI in this bundle

#### PC3 — Hispanic / environmental burden / walk / vacancy

Largest loadings:

- `pct_hispanic`
- `ejs_pm25`
- `pct_commute_walk`
- `vacancy_rate`

Interpretation:

- this looks like a distinct neighborhood morphology + burden pattern rather than simple SES duplication

#### PC4 — stability / aging / lower-density residential structure

Largest loadings:

- `pct_same_house`
- `pop_weighted_density_sqmi`
- `jobs_access_45min_transit`
- `pct_age_over_64`

#### PC5 — FEMA risk / aging / vacancy

Largest loadings:

- `fema_risk_score`
- `pct_age_over_64`
- `vacancy_rate`

Interpretation:

- FEMA still behaves like a meaningful modifier and is not collapsing entirely into EJScreen or broad distress

#### PC6 — directional momentum

Largest loadings:

- `pov_rate_change_3yr`
- `pct_ba_plus_change_3yr`

Interpretation:

- the tract momentum fields survive as their own dimension
- that is a strong argument for keeping at least one, and probably both

#### PC7 / PC8 — labor market and jobs-side structure

Largest loadings:

- `pct_rent_burden_30plus`
- `jobs_per_resident`
- `pct_jobs_high_wage`
- `pct_unemployment_rate`

Interpretation:

- the labor / opportunity signal is not reducible to one single LODES field
- `pct_unemployment_rate` is especially unusual: it has **very high uniqueness** in the trimmed run

### Trimmed-run uniqueness read

Lowest-uniqueness fields in the `26`-KPI rerun:

- `pct_hh_0_vehicles 0.185`
- `pct_ba_plus 0.194`
- `pop_weighted_density_sqmi 0.220`
- `median_hh_income 0.223`
- `owner_occ_rate 0.226`
- `jobs_access_45min_transit 0.227`
- `pct_same_house 0.230`

These are the best additional cut candidates if we want a leaner clustering vector.

Highest-uniqueness fields in the `26`-KPI rerun:

- `pct_unemployment_rate 0.930`
- `pct_jobs_professional_services 0.627`
- `pct_rent_burden_30plus 0.604`
- `pct_ba_plus_change_3yr 0.548`
- `jobs_per_resident 0.498`
- `pct_asian_nh 0.495`
- `ejs_pm25 0.454`

These are the fields PCA most strongly argues **not** to cut.

### Coverage + PCA combined read

The combined read is more useful than PCA alone.

#### Clear cuts

- `median_gross_rent`
  - worst coverage in the live table (`5.77%` missing)
  - lives inside the broad SES / housing-price bundle
  - adds less than `median_home_value`, `median_hh_income`, or `pct_rent_burden_30plus`

- `pct_struct_multifam`
  - only truly high-correlation pair in the matrix
  - largely interchangeable with `owner_occ_rate`

- `pct_commute_transit`
  - already weak on within-CBSA variance
  - also embedded in the same dense urbanity bundle as zero-car share, density, and SLD accessibility

- `pct_foreign_born`
  - weak within-CBSA signal in the earlier EDA
  - heavily absorbed into the broader urbanity / composition bundle

- `median_home_value`
  - coverage is acceptable but worse than most peers
  - sits squarely inside the SES cluster with `median_hh_income`, `pct_ba_plus`, and `pov_rate`

#### Additional PCA-driven cut candidates

- `pct_hh_0_vehicles`
  - very low uniqueness
  - substantially overlaps with density, walkability, and the urban accessibility bundle

- `jobs_access_45min_transit`
  - tract SLD coverage is now usable, but this specific KPI is still largely absorbed by the same latent structure as density and walkability
  - if we keep one SLD KPI for clustering, `walkability_index` is the cleaner pick

- `diversity_index`
  - conceptually useful as a summary field
  - but if we already retain the component race/ethnicity shares, the composite starts to double-count that neighborhood-composition dimension

- `median_hh_income`
  - highly interpretable
  - but PCA suggests it is one of the most replaceable fields once `pct_ba_plus` and `pov_rate` are already in the model

### Recommended KPI sets after PCA

#### 1. Recommended lean core model: `22` KPIs

This is the set I would use for the first serious clustering run.

**Character**

- `pct_hispanic`
- `pct_black_nh`
- `pct_asian_nh`
- `pct_age_over_64`
- `pct_ba_plus`
- `pct_same_house`
- `owner_occ_rate`
- `pop_weighted_density_sqmi`

**Livability**

- `pct_rent_burden_30plus`
- `vacancy_rate`
- `pct_commute_walk`
- `walkability_index`
- `pct_no_internet_access`
- `ejs_pm25`
- `fema_risk_score`

**Opportunity**

- `pov_rate`
- `pct_unemployment_rate`
- `pov_rate_change_3yr`
- `pct_ba_plus_change_3yr`
- `jobs_per_resident`
- `pct_jobs_high_wage`
- `pct_jobs_professional_services`

Fields removed to get to this `22`-KPI core:

- `diversity_index`
- `pct_foreign_born`
- `pct_struct_multifam`
- `median_gross_rent`
- `median_home_value`
- `pct_hh_0_vehicles`
- `pct_commute_transit`
- `jobs_access_45min_transit`
- `median_hh_income`

#### 2. Slightly broader compromise model: `24` KPIs

If we want to be less aggressive, add back:

- `median_hh_income`
- `jobs_access_45min_transit`

That version keeps one direct income-level field and both SLD measures, while still removing the clearest redundancies.

### Recommendation

My read after the PCA rerun is:

- the old `31`-KPI list is too crowded for clustering
- the earlier `26`-KPI shortlist is better, but still more redundant than it needs to be
- the best balance for a first national zone model is a **`22`-KPI core vector**

The most important conceptual takeaway is this:

- PCA supports **targeted pruning**
- PCA does **not** support collapsing the tract model into a tiny handful of variables
- even after cleanup, the live Phase 7 tract surface still carries about **8 meaningful latent dimensions**

So the right move is not "reduce to 10 KPIs no matter what."  
The right move is "keep one or two good representatives for each real dimension, and stop double-counting the same neighborhood story."
