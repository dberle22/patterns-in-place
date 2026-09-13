# POI Taxonomy: Category Layer v1

Companion to `poi_subcategory_draft_v0.md`. Together these define levels 1 and 2
of the three-level taxonomy (Category, Sub Category, Detailed Category).

## Source field decision

The field names are actively misleading. `basic` sounds legacy and `primary`
sounds current. It is the other way around: `basic_category` is the new
property, introduced alongside `taxonomy` to replace the older `categories`
property. If this rule ever reads backwards to you, check a row where
`source_category_basic = food_and_drink` and `source_category_primary =
eat_and_drink`. The new taxonomy's top-level bucket is `food_and_drink`; the old
one is `eat_and_drink`. The new vocabulary is in the `basic` column.

Note also that `source_category_primary` is **not** `taxonomy.primary`. Those
are different vocabularies from different taxonomy generations, and
`taxonomy.primary` is not present in the current extract.

| Field | Overture property | Status | Use |
|---|---|---|---|
| `source_category_basic` | `basic_category` (new) | Current, ~280 values | **Primary key for Category assignment** |
| `source_category_primary` | `categories.primary` (legacy) | Deprecated, removed in the September 2026 release | Do not build on. Use for back-compat checks only |
| not yet pulled | `taxonomy.primary` | Current | Required for overrides and for Sub Category drilldown |
| not yet pulled | `taxonomy.hierarchy` | Current | Rollup logic and ambiguity resolution |

**Category is assigned from `basic_category` alone, plus a short override table
keyed on `taxonomy.primary`.** Nothing in the governed taxonomy may depend on
`categories.primary`.

Rationale: 258 distinct basic values cover 59,459 of 61,513 places (96.7%) with
no unmapped values. The remaining 2,054 are null at source. Assigning at the
`(basic, legacy primary)` pair grain instead would mean 1,361 rules, roughly half
of whose grain disappears in September.

### Versioning requirement

The Overture taxonomy is maintained on a quarterly cycle with updates in March,
June, September and December. The mapping table needs a `taxonomy_version` and
`effective_date`, plus a quarterly reconciliation job that fails loudly on new or
retired basic values. Without it, an upstream taxonomy change silently
reclassifies places.

---

## Category definitions

Volumes are pre-override, from the current file.

### Services — 13,486 places (21.9%), 27 basic values
Businesses that sell a service rather than a physical good or an experience.
- **Includes:** real estate, home and trade contractors, legal, financial and
  insurance advisory, business and professional services, B2B, media and
  communications, rental and events, travel agencies
- **Excludes:** anything with a retail storefront selling goods (Retail),
  vehicle-related services (Automotive), services delivered by government
  (Government & Public Safety)
- **Note:** the largest category by a wide margin. Accepted on the basis that
  its eight sub-categories carry the analytical weight. If Detailed Category
  comes out thin under them, promote Real Estate and Home & Trade to Category.

### Retail — 7,829 places (12.7%), 26 basic values
Establishments selling physical goods to consumers.
- **Includes:** grocery, convenience, pharmacy, general merchandise, apparel,
  hardware and garden, electronics and media, specialty, resale
- **Excludes:** food and drink for immediate consumption (Food & Drink), vehicle
  parts (Automotive), wholesale and distribution (Industrial & Logistics)
- **Note:** pharmacy sits here rather than Healthcare by decision. Must remain a
  named Sub Category for the daily-needs basket.

### Healthcare — 7,776 places (12.6%), 22 basic values
Facilities delivering medical, dental, behavioral or veterinary care.
- **Includes:** primary care, hospitals and emergency, specialty care, dental,
  vision, behavioral health, diagnostics and labs, alternative medicine, senior
  and long-term care, veterinary
- **Excludes:** pharmacies (Retail), spas and massage (Personal Care), pet
  grooming and boarding (Personal Care), gyms (Recreation & Fitness)
- **Note:** carries the largest unspecified bucket in the taxonomy, 1,562 places
  on `health_care` and `medical_service` with no finer detail available.

### Food & Drink — 5,730 places (9.3%), 17 basic values
Establishments preparing or serving food and drink for immediate consumption.
- **Includes:** restaurants, quick service, cafes, bars, breweries and wineries
  and distilleries, catering
- **Excludes:** grocery and food retail (Retail), nightlife venues whose primary
  function is entertainment rather than service (Entertainment & Nightlife)
- **Note:** cuisine belongs at Detailed Category, never at Sub Category.

### Personal Care — 4,392 places (7.1%), 6 basic values
Services performed on the person or their household goods.
- **Includes:** hair and barber, nail and beauty, spa and massage, tattoo,
  laundry and dry cleaning, pet grooming and boarding
- **Excludes:** medical and behavioral care (Healthcare), fitness (Recreation &
  Fitness), beauty product retail (Retail)
- **Note:** only 6 basic values for 4,392 places. Sub Category here cannot be
  derived from basic and requires `taxonomy.primary`.

### Automotive — 3,956 places (6.4%), 8 basic values
Everything relating to the sale, service and fueling of vehicles.
- **Includes:** dealers, repair and maintenance, parts and accessories, fuel and
  charging
- **Excludes:** parking (Transportation), taxi and rideshare (Transportation),
  freight and trucking (Industrial & Logistics)
- **Note:** gas stations moved here from their former top-level position. If
  fuel access matters more as a transport measure than a retail one, the Fuel &
  Charging sub-category can be dual-tagged rather than moved.

### Religious Institutions — 2,455 places (4.0%), 7 basic values
Places of worship and religious organizations.
- **Includes:** all faith traditions, religious organizations
- **Excludes:** religious schools (Education), cemeteries (Community & Civic),
  faith-based charities (Community & Civic)
- **Note:** Sub Category is faith tradition. Denomination goes to Detailed.

### Education — 1,944 places (3.2%), 16 basic values
Institutions whose primary function is teaching, learning or research.
- **Includes:** early childhood, K-12, higher education, specialty and
  vocational, tutoring, libraries, administration, non-medical research
- **Excludes:** medical research institutes (Healthcare), childcare framed as a
  family service (Community & Civic), campus recreation facilities (Recreation &
  Fitness)

### Recreation & Fitness — 1,807 places (2.9%), 17 basic values
Places for active participation in sport, fitness and recreation.
- **Includes:** gyms and studios, sports facilities, clubs and leagues and
  teams, outdoor recreation
- **Excludes:** spectator venues (Entertainment & Nightlife), parks and trails
  (Parks & Nature), sporting goods retail (Retail)
- **Note:** the participation vs spectation line is the governing rule. Stadiums
  and arenas sit in Entertainment.

### Community & Civic — 1,796 places (2.9%), 9 basic values
Nonprofit, civic and mutual organizations serving the community.
- **Includes:** civic and nonprofit organizations, community centers, youth and
  family services, food assistance, labor and political organizations, social
  clubs, cemeteries
- **Excludes:** government agencies (Government & Public Safety), religious
  organizations (Religious Institutions)

### Industrial & Logistics — 1,686 places (2.7%), 8 basic values
Production, distribution and movement of goods.
- **Includes:** manufacturing, wholesale and distribution, warehousing and
  storage, commercial shipping and delivery
- **Excludes:** postal service (Government & Public Safety), retail warehouse
  clubs (Retail), passenger transport (Transportation)

### Arts, Culture & Landmarks — 1,433 places (2.3%), 14 basic values
Cultural institutions and places of historic or civic significance.
- **Includes:** historic sites and monuments, museums, galleries, performing
  arts, cultural and creative spaces
- **Excludes:** commercial entertainment (Entertainment & Nightlife), parks
  (Parks & Nature)
- **Note:** `historic_site` alone is 923 places, which is why this split from
  Entertainment rather than staying merged.

### Financial Institutions — 1,166 places (1.9%), 2 basic values
Depository institutions and consumer money services.
- **Includes:** banks, credit unions, ATMs, money transfer and check cashing
- **Excludes:** insurance agencies, financial advisory and brokerage (Services)
- **Note:** volume rises to roughly 1,700 once money services are pulled out of
  `financial_service` by override. The bank/advisory line is the distinction:
  depository and transactional here, advisory in Services.

### Government & Public Safety — 1,064 places (1.7%), 11 basic values
Government agencies, public safety and the justice system.
- **Includes:** government offices, police and fire, courts and corrections,
  military, postal
- **Excludes:** public schools (Education), public libraries (Education),
  publicly owned utilities (Utilities), public parks (Parks & Nature)
- **Note:** the ownership question is deliberately not the rule here. Function
  decides. A public library is Education, not Government.

### Lodging — 754 places (1.2%), 8 basic values
Places providing overnight accommodation.
- **Includes:** hotels and motels, inns and B&Bs, resorts, short-term rental,
  campgrounds and RV parks
- **Excludes:** long-term residential (Residential), senior living (Healthcare)

### Parks & Nature — 610 places (1.0%), 18 basic values
Open space and natural features.
- **Includes:** parks and public space, playgrounds and dog parks, trails,
  gardens, protected land, natural features
- **Excludes:** built sports facilities (Recreation & Fitness), zoos and
  aquariums (Entertainment & Nightlife), farms (Agriculture)
- **Note:** low place count is expected. Parks are better measured as geometry
  than as points, so this category should be read alongside the OSM polygon
  layers rather than on its own.

### Entertainment & Nightlife — 480 places (0.8%), 19 basic values
Commercial venues for spectation, amusement and nightlife.
- **Includes:** cinema, live music and comedy, nightlife, gaming and gambling,
  attractions and amusement, event and spectator venues
- **Excludes:** cultural institutions (Arts, Culture & Landmarks), bars whose
  primary function is drink service (Food & Drink)

### Transportation — 406 places (0.7%), 14 basic values
Passenger transport facilities and road infrastructure as points.
- **Includes:** air, rail and transit, parking, ground transport services, road
  infrastructure
- **Excludes:** freight and logistics (Industrial & Logistics), fuel and
  charging (Automotive), travel agencies (Services)
- **Note:** transit stops and platforms are excluded from Overture places by
  definition and live in the base theme's infrastructure type. Do not expect
  bus-stop coverage here. This category will stay thin and should be read
  alongside the OSM line and polygon layers.

### Agriculture — 360 places (0.6%), 2 basic values
Working agricultural land and services.
- **Includes:** farms, agricultural services
- **Excludes:** farmers markets (Retail), nature reserves (Parks & Nature)

### Residential — 174 places (0.3%), 2 basic values
Multi-family residential buildings appearing as POIs.
- **Includes:** apartments, condominiums
- **Excludes:** short-term and vacation accommodation (Lodging), senior living
  (Healthcare), real estate brokerages (Services)
- **Note:** POI coverage of residential buildings is incidental and not a
  reliable housing inventory. Do not use for housing counts.

### Utilities — 154 places (0.3%), 4 basic values
Utility providers and facilities.
- **Includes:** electric, water, natural gas
- **Excludes:** telecommunications providers (Services), utility contractors
  (Services)

### Unclassified — 2,055 places (3.3%)
Null source values plus anything failing both basic and taxonomy lookup.
Currently 2,054 places on a null/null pair plus one `building`. Re-profile after
the September release: a null legacy `categories` does not imply a null
`basic_category`, so this bucket may shrink on its own.

---

## Override table

Cases where `basic_category` alone assigns the wrong Category. Keyed on
`taxonomy.primary`, **not** on the deprecated `categories.primary`.

| Basic value | Places | Default Category | Override to | Trigger |
|---|---|---|---|---|
| `financial_service` | 2,578 | Services | Financial Institutions | money transfer, check cashing, currency exchange |
| `animal_or_pet_service` | 578 | Personal Care | Healthcare | veterinary |
| `shipping_or_delivery_service` | 374 | Industrial & Logistics | Government & Public Safety | postal service |
| `family_service` | 238 | Services | Education | childcare, daycare |
| `family_service` | 238 | Services | Healthcare | counseling, therapy |
| `research_institute` | 18 | Education | Healthcare | medical or clinical research |

Six overrides against 258 base rules. Any growth in this list is a signal that a
Category boundary is drawn in the wrong place and should be revisited rather
than patched.

---

## Governance rules

1. **Category is a foreign key**, not free text. The source file currently has 35
   distinct category strings for what should be 22, including three spellings of
   Commercial and four of Government. A constraint prevents recurrence.
2. **One home per place.** No multi-assignment at Category. Where a place
   genuinely spans two, the primary hierarchy decides and the other is recorded
   via `taxonomy.alternates` rather than a second Category.
3. **Unspecified is a value, not a null.** Every Category that needs one gets an
   explicit Unspecified Sub Category. Roughly 4,100 places sit on source values
   that name a category but nothing finer, and that share is a coverage metric
   the analyses need to see.
4. **Function over ownership.** Public library is Education. Public park is
   Parks & Nature. Municipal utility is Utilities. Ownership is an attribute,
   not a category.
5. **Category names are stable identifiers.** Renaming is a breaking change.
   Q4's daily-needs basket depends on Retail, Healthcare, Education, Parks &
   Nature and Financial Institutions resolving by name.

## Open questions carried from the Sub Category draft

- **Galleries:** commercial vs institutional. Basic cannot distinguish. Draft
  puts all 135 in Arts, Culture & Landmarks.
- **Stadiums and arenas:** Entertainment (spectation) or Recreation
  (participation)? Draft says Entertainment.
- **Senior living:** Healthcare or Residential? 231 places. Draft says
  Healthcare.
- **Cemeteries:** Community & Civic or Parks & Nature? Draft says Community.
- **Social clubs:** Community & Civic or Recreation? Draft says Community.
- **Services depth:** eight sub-categories may be too many if Detailed Category
  is thin under Legal, Media and Travel.

## Sequencing before codification

1. Confirm the Overture release the current extract came from. If it predates
   July 2026 the basic values may have shifted.
2. Re-pull with `basic_category`, `taxonomy.primary`, `taxonomy.hierarchy`,
   `taxonomy.alternates` and `confidence`. The override table and every [T] row
   in the Sub Category draft depend on this.
3. Load the 258-row basic-to-Category mapping and the 6-row override table as
   versioned seeds.
4. Re-profile the 2,054 null bucket against `basic_category`.
5. Only then map Detailed Category, which needs the full ~2.1k taxonomy.