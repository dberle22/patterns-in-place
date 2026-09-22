# Thematic A8 — Geography of Life Expectancy Spec

**Status:** Provisional; revise after Epic 1 audit

**Updated:** 2026-09-20

**Family plan:** [THEMATIC_ANALYSES_PLAN.md](../THEMATIC_ANALYSES_PLAN.md)

## 1. Question and purpose

How much geographic variation in life expectancy remains after accounting for
income and other observable market context, and which housing, social-fabric,
access, and environmental conditions accompany that residual variation?

This wording is deliberately associational. “Place effect” should be reserved
for a design that identifies causal effects rather than contextual differences.

**Themes crossed:** Health & Wellbeing × Housing & Affordability × Social
Fabric.

## 2. Provisional claim and alternatives

**Claim direction to review:** Income explains an important share of geographic
life-expectancy variation, but metros and counties with similar income still
differ in ways associated with housing stress, social fabric, access, and
environmental conditions.

The claim is weakened if little stable residual variation remains, if context
relationships disappear under regional or demographic controls, or if source
vintage/aggregation choices drive the result.

## 3. Analytical unit and universe

- Primary native health unit: county, with a national county analysis and
  governed CBSA rollups where valid.
- National comparison unit: county and/or CBSA, kept distinct rather than
  pooled silently.
- Market unit: counties within a selected CBSA; finer geography may provide
  context but not life-expectancy outcomes unless a governed source exists.
- Time: source-specific CHR vintages and available change fields, subject to
  audit of what period each estimate represents.

## 4. Notebook contracts

### National notebook

The national notebook should:

1. document life-expectancy source period, reliability, and geographic coverage
2. show county and CBSA distributions separately
3. establish income and demographic baselines before residual analysis
4. test housing, social-fabric, food/access, and environmental context in
   transparent stages
5. test region, urbanicity/metro size, weighting, and influential observations
6. avoid ecological or causal interpretation of aggregate associations
7. identify stable contextual patterns and counterexamples

### Parameterized market notebook

The market notebook should:

- show the selected CBSA’s life expectancy in national, division, and peer
  context
- compare member counties without presenting them as neighborhoods
- show observed versus income-expected outcomes if the national method retains
  that residual
- display the reviewed housing, social, access, and environment components
- identify data gaps and unstable county estimates
- provide standard deep dives for above-expected, below-expected, internally
  unequal, and inconclusive markets

## 5. Current repository assets

- `gold.health_wide` at county and CBSA grains with life expectancy and related
  health measures
- `gold.economics_income_wide`, housing/affordability, social-fabric,
  environment, and food-access marts
- Benchmarking, Geography, Peers, and Time-Series context
- Q4 Daily-Needs planning and POI outputs as optional later access context
- county-to-CBSA relationships and display geometry

## 6. Audit findings to verify

- `health_wide` contains multiple annual rows, but each measure may represent a
  lagged or multi-year source estimate rather than the table row year alone.
- Social Capital and food-access inputs include static or one-time vintages.
- County and CBSA estimates have different aggregation and inference meanings.
- Aggregate income residuals do not isolate causal place effects.
- Small-county reliability, population weighting, and multi-county metros may
  strongly affect results.
- Adding many correlated context variables could produce an unstable story.

## 7. Provisional outputs

- health/context metric contract and coverage table
- national county and CBSA distributions
- staged income/context models or descriptive residual analysis
- region, weighting, and variable-set sensitivity
- selected-market county and component comparison
- finding ledger with ecological and causal caveats

## 8. Decisions Epic 1 must prepare

- primary outcome and exact source period
- county versus CBSA lead analysis
- income and demographic baseline
- context families and variable-selection rule
- weighting, reliability, and minimum-population rules
- residual interpretation language
- treatment of multi-collinearity and regional structure
- valid market notebook geography and standard deep dives

## 9. Non-goals

- claiming causal place effects from aggregate residuals
- inferring individual health outcomes from metro averages
- building an opaque composite health/place score
- using tract context as if tract life expectancy were observed
- making clinical or public-health intervention recommendations

