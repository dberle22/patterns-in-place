# Findings — National Vacancy Rate Trend

**Written:** after EDA  
**Status:** complete

---

## Key Stats

- US vacancy rate was `12.1%` in 2019 and `10.1%` in 2024, a `-2.0 percentage
  point` decline over five years.
- Every year from 2020 through 2024 was lower than the year before:
  `11.6%`, `11.2%`, `10.8%`, `10.4%`, `10.1%`.
- Before 2019, the national series was relatively flat, staying between `12.1%`
  and `12.5%` from 2012 through 2019.
- The largest one-year decline in the series was from 2019 to 2020
  (`-0.5pp`), followed by four more annual declines.

## Confirmed Angle

The data confirms the core hypothesis: the national housing market has tightened
meaningfully since 2019, and the decline in vacancy is steady enough to make a
clean national trend chart. The best framing is that the US has moved from a
long period of relative stability into a clear post-2019 tightening cycle.

## Surprises

- The national line is flatter before 2019 than expected. Most of the real
  movement is concentrated in the 2020-2024 period.
- Adding a "US metro average" comparison is less straightforward than it looked
  in the question brief. In 2024, the unweighted CBSA average is `13.0%`, the
  CBSA median is `11.3%`, and a housing-unit-weighted CBSA rollup is `9.4%`,
  versus the true US rate of `10.1%`.
- That spread suggests metro benchmarks are useful for exploration, but they are
  not clean apples-to-apples companions for the national headline chart.

## Data Notes

- Source table is `gold.housing_core_wide`.
- `vacancy_rate` is stored as a decimal, so values should be multiplied by `100`
  for display.
- The clean national series comes from `geo_level = 'us'`.
- Coverage is complete for the US series from 2012 through 2024, with no null,
  NaN, or infinite `vacancy_rate` values.
- Smaller geographies such as tract, ZCTA, and place contain some `NaN`
  vacancy-rate values, but those do not affect this insight.

## What We're Not Showing

- We are not showing state or regional variation here, even though the EDA
  confirms meaningful differences across those geographies, because those are
  stronger as standalone follow-on posts.
