# Findings — Metro Vacancy Rankings

**Written:** after EDA  
**Status:** complete

---

## Key Stats

- There are `935` CBSA rows for 2024 with complete vacancy, housing-unit, and
  population coverage after joining `gold.housing_core_wide` to
  `gold.population_demographics`.
- Applying the question brief's `250k+` population filter leaves `197` major
  metros to rank.
- The tightest major metros in 2024 are `Lancaster, PA` (`3.0%`),
  `Provo-Orem-Lehi, UT` (`3.8%`), `Modesto, CA` (`3.9%`), `Greeley, CO`
  (`4.1%`), and a three-way `4.4%` cluster of `Madison, WI`,
  `York-Hanover, PA`, `Vallejo, CA`, and `Salem, OR`.
- The 20th-tightest major metro is still only `5.1%` (`Yakima, WA`), so the
  low-vacancy end of the ranking is tightly packed.
- The loosest major metros are `Atlantic City-Hammonton, NJ` (`33.4%`),
  `Naples-Marco Island, FL` (`30.7%`), `Seaford, DE` (`29.9%`),
  `Crestview-Fort Walton Beach-Destin, FL` (`27.5%`), and
  `Myrtle Beach-Conway-North Myrtle Beach, SC` (`27.0%`).
- The 20th-loosest major metro is `New Orleans-Metairie, LA` at `14.3%`,
  showing a much fatter upper tail than the tight end.
- Across all `197` major metros, the median vacancy rate is `8.0%` and the
  average is `9.5%`, both below the 2024 US rate of `10.1%`.
- `138` of `197` major metros are tighter than the US benchmark.

## Confirmed Angle

The data confirms that many large metros are operating with very little housing
slack in 2024. A metro ranking chart works, but the strongest version is not
just "coastal blue metros are tight." Instead, the clearer takeaway is that
most major metros are tighter than the national market, while the highest
vacancy rates are concentrated in a very different set of seasonal,
retirement-oriented, and tourism-heavy metros.

## Surprises

- The tightest metros are more mixed geographically than the initial hypothesis
  suggested. California does appear, but so do Pennsylvania, Utah, Wisconsin,
  Nebraska, Colorado, and Oregon.
- The tight tail is much less dramatic than the loose tail. Top-20 tight metros
  span only `3.0%` to `5.1%`, while the loose side stretches from `14.3%` to
  `33.4%`.
- Using all CBSAs would have badly distorted the story. The highest vacancy
  markets outside the filter are small seasonal places like `Nantucket`,
  `Vineyard Haven`, and `Breckenridge`, all above `57%`.

## Data Notes

- Vacancy rate comes from `gold.housing_core_wide`.
- Population for the major-metro filter comes from `gold.population_demographics`
  using the shared `geo_level + geo_id + year` key.
- `vacancy_rate` is stored as a decimal, so values should be multiplied by
  `100` for display.
- The `250k+` filter is doing real work here; without it, the CBSA average rises
  to `13.0%` and the max jumps to `58.3%`.

## What We're Not Showing

- We are not showing every major metro in the final editorial output, even
  though the EDA supports a full ranking table.
- We are also not trying to explain *why* each metro is tight or loose in this
  post. The vacancy ranking is descriptive and should stay focused on the 2024
  distribution.
