# Findings — Regional Vacancy Trends

**Written:** after EDA  
**Status:** complete

---

## Key Stats

- There are `5` clean annual series with complete vacancy-rate coverage from
  `2012` through `2024`: the `US` plus the `4` Census regions.
- All four regions saw vacancy rates decline from `2019` to `2024`:
  `South` fell from `14.0%` to `11.7%` (`-2.3pp`),
  `Northeast` from `11.8%` to `9.6%` (`-2.2pp`),
  `Midwest` from `11.4%` to `9.4%` (`-2.0pp`),
  and `West` from `10.0%` to `8.5%` (`-1.5pp`).
- In `2024`, the regions line up as `West` (`8.5%`), `Midwest` (`9.4%`),
  `Northeast` (`9.6%`), and `South` (`11.7%`), versus a `10.1%` US vacancy
  rate.
- The `West` is below the US line in every year from `2019` through `2024`,
  while the `South` is above it in every year across the same window.
- The gap between the tightest and loosest regions narrowed from `4.0pp` in
  `2019` to `3.1pp` in `2024`, so the regions moved closer together but did not
  fully converge.
- The broad rank order is highly stable: `West` is the tightest region in every
  year from `2012` through `2024`, and `South` is the loosest in every year.

## Confirmed Angle

The data confirms the regional story works well as a five-line trend chart. The
best framing is that housing slack has compressed across every major region
since 2019, but the regional hierarchy has barely changed: the West remains the
tightest part of the country, the South remains the loosest, and the Midwest
and Northeast sit in the middle.

## Surprises

- The strongest surprise is how stable the rank order is. There is no dramatic
  regional reshuffling after 2019 even though every line moves down.
- The `South` shows the biggest absolute decline (`-2.3pp`) but is still the
  loosest region in `2024`, so the biggest tightening does not equal the
  tightest current market.
- The `Northeast` is not on a simple long-run decline. Its vacancy rate rose
  from `11.1%` in `2012` to `11.8%` in `2019` before falling sharply after
  that.
- Regional convergence is real but limited. Even after five years of decline,
  the `2024` spread across regions is still more than `3` percentage points.

## Data Notes

- Source table is `gold.housing_core_wide`.
- `vacancy_rate` is stored as a decimal, so values should be multiplied by
  `100` for display.
- The relevant comparison set is `geo_level in ('us', 'region')`.
- Source labels are `Northeast Region`, `Midwest Region`, `South Region`, and
  `West Region`; shorter display labels can be applied later in chart SQL.
- Coverage is complete for the full `2012`-`2024` regional file, with no null,
  NaN, or infinite `vacancy_rate` values.

## What We're Not Showing

- We are not explaining the causal drivers behind why the `West` is
  persistently tighter or why the `South` remains looser.
- We are also not drilling down to states or metros here, even though those
  follow-on views help explain the regional lines in more detail.
