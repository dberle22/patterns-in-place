# POI Taxonomy

Canonical reference for the POI Engine's governed taxonomy. Start here.

Companion documents:
- [`taxonomy_category_layer_v1.md`](taxonomy_category_layer_v1.md) — what belongs
  in each Category, and why
- [`taxonomy_sub_category_layer_v1.md`](taxonomy_sub_category_layer_v1.md) — the
  same for Sub Category

Those two carry the **category intent** and remain authoritative for meaning.
This document is the **mechanism**: the fields, the rule, the pipeline, and how
to change any of it.

---

## 1. The three layers

| Layer | Source field | Governed? | Distinct values | Coverage |
|---|---|---|---|---|
| **Category** | `basic_category` | Yes — 22 names | 22 | 96.2–96.7% |
| **Sub Category** | `basic_category`, plus `taxonomy.primary` on split rules | Yes — 117 names | 117 | same |
| **Detail** | `taxonomy.primary` | No — passthrough | ~1,300 per market | 59–61% |

Category and Sub Category are what we maintain. Detail is optional and exists
for specific analyses; it is never cleaned or governed.

Current state, Overture `2026-08-19.0`:

| CBSA | Market | Places | Mapped | Categories | Sub Categories | Detail |
|---|---|---:|---:|---:|---:|---:|
| 40060 | Richmond, VA | 61,513 | 59,459 (96.7%) | 22 | 117 | 59.0% |
| 27260 | Jacksonville, FL | 86,933 | 83,597 (96.2%) | 22 | 117 | 60.9% |

Every unmapped place is null at source (`mapping_evidence = 'no source
category'`). **No place is unmapped for want of a rule.**

## 2. The source fields

Overture's field names are actively misleading. `basic` sounds legacy and
`primary` sounds current; it is the other way around.

| Extract column | Overture property | Status |
|---|---|---|
| `source_category_basic` | `basic_category` | **Current. The assignment key.** |
| `source_taxonomy_primary` | `taxonomy.primary` | Current. Splits and Detail. |
| `source_taxonomy_hierarchy` | `taxonomy.hierarchy` | Current. Validation only. |
| `source_category_primary` | `categories.primary` | **Deprecated**, removed in the September 2026 release. Do not build on it. |

If that ever reads backwards, check a row with `source_category_basic =
food_and_drink` and `source_category_primary = eat_and_drink`. The new
vocabulary is the `basic` column.

### Why `basic_category` is the key

It is a clean function: each basic value sits at exactly one place in the
hierarchy, so one basic yields one Category and one Sub Category. At 258–267
values per market it is a reviewable surface, and it survives the September
release.

It also preserves distinctions the hierarchy merges. `fast_food_restaurant` and
`cafe` both roll up to `casual_eatery` at hierarchy depth 2, but the v1 docs
place them in Quick Service and Cafes & Coffee respectively. Keying on `basic`
keeps that split; keying on depth 2 would lose it.

### What `taxonomy.hierarchy` is for

An ordered array, broadest to narrowest. Two invariants hold on **every**
non-null row across both markets — 141,521 rows, zero exceptions:

```
list_contains(hierarchy, basic_category) = true
hierarchy[-1]                            = taxonomy_primary
```

So `basic_category` and `taxonomy.primary` are positions on one path, not
parallel vocabularies. We do not assign from the hierarchy, but we check it:
if either invariant breaks, the source has restructured and the seed's
assumptions no longer hold. `build_taxonomy_hierarchy_profile.py` enforces this.

## 3. The rule

```
Category    := seed[basic_category].category      (split leaf overrides)
SubCategory := seed[basic_category].sub_category  (split leaf overrides)
Detail      := taxonomy_primary, or NULL where it equals basic_category
```

**271 base rules + 50 split leaves**, all in
[`overture_taxonomy.yml`](overture_taxonomy.yml).

A split rule fires when `basic_category` alone cannot decide. It is keyed on
`taxonomy.primary` and wins over its row default. These correspond exactly to
the rows the v1 sub-category doc marks `[T]`:

| Basic value | Split decides |
|---|---|
| `personal_or_beauty_service` | Hair & Barber / Nail & Beauty / Tattoo |
| `financial_service` | Financial Institutions vs Services (money vs advisory) |
| `animal_or_pet_service` | Healthcare (veterinary) vs Personal Care (grooming) |
| `shipping_or_delivery_service` | Government (postal) vs Industrial (courier) |
| `family_service` | Education (childcare) vs Community & Civic |
| `research_institute` | Healthcare (medical) vs Education |
| `sport_or_fitness_facility` | Gyms & Fitness vs Sports Facilities |

Exactly one rule fires per place. No first-match ordering, no ambiguity.

### Detail coverage is structural, not a defect

For ~40% of places the source leaf **is** the browsable node — `basic_category
== taxonomy_primary` — so no finer value exists. That is `historic_site` (921),
`restaurant` (806), `gas_station` (701), `atm` (638). Detail is null there by
design. Coverage varies sharply by category: Personal Care 96.6%, Services
76.7%, but Arts 4.6% and Parks 3.8%. Check coverage before building an analysis
on Detail.

## 4. The pipeline

```
sources/overture_places.yml         source release, S3 path, market → CBSA code
  ↓ acquire_overture_places.py      CBSA boundary from Geography Engine; S3 pull
overture_places_source.parquet      immutable per-run cache
  ↓ normalize_overture_places.py    contract fields, validation, representative point
normalized/poi_source_place.parquet
  ↓ classify_overture_places.py     ← READS overture_taxonomy.yml
classified/poi_classified_place.parquet    category, sub_category, taxonomy_detail
  ↓ assign_poi_geography.py         tract / county / postal ZIP
  ↓ publish_poi_mart.py             → mart_poi.* tables
```

Supporting, not in the path:

| Script | Purpose |
|---|---|
| `validate_taxonomy_rules.py` | Checks the seed against a classified run |
| `build_taxonomy_hierarchy_profile.py` | Hierarchy invariants and vocabulary drift |
| `TAXONOMY_EXPLORATION_NOTEBOOK.py` | Two-table review: Rules and Counts |

**The YAML is the single source of truth.** The classifier reads it, the
validator reads it, the notebook reads it. It is never copied into the mart —
a published copy could only drift from the contract.

## 5. Market handling

`market_id` **is** the CBSA code, resolved at acquisition against
`mart_geography.rollup_county_to_cbsa`. Every mart table carries `cbsa_code`,
so markets can be filtered and joined:

```sql
SELECT cbsa_code, category, count(*)
FROM mart_poi.poi_classified_place
WHERE category = 'Retail'
GROUP BY 1, 2
```

Publishing is **delete-then-insert per CBSA**. Re-running a market replaces
that market's rows and leaves others untouched. POI history is not retained:
the newest run per CBSA is the only one served. Never a bare `INSERT` — that
would double rows on a re-run.

## 6. Changing the taxonomy

There is **one** seed file and it is never versioned by filename. Git history
is the changelog. Do not create `overture_taxonomy_v2.yml`.

1. Edit [`overture_taxonomy.yml`](overture_taxonomy.yml).
2. `python3 taxonomy/validate_taxonomy_rules.py --market richmond_va --write-profile`
3. Repeat for every other market — a seed valid in one may be incomplete in another.
4. `python3 classify_overture_places.py --market <market>`
5. `python3 assign_poi_geography.py --market <market>`
6. `python3 publish_poi_mart.py --market <market>`

Bump `mapping_version` inside the YAML only when the change is meaningful to a
downstream consumer. Category and Sub Category **names** are stable
identifiers: renaming one is a breaking change for any analysis selecting by
name.

### Adding a market

Declare it in `sources/overture_places.yml` with its CBSA code, run the
pipeline, then validate against an existing market as baseline:

```
python3 taxonomy/validate_taxonomy_rules.py --market <new> \
    --baseline-run-dir <existing run dir>
```

This reports basic values present in the new market and absent from the seed.
Jacksonville surfaced 10 that Richmond never had (`pier`, `castle`,
`general_hospital`, …). A hard fail here means a real gap; add rules and re-run.

### Quarterly Overture releases

Overture updates in March, June, September and December. Run
`build_taxonomy_hierarchy_profile.py` with `--baseline-run-dir` against the
prior release:

| Signal | Action |
|---|---|
| Invariant (§2) broken | **Hard stop.** Source restructured; do not publish |
| New hierarchy root | Category decision required |
| New basic value | Seed entry required before publish |
| New leaf only | Safe. Detail is passthrough |
| Retired value | Remove its rule |

Richmond → Jacksonville drift, for calibration: 0 new roots, 2 new depth-2
values, 186 new leaves, 94 retired.

## 7. Rules needing review

Query the notebook's Rules table on the `review` column.

| Flag | Count | Meaning |
|---|---:|---|
| `not_in_v1_docs` | 5 | Present in data, absent from both v1 docs; assigned by source root |
| `new_in_jacksonville` | 10 | Surfaced by market two; assigned by source root |
| `UNRESOLVED_funeral` | 87 places | Funeral homes have no home in either v1 doc. Parked deliberately, not filed silently |

Three Category calls deliberately override the source hierarchy. All three are
defensible; all three are decisions, not accidents:

| Basic value | Source root says | We say | Places |
|---|---|---|---:|
| `senior_living_facility` | `services_and_business` | Healthcare | 231 |
| `social_club` | `arts_and_entertainment` | Community & Civic | 27 |
| `cemetery` | `cultural_and_historic` | Community & Civic | 6 |

Also open: **Financial Institutions runs ~646 places above the v1 doc's
estimate**, because `insurance_agency` (564) and the advisory leaves outweigh
money services within `financial_service`. The category boundary is right; the
doc's volume projection was not.

## 8. History

`poi_categories.csv` was the first pass — 1,361 rows at `(basic, legacy
primary)` grain with 37 distinct category strings for 22 intended categories
(three spellings of Commercial, four of Government, one literal `0`).
Superseded by the v1 layer docs and removed.

`q4_overture_v1.yml` and `q4_overture_v2.yml` matched on exact
`taxonomy.primary` and mapped 19.3% of Richmond. Superseded by this seed and
removed; both remain in Git history.
