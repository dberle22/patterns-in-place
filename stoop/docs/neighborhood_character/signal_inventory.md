# Neighborhood Intelligence Signal Inventory

## Purpose

This document is the first lane-first inventory for Stoop's broader
neighborhood intelligence model.

It answers two questions:

1. What data lanes do we have, or expect to have soon?
2. What can each lane reasonably point to in Character, Livability, and
   Opportunity?

The goal is to stay grounded in evidence before defining a more detailed
taxonomy of labels.

## Top-Level Framing

Neighborhood intelligence should be organized into three major lanes:

- **Character**: what a place is like, what it is known for, and what kind of
  social or cultural identity it projects
- **Livability**: how well a place supports day-to-day life, routines, access,
  and household needs
- **Opportunity**: what kind of economic energy, work presence, or business
  environment a place appears to have

These lanes can draw from some of the same data, but they should not collapse
into one score. The same input may matter differently in each lane.

## Source Status Key

- **Active**: available now in the current platform
- **Planned**: already identified in product/backlog and likely to be added
- **Future**: conceptually useful but not yet defined as an implementation task

## Signal Families

### 1. Demographic Context

Status: **Active** in `fct_tract_features` and `fct_nta_features`

Current examples:

- median income
- median rent
- median home value
- bachelor's degree share
- median age

Planned additions:

- renter share
- vacancy rate
- population density
- transit commute share

Most useful for:

- Character: background social and economic tone
- Livability: housing pressure, renter orientation, density context
- Opportunity: early proxy for economic profile, but weak on its own

What this can point to:

- affluent vs. budget-constrained context
- younger vs. older neighborhood profile
- high-density vs. lower-density urban living patterns
- renter-heavy vs. owner-leaning household orientation
- educational attainment tone

What this should not do alone:

- define neighborhood identity by itself
- stand in for culture
- make strong claims about fit or quality without other evidence

### 2. Curated Cultural Places

Status: **Active** in `dim_user_poi_v2`

Current examples:

- restaurants
- bars
- coffee
- music venues
- bookstores
- record stores
- museums
- shopping
- hotels

Potential supporting fields:

- category
- subcategory
- detail_level_3
- source lineage
- editorial context
- Google-backed location and enrichment fields

Most useful for:

- Character: strongest source for destination identity and neighborhood texture
- Livability: selective support for lifestyle fit, but not enough by itself
- Opportunity: weak direct signal unless later tied to business mix analysis

What this can point to:

- neighborhood distinctiveness
- destination appeal
- cultural concentration
- over-indexing in food, nightlife, arts, shopping, or specialty interests
- what a neighborhood is known for in a local or editorial sense

What this should not do alone:

- imply daily-life practicality
- imply broad economic opportunity
- reward sheer volume over uniqueness without normalization

### 3. Public and Civic Amenities

Status: **Active** in `dim_public_poi`

Current examples:

- subway stations
- bus stops
- Citi Bike stations
- ferry terminals
- PATH stations
- bike lanes
- parks
- playgrounds
- grocery stores
- pharmacies
- laundromats
- dry cleaners
- banks
- ATMs
- hardware stores
- public libraries
- post offices
- public schools
- farmers markets
- hospitals
- urgent care
- gyms
- landmarks
- historic districts
- institutional museums
- public art

Most useful for:

- Character: partial support, especially for civic identity and neighborhood
  type
- Livability: core signal family
- Opportunity: limited support, mainly through commercial and access structure

What this can point to:

- transit richness
- daily-needs coverage
- family-serving infrastructure
- civic and institutional presence
- recreation and park access
- urban convenience and service density
- tourism or heritage orientation in some areas

What this should not do alone:

- define culture in a rich way
- distinguish generic convenience from true identity
- stand in for school quality or safety quality where those data are absent

### 4. School Quality and Education Quality

Status: **Planned**

Expected examples:

- school quality scores
- school type
- grade coverage
- proximity or neighborhood-level access measures

Most useful for:

- Character: limited influence, mainly as part of institutional/residential
  tone
- Livability: major signal for households with children
- Opportunity: indirect long-term human-capital signal

What this can point to:

- family-oriented neighborhood support
- educational access strength
- stronger residential stability appeal for some users

What this should not do alone:

- define a neighborhood's identity
- dominate non-family livability profiles

### 5. Crime and Safety Context

Status: **Planned**

Expected examples:

- neighborhood-level crime rate
- offense mix
- time-windowed safety context

Most useful for:

- Character: little direct role
- Livability: major contextual signal
- Opportunity: possible business-climate context in future

What this can point to:

- perceived or measured safety context
- tradeoffs between vibrancy and comfort in some areas
- baseline residential suitability for certain user profiles

What this should not do alone:

- become the whole livability story
- replace a nuanced view of neighborhood use and feel
- drive moralized neighborhood labeling

### 6. Built Environment and Land-Use Form

Status: **Future**, with some pieces partially inferable from current data

Potential examples:

- property type mix
- residential vs. commercial mix
- business district presence
- block density
- built form intensity
- land-use pattern

Partial proxies available now:

- density-related demographic metrics
- concentration of public amenities
- concentration and variety of curated places

Most useful for:

- Character: major source for neighborhood type
- Livability: important for practicality and daily rhythm
- Opportunity: strong support for business and job clustering

What this can point to:

- city center vs. neighborhood main street vs. quieter residential district
- mixed-use urban core vs. low-intensity residential area
- commuter-oriented vs. destination-oriented form

What this should not do alone:

- imply cultural identity without place signals
- imply quality without context

### 7. Community and Institutional Presence

Status: **Partly Active**, partly **Future**

Current or partial examples:

- public libraries
- public schools
- hospitals
- post offices
- parks

Future expansions may include:

- community centers
- religious institutions
- nonprofit and civic anchors

Most useful for:

- Character: neighborhood rootedness and institutional tone
- Livability: strong support for everyday use
- Opportunity: modest civic-employment context

What this can point to:

- family orientation
- neighborhood stability
- civic density
- long-standing local identity

What this should not do alone:

- stand in for broader culture
- substitute for actual community activity measures

### 8. Destination and Visitor Assets

Status: **Active** and **Planned**, depending on category

Current or partial examples:

- museums
- landmarks
- public art
- institutional museums
- curated shopping
- hotels

Most useful for:

- Character: very strong for Explore-oriented identity
- Livability: limited, except where tourism load affects daily life
- Opportunity: modest signal for visitor economy

What this can point to:

- tourism pull
- day-trip appeal
- arts and culture concentration
- "best of the city" neighborhood patterns

What this should not do alone:

- determine residential fit
- override lack of daily-use infrastructure

### 9. Commercial and Business Activity

Status: **Future**, with a few weak proxies available now

Potential examples:

- business count and density
- business type mix
- office presence
- retail corridor concentration
- employer density
- job access

Partial proxies available now:

- grocery, pharmacy, bank, hardware, gym, and service-business density
- curated shopping and dining concentration

Most useful for:

- Character: commercial energy and street activity
- Livability: convenience and errand coverage
- Opportunity: core signal family

What this can point to:

- commercial vibrancy
- local-serving vs. destination-serving business mix
- white-collar, creative, or service-heavy economic profile
- neighborhood convenience and corridor strength

What this should not do alone:

- overstate true employment opportunity without jobs data
- confuse amenity density with labor-market access

### 10. Mobility and Access Structure

Status: **Active**, with room for more structured derived metrics

Current examples:

- subway stations
- bus stops
- Citi Bike
- ferry terminals
- PATH stations
- bike lanes

Planned additions:

- transit commute share
- derived accessibility metrics by neighborhood

Most useful for:

- Character: urban rhythm and neighborhood type
- Livability: major signal
- Opportunity: access to jobs and citywide reach

What this can point to:

- transit-rich vs. transit-light neighborhoods
- car-light urban living support
- regional accessibility
- day-trip ease and exploration friendliness

What this should not do alone:

- define total livability
- replace actual destination or cultural interest

## Lane Summary

### Character

Character should be driven primarily by:

- curated cultural places
- destination and visitor assets
- built environment and land-use form
- community and institutional presence

Character should be informed secondarily by:

- demographic context
- mobility and access structure
- selected civic amenities

Character should answer:

- what kind of place is this?
- what is it known for?
- what does it feel like to spend time here?

### Livability

Livability should be driven primarily by:

- public and civic amenities
- mobility and access structure
- school quality
- crime and safety context
- demographic and housing context

Livability should be informed secondarily by:

- community and institutional presence
- selected curated places relevant to routine life

Livability should answer:

- how easy is it to live here day to day?
- what practical needs does this neighborhood support well?
- what kinds of households or routines is it compatible with?

### Opportunity

Opportunity is still the least defined lane and should stay conceptual for now.

Opportunity will likely be driven by:

- commercial and business activity
- mobility and access structure
- built environment and land-use form
- selected demographic context

Opportunity may eventually answer:

- what kind of work and business environment exists here?
- where does commercial energy cluster?
- which neighborhoods appear to have stronger economic momentum or access?

## Recommended Next Step

Before drafting a full label taxonomy, the next design pass should define:

1. Which derived metrics belong to each signal family
2. Which signal families are allowed to influence dominant labels
3. Which signal families can only act as supporting evidence
4. Which inputs are NYC-relative from day one
5. Which inputs need guardrails before they appear in user-facing language
