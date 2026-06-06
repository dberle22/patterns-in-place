# Neighborhood Character Framework

## Purpose

This document defines what "neighborhood character" means for Stoop and how it
should evolve into a reusable product concept across Stoop Explore and Stoop
Search.

The immediate goal is to support Sprint 2 design work for the Stoop Explore
intelligence layer. The longer-term goal is to create a framework that can
eventually support evaluative scoring, recommendation systems, and
market-to-market expansion.

This work is also the beginning of a broader framework for understanding
neighborhoods, cities, and metro areas based on how people use them, not only
what raw data exists about them.

## Core Definition

Neighborhood character is Stoop's descriptive model of what a neighborhood is
like.

It is not only about who lives there, and it is not only about what amenities
are nearby. It is a layered view that combines:

- **Demographic context**: broad population and economic signals
- **Built environment and infrastructure**: how the area functions physically
- **Cultural and social fabric**: the places and institutions that shape lived
  experience

In practice, neighborhood character should help answer three related questions:

- What kind of place is this?
- What does daily life here likely feel like?
- What kinds of experiences or lifestyles does this area support?
- What is this place especially known for?

## Two-Phase Product Approach

Neighborhood character should develop in two phases.

### Phase 1: Descriptive

Start with descriptive character.

This phase focuses on identifying and explaining what is happening in a
neighborhood without yet making strong judgments about whether it is good or bad
for a particular person.

Examples:

- transit-rich mixed-use core
- family-oriented residential neighborhood
- nightlife-heavy creative district
- affluent low-key enclave

### Phase 2: Evaluative

Over time, neighborhood character should become more evaluative.

This phase uses the same underlying descriptive signals, but interprets them
against user profiles or use cases.

Examples:

- great neighborhood for a coffee-focused day out
- strong fit for families prioritizing schools and libraries
- weak fit for someone seeking quiet residential character

The descriptive model should remain the foundation. Evaluative outputs should
build on top of it rather than replace it.

## Relationship To Broader Neighborhood Intelligence

Neighborhood character should be treated as one major lens within a broader
neighborhood intelligence system.

The emerging top-level lenses are:

- **Character**: what the neighborhood is like and what it is known for
- **Livability**: how well the neighborhood supports daily life
- **Opportunity**: what kinds of economic activity, work, and business presence
  exist in the area

These lenses should stay related but distinct.

Character is the most narrative and identity-oriented lens. Livability is more
practical and household-oriented. Opportunity is more economic and directional,
and may eventually be useful for understanding career access, business density,
or commercial energy.

This document focuses on Character first, while keeping room for Livability and
Opportunity to become parallel frameworks.

## Character Layers

Neighborhood character should be built from multiple source layers that can be
developed and tested independently.

### 1. Demographic Character

Demographics should act as foundational context, not the dominant story.

Potential inputs:

- age profile
- income levels
- educational attainment
- race and ethnicity
- renter share
- housing stability or turnover proxies

Role in the model:

- provides high-level social and economic context
- helps explain broad neighborhood profile
- should remain one source among several, not the final definition of character

### 2. Built Environment and Infrastructure Character

This layer explains how the neighborhood functions physically and structurally.

Potential inputs:

- property types and land-use mix
- density and business district structure
- transit access
- proximity to major roads or hubs
- schools, libraries, community facilities
- parks and civic infrastructure

Role in the model:

- distinguishes urban core vs. commuter district vs. residential enclave
- captures practical accessibility and daily-life support
- provides a strong bridge between descriptive context and livability framing

### 3. Cultural and Social Character

This layer explains what the place feels like on the ground.

Potential inputs:

- curated restaurants, bars, cafes, music venues
- bookstores, galleries, museums, performance spaces
- specialty shopping and activity destinations
- civic and religious institutions where they shape neighborhood identity

Role in the model:

- captures the neighborhood's texture and personality
- identifies what the area over-indexes or under-indexes on
- supports natural-language descriptions that feel local and human

## Two Applied Product Views

The same underlying character system should support two different product views.

### Stoop Explore Character

Primary question: Where should I spend a day?

This view should emphasize:

- uniqueness
- destination appeal
- destination culture
- editorial and curated places
- activities, arts, nightlife, food, shopping, and leisure
- signals that help users choose neighborhoods for outings

Examples of important source types:

- museums
- galleries
- music venues
- bars
- coffee and pastry destinations
- premium or distinctive shopping
- hotels and landmarks where relevant

This view should lean more toward cultural discovery than daily practicality.
It should also prioritize distinctiveness over completeness. The goal is not to
reward neighborhoods for having the most generic options, but to identify areas
that are especially compelling when someone has limited time and wants a strong
experience.

### Stoop Search Character

Primary question: Is this somewhere I would like to live?

This view should emphasize:

- everyday practical support
- civic and community infrastructure
- household fit and daily rhythm
- signals that help users evaluate neighborhood suitability for living

Examples of important source types:

- libraries
- schools
- grocery and pharmacy access
- parks
- community centers
- religious institutions
- transit and commute structure
- background demographic context

This view should lean more toward ongoing livability than destination appeal.

## Output Philosophy

The end product should be natural-language neighborhood profiles, not just raw
scores.

The system should eventually include:

- one dominant character label per neighborhood
- 3 to 5 supporting sublabels
- a hierarchy of explainable character terms
- backing tables or models for each contributing signal
- profile generation logic that turns structured signals into readable language

Possible output shapes:

- one headline character label
- supporting sublabels that capture different facets
- one-paragraph neighborhood summaries
- ranked neighborhood lists for a selected use case
- supporting evidence fields that explain why a label was assigned

The dominant label should describe the neighborhood's primary identity. The
sublabels should add nuance. Some sublabels may describe what a neighborhood is,
while others may describe what it is especially known for. Both are valid parts
of the profile.

Example structure:

- dominant label: creative nightlife district
- sublabels: known-for-live-music, destination-bar-scene, young-adult-energy,
  mixed-use-urban-core

## Geographic Framing

The first implementation should be NYC-relative.

That means character signals, rankings, and "over-indexing" should initially be
interpreted relative to other NYC neighborhoods.

The model should still be designed so it can later expand to:

- NYC suburbs and the broader metro area
- additional markets
- future cross-market or market-profile comparisons

For future expansion, the default pattern should be:

- compare neighborhoods within market first
- compare markets to other markets separately

## Design Principles

- Start simple and descriptive before building scores.
- Keep source layers separable so methods can evolve independently.
- Avoid letting demographic variables dominate the user-facing story.
- Use different source mixes for Explore and Search even when they share the
  same root model.
- Separate identity, practicality, and economic-use concepts instead of forcing
  them into one score.
- Keep outputs explainable enough that a user can understand why a neighborhood
  received a description or ranking.

## Open Questions

These questions should guide the next round of refinement.

1. What is the first controlled vocabulary for dominant labels and sublabels?
2. Which cultural signals are identity-defining vs. merely present?
3. What qualifies as "known for" rather than simply "has"?
4. How should residential civic assets be split between Character and
   Livability?
5. What should Opportunity include first: jobs, business density, industry
   types, or something else?
6. What messaging guardrails should govern demographic language and avoid
   over-claiming?
7. What is the minimum evidence threshold before assigning a strong character
   label?

## Suggested Next Documents

As this area grows, this folder can expand into:

- `explore_character.md`
- `search_character.md`
- `livability_framework.md`
- `opportunity_framework.md`
- `character_taxonomy.md`
- `signal_inventory.md`
- `messaging_guardrails.md`
- `validation_examples.md`
