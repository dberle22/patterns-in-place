# Overheating Methodology

This note explains how the current housing overheating methodology works in
plain language. It is meant to make the section easier to review, revise, and
write from.

## What We Mean By "Overheating"

In this project, overheating does **not** mean only that a market is expensive.

A market can be expensive but stable.
A market can be fast-growing but still relatively affordable.
A market can have strong price momentum without broad affordability strain.

The current methodology treats overheating as a combination of several pressures
happening at once:

- price and rent momentum
- growth pressure
- affordability strain
- tightness and supply stress

That is why the section uses a multi-component score rather than a single raw
metric like home prices or rent growth.

## Data Source And Grain

The current source table is `mart_housing.overheating_matrix`.

For the first-pass editorial work, we are using:

- geography: `cbsa`
- universe: `major_cbsa_100k_flag = TRUE`
- snapshot year: `2024`

This keeps the methodology focused on larger metro markets first, where the data
coverage is stronger and the editorial interpretation is easier to defend.

## The Four Component Families

The overheating mart groups metrics into four component families.

### 1. Momentum

This measures whether housing-market prices and rents have been running hot.

Current inputs include:

- `hpi_yoy_pct`
- `hpi_5yr_pct`
- `zori_annual_avg_yoy_pct`

Interpretation:

- higher momentum score = stronger recent housing-market acceleration

### 2. Pressure

This measures whether people and incomes are still pushing into the market.

Current inputs include:

- `acs_income_pc_growth_1yr`
- `acs_income_pc_growth_5yr`
- `pop_growth_1yr`
- `pop_growth_5yr`

Interpretation:

- higher pressure score = stronger demographic or income-side growth pressure

### 3. Strain

This measures whether households already look stretched.

Current inputs include:

- `rent_to_income`
- `value_to_income`
- `pct_rent_burden_30plus`

Interpretation:

- higher strain score = less affordability cushion

### 4. Tightness / Supply

This measures whether the market still looks supply-constrained.

Current inputs include:

- `vacancy_rate`
- `permits_per_1000_housing_units`
- `permits_share_multifam_units`

Interpretation:

- lower vacancy and weaker supply response imply more overheating
- because of that, these metrics are direction-adjusted before scoring

## How Raw Metrics Become Scores

The raw metrics do not share a common scale, so they are normalized within each
`geo_level + year` universe.

The mart keeps two normalization layers:

- percentile-style rank fields
- z-score fields

For the current editorial visuals, we are mainly using the component score
surface rather than raw z-scores.

Direction matters:

- higher is more overheating for momentum, pressure, and strain metrics
- lower is more overheating for vacancy and supply-response metrics

This directional handling is important because otherwise more permitting would
incorrectly look like more overheating.

## How The Component Scores Are Built

Each component score is the average of the normalized metrics available in that
component.

The current component fields are:

- `momentum_component_score`
- `pressure_component_score`
- `strain_component_score`
- `tightness_component_score`

Interpretation:

- higher component score = more of that kind of overheating pressure

These scores are stored on a `0` to `1` scale in the mart.
In the charts, we often multiply them by `100` so they read as a simple `0` to
`100` index.

## How The Provisional Composite Works

The overall ranking field is `provisional_overheating_score`.

Right now, it is built as the average of the four component scores that are
present for a row.

That means:

- no explicit custom weights yet
- no locked ideological assumption that one component should dominate
- enough flexibility to revise later if the outputs suggest the blend is off

The section also uses:

- `provisional_overheating_score_pctile`
- `provisional_overheating_rank`

These help with ranking and chart communication.

## Why The Composite Is Called Provisional

We are labeling it provisional on purpose.

Reasons:

- we have not yet tuned weights
- we have not yet decided whether all four families should matter equally
- some source families have weaker coverage than others
- editorial interpretation may still change after we compare the outputs

So the current goal is not to claim "this is the final overheating formula."
The goal is to create a disciplined first pass that is consistent, explainable,
and easy to pressure-test.

## Coverage Caveats

The biggest data caveat is rent momentum.

`ZORI` coverage is partial, especially compared with FHFA price coverage.
Because of that:

- rent momentum is treated as a useful enhancer
- it is **not** required for row inclusion
- the methodology leans more heavily on FHFA plus affordability and supply
  context where rent coverage is thinner

This is one reason the methodology should be explained alongside the charts
rather than hidden behind a single ranking table.

## How The Current First-Pass Visuals Use The Methodology

The section currently uses the methodology in five ways.

### Hottest Major CBSAs

`cbsa_overheating_hottest.png`

- ranks major metros by `provisional_overheating_score`
- this is the cleanest listicle output
- it is useful, but it should never stand alone

### Still-Affordable Shortlist

`cbsa_overheating_still_affordable.png`

This is **not** the same thing as "least overheating."

The shortlist first requires:

- below-median `rent_to_income`
- below-median `value_to_income`

Then, within that more affordable subset, it ranks metros by a simple
shortlist score that prefers:

- lower strain
- lower momentum

Current formula:

- `1 - (0.6 * strain_component_score + 0.4 * momentum_component_score)`

Why this exists:

- some low-composite metros are calm only because growth pressure is weak
- that does not automatically make them interesting editorially
- the shortlist tries to surface markets that still look comparatively
  affordable while also not running especially hot

This is still a heuristic, not a final investment or migration recommendation.

### Momentum Vs Strain Scatter

`cbsa_overheating_scatter.png`

- plots `momentum_component_score` against `strain_component_score`
- helps separate metros that are hot because prices are running from metros
  that are hot because households are already stretched
- makes the composite easier to reason about visually

### Momentum Vs Strain Bivariate Map

`cbsa_overheating_bivariate_map.png`

- maps the same two core dimensions geographically
- useful for spotting regional clusters or outliers
- intentionally narrows the story to the most legible two-component overlap

### Component Heatmap

`cbsa_overheating_component_heatmap.png`

- shows the component profile behind the hottest metros
- keeps us from overreading the composite as if every hot market got there the
  same way

## What This Methodology Is Good At

- creating a structured first-pass overheating ranking
- combining prices, affordability, growth, and supply context in one surface
- making cross-market comparison easier
- supporting multiple visual framings from the same mart

## What This Methodology Does Not Yet Do

- produce a final canonical overheating definition
- prove causal relationships
- distinguish between "badly overheated" and "desirable but in-demand"
- encode a fully worked theory of what counts as a "good deal"
- settle whether all component families deserve equal weight

## Questions To Keep In Mind While Reviewing It

- Do the top-ranked metros look intuitively right?
- Are some metros ranking high because one component is overpowering the rest?
- Does the methodology overreward growth pressure in ways that blur demand
  strength with overheating?
- Is the tightness / supply component behaving as intended?
- Does the still-affordable shortlist feel editorially meaningful, or just
  mechanically calm?

## Current Bottom Line

The methodology is best understood as a **reviewable framework**, not a finished
truth.

It gives us:

- a consistent way to rank metros
- a way to decompose those rankings
- a better starting point for synthesis writing

But it should stay open to revision as we compare it with the Vacancy, Costs,
and Supply Character outputs.
