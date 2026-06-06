# Stoop Place Classification Implementation Plan

## Purpose

This document translates the place classification strategy into a concrete implementation plan for the current repo, with initial focus on restaurant reclassification and especially `mixed_restaurants`.

It is designed to implement the strategy defined in:

- [docs/stoop_place_classification_strategy.md]

and to build on the current work in:

- [sql/ddl/003_property_classification_mart.sql]
- [sql/marts/place_classification/place_classification_text.sql]
- [sql/marts/place_classification/place_word_profile.sql]
- [sql/marts/place_classification/place_phrase_profile.sql]
- [sql/qa/curated_categories.sql/category_retaurant_update.sql]

---

## Current State

The repo already has a promising foundation:

- a draft mart schema for classification workflow tables
- a text assembly table
- exploratory token and phrase profiling queries
- a QA script showing the first pass at `mixed_restaurants` cleanup

The main gap is that the system is not yet fully connected into a repeatable recommendation pipeline.

Right now the work is strongest in exploration and weakest in:

- contract consistency
- reusable rule management
- scoring logic
- ambiguity handling
- manual override workflow

---

## Implementation Goals

The implementation should produce a repeatable workflow that:

1. builds classification text from curated place metadata
2. profiles text to discover useful restaurant signals
3. stores production-approved mappings in a durable table
4. generates explainable keyword matches
5. scores classification candidates
6. emits recommendations with confidence
7. creates a manual review queue
8. applies durable overrides
9. publishes final classified output

---

## Key Design Corrections To Make First

Before building more logic, we should tighten a few structural issues.

### 1. Normalize ID naming

The current DDL mixes `poi_id` and `place_id`.

Recommendation:

- choose one identifier convention for the mart, use `poi_id` for consistency with the Gold layer.
- keep source table IDs mapped into that canonical field
- align all downstream SQL with that convention

This matters because the current DDL for `place_classification_text` defines `poi_id` but sets the primary key on `place_id`.

### 2. Align category field names with source truth

The current work references both `detail_level_3` and `details_level_3`.

Recommendation:

- standardize mart field naming. Use `detail_level_3` for now to match Gold Layer.
- preserve source field names only at extraction time
- use one downstream naming scheme consistently

### 3. Include all intended classification sources

The strategy and original plan include `google_types`, but the current text build does not yet include it.

Recommendation:

- include `google_types` in the text mart, but first check the Gold Layer and Staging layers to see if we have this field.
- add coverage flags for every input source
- preserve source-specific cleaned text fields

If we do not have `google_types` now then we should leave it out of the current system and Defer it to a future improvement.

### 4. Keep exploratory outputs separate from production decisions

The `category_retaurant_update.sql` QA script is useful as a prototype, but it should not become the long-term production logic.

Recommendation:

- keep QA scripts for ad hoc inspection
- move production classification logic into mart build SQL or a notebook pipeline that reads managed mappings

---

## Target Build Stages

### Stage 1. Classification text mart

Build `property_classification_mart.place_classification_text` as the base table.

It should include:

- canonical `poi_id`
- place name
- current `category`, `subcategory`, `detail_level_3`
- `comment`
- `editorial_summary`
- `source_list_names`
- `tags`
- `google_types` (if this exists in lower levels)
- source coverage flags
- a combined raw classification text field
- a combined cleaned classification text field
- source-specific cleaned text fields

Suggested refinement:

- keep both raw and cleaned versions because raw text helps manual review while cleaned text helps deterministic matching
- Check lower level column names first to check the correct column names and to see if our expected columns exist.

### Stage 2. Exploratory profiling outputs

Keep and expand the existing profiling queries:

- `place_word_profile`
- `place_phrase_profile`

These should be filtered for restaurant-focused analysis and especially useful for `mixed_restaurants`.

Suggested improvements:

- create restaurant-only profiles for all restaurants
- create separate profiles for `mixed_restaurants`
- include the ability to profile by current subcategory
- consider source-aware profiles in a later pass if needed

The purpose of these tables is discovery, not final classification.

### Stage 3. Managed keyword mapping table

Build and maintain `property_classification_mart.place_keyword_mapping` as the core rule table.

This table should define:

- keyword or phrase
- normalized keyword
- match type
- place domain
- mapped category
- mapped subcategory
- mapped `detail_level_3`
- keyword role
- base weight
- priority
- active flag
- notes

Suggested additions if needed:

- source scope or source weight override
- exclude patterns
- negative signal flag
- candidate confidence tier

This table should become the main production control surface for classification logic.

### Stage 4. Keyword matching layer

Build `property_classification_mart.place_keyword_matches`.

Each row should represent one matched signal for one place and should include:

- `poi_id`
- matched keyword
- source field matched in
- mapped category
- mapped subcategory
- mapped `detail_level_3`
- role
- effective weight
- priority

This is the explainability layer and should be easy to inspect for one place at a time.

### Stage 5. Candidate scoring layer

Build `property_classification_mart.place_classification_scores`.

This table should aggregate matches into candidate labels and include:

- candidate category
- candidate subcategory
- candidate `detail_level_3`
- total score
- matched keyword count
- matched keywords summary
- top signal priority
- optional source diversity count

Suggested scoring rules for V1:

- phrase matches score higher than token matches
- editorial summary matches score higher than list-name matches
- repeated support across multiple fields gets a bonus
- generic terms receive lower weights than highly specific terms

### Stage 6. Recommendation layer

Build `property_classification_mart.place_classification_recommendations`.

Each place should receive:

- recommended category
- recommended subcategory
- recommended `detail_level_3`
- top score
- matched keyword summary
- confidence label
- recommendation rank

Suggested V1 confidence logic:

- `high` when there are multiple reinforcing signals or highly specific phrases
- `medium` when one strong signal or several moderate signals agree
- `low` when evidence is weak
- `needs_review` when the place has conflicting or insufficient evidence

### Stage 7. Review queue

Build `property_classification_mart.place_classification_review_queue`.

Places should enter this queue when:

- they remain `mixed_restaurants`
- recommendation confidence is low
- the recommendation differs from the current classification
- the top two candidates are too close
- no usable match is found

This table should support analyst workflow and should include enough raw text and match context to review a place without re-querying everything.

### Stage 8. Override layer

Build and preserve `property_classification_mart.place_classification_overrides`.

This table should:

- store analyst-approved overrides
- remain durable across rebuilds
- always take precedence over recommendations when active

### Stage 9. Final published output

Build `property_classification_mart.curated_places_classified`.

This table should combine:

- original classification
- recommendation output
- override output
- final chosen classification
- method used such as `override` or `rule_based`
- confidence
- classification score

This becomes the downstream-facing output of the classification workflow.

---

## Suggested Notebook Or Analytics Workflow

The notebook or analytics pipeline should be built around review and iteration, not just data exploration.

Recommended workflow:

1. rebuild `place_classification_text`
2. rebuild word and phrase profiles
3. inspect high-frequency unmatched terms for `mixed_restaurants`
4. promote useful terms into `place_keyword_mapping`
5. rebuild matches, scores, and recommendations
6. inspect low-confidence and conflicting cases
7. save manual overrides
8. rebuild final output and QA summaries

The best notebook views will likely be:

- top words and phrases among `mixed_restaurants`
- examples for each candidate keyword
- all matched signals for a single place
- current versus recommended classification
- unresolved review queue

---

## Immediate Work Plan

### Phase 1. Stabilize the mart contract

Work to do:

- fix naming drift between `poi_id` and `place_id`
- standardize `detail_level_3` naming
- add missing input fields such as `google_types`
- align source flags and created-at fields

Definition of done:

- DDL and mart SQL agree on field names and primary keys

### Phase 2. Complete the core mart build

Work to do:

- finish `place_classification_text`
- validate and tune `place_word_profile`
- validate and tune `place_phrase_profile`
- create initial `place_keyword_mapping` seed content

Definition of done:

- we can reliably discover and manage restaurant classification terms

### Phase 3. Build explainable recommendation outputs

Work to do:

- create `place_keyword_matches`
- create `place_classification_scores`
- create `place_classification_recommendations`
- implement confidence logic

Definition of done:

- every recommendation is tied to matched evidence and a score

### Phase 4. Add review and override workflow

Work to do:

- create review queue logic
- create override application logic
- publish final classified output

Definition of done:

- low-confidence and changed cases are easy to review
- manual decisions persist across rebuilds

### Phase 5. Add QA reporting

Work to do:

- summarize how many places leave `mixed_restaurants`
- summarize confidence distribution
- report top unmatched frequent phrases
- report top conflicting recommendations
- report override counts

Definition of done:

- each run tells us whether classification quality is improving

---

## Suggested Initial Restaurant Taxonomy Work

Before expanding the mapping table too far, it would be helpful to confirm the initial target taxonomy for restaurant outputs.

At minimum, we should define:

- allowed restaurant `subcategory` values
- allowed restaurant `detail_level_3` values
- which labels are cuisine-based versus format-based
- when a place should remain broad versus receive a narrow specialty

This matters because the quality of the mapping table depends on a stable target vocabulary.

---

## Initial Priorities

The first classifications to optimize should be the ones most likely to reduce `mixed_restaurants` quickly and accurately.

Suggested early targets:

- `italian`
- `japanese`
- `chinese`
- `mexican`
- `greek`
- `middle_eastern`
- `steakhouse`
- `pizza`
- `bakery`

Suggested early `detail_level_3` targets:

- `ramen`
- `omakase`
- `slice_shop`
- `dim_sum`
- `dumplings`
- `pastry`

These classes already appear in the current QA script and plan, so they are good first production targets.

---

## Risks To Watch

### 1. False positives from generic list language

Terms in source list names may reflect list theme more than place identity.

Mitigation:

- weight list-name matches lower
- prefer exact phrases and stronger source fields

### 2. Ambiguous multi-concept places

A place may be both `wine bar` and `italian`, or both `bakery` and `cafe`.

Mitigation:

- separate broad subcategory from more specific `detail_level_3`
- use confidence and review routing

### 3. Taxonomy drift

Mappings become messy if target labels change frequently.

Mitigation:

- lock an initial V1 taxonomy before broad mapping expansion

### 4. Rule sprawl

The mapping table can become hard to maintain if it grows without conventions.

Mitigation:

- define keyword roles, naming conventions, and notes expectations early

---

## Recommended Deliverables

The implementation should produce these artifacts:

- stable DDL for the classification mart
- mart build SQL for text, profiles, matches, scores, recommendations, and final output
- a managed keyword mapping seed process
- QA queries for classification review
- a notebook or analytics workflow for iterative mapping and override review

---

## Definition Of Success

The implementation is successful when:

- `mixed_restaurants` is materially reduced
- recommendations are explainable and reviewable
- manual overrides persist cleanly
- taxonomy updates happen through managed mappings instead of ad hoc `CASE` statements
- the workflow is reusable for other place domains after restaurants
