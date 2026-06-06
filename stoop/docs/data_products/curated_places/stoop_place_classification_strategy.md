# Stoop Place Classification Strategy

## Purpose

This document defines the operating strategy for automated and analytics-driven place classification, starting with restaurant reclassification and especially the `mixed_restaurants` cleanup problem.

This is the canonical starting-point document for the place classification initiative. It explains the operating model, decision principles, and intended workflow at a strategy level. The companion implementation plan translates this strategy into concrete build steps in this repo.

The goal is to move from one-off manual SQL updates toward an explainable classification system that:

- uses text we already ingest
- produces consistent `category`, `subcategory`, and `detail_level_3` recommendations
- supports analyst review and manual overrides
- can be reused for other place domains over time

This strategy is classification-focused. It is not a redesign of the full curated places ingestion pipeline.

---

## Core Problem

Many places were ingested from mixed or editorial lists and assigned broad categories at ingest time. For restaurants, this creates an especially large `mixed_restaurants` bucket that hides useful distinctions like:

- `italian`
- `japanese`
- `chinese`
- `mexican`
- `steakhouse`
- `bakery`
- `pizza`
- `ramen`
- `omakase`

The source data already contains useful classification signals in article comments, Google editorial summaries, tags, and source list names. The problem is not missing information so much as the absence of a repeatable classification system.

---

## Strategy Summary

We will treat classification as a repeatable decision system with two major layers:

1. A classification mart that assembles text, extracts matchable signals, and records explainable evidence.
2. A recommendation layer that turns those signals into scored candidate classifications, routes ambiguous cases into review, and applies durable manual overrides.

This should be deterministic, explainable, and easy to improve incrementally.

---

## Classification Principles

### 1. Preserve explainability

Every recommendation should be traceable to the words or phrases that caused it.

We should always be able to answer:

- which signals matched
- where they came from
- why one classification beat another
- whether the final answer came from automation or override

### 2. Separate discovery from production logic

Exploratory profiling and production classification should not be the same thing.

- Profiling tables help us discover useful words and phrases.
- Managed mapping tables define which signals are allowed to affect classification.

This lets us iterate safely without turning exploratory logic into fragile production SQL.

### 3. Classify in layers, not with one flat label

Restaurant classification is not one-dimensional. A place may have:

- a broad cuisine or restaurant type
- a more specific specialty or service style

The system should therefore support:

- `category`: broad domain such as `restaurants` or `bars`
- `subcategory`: broad cuisine or restaurant type such as `italian`, `japanese`, `bakery`, `pizza`
- `detail_level_3`: narrower specialty or format such as `ramen`, `slice_shop`, `omakase`, `natural_wine`

### 4. Use source-aware evidence

Not all text sources are equally reliable.

In general, the strongest text signals should come from:

1. Google editorial summary
2. article comments
3. tags
4. Google types
5. source list names

List names are still valuable, but they are often noisier because they reflect curation context rather than the place’s core identity.

### 5. Build for analyst review

The system should not aim for perfect autonomy. It should aim to:

- automate obvious cases
- make uncertain cases easy to review
- learn from overrides

The review workflow is a product requirement, not an afterthought.

---

## Classification Inputs

The initial text inputs should be:

- `comment`
- `editorial_summary`
- `source_list_names`
- `tags`
- `google_types`

These should be preserved both as:

- source-specific cleaned fields
- one combined classification text field

The combined field supports broad matching, while source-specific fields allow weighting and debugging.

---

## Signal Model

The system should match more than just raw keywords. It should support several signal types:

- single words: `ramen`, `bakery`, `sushi`
- phrases: `wine bar`, `dim sum`, `small plates`, `ice cream`
- contextual terms: `tasting menu`, `counter service`, `natural wine`
- source-specific signals: the same term in `editorial_summary` should usually carry more weight than in `source_list_names`

Signals should also have semantic roles so that the scoring logic can reason more clearly about them. Useful roles include:

- `cuisine`
- `type`
- `format`
- `product`
- `experience`
- `quality_signal`
- `disambiguation`

Examples:

- `italian` is a `cuisine` signal
- `pizza` can be a `type` or `product` signal
- `slice` is often a `format` or `product` signal
- `omakase` is an `experience` and highly specific classification signal
- `natural wine` is an `experience` or `type` signal for bars

---

## Decision Model

Recommendations should be created through deterministic scoring rather than first-match `CASE` logic.

Each matched signal should contribute to one or more candidate labels using:

- base weight
- source weight
- phrase bonus
- optional priority or tie-break logic

The recommendation layer should then:

1. score candidate `subcategory` values
2. score candidate `detail_level_3` values
3. aggregate matched keywords
4. rank candidates
5. assign confidence
6. route ambiguous cases into manual review

This model is easier to debug and tune than ordered `CASE` statements.

---

## Confidence Framework

Recommendations should be tagged with a confidence class such as:

- `high`
- `medium`
- `low`
- `needs_review`

Suggested interpretation:

- `high`: multiple reinforcing signals or highly specific phrase matches
- `medium`: one strong signal or several moderate signals
- `low`: weak or generic evidence
- `needs_review`: conflicting top candidates, sparse evidence, or no usable signal

Confidence should be based on evidence quality, not just score magnitude.

---

## Review and Override Model

Manual review should be structured around a queue rather than ad hoc investigation.

Places should enter the review queue when:

- they remain in `mixed_restaurants`
- the top recommendation conflicts with the current classification
- the confidence is low
- the top two candidates are too close
- no usable match is found

Manual overrides should be durable and should always win over automated outputs until explicitly deactivated.

This creates a stable hybrid model:

- automation handles the obvious cases
- review resolves hard cases
- overrides preserve analyst decisions across runs

---

## Target Operating Workflow

The intended workflow is:

1. assemble classification text
2. profile tokens and phrases
3. promote useful signals into the managed mapping table
4. match places to signals
5. score candidate classifications
6. generate recommendations and confidence
7. review ambiguous or changed cases
8. save manual overrides
9. publish final classified output

This workflow should be iterative. The system improves as the mapping table and override coverage improve.

---

## Scope for V1

The first implementation should focus on restaurants, with priority on `mixed_restaurants`.

V1 should aim to:

- reduce the size of `mixed_restaurants`
- establish an explainable text-based classification mart
- support `subcategory` and `detail_level_3` recommendations
- create a durable review and override workflow

It does not need to:

- solve every category domain at once
- use machine learning
- replace the curated places table structure

---

## Future Expansion

Once the restaurant workflow is stable, the same framework can support:

- bars
- bakeries
- specialty groceries
- hotels
- music venues

The architecture should therefore stay place-domain aware, even if restaurants are the first production use case.

---

## Success Criteria

This strategy is working if we can:

- materially reduce `mixed_restaurants`
- explain every recommendation with matched evidence
- review uncertain cases efficiently
- preserve manual decisions across reruns
- improve classification quality by updating mappings rather than rewriting ad hoc SQL

The long-term asset is not just a cleaned restaurant table. It is a reusable classification system.
