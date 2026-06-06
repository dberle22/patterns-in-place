# Neighborhood Intelligence Narrative Concepts

## Purpose

This document defines the human meaning behind Stoop's neighborhood
intelligence framework before it becomes a scoring or taxonomy system.

The goal is to make sure the framework is grounded in the real world: how
people understand neighborhoods, how they talk about them, and how they decide
where to spend time, where to live, and where to seek opportunity.

This is intentionally a narrative layer first. It should help us build language
that feels true before we convert those ideas into indicators, labels, or
scores.

## Why This Matters

Most neighborhood data products begin with measurable fields and then try to
assemble a story from them. Stoop should work the other way around.

People do not experience neighborhoods as a list of variables. They experience
them as places with identity, rhythm, tradeoffs, routines, and emotional pull.
They ask questions like:

- What kind of neighborhood is this?
- What is it known for?
- Would I enjoy spending time here?
- Could I imagine my life working here?
- Does this place feel like it has energy or possibility?

The framework should start from those lived questions and then use data as the
evidence layer underneath.

## The Three Lenses

Stoop's broader neighborhood intelligence model should be organized around
three major lenses:

- Character
- Livability
- Opportunity

These are related, but they are not interchangeable. A neighborhood can be
strong in one and weaker in another. That is part of what makes neighborhoods
real.

## Character

### Plain-language meaning

Character is the story of what a place feels like and what it is known for.

It captures identity, texture, atmosphere, and social meaning. It is the most
human and narrative lens. When someone says "that neighborhood has a certain
vibe" or "that area is really known for X," they are talking about character.

Character should answer:

- What kind of place is this?
- What makes it distinct from other neighborhoods?
- What is it known for?
- What kind of experience does it offer?

### What character is not

Character is not a raw amenity count.

It is also not just demographics, and it is not the same as livability. A
neighborhood can have strong character without being convenient, quiet, or easy
to live in. It can also be highly livable without being especially distinctive.

### The kind of story character tells

Character tells the story of neighborhood identity.

It should surface things like:

- whether a place feels creative, polished, local, busy, residential, historic,
  or destination-driven
- whether people go there for a reason or simply pass through it
- whether it feels rooted in institutions, nightlife, food culture, family
  life, or commercial energy

### Grounded examples

These are illustrative examples of the kind of story Character should help us
tell. They are not final labels.

- A neighborhood might feel like a creative nightlife district because live
  music venues, bars, late-night food spots, and younger demographic signals all
  point in the same direction.
- Another neighborhood might read as an institutional cultural core because it
  concentrates museums, landmarks, and civic anchors that make it a destination
  even if it is not the strongest residential fit.
- Another might feel like a quiet affluent enclave because the social and built
  environment signals point toward privacy, stability, and a lower-key rhythm.

### Why character matters in the product

Character is likely the clearest storytelling advantage for Stoop.

It is especially important for Stoop Explore, where users are not just trying
to find somewhere with enough options. They are trying to find somewhere worth
going to. They want to understand what makes an area compelling, distinct, or
memorable.

For Stoop Search, Character still matters, but in a different way. It helps a
user ask whether a neighborhood feels aligned with the kind of life they want,
not just whether it checks practical boxes.

### Stoop Explore v1 product framing

For Stoop Explore, the dominant Character framing should be:

- what a neighborhood is **known for**

This is a better MVP frame than telling users where they "should" go. It keeps
the product descriptive, lets the reader decide what they want, and avoids
pretending the app has a fully personalized point of view before the evidence
base is mature enough.

The copy can still feel playful and editorial. The data does the analytical
work underneath. The surface language should make neighborhoods feel vivid,
human, and inviting without overstating confidence.

In practice, Stoop Explore Character should answer two user-facing questions:

- What is this neighborhood known for?
- If I only have part of a day, what kind of experience is this place most
  likely to deliver?

For MVP, the first question is primary. The second question is supporting
texture.

### Stoop Explore v1 story types

These are the initial story types for Explore. They are product concepts first,
not rigid ontology terms.

#### 1. Destination food district

A neighborhood that stands out for going out to eat, snacking, or building a
food-centered day around.

This story is primarily supported by curated food and drink categories. It
should be strongest where restaurant depth and subcategory variety point to a
true destination, not just generic abundance.

#### 2. Cultural core

A neighborhood known for institutional or civic culture: museums, public art,
landmarks, bookstores, and other places that make it feel like a destination
for browsing, learning, or wandering.

This story can use both curated and civic support signals. It should not be
assigned just because an area has many restaurants near cultural institutions.

#### 3. Nightlife scene

A neighborhood known for social energy after dark: bars, music venues, late
hours, and a stronger evening identity.

This story should only appear when nightlife categories are real anchor
signals. Restaurant density alone should not stand in for nightlife.

#### 4. Specialty shopping area

A neighborhood known for browsing, collecting, or seeking out specific kinds of
retail culture: bookstores, record stores, design-forward shopping, niche
retail, and destination retail pockets.

This story should reward distinct shopping identity, not just generic retail
mass.

#### 5. Local neighborhood main street

A neighborhood with a balanced, walkable cluster of neighborhood-serving places
that feels active and pleasant without necessarily being citywide-famous for one
thing.

This story is useful because not every compelling neighborhood experience is a
spike. Some places are known for having a steady, layered, locally enjoyable
mix.

#### 6. Quiet residential enclave

A neighborhood better known for low-key residential character than for being a
major destination.

This story sits closest to the boundary between Character and Livability. In
Explore it should be used sparingly and mainly for completeness. Its stronger
long-term home is likely in Search and Livability, where demographic context and
public-serving infrastructure can carry more of the explanation.

### Evidence model for Explore v1

Each story type should have at least one curated anchor category. This is an
important guardrail for MVP because Stoop Explore is supposed to surface
distinctive destination character, not just generic convenience.

Public and civic signals can help support an Explore story when they are part
of what makes a neighborhood feel known for something. Museums and public art
are good examples. Grocery stores, pharmacies, and other daily-needs signals
should not dominate Explore character stories even when they are useful in
Livability.

Because current curated coverage is still strongest in restaurants, the first
version should treat story types as soft product language layered on top of the
ranking outputs, not as fully automated labels that need to fire everywhere.

### Evidence guide by story type

#### Destination food district

- Primary anchors: restaurants, bakeries, food markets, specialty grocery, bars
- Optional support: hotels, transit, landmarks
- Strong evidence: high restaurant count plus strong cuisine/subcategory
  diversity
- Should not dominate: grocery/pharmacy convenience, generic commercial density

#### Cultural core

- Primary anchors: museums, bookstores
- Optional support: public art, landmarks, libraries, hotels
- Strong evidence: multiple cultural anchors pointing in the same direction
- Should not dominate: restaurants by themselves

#### Nightlife scene

- Primary anchors: bars, music venues
- Optional support: restaurants, hotels, transit
- Strong evidence: bars or music venues rank meaningfully, with restaurant
  support
- Should not dominate: restaurant concentration alone

#### Specialty shopping area

- Primary anchors: shopping, bookstores, record stores
- Optional support: hotels, landmarks
- Strong evidence: destination-style shopping depth plus at least one niche
  retail anchor
- Should not dominate: broad retail mass without identity

#### Local neighborhood main street

- Primary anchors: restaurants, bakeries, shopping, bookstores
- Optional support: parks, libraries
- Strong evidence: balanced presence across several categories rather than one
  dominant spike
- Should not dominate: a single top-decile category with little supporting mix

#### Quiet residential enclave

- Primary anchors: minimal curated destination intensity paired with residential
  context
- Optional support: parks, libraries, schools, demographic stability signals
- Strong evidence: low-key curated profile plus public-serving and residential
  context that consistently point toward calm daily rhythm
- Should not dominate: absence of data alone; this cannot become the default
  fallback label

### Explore MVP boundary lines

For MVP, Stoop Explore should keep a clean line between:

- **Known for**: what the rankings and evidence can confidently support now
- **Good for**: a more evaluative interpretation that should expand later as
  coverage improves

This means the core Explore surface should remain category-led:

- Top neighborhoods for X
- What this neighborhood is known for

Headline labels and story types can help the experience feel more editorial,
but they should remain secondary to the category evidence until broader coverage
exists across nightlife, shopping, and cultural categories.

## Livability

### Plain-language meaning

Livability is the story of whether day-to-day life works well in a place.

It captures practical support, convenience, access, daily rhythms, and the
conditions that shape how manageable or enjoyable it is to live there over
time.

Livability should answer:

- Could my life function well here?
- Would everyday needs be supported?
- What kinds of routines would this neighborhood make easier or harder?
- For what kinds of households or lifestyles does this place seem to work well?

### What livability is not

Livability is not the same as character.

An area can be exciting, beautiful, or culturally rich and still be hard to
live in for certain people. It can also be practical and reliable without being
especially distinctive or aspirational.

Livability is also not one universal truth. What feels livable for a family
with children may not be the same as what feels livable for a young renter
prioritizing nightlife and transit.

### The kind of story livability tells

Livability tells the story of daily fit.

It should surface things like:

- whether daily errands are easy
- whether transit access supports routine movement
- whether schools, libraries, parks, and other civic assets support everyday
  life
- whether the area feels supportive for certain household patterns or life
  stages

### Grounded examples

- A neighborhood may not be a major destination, but it may still feel highly
  livable because it has strong transit, grocery coverage, parks, libraries, and
  a steady residential rhythm.
- Another neighborhood may be socially exciting but less livable for someone
  seeking quiet, school access, and lower daily friction.
- Another may work well for a car-light urban lifestyle because practical needs
  and movement options are easy to reach without needing a car.

### Why livability matters in the product

Livability is the center of Stoop Search.

This is the lens people need when they are trying to imagine their actual life
in a neighborhood, not just their ideal Saturday. It lets Stoop move beyond
generic neighborhood descriptions and into a more useful question: does this
place support the life I want to build?

## Opportunity

### Plain-language meaning

Opportunity is the story of what kinds of economic energy or possibility a
place appears to hold.

It is the least defined of the three lenses right now, but it matters because
people do not only choose neighborhoods for culture or comfort. They also care
about work, business activity, growth, and access to economic life.

Opportunity should answer:

- What kinds of work or business activity seem present here?
- Does this place feel economically active, stable, growing, or specialized?
- What kinds of ambitions or work patterns might this area support?

### What opportunity is not

Opportunity is not simply wealth.

A high-income neighborhood is not necessarily the same thing as a place with
strong opportunity for jobs, business creation, or economic momentum. Likewise,
a place with visible commercial energy may not read as affluent in demographic
terms.

Opportunity is also not the same as livability. A strong job center may be
intense, expensive, or inconvenient as a place to live.

### The kind of story opportunity tells

Opportunity tells the story of economic direction and practical possibility.

It may eventually surface things like:

- job access
- business density
- industry identity
- commercial corridor strength
- signs of growth or transformation

### Grounded examples

- A neighborhood may feel like a strong commercial hub because of dense retail,
  office activity, and easy regional access.
- Another may feel like an emerging creative-business area because smaller-scale
  commercial energy and cultural identity are rising together.
- Another may feel stable and wealthy but not especially dynamic in terms of new
  opportunity.

### Why opportunity matters in the product

Opportunity gives Stoop a way to eventually talk about how neighborhoods fit
people's working lives, ambitions, and business patterns, not only their social
or residential preferences.

This lens is likely less mature than Character and Livability, but it could
become important as the platform grows into metro-area and cross-market
comparisons.

## How The Lenses Work Together

The three lenses should not compete for one winner. They should work together to
describe different truths about the same place.

A neighborhood can be:

- high-character, mixed-livability, strong-opportunity
- low-drama character, high livability, modest opportunity
- high destination appeal, lower residential fit, strong visitor economy

That is a feature, not a flaw. Real neighborhoods are full of tradeoffs, and
the framework should preserve those tradeoffs instead of flattening them.

## A Story-First Product Principle

The sequence should be:

1. Define the human story each lens is trying to tell.
2. Identify what kinds of neighborhood truths belong inside that story.
3. Use data to support those truths.
4. Convert evidence into labels, summaries, and rankings carefully.

This order matters because it keeps the product grounded in lived experience.

## Open Narrative Questions

These questions should guide the next refinement pass.

1. What kinds of neighborhood stories do New Yorkers actually tell most often?
2. Which stories belong under Character versus Livability?
3. Where should we draw the line between "known for" and "good for"?
4. What kinds of tradeoffs should the product surface explicitly instead of
   hiding behind a single label?
5. Which neighborhood examples feel most useful as calibration cases for each
   lens?
