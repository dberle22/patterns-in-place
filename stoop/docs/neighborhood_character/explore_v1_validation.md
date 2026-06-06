# Stoop Explore V1 Validation

Last updated: 2026-05-08

## Purpose

This note records the first live validation pass for Stoop Explore MVP
intelligence after building the `neighborhood_character_mart`.

The goal is not to prove the system is perfect. The goal is to check whether
the first category-led outputs broadly match New York intuition, and to expose
where category coverage or ranking rules still need tuning before Sprint 3.

## Validation Set

These neighborhood × category pairs were chosen to include both expected wins
and likely misses.

| NTA | Category | Why this pair matters |
| --- | --- | --- |
| Williamsburg | restaurants | Should validate as a destination food area |
| Williamsburg | shopping | Should show strong destination-shopping energy |
| Williamsburg | bars | Good test of nightlife under current coverage |
| Greenwich Village | bookstores | Canonical bookstore expectation |
| East Village | record_stores | Canonical specialty retail / music-adjacent expectation |
| Midtown-Times Square | hotels | Strong control case for visitor-oriented ranking |
| Upper East Side-Carnegie Hill | museums | Strong control case for cultural-core ranking |
| Chelsea-Hudson Yards | museums | Useful miss test; likely under-covered in curated data |
| Lower East Side | music_venues | Good test of whether nightlife/music coverage is already usable |

## Live Results

Source: `neighborhood_character_mart.nta_category_density`

| NTA | Category | Rank | Tier | Result |
| --- | --- | --- | --- | --- |
| Williamsburg | restaurants | 10 | `destination` | Match |
| Williamsburg | shopping | 1 | `destination` | Strong match |
| Williamsburg | bars | 7 | `present` | Partial match |
| Greenwich Village | bookstores | 4 | `destination` | Strong match |
| East Village | record_stores | 1 | `destination` | Strong match |
| Midtown-Times Square | hotels | 1 | `destination` | Strong match |
| Upper East Side-Carnegie Hill | museums | 1 | `destination` | Strong match |
| Chelsea-Hudson Yards | museums | 8 | `limited` | Miss |
| Lower East Side | music_venues | 3 | `destination` | Positive surprise |

## What matched intuition

- The system already produces credible destination-level signals for
  `restaurants`, `shopping`, `bookstores`, `record_stores`, `hotels`, and
  `museums`.
- Williamsburg performs well as an Explore neighborhood even without extra
  narrative logic. It already lands as `destination` for both restaurants and
  shopping.
- Midtown-Times Square and Upper East Side-Carnegie Hill behave as useful
  control cases. That is a good sign that the basic NTA ranking logic is
  working.
- Lower East Side ranking `destination` for `music_venues` suggests that this
  category may already be more usable than expected, even if it remains
  app-hidden for now.

## What missed or needs caution

- `bars` remains directionally useful but underpowered. Williamsburg shows up,
  but only as `present`, not `strong` or `destination`.
- `museums` looks too thin outside the clearest museum-heavy NTAs. Chelsea
  landing `limited` does not match many users' intuitive picture of the area as
  a strong arts destination.
- `bookstores`, `record_stores`, and `museums` can produce good headline
  results, but their total category counts are still small enough that the
  output should be treated as MVP-grade rather than fully stable.

## Recommended first tuning pass

Keep tuning tightly scoped in Sprint 2.

1. Keep `restaurants`, `shopping`, `bookstores`, `hotels`, `bakeries`,
   `food_markets`, `specialty_grocery`, `record_stores`, and `bars` in the
   Explore control table for now.
2. Keep `music_venues` hidden in the app for now. It can stay in the
   background as a useful signal, but it should not become a front-door Explore
   category in v1. If someone is traveling for music, the draw is more often
   the artist or event than the neighborhood alone.
3. Keep `bars` visible in v1 specifically because the weak Williamsburg result
   is useful feedback; it makes the data gap visible instead of hiding it.
4. Avoid changing the global ranking method in Sprint 2. Raw count plus
   subcategory-diversity tie-break is behaving reasonably well.
5. Treat the first likely tuning lever as per-category evidence thresholds and
   category visibility, not a more complicated score.

## Confirmed tuning decisions

These were the decisions taken after the first validation pass.

- `music_venues` stays hidden in the app for v1.
- `museums` stays live as-is. In the future, a separate `art_galleries`
  category should help neighborhood stories like Chelsea that are not captured
  well by institutional museum coverage alone.
- Sprint 2 sign-off standard is "good enough to ship with known blind spots,"
  not "hold until coverage is comprehensive."

## Coverage expansion ideas

The first release should be explicit about where better source coverage would
improve the Explore layer most.

- **Bars**: add more editorial bar and cocktail coverage. Williamsburg landing
  only `present` is a strong sign that nightlife coverage is still thin.
- **Shopping**: keep expanding neighborhood-specific and specialty retail
  articles so more shopping districts can compete with Williamsburg and SoHo.
- **Art galleries**: create a future standalone curated category rather than
  expecting `museums` to carry all arts-oriented neighborhoods.
- **Bookstores and record stores**: these categories are already useful, but
  more source depth would make the lower ranks feel less brittle.
- **Restaurants**: coverage is strong enough for MVP, but broadening cuisine and
  neighborhood spread will make the long tail more trustworthy.

## Recommended Sprint 2 disposition

- The validation-set build task can be considered complete.
- The tuning review can be considered complete.
- Explore intelligence can move to Sprint 3 as a ship-ready MVP with known
  blind spots.

## Post-App Integration Check

Updated: 2026-05-10

Sprint 3 integrated the Explore panel directly against:

- `neighborhood_character_mart.nta_category_controls`
- `neighborhood_character_mart.nta_category_density`
- `neighborhood_character_mart.nta_character_profile`

That means the app now renders the same precomputed category visibility,
ranking order, and "known for" fields that the validation queries reviewed in
Sprint 2, rather than re-deriving them in the frontend.

Quick integration check against the local mart:

- Enabled Explore categories still match the intended v1 visible set:
  `bakeries`, `bars`, `bookstores`, `food_markets`, `hotels`, `museums`,
  `record_stores`, `restaurants`, `shopping`, `specialty_grocery`.
- Top 5 `restaurants` neighborhoods remain:
  East Village, West Village, SoHo-Little Italy-Hudson Square,
  Midtown South-Flatiron-Union Square, Midtown-Times Square.
- Top 5 `hotels` neighborhoods remain:
  Midtown-Times Square, Upper East Side-Carnegie Hill,
  SoHo-Little Italy-Hudson Square, Midtown South-Flatiron-Union Square,
  Financial District-Battery Park City.
- Williamsburg still profiles as `top_category = restaurants` with
  `destination_categories = restaurants|shopping` and
  `strong_categories = bookstores|food_markets`.

Observed regression status:

- No ranking or profile regressions found at the app-read layer.
- The remaining risks are coverage and presentation risks, not query drift.
