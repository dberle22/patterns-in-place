# Decision Log — National Vacancy Rate Trend

This file captures the main decisions made while building
`analysis/vacancy_rates/national_trend/`, why we made them, and what they
suggest for future insight builds.

---

## 1. Editorial framing

**Decision**

Start with the national vacancy trend as the first post in the vacancy-rate
series.

**Why**

- The topic README already identified the national decline as the cleanest hook.
- It is the simplest possible entry point for the audience before moving into
  state, metro, and regional breakdowns.
- A single time series is easy to explain on both X and Substack.

**What worked**

- The national story is intuitive and data-rich without needing much setup.
- It gives the rest of the topic a clear thesis: the country is running out of
  housing slack.

**What did not work as well**

- The original question phrasing assumed the strongest signal might be just
  “since 2019,” but the EDA showed the fuller shape matters too: the 2010s were
  mostly flat, and the real tightening is concentrated in 2020-2024.

---

## 2. EDA folder structure

**Decision**

Create a dedicated `eda/` folder inside `national_trend/` with separate SQL
files and markdown summaries.

**Why**

- There was no existing EDA subfolder pattern in `analysis/`.
- Keeping exploratory SQL and notes separate from `query.sql` made the process
  easier to review and reuse.

**What worked**

- Splitting EDA into coverage/quality, US trend, US-vs-CBSA comparison, and
  outliers made it easy to move from exploration into findings.
- Paired markdown summaries helped preserve the reasoning behind later choices.

**What did not work as well**

- Because there was no pre-existing convention, we had to make a structure
  choice ad hoc. It may be worth standardizing this pattern across future
  insights.

---

## 3. National series source

**Decision**

Use `geo_level = 'us'` from `gold.housing_core_wide` as the headline national
series.

**Why**

- The topic README explicitly noted that the US row should be used for national
  headlines.
- The EDA confirmed complete 2012-2024 coverage with no null, NaN, or infinite
  values.

**What worked**

- This produced a very clean series with a strong headline:
  `12.1%` in 2019 to `10.1%` in 2024.
- It avoided introducing aggregation choices into the main series.

**What did not work as well**

- None for this specific insight. This was the cleanest part of the build.

---

## 4. Handling the metro comparison

**Decision**

Do not use an unweighted “US metro average.” Use a housing-unit-weighted CBSA
rollup instead.

**Why**

- The original question brief suggested showing a US average and a US metro
  average together.
- EDA showed that an unweighted CBSA average is not directly comparable to the
  US series because small metros count the same as large ones.
- The weighted formula better represents a combined metro housing stock:

```sql
sum(hu_total * vacancy_rate) / nullif(sum(hu_total), 0) * 100
```

**What worked**

- The weighted series gave a more defensible comparison line.
- It preserved the editorial idea of adding depth without using a misleading
  average.

**What did not work as well**

- Even weighted, the metro comparison is still not a perfect apples-to-apples
  national benchmark because it excludes non-CBSA areas.
- This means the second line is best treated as supporting context, not the main
  claim.

---

## 5. Findings synthesis

**Decision**

Frame the findings around two ideas:
1. the 2010s were relatively flat
2. the tightening is a post-2019 story

**Why**

- The EDA showed the line is much flatter before 2019 than the initial brief
  implied.
- That contrast makes the later decline more informative and easier to explain.

**How we analyzed and summarized**

- We pulled the full US series and year-over-year changes.
- We compared 2019 and 2024 directly for the headline statistic.
- We tested alternative CBSA rollups before deciding how to treat the comparison
  line.
- We documented surprises in `findings.md` rather than forcing the original
  hypothesis unchanged.

**What worked**

- The final `findings.md` stayed grounded in data rather than in the initial
  expectation.
- The “flat, then falling every year” framing is memorable and accurate.

**What did not work as well**

- The original “US average vs US metro average” idea needed more caveating than
  expected.

---

## 6. Query design

**Decision**

Write `query.sql` in the line-chart contract with two series:

- `United States`
- `US Metro Average (Weighted)`

**Why**

- The line renderer expects a long-format table with one row per series per
  period.
- Keeping the query output chart-ready reduces later transformation risk.

**What worked**

- The query validated cleanly and returned 26 rows, covering both series from
  2012 through 2024.
- The contract was straightforward once the series definitions were settled.

**What did not work as well**

- None materially, though it was important to validate the meaning of the
  weighted calculation before locking it into the query.

---

## 7. Percent formatting choice

**Decision**

Use `label_style = "number"` in `chart_config.json`, not `percent`.

**Why**

- The query already outputs values like `10.1` rather than fractions like
  `0.101`.
- The renderer’s percent formatter multiplies by 100 again, which would have
  produced incorrect axis labels.

**What worked**

- Using `number` plus the axis label `Vacancy rate (%)` produced the correct
  visual output.

**What did not work as well**

- This is a subtle renderer behavior that could easily cause mistakes later. It
  may be worth documenting more explicitly in charting guidance.

---

## 8. Y-axis fairness review

**Decision**

Change the chart y-axis from a tighter auto-scaled range to a fixed `0` to `20`
 percent range.

**Why**

- The first render made the decline look more dramatic than it should because
  the visible data range was compressed.
- A broader axis made the chart feel more honest and proportionate.

**What worked**

- The revised chart still shows the trend clearly.
- It is much less likely to be criticized as visually exaggerated.

**What did not work as well**

- The slope is less visually dramatic, which slightly reduces punch on social.
- In this case, fairness was the better tradeoff.

---

## 9. Summary approach

**Decision**

Keep `summary.md` data-first and restrained, using the weighted metro line only
 as supporting context.

**Why**

- `summary.md` is the analytical interpretation, not the social copy.
- The clearest claim is still the national drop from `12.1%` to `10.1%`.

**How we summarized**

- First sentence: describe the pre-2019 baseline.
- Second sentence: describe the post-2019 decline and quantify it.
- Final sentence: add the weighted metro comparison as reinforcement.

**What worked**

- The summary is short, readable, and faithful to the chart.

**What did not work as well**

- None materially. This was a good example of keeping the write-up narrower than
  the full EDA.

---

## 10. Social copy approach

**Decision**

Use `post_draft.md` to translate the same facts into sharper, platform-friendly
 language for X and Substack.

**Why**

- The social step should be more readable and more hook-driven than
  `summary.md`.
- X needs a cleaner opening and simpler pacing than the analytical summary.

**How we summarized for social**

- Lead with the claim: “The US housing market has gotten materially tighter.”
- Use a concrete before/after statistic: `12.1%` to `10.1%`.
- Explain why it matters: vacancy is a signal of housing slack.
- Use the weighted metro figure as supporting evidence that the tightening is
  broad.

**What worked**

- The draft now has separate voices for X and Substack while keeping the same
  facts.
- The thread structure naturally moves from headline to explanation to broader
  implication.

**What did not work as well**

- The current X draft is measured rather than maximally punchy. That may be the
  right default, but it could still use a future polish pass if we want a more
  aggressive posting style.

---

## Reusable takeaways

- Start with the cleanest headline geography first when introducing a topic.
- Separate EDA from production SQL so tradeoffs stay legible.
- Test whether “average” comparison lines are actually comparable before putting
  them on a chart.
- Validate renderer formatting assumptions, especially around percents.
- Review axis fairness after the first render, even if the chart looks polished.
- Keep `summary.md` analytical and let `post_draft.md` do the platform-specific
  work.
