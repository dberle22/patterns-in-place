# Decision Log — Metro Vacancy Rankings

This file captures the main decisions made while building
`analysis/vacancy_rates/metro_rankings/`, why we made them, and what they
suggest for future metro-ranking or backlog insight builds.

---

## 1. Editorial framing

**Decision**

Start with a metro-ranking question focused on 2024 housing vacancy, then widen
the framing from only the tightest markets to both the tightest and loosest
major metros.

**Why**

- The topic README already identified metro rankings as the most shareable
  follow-on to the national trend.
- The original question emphasized tight markets, but the EDA showed that the
  loose tail was much more visually dramatic and editorially distinctive.
- The updated question wording made room for a fuller contrast:
  tightest metros, loosest metros, and the national benchmark.

**What worked**

- The final framing tells a more complete story than a single “top 20 tightest”
  chart would have.
- The build now supports three distinct visuals from one analysis:
  tightest, loosest, and a combined comparison chart.

**What did not work as well**

- The original brief was narrower than the strongest data story, so we had to
  revise the output structure mid-build.

---

## 2. EDA folder structure

**Decision**

Reuse the same paired `eda/*.sql` + `eda/*_summary.md` pattern established in
 `national_trend/`.

**Why**

- The national-trend build had already shown that separating exploratory SQL
  from production SQL keeps tradeoffs legible.
- This question required several distinct checks:
  coverage, population filter behavior, ranking shape, and small-market
  outliers.

**What worked**

- The EDA split cleanly into four useful buckets:
  1. coverage and population filters
  2. major-metro rankings
  3. distribution and national benchmarking
  4. small-metro outliers
- The paired summaries made it easier to write `findings.md` without
  re-querying the data from scratch.

**What did not work as well**

- Some early EDA numbers were superseded once we later restricted the scope to
  the 50 states plus DC. That suggests future analyses should lock geography
  scope earlier when possible.

---

## 3. Source tables and join pattern

**Decision**

Use `gold.housing_core_wide` for vacancy rates and
`gold.population_demographics` for the population filter, joined on
`geo_level + geo_id + year`.

**Why**

- `housing_core_wide` contains `vacancy_rate` and `hu_total`, but not
  `pop_total` in the runtime DB surface we queried.
- `population_demographics` provides the clean population cutoff needed for a
  “major metro” ranking.

**What worked**

- The join gave complete 2024 CBSA coverage for vacancy, housing units, and
  population.
- The join pattern is simple and reusable for many other ranking questions that
  need a metric from one gold mart and a scope filter from another.

**What did not work as well**

- The data dictionary for `housing_core_wide` suggests broader context than what
  was actually visible in the queried runtime table, so we had to verify fields
  directly rather than assume.

---

## 4. Population cutoff choice

**Decision**

Keep the question brief’s `250k+` population filter for defining “major
 metros.”

**Why**

- EDA showed that the full CBSA universe is too broad, mixing large labor
  markets with very small seasonal and second-home destinations.
- The `250k+` threshold left `197` metros in the initial universe, which is
  large enough to rank while still filtering out the most distorted outliers.
- Tighter filters like `500k+` or `1M+` would have produced a cleaner but much
  narrower peer set than the brief called for.

**What worked**

- The cutoff materially changed the distribution in the right direction.
- It removed vacation-market distortion without collapsing the set into only
  very large metros.

**What did not work as well**

- The term “major metro” is still a judgment call. If future backlog work uses a
  different threshold, that choice should be made explicit in both the question
  and the chart subtitle.

---

## 5. Interpreting the ranking shape

**Decision**

Treat the metro distribution as asymmetric rather than as a simple symmetric
 top-vs-bottom ranking.

**Why**

- EDA showed the tight end is compressed:
  top 20 tight metros ran only from `3.0%` to `5.1%`.
- The loose end is much broader:
  top 20 loose metros stretched from `13.9%` to `33.4%` after the final
  state/DC filter.
- That means a “tightest metros” chart is valid, but the full story becomes much
  stronger once the loose tail is shown alongside it.

**What worked**

- This choice directly motivated the three-chart package.
- It made the final takeaway sharper:
  low vacancy is broadly distributed across large metros, while very high
  vacancy is concentrated in a smaller set of markets.

**What did not work as well**

- The first single-chart render, while correct, did not fully surface the most
  interesting structure in the data by itself.

---

## 6. National benchmark choice

**Decision**

Use the true US vacancy rate from `geo_level = 'us'` as the benchmark line and
 as the national bar in the combined chart.

**Why**

- The true national row is the cleanest reference point for audiences.
- The EDA confirmed that a large share of major metros sit below the national
  vacancy rate.
- For the combined chart, a real US bar is more intuitive than a benchmark line
  because it turns the middle reference point into a direct visual category.

**What worked**

- The `10.1%` US benchmark clearly separated the tight metro group from the
  loose metro group.
- The combined chart became easier to read once the national value was rendered
  as its own bar.

**What did not work as well**

- None materially. This was the cleanest benchmark choice for this question.

---

## 7. Query design strategy

**Decision**

Use separate production SQL files for each final visual:

- `query.sql` for tightest 20
- `query_loosest.sql` for loosest 20
- `query_combined.sql` for tightest 10 + US + loosest 10

**Why**

- Each chart has a distinct editorial job and slightly different ranking logic.
- A single “do everything” query would have been harder to inspect, rerun, and
  debug.
- The bar renderer expects chart-ready long-format rows, so keeping each query
  purpose-built reduced transformation risk.

**What worked**

- Each output could be reviewed independently without confusing filters or
  display rules.
- The combined query remained understandable because it explicitly unions three
  conceptual sections: tightest, national, loosest.

**What did not work as well**

- There is some duplicated SQL across the three files. If this pattern appears
  often in the backlog, it may be worth creating a reusable metro-ranking SQL
  skeleton.

---

## 8. Bar-chart config choices

**Decision**

Use ranked horizontal bars with direct labels, `label_style = "number"`, and a
 benchmark line for the tightest and loosest charts.

**Why**

- Horizontal bars are the most readable format for ranking metro names.
- The query outputs percentages like `10.1`, not decimal fractions like
  `0.101`, so `label_style = "number"` is the correct renderer setting.
- Direct value labels reduce scanning effort, especially for social uses.

**What worked**

- The charts are easy to read quickly on both desktop and social-sized review.
- The benchmark line adds context without forcing a second series.

**What did not work as well**

- The renderer does not automatically “know” that these are already percentage
  points, so using `percent` formatting would have been wrong.
- The benchmark label needed extra right margin to avoid crowding.

---

## 9. Combined-chart design

**Decision**

Build a third chart that combines:

- 10 tightest major metros
- the United States
- 10 loosest major metros

Use the US bar as the highlighted row.

**Why**

- The updated brief explicitly asked for a single visual that puts both ends of
  the distribution around a national anchor.
- A combined chart works as a synthesis view after the two endpoint charts
  establish the details.

**What worked**

- The combined chart clearly shows the gap between the compressed tight side and
  the far more spread-out loose side.
- Highlighting the US bar helps the eye find the midpoint immediately.

**What did not work as well**

- The combined chart is more interpretive than the endpoint charts. It works
  best as a companion visual, not as the only chart.

---

## 10. Geography scope correction

**Decision**

Restrict all final metro visuals to the 50 states plus DC, excluding territories
 such as Puerto Rico.

**Why**

- During chart review we noticed Puerto Rico metros appearing in the loose
  rankings.
- For this question, the intended audience framing was “US metros” in the
  state/DC sense rather than the full territory-inclusive CBSA universe.

**How we implemented it**

- We first looked for `silver.xwalk_cbsa_county`, but that table was not exposed
  in the runtime DB we were using.
- The runtime DB did expose `silver.xwalk_cbsa_state` and
  `silver.xwalk_state_region`, which gave a cleaner solution:

```sql
with allowed_cbsa as (
  select distinct
    cs.cbsa_code as geo_id
  from silver.xwalk_cbsa_state cs
  join silver.xwalk_state_region sr
    on cs.state_fips = sr.state_fips
)
```

- Joining the chart queries to `allowed_cbsa` cut the 2024 CBSA universe from
  `935` to `925`.

**What worked**

- This excluded territory CBSAs by state-mapping logic rather than by string
  filtering.
- It immediately cleaned up the loose and combined charts.

**What did not work as well**

- The scope change came late in the process, which forced us to rerun all three
  chart outputs.
- Future backlog analyses should explicitly decide territory treatment during
  EDA, not after render review.

---

## 11. Execution workflow choices

**Decision**

Execute SQL via Python DuckDB calls rather than relying on the `duckdb` CLI,
 and write CSVs with `COPY (...) TO ...`.

**Why**

- The local environment did not have the `duckdb` CLI installed.
- Python already had DuckDB available, so it was the simplest reliable path.

**What worked**

- This kept the full analysis inside the repo-local workflow with no setup
  detours.
- It made validation and CSV export easy to script.

**What did not work as well**

- Wrapping `COPY (...)` around a SQL file with a trailing semicolon caused a
  parser error. We had to strip the trailing semicolon before export.
- This is a small but reusable reminder for any future scripted `COPY` step.

---

## 12. Findings, summary, and social synthesis

**Decision**

Let the analytical write-ups emphasize the asymmetric distribution rather than
 the initial “coastal liberal metros are tight” hunch.

**Why**

- The EDA showed the geography of tightness was more mixed than the initial
  stereotype suggested.
- The stronger data-first claim is that tight vacancy is common across many
  large metros, while very high vacancy is more concentrated.

**What worked**

- `findings.md`, `summary.md`, and `post_draft.md` now all align around the same
  core structure while speaking in different levels of detail.
- The social draft works especially well with the three-chart package:
  one endpoint chart for each side plus one synthesis chart.

**What did not work as well**

- Because the scope changed late, some early EDA framing had to be mentally
  updated when writing the final copy.

---

## Reusable takeaways

- Lock geography scope early, especially whether territories are in or out.
- When a ranking question feels one-sided, test the opposite tail before
  committing to a single chart.
- Use separate production queries when multiple final visuals have distinct
  editorial roles.
- Verify runtime table availability directly; do not assume every documented
  silver helper exists in the runtime DB.
- For chart exports driven through DuckDB `COPY`, strip trailing semicolons from
  the source SQL.
- Use `label_style = "number"` whenever the query already outputs human-scale
  percentages like `10.1`.
- Combined charts work best as synthesis views after endpoint charts establish
  the distribution.
