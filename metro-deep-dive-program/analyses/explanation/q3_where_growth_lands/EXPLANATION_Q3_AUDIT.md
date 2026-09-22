# Explanation Q3 — Epic 1 Audit

**Status:** Complete — method alignment still required before Epic 2

**Audit date:** 2026-09-22

**Warehouse reviewed:** `foundations/etl/data/duckdb/patterns_in_place.duckdb`

## Decision summary

Q3 can build a nationally reusable, locally read method for locating population
and housing growth. The primary evidence can be a harmonized tract panel, with
county and Census Place summaries as named-location reporting lenses. The
existing 2010-to-2020 temporal crosswalk is fit to reuse as the relationship
and allocation interface; Q3 must still construct the metric-specific panel
and disclose its allocation assumptions and exceptions. It does not need to
build a new tract crosswalk.

The audit does **not** support making an infill/greenfield classification the
question's primary result. Those are site-development concepts that require a
separate, defensible built-footprint standard. The more supportable primary
question is where growth is landing: near existing centers, in outlying
counties, in named Places, or in other recurring spatial patterns. A later
infill/greenfield lens may be retained only if it adds explanatory value after
the growth geography is visible.

Q2 currently supplies physical proximity to reviewed job-center tracts, not a
15-minute access surface. Q3 may join that explicitly labeled proximity result
when relevant, but cannot describe it as travel, access, or a 15-minute area.

## What exists in the live warehouse

### Temporal tract crosswalk

`silver.xwalk_temporal` is a national 2010 Census tract to 2020 Census tract
relationship table. It has separate `population`, `housing_units`, and
`land_area` weight bases, allocation denominators and numerators, weight-sum
diagnostics, `change_type`, and `quality_flag`.

For population and housing units, the table routes 2010 PL 94-171 block counts
through Census 2010-to-2020 block intersections using intersection land area.
Land area uses the Census tract relationship file directly. This makes the
population and housing weights an areal-interpolation model, not observed
annual population or housing placement.

The 2010 source cohort has 73,057 tracts. For both population and housing
weights, 72,507 source tracts are fully allocated, 24 are partial, and 526 have
zero denominators. The partial count-weight sources have a maximum weight-sum
shortfall of about 0.66%. `change_type` identifies unchanged, split, and
redrawn relationships and must remain in Q3 QA and interpretation.

**Audit decision:** reuse this temporal relationship. Epic 2 remains genuine
panel construction: select source estimates, apply the matching count weights,
retain quality fields, and visibly report residual/error behavior. Do not build
another temporal crosswalk unless validation exposes a metric-specific failure.

### Population, housing, and built-condition inputs

`gold.housing_core_wide` supplies populated tract rows for 2012–2024. Its
tract series has 73,056 rows in each 2012–2019 vintage and about 84,400 in
2020–2024, matching the expected boundary-vintage break. All current rows have
the audited Q3 basics populated: `pop_total`, `hu_total`, `occ_vacant`, and the
housing structure counts and shares.

The useful prior-condition fields are `pop_total`, `hu_total`,
`vacancy_rate`/`occ_vacant`, `struct_*`, and `pct_struct_*`. A tract population
density metric is also available from `gold.transport_built_form_wide`, but its
geometry provenance must be checked before it is used for analytical footprint
classification; the current geography catalog labels `geo.tracts_all_us` as
display-only for analytical spatial work.

The ACS staging tables retain margins of error, while the Gold mart retains
estimates only. Any short-window growth call needs a reliability rule that
either brings the relevant ACS MOEs back into the analysis or avoids presenting
small estimate differences as observed growth. The 2012–2024 values are annual
ACS 5-year releases, so adjacent estimates overlap and are not independent
annual observations.

### County and Census Place lenses

Direct county and Place population/housing histories exist in
`gold.housing_core_wide` for 2012–2024. County is the cleanest named-location
lens: it has exact county-to-CBSA containment and nearly complete permit
coverage. Direct Place rows are useful for identifying named growth locations,
but the governed exact-relationship surface has no Place-to-county or
Place-to-CBSA edge. Q3 has therefore opened a Geography-engine epic to build a
2020 weighted Place-to-CBSA membership interface and a declared primary-CBSA
association. It must retain split memberships and unincorporated geography;
neither may disappear behind a primary association.

The existing tract-to-Place allocation interface is 2020-only, metric-specific,
and explicitly an allocation rather than containment. It is the appropriate
foundation for the new governed membership surface, not an automatic exact
metro membership rule.

### Permits

`gold.housing_core_wide` has no tract or ZCTA permit observations: all
1,006,492 tract rows have null permit units. Permit coverage is 94.5% of
county-year rows, 98.7% of CBSA-year rows, and 42.1% of Place-year rows. Q3
must retain permits at their native county, Place, or CBSA grain; it must never
assign them to tracts.

### Q2 relationship

Q2 has published candidate-center and tract-distance output in
`mart_explanation_q2` for its reviewed 2023 LODES WAC job-center versions. Its
V0 proximity is centroid-to-centroid Haversine miles to the nearest
candidate-center tract. It is physical proximity only, not a network route,
commute, travel time, or 15-minute-access measure.

**Audit decision:** Q3 may use this as a labeled optional explanatory gradient
after the growth geography is established. It does not yet have a Q2 access
surface to adopt.

## Recommended output structure for alignment

The evidence should proceed from observed geography to interpretation:

1. **Coverage and method panel:** comparison years, ACS vintages, tract
   harmonization coverage/quality, and reliability treatment.
2. **Metro growth ledger:** total population and housing-unit change, then the
   shares attributable to counties, named Places, and the remaining
   unincorporated/split geography.
3. **Native-grain location lenses:** harmonized tract map/table; direct county
   change table; Place change table with its association and coverage labels.
4. **Pattern reads:** concentration versus dispersion, growth near existing
   job centers (physical proximity only), and outlying-county/Place patterns.
5. **Separate permit context:** county/Place/CBSA permits beside—not allocated
   into—the growth evidence.
6. **Residuals:** no-growth/decline and unclassified/association-ambiguous
   units remain visible.

This structure makes “where growth lands” the conclusion and leaves
infill/greenfield as an optional subsequent classification rather than a
prerequisite.

## Epic 1 disposition

| Required audit question | Finding | Disposition |
|---|---|---|
| Temporal crosswalk coverage, weights, change types, and QA | Present and metric-specific for 2010 to 2020 tracts | Reuse relationship; construct Q3 panel with disclosure. |
| Population and housing tract coverage | Populated 2012–2024; boundary break visible in 2020 | Select a non-overlapping ACS comparison interval and reliability policy. |
| Permit coverage by grain | County/CBSA strong; Place partial; tract/ZCTA absent | Native-grain context only. |
| Prior density/built condition | Housing stock, vacancy, and structure context available; density needs geometry-role validation | Use as descriptive context first; do not force footprint classes. |
| Q2 method to adopt | Reviewed job-center physical proximity, not access | Optional explanatory proximity lens, not 15-minute result. |
| Is harmonization solved? | The relationship is solved; metric panel construction and validation remain | Epic 2 is required but does not require a new crosswalk. |

## Required decisions before Epic 2

1. Should Q3's primary product be the growth-location ledger and pattern read
   described above, with infill/greenfield deferred to an optional later lens?
2. Which comparison period should define “recent” growth, given ACS 5-year
   overlap and the 2010/2020 tract break?
3. Confirm the Geography-owned Place-to-CBSA membership contract before Q3
   consumes direct Place estimates.
4. Decide whether short-horizon signals warrant a Q3-scoped ACS MOE check
   before publication; a platform-wide MOE mart is not a Q3 prerequisite.
