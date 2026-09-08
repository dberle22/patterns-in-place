# POI Taxonomy Guide

This guide explains how source labels become stable, reviewable POI categories.
It is separate from Q4: the engine describes a place; Q4 decides how to use it.

## Three label layers

| Layer | Example | Owner | Meaning |
|---|---|---|---|
| Source taxonomy | Overture `taxonomy.primary = supermarket` | Source | What the provider calls the place. |
| Governed category | `grocery` | POI Engine | Stable descriptive label reusable across analyses. |
| Analysis basket | `daily_needs` | Q4 | Analysis-specific grouping of governed categories. |

A `supermarket` is a source label, `grocery` is the engine category, and
whether `grocery` belongs in `daily_needs` is Q4's decision.

## Flow for one place

```text
source record
  → preserve source ID, address, geometry, and raw labels
  → validate ID and representative-point coordinates
  → compare its source taxonomy to approved rules
  → publish a mapped record or an explicit review-queue record
  → analysis may select governed categories into a basket
```

For an Overture record where `taxonomy.primary = supermarket`, the current
rule produces `governed_category = grocery`, `mapping_status = mapped`,
`mapping_rule_id = overture_supermarket`, and evidence reading
`exact taxonomy.primary = supermarket`. Its original source value stays on the
record. This does not automatically place it in a score, catchment, or corridor.

## Current matching rule

The first rule registry is [q4_overture_v1.yml](q4_overture_v1.yml). It uses
an **exact match** on Overture's preserved `taxonomy.primary`. It does not use
substring matching, keywords, scoring, or first-match ordering.

| Source value | Governed category | Rule ID |
|---|---|---|
| `grocery_store` | `grocery` | `overture_grocery_store` |
| `supermarket` | `grocery` | `overture_supermarket` |
| `specialty_grocery_store` | `grocery` | `overture_specialty_grocery_store` |
| `hospital` | `hospital` | `overture_hospital` |
| `pharmacy` | `pharmacy` | `overture_pharmacy` |
| `school` | `school` | `overture_school` |
| `university` | `university` | `overture_university` |

Multiple precise source labels may roll into one governed category. The source
label is always retained alongside the governed result.

## Unmapped, ambiguous, and overrides

If no approved rule matches, the valid place remains in the output with
`mapping_status = unmapped`, `review_status = needs_review`, and no governed
category. It is written to `poi_unmapped_review.parquet`; it is never deleted.

The first rule set has no overlaps, so it cannot produce an ambiguous automated
match. `poi_ambiguous_review.parquet` exists for future mapping versions.

An override is a durable, reviewed, place-specific correction—for example, a
provider error for one named place. Overrides do not exist yet. When added,
they must be versioned, retain a reason, link to the source record, and win
over an active automated rule.

## Adding a category

1. Profile unmapped source values and inspect real records.
2. Confirm the label is a stable descriptive category, not an analysis basket.
3. Add a unique exact rule in a new mapping version.
4. Record rationale, inspect counts/samples, and rerun classification.

Do not map based only on a similar word. For example, a broad
`food_and_beverage_store` rule needs review before it can be treated as grocery.

## Multiple source lanes

Overture, official specialist, and curated/article sources can use this same
workflow while keeping their own IDs and provenance. A shared governed category
does not make records the same entity. OSM physical geometry remains in the
Infrastructure Engine; only intentionally place-like OSM records enter here.
