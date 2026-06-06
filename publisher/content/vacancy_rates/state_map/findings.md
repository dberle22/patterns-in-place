# Findings — State Vacancy Map

**Written:** after EDA  
**Status:** complete

---

## Key Stats

- There are `52` state-level rows with complete 2019 and 2024 vacancy data:
  the `50` states plus `District of Columbia` and `Puerto Rico`.
- Restricting to the contiguous map footprint leaves `49` geographies:
  the lower `48` states plus `DC`.
- The tightest contiguous-state housing markets in 2024 are `Connecticut`
  (`7.0%`), `Washington` (`7.3%`), and a three-way `7.5%` cluster of
  `New Jersey`, `California`, and `Oregon`.
- The loosest contiguous-state markets in 2024 are `Maine` (`20.6%`),
  `Vermont` (`19.4%`), `West Virginia` (`15.4%`), `Florida` (`14.7%`), and
  `Mississippi` (`14.6%`).
- The median 2024 vacancy rate across the contiguous footprint is `10.3%`,
  so the gap between the tightest and loosest states is large enough to read
  clearly on a national map.
- `48` of the `49` contiguous states plus `DC` saw vacancy rates decline from
  2019 to 2024. `District of Columbia` is the lone exception, edging up from
  `9.8%` to `10.1%` (`+0.3pp`).
- The biggest 2019 to 2024 declines are `Wyoming` (`-4.7pp`), `New Mexico`
  (`-4.3pp`), `Maine` (`-4.0pp`), `Arizona` (`-3.8pp`), and `Florida`
  (`-3.5pp`).
- The average state-level change is `-2.2pp`, with a median of `-2.1pp`.

## Confirmed Angle

The data confirms that the state story works best as two related but distinct
views: where vacancy is lowest today, and where vacancy has compressed the most
since 2019. The 2024 map will highlight a tight coastal-and-constraint pattern,
while the change story is more concentrated in the Mountain West, Sun Belt, and
high-vacancy vacation states. That makes the state map a strong follow-on to
the national trend because it shows both the geography of tightness and the
uneven pace of tightening.

## Surprises

- The tightest states are not the same as the fastest-tightening states. Among
  the top `10` tightest contiguous states, only `New Jersey` also appears in
  the top `10` biggest declines.
- Several states tightened sharply but are still loose in 2024, especially
  `Maine`, `Vermont`, `Florida`, `Wyoming`, and `New Mexico`.
- The loose end of the map is not only a rural story. High-vacancy states mix
  vacation-home markets in northern New England with Sun Belt and Gulf Coast
  states.
- `Puerto Rico` has the highest 2024 vacancy rate in the full state-level file
  at `21.0%`, but it should sit outside the default contiguous-US choropleth
  footprint.

## Data Notes

- Source table is `gold.housing_core_wide`.
- `vacancy_rate` is stored as a decimal, so values should be multiplied by
  `100` for display.
- The choropleth spec defaults national comparison maps to the contiguous `48`
  states plus `DC`, which lines up with this insight better than using the full
  state-level file.
- `Alaska` (`17.6%`) and `Hawaii` (`13.3%`) both declined from 2019 to 2024,
  but excluding them from the contiguous map should not change the core story.
- Because current tightness and 2019 to 2024 change overlap only weakly, a
  single map will need a deliberate choice about which measure is primary.

## What We're Not Showing

- We are not trying to explain the causal drivers of each state's vacancy
  change in this post.
- We are also not treating this as a precise state ranking chart. The stronger
  editorial use is spatial pattern first, exact ordering second.
