# POI Taxonomy — Follow-up Fixes

Work identified during the 2026-09-11 taxonomy cleanup but deliberately not
done, because each touches a contract or another engine and deserves its own
review. Ordered by risk.

Context: [`TAXONOMY.md`](TAXONOMY.md) is the canonical reference. The governed
taxonomy is 271 rules + 50 split leaves in `overture_taxonomy.yml`, applied by
`classify_overture_places.py`, serving 22 categories and 117 sub-categories
across two CBSAs.

---

## 1. Corridor Intelligence pins a dead mapping version — **broken today**

**File:** `metro-deep-dive-program/engines/corridor_intelligence/inputs/corridor_inputs_v1.yml`

Four references to a mapping version that no longer exists:

```yaml
poi:
  required_mapping_version: q4_overture_v1        # line 81
  eligible_categories: [grocery, pharmacy, hospital, school, university]
markets:
  jacksonville_fl:
    poi:
      mapping_version: q4_overture_v1             # line 106
  richmond_va:
    poi:
      mapping_version: q4_overture_v1             # line 121
```

Two distinct problems:

**The version pin is stale.** Classification now emits `q4_overture_v3`. No
code enforces `required_mapping_version`, so nothing failed — the contract is
declarative. That is why this went unnoticed and why it needs a deliberate fix
rather than a silent one.

**`eligible_categories` no longer exist.** Those five are v1/v2-era governed
category names. Under the current taxonomy they are Category / Sub Category
pairs:

| Old governed category | Current Category | Current Sub Category |
|---|---|---|
| `grocery` | Retail | Grocery & Food Retail |
| `pharmacy` | Retail | Pharmacy & Drug Stores |
| `hospital` | Healthcare | Hospitals & Emergency |
| `school` | Education | K-12 |
| `university` | Education | Higher Education |

**Fix:** decide whether corridor eligibility selects on Category, Sub Category,
or an explicit pair list, then update the YAML and bump
`required_mapping_version` to `q4_overture_v3`. This is a corridor-engine
decision about what the analysis needs — do not guess it from the POI side.

**Also:** the `classified_artifact` and `tract_assignment_artifact` paths in
that file point at specific run directories. Those runs were re-classified on
2026-09-11, so the files still exist but their **contents changed** — they now
carry `category`/`sub_category`/`taxonomy_detail` instead of
`governed_category`. Any consumer reading those columns needs updating.

## 2. Consider enforcing the mapping-version pin

A declarative contract that nothing checks will drift again. Cheapest fix: have
the corridor engine read `mapping_version` from the classified parquet and fail
loudly on mismatch with `required_mapping_version`. Roughly the same shape as
the invariant gate in `build_taxonomy_hierarchy_profile.py`.

## 3. Documentation referencing superseded artifacts

Both still describe the retired exact-`taxonomy.primary` matcher as current:

- `metro-deep-dive-program/engines/poi/POI_ENGINE_BUILD_PLAN.md:197` — cites
  `taxonomy/q4_overture_v1.yml` as the classifier's registry
- `metro-deep-dive-program/engines/poi/NOTES.md:115` — "The first approved
  mapping registry, `q4_overture_v1`…"

`NOTES.md` is an audit log, so its Epic 4 entry is legitimately historical —
consider appending a dated entry rather than editing the record.
`POI_ENGINE_BUILD_PLAN.md` describes intended current state and should be
updated.

## 4. `CONTRACT.md` field list is out of date

`metro-deep-dive-program/engines/poi/CONTRACT.md:74` requires each
`poi_classified_place` to retain `mapping_version`, `mapping_status`,
`mapping_rule_id`, `mapping_evidence`, `review_status`. All five are still
emitted — but the contract does not mention `category`, `sub_category`,
`taxonomy_detail`, or `cbsa_code`, which are now first-class governed columns.

The contract also describes a single `governed_category` label. That column no
longer exists; it was replaced by the two-level pair. Update the taxonomy
section to describe three layers and note that Detail is an ungoverned
passthrough with partial coverage.

## 5. Stale run artifacts on disk

Run directories under `engines/poi/outputs/` retain superseded files:

- `poi_taxonomy_assignment.parquet` — from a design we abandoned; nothing reads it
- `poi_taxonomy_rule.parquet` — the rules are read from YAML now
- Earlier `taxonomy_profile/` outputs under old filenames

Harmless today, because `publish_poi_mart.py` names its artifacts explicitly.
But a stale file under an old name **did** cause a silent bad publish during
this cleanup: the publish script looked for
`poi_taxonomy_hierarchy_tag_profile.parquet` while the profiler had started
writing `poi_taxonomy_hierarchy_tag.parquet`, and an old file satisfied the
lookup. Consider having the profiler clear its output directory, or stamping
artifacts with the run ID.

`engines/poi/outputs/` is gitignored, so this is local-only cleanup.

## 6. Open taxonomy decisions

Not bugs. Deliberate parking spots, listed in `TAXONOMY.md` §7.

- **87 funeral homes** on `UNRESOLVED_funeral`. Neither v1 doc has a home for
  them. Candidates: a new Services sub-category, or Community & Civic.
- **15 rules flagged** `not_in_v1_docs` / `new_in_jacksonville`, assigned
  provisionally by source root.
- **Three deliberate overrides** of the source hierarchy (senior living, social
  clubs, cemeteries). Cemeteries rest on 6 Richmond places — worth re-checking
  against a market with real volume.
- **Financial Institutions ~+646** vs the v1 doc's estimate. Boundary is right,
  projection was wrong. Worth a correction note in the layer doc.

## 7. Multi-market validation is manual

`validate_taxonomy_rules.py` runs one market at a time, and a seed valid in one
market can be incomplete in another — Jacksonville needed 10 rules Richmond
never exercised. A loop over all declared markets in
`sources/overture_places.yml`, failing if any market fails, would make the
"valid seed" claim mean something across the portfolio.
