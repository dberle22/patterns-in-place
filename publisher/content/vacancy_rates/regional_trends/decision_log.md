# Decision Log — Regional Vacancy Trends

This file captures the main decisions made while building
`analysis/vacancy_rates/regional_trends/`, why we made them, and what they
suggest for future regional or multi-series insight builds.

---

## 1. Editorial framing

**Decision**

Treat the regional post as a follow-on to the national vacancy trend, focused on
shared tightening with persistent regional differences.

**Why**

- The topic README already framed this insight as the deeper-read companion to
  the national chart.
- The question started with a post-2019 angle, but the EDA showed the more
  interesting story is not only that all regions tightened, but that the
  regional order barely changed while they did.

**What worked**

- The final framing is more distinctive than a generic “all regions declined”
  message.
- It ties directly back to the larger topic thesis that the US is running out
  of housing slack, while still adding something new.

**What did not work as well**

- The initial question implied that regional differences might have shifted more
  dramatically than they actually did. The strongest version of the story
  turned out to be about stability as much as change.

---

## 2. EDA structure

**Decision**

Create a dedicated `eda/` folder with separate SQL files and paired markdown
summaries.

**Why**

- The same pattern worked well in `national_trend/` and `metro_rankings/`.
- This insight needed a few distinct checks:
  coverage and labels, full series behavior, and post-2019 change with rank
  stability.

**What worked**

- The EDA split cleanly into three useful buckets instead of one oversized
  exploratory file.
- Saving the SQL made it easy to revisit the time-window choice later when the
  chart start year changed from `2019` to `2014`.

**What did not work as well**

- The findings and chart decisions depended on both the full `2012`-`2024`
  context and the narrower post-2019 framing, so the distinction between
  exploratory range and production range had to be managed carefully.

---

## 3. Source table choice

**Decision**

Use `gold.housing_core_wide` only, restricted to `geo_level in ('us', 'region')`.

**Why**

- This insight is purely about vacancy rate, so a single source table is enough.
- The table already contains clean annual series for the US and all four Census
  regions, with no need for joins or derived rollups.

**What worked**

- The source is simple, legible, and highly reusable.
- Coverage was complete from `2012` through `2024` for all five series.

**What did not work as well**

- None materially. This was one of the cleanest data setups in the vacancy-rate
  topic.

---

## 4. Choosing the core takeaway

**Decision**

Center the analysis on two linked facts:
1. all four regions tightened after `2019`
2. the regional hierarchy stayed mostly intact

**Why**

- The EDA showed broad declines in every region.
- It also showed that `West` was tightest in every year and `South` loosest in
  every year, with only a minor `Midwest`/`Northeast` swap earlier in the
  series.

**What worked**

- This gave the chart a clearer narrative than simply listing regional rates.
- It prevented the writeup from overstating convergence that the data does not
  actually show.

**What did not work as well**

- The “no big reshuffle” result is analytically strong but a little less flashy
  than a dramatic crossing-lines story would have been.

---

## 5. Time-window decision

**Decision**

Use the full `2012`-`2024` range for EDA, then build the production chart first
for `2019`-`2024` and later revise it to start in `2014`.

**Why**

- The question brief explicitly focused on `since 2019`, so the first chart
  build stayed close to that framing.
- The EDA showed that some longer-run context was valuable, especially for the
  `Northeast`, which rose before falling, and for understanding how stable the
  regional order really is.
- After review, extending the chart back to `2014` provided more runway without
  making the graphic too dense.

**What worked**

- The saved EDA preserved the broader context even while the production query
  evolved.
- The final `2014` start gives readers enough pre-2019 context to understand
  that the recent tightening sits on top of longer regional structure.

**What did not work as well**

- The title still emphasizes “since 2019” while the plotted series now begins in
  `2014`, which is directionally right but requires the subtitle to do some
  interpretive work.

---

## 6. Series design and highlighting

**Decision**

Use five lines in the final chart:

- `United States`
- `Northeast`
- `Midwest`
- `South`
- `West`

Highlight the US series and treat the regions as the comparison set.

**Why**

- The question explicitly called for the US average plus the four Census
  regions.
- Highlighting the US line gives readers a clean benchmark without cluttering
  the chart with extra reference mechanics.

**What worked**

- The chart remains readable even with five series.
- The US highlight helps frame which regions sit persistently above or below the
  national line.

**What did not work as well**

- Five lines are still more cognitively demanding than a single-series chart, so
  short display labels and a clean legend were important.

---

## 7. Label cleanup in production SQL

**Decision**

Rename source labels in `query.sql` from `Northeast Region`, `Midwest Region`,
`South Region`, and `West Region` to shorter display names.

**Why**

- The raw labels are accurate but slightly bulky for a line-chart legend.
- The shorter labels make the chart cleaner without changing any analytical
  meaning.

**What worked**

- The resulting legend is easier to scan quickly.
- The findings still document the original source labels so the transformation
  stays transparent.

**What did not work as well**

- This is another place where analytical labels and presentation labels diverge,
  so it is worth documenting explicitly to avoid confusion later.

---

## 8. Axis and formatting choices

**Decision**

Use `label_style = "number"`, keep a zero baseline, and cap the y-axis at `15`.

**Why**

- The SQL outputs percent values like `8.5`, not decimal fractions like `0.085`,
  so percent formatting would have been wrong.
- A zero baseline keeps the chart visually fair across a relatively narrow range
  of values.
- A `0` to `15` y-axis captures the full regional spread while keeping the lines
  readable.

**What worked**

- The chart reads cleanly and does not overstate the slope differences.
- The chosen range is tight enough to be legible but broad enough to stay
  honest.

**What did not work as well**

- As with the national chart, the fairer axis is a bit less dramatic on first
  glance than a tighter cropped range would have been.

---

## 9. Summary and post-draft approach

**Decision**

Keep `summary.md` analytical and compact, then use `post_draft.md` to sharpen
the same message for X and Substack.

**Why**

- The summary step should interpret the chart in a restrained, data-first way.
- The social step can be more direct and hook-driven while staying faithful to
  the same numbers.

**What worked**

- Both outputs stayed tightly aligned with the approved chart.
- The post draft translated the “shared tightening, limited convergence” idea
  into simpler language without losing the core argument.

**What did not work as well**

- This insight is a little less naturally punchy for X than the national or
  metro stories, so the copy has to work harder to make the stability result
  feel interesting.

---

## 10. Overall lesson for future regional analyses

**Decision**

Treat regional charts as structure-revealing views, not just narrower copies of
national trend charts.

**Why**

- The value of a regional cut is often in the relationship among lines:
  rank stability, spread, convergence, or divergence.
- Simply proving that “all regions declined” is not enough if the same thing is
  already visible nationally.

**What worked**

- This build found a stronger message by focusing on the persistence of regional
  differences.
- The saved EDA now gives us reusable checks for future region-level questions:
  coverage, spread, rank order, and gap versus US.

**What did not work as well**

- Future regional work should probably decide earlier whether the production
  chart is meant to emphasize recent change or longer-run structure, because
  that choice affects the final time window and subtitle.
