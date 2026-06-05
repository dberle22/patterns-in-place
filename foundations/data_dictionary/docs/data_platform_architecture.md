# Patterns in Place — Data Platform Architecture & Source Mapping

**Last updated:** 2026-06-05
**Purpose:** Canonical reference for the data platform's structure, source inventory, ingestion rules, and pipeline architecture. Intended for use as repository context and as an agent-facing reference doc.

---

## Mental Model: Three Data Types

The platform organizes all spatial data into three fundamental types:

| Type | Definition | Examples |
|---|---|---|
| **Points** | A discrete real-world location with a lat/lon. May or may not sit on a parcel. | Restaurant, school, transit stop, fire hydrant, park bench |
| **Parcels** | The legal land unit of record. Defined by tax/assessor systems. | Tax lot, BBL (NYC), APN (national) |
| **Polygons** | A named geographic zone composed of multiple points and/or parcels. Maps upward toward Places. | Zoning district, school attendance zone, flood zone, park boundary, NTA, census tract |

**Key distinctions:**
- A restaurant is a Point that occupies a Parcel, but a transit stop is a Point that exists in public right-of-way with no associated Parcel.
- Points and Parcels often co-locate but are maintained separately because they come from different sources and serve different analytical purposes.
- Polygons provide the geographic context that connects Points and Parcels to the Places layer.

---

## Platform Overview

The platform has two primary data layers:

### Places layer
Tabular metrics organized by geographic grain (census tract → CBSA → US). Covers demographic, economic, housing, education, quality of life, transportation, and climate topics. Built from federal statistical sources (ACS, BEA, BLS, HUD, Zillow, FHFA, etc.) plus aggregations that flow up from the Points/Parcels/Polygons layers.

### Spatial layer (Points / Parcels / Polygons)
Individual locations, land units, and geographic zones. Ingested at varying scopes (national once vs. per market on deep-dive). Aggregates feed back into the Places layer as neighborhood-level density, mix, and coverage metrics.

### How they connect
```
Points + Parcels + Polygons
    → spatial join (GeoPandas, point-in-polygon)
    → fct_geo_aggregations (NTA / tract / county grain)
    → Places Gold layer (joined to ACS, BEA, BLS, etc.)
```

---

## Part 1: Places Layer

### Geography hierarchy
```
Census Tract → County → CBSA → State → Division → Region → US
```
All Gold tables carry `(geo_level, geo_id, geo_name, year)` as the primary key grain. Supported grains: US, Region, Division, State, CBSA, County, Census Place, Census Tract, ZCTA.

---

### Topic: Demographics

| Source | Metrics | Geo grain | Status |
|---|---|---|---|
| ACS | Race, age, population, nativity, household type, household size, disability, language spoken at home | Tract → US | Live |
| IRS Migration | County-to-county in/out flows, AGI of movers | County | Live (Silver + Gold complete) |
| Census Population Projections | Forward-looking estimates to 2060 | County | Add later (if ingestion is straightforward) |

**ACS tables of note:** B01001 (age/sex), B02001 (race), B03001 (Hispanic origin), B05001 (nativity), B11001 (household type), B16001 (language spoken at home), B18101 (disability by age).

---

### Topic: Education

| Source | Metrics | Geo grain | Status |
|---|---|---|---|
| ACS | Adult attainment (HS diploma, some college, BA+, graduate degree) | Tract → US | Live |
| CHR | HS graduation rate, some college access | County | Live |
| IPEDS → aggregate | College enrollment, completion, cost — rolled up from Points layer | Institution → county / CBSA | Scope (aggregate from Points) |
| NCES CCD → aggregate | K–12 enrollment, Title I share, school density — rolled up from Points layer | School → district | Scope (aggregate from Points) |
| GreatSchools API | School quality ratings aggregated to district/NTA | School → district | Deferred — $52/mo, 15k call limit; market-specific on deep-dive |

**Note:** IPEDS and NCES CCD are ingested once at the Points layer. Places receives aggregated metrics from those tables, not a separate ingest.

**Gap — school boundaries:** Attendance zone polygons (for property-level school assignment in Stoop Search) are a Polygons layer item, not a Places metric. Source: NCES SABINS. Market-specific, deep-dive only.

---

### Topic: Economics

| Source | Metrics | Geo grain | Status |
|---|---|---|---|
| BEA | GDP by metro, personal income, Regional Price Parity | CBSA → national | Live |
| BLS LAUS | Unemployment, labor force | County → national | Live |
| BLS QCEW | Industry employment and wages by NAICS sector | County | Live |
| ACS | Income, labor participation, poverty, Gini coefficient, commute | Tract → US | Live |
| CBP (County Business Patterns) | Establishment count, employment, payroll by NAICS | County | Scope |
| BFS (Business Formation Statistics) | New business applications, startup activity | County / state | Scope (add alongside CBP) |
| Opportunity Zones | OZ tract designation flag | Census tract | Live (`gold.dim_policy_designations`) |
| HMDA (via CFPB) | Mortgage originations, denial rates, lending equity by tract | Census tract | Scope (after FHFA stable) |

**Note:** Opportunity Zones and FHFA Underserved designations are ingested as their own Gold table (`gold.dim_policy_designations`) rather than joined inline to topic tables.

---

### Topic: Housing

| Source | Metrics | Geo grain | Status |
|---|---|---|---|
| ACS | Vacancies, values, rents, units, tenure, age of stock, overcrowding, median rooms | Tract → US | Live |
| HUD CHAS | Rent burden by income tier | Tract | Live |
| HUD FMR | Fair Market Rent by bedroom count | County | Live |
| BPS | Residential building permits by type | Metro / county | Live |
| Zillow ZHVI + ZORI | Home value index; observed rent index; inventory; days on market | ZIP / metro | Live |
| FHFA HPI | Repeat-sales home price index (1970s–present) | Tract → national | Live |
| FHFA Underserved Areas | Duty-to-serve designation flag | County / tract | Live (`gold.dim_policy_designations`) |
| HMDA | Lending access, denial rates, equity metrics | Census tract | Scope |

**ACS tables of note:** B25001 (total units), B25002 (vacancy), B25003 (tenure), B25014 (occupants per room), B25018 (median rooms), B25035 (year structure built), B25064 (median gross rent), B25077 (median home value).

---

### Topic: Crime & Safety

| Source | Metrics | Geo grain | Status |
|---|---|---|---|
| CHR | Injury deaths, violence outcomes | County | Live |
| City open data portals | Geocoded incident-level crime data | Incident → tract / NTA | Per market, deep-dive only |
| FBI UCR / NIBRS | City/agency-level offense counts | Agency / city | Skip — county files exist via ICPSR but require non-standard FIPS crosswalk and have significant voluntary reporting gaps; signal not worth the pipeline complexity |

---

### Topic: Quality of Life

| Source | Metrics | Geo grain | Status |
|---|---|---|---|
| ACS — social infrastructure | Health insurance (B27001), broadband subscription (B28002), commute mode / WFH (B08301), vehicle access (B08201), travel time (B08012) | Tract → US | Scope (household type, insurance, commute, WFH, vehicles already ingested; broadband, disability B18101, language B16001 not yet added) |
| CHR | Life expectancy, obesity, smoking, mental health, physical inactivity | County | Live |
| CDC PLACES | 36 health outcomes at tract level (diabetes, obesity, smoking, depression, etc.) | Tract / ZCTA | Add later (CHR covers county well; CDC PLACES for neighborhood-level health scoring in Stoop Search) |
| Walk Score API | Walk / Transit / Bike score per address | Point / address | Skip / defer — explore free license for Stoop Search display only; moves to Points layer if available |
| Social Capital Index (JEC) | County-level civic engagement, social trust, associational density | County | Add later — interesting editorial angle, low complexity |

---

### Topic: Transportation *(proposed new topic)*

| Source | Metrics | Geo grain | Status |
|---|---|---|---|
| ACS | Commute mode share: drive alone, transit, bike, walk, WFH (B08301); mean travel time (B08012); vehicle availability (B08201) | Tract → US | Scope (move from QoL to this topic) |
| EPA Smart Location Database | 90+ built-environment indicators: transit accessibility, intersection density, land use mix, employment density | Block group → aggregate to tract | Add later (2021 vintage; aggregate to tract/ZCTA for consistency) |
| Transitland / BTS | Transit stop coverage and route density by county / metro | County / metro | Aggregated from Points layer |

**Note:** Transit stop counts and density aggregate up from the Points layer (Transitland GTFS ingest) — this topic receives those aggregations, not a separate Places-level ingest.

---

### Topic: Climate & Environmental Risk *(proposed new topic)*

| Source | Metrics | Geo grain | Status |
|---|---|---|---|
| FEMA NRI | Natural hazard risk scores: 18 hazard types (flood, wind, earthquake, wildfire, etc.) | Census tract / county | Scope |
| FEMA NFHL | Flood zone designations (SFHA, 100-year, 500-year) | Parcel / polygon | Aggregated from Polygons layer |
| EPA EJScreen | Particulates, ozone, superfund proximity, wastewater discharge, pollution burden | Block group → aggregate to tract | Add later (lower priority; aggregate to tract for grain consistency) |
| NOAA | Heat days, precipitation trends | County / metro | Planned (longer term) |

**Note:** FEMA flood zone coverage (percent of NTA in SFHA) aggregates up from the Polygons layer — this topic receives those aggregations.

---

## Part 2: Spatial Layer (Points / Parcels / Polygons)

### Pipeline flow

```
Source data (various)
    ↓
Bronze — raw ingest (as-is from source)
    ↓
Silver — clean, standardize, geolocate
    - Points: assign surrogate point_id, write source IDs to point_source_mapping,
              dedupe by proximity + name match, normalize taxonomy,
              enrich via Google Places (curated layer), geocode addresses where
              no coordinates exist, pass through native lat/lon for OSM/Overture/GTFS
    - Parcels: standardize schema, reproject to WGS84, join zoning attributes,
               flag vacant/type, link to NTA/tract
    - Polygons: standardize geometry, reproject to WGS84, validate topology,
                attach attributes, dissolve/simplify
    ↓
Gold — final databases
    - dim_point_of_interest (one row per physical location, surrogate point_id)
    - point_source_mapping (one row per source ID per point — see schema below)
    - dim_parcel (one row per tax lot)
    - dim_polygon (one row per zone or boundary)
    ↓
fct_geo_aggregations — spatial joins → NTA / tract metrics
    - Point-in-polygon: POI counts and density per NTA / tract by category
    - Parcel aggregations: zoning mix, vacancy rate, avg assessed value per NTA
    - Polygon overlaps: school zone assignment, flood exposure share per tract
    ↓
Places Gold layer (joined to ACS, BEA, BLS, HUD, Zillow, FHFA metrics)
```

---

### Points layer

**Primary table:** `dim_point_of_interest`
**Grain:** One row per physical location
**Key identifier:** Surrogate `point_id` — generated at ingest time, owned by the platform
**Geometry:** lat/lon stored in DuckDB; WGS84
**Taxonomy:** `category / subcategory / detail` driven by `config/poi_categories.yaml`
**Geography links:** NTA, census tract, borough/county — from spatial join at pipeline time
**Enrichment flags:** `is_curated`, `rating`, `review_count`, `source_list`

#### ID strategy

No single external ID covers all point types, so the platform uses a surrogate key with a separate mapping table linking back to each source's native ID.

```
dim_point_of_interest          point_source_mapping
─────────────────────          ──────────────────────────────────
point_id  (surrogate PK)  →    point_id    (FK)
name                           source_name (google | osm | overture |
category                                    nces | ipeds | gtfs | ...)
lat, lon                       source_id   (native ID from that source)
nta_id, tract_id, ...          source_url  (optional deep link)
```

The same physical location may have records from multiple sources (an Overture place, an OSM node, and a Google Place ID all referring to the same restaurant). Deduplication at silver produces one `point_id` with all source IDs attached in `point_source_mapping`.

**Source-native IDs by point type:**

| Point type | Source ID | Notes |
|---|---|---|
| Curated POIs (restaurants, hotels, bars) | Google Place ID | Stable; cache-first per ToS |
| OSM points | OSM node ID | Prefix with `osm:` to namespace |
| Overture places | Overture place ID | Persistent across Overture releases |
| K–12 schools | NCES NCESSCH (12-digit) | Federal standard; cross-referenceable |
| Colleges / universities | IPEDS UnitID | Permanent per institution |
| Hospitals | CMS Certification Number | Most cross-referenceable federal ID |
| Transit stops | GTFS `stop_id` (per agency) | Not globally unique — prefix with agency ID |
| Parcels | BBL (NYC) / APN (national) | Tax system IDs; stable within jurisdiction |

#### Coordinate strategy

Most source datasets ship with native coordinates. Geocoding is only needed for sources that provide an address but no geometry.

| Source type | Has coordinates? | Action at silver |
|---|---|---|
| OSM / Overture | Yes — lat/lon native | Pass through; validate range |
| GTFS transit stops | Yes — lat/lon in stops.txt | Pass through directly |
| NCES, IPEDS, HIFLD, IMLS | Yes — lat/lon in federal dataset | Pass through; validate range |
| Editorial scrapes (Eater, Infatuation, etc.) | No — address only | Geocode via Google Places API |
| HMDA, crime incidents | No — address only | Geocode via Census Geocoder batch |
| User-submitted / Excel upload | Maybe | Geocode if lat/lon missing |

#### Geocoding tools (curated layer only)
- Google Places API — primary for curated POI resolution by name; returns enriched metadata alongside coordinates
- Census Geocoder — free batch fallback for address-only lists (up to 10k/batch); returns Census tract enrichment
- Geocodio — cost-effective commercial option (~$0.50/1k) for large address batches with Census tract enrichment built in

#### Enrichment path (curated layer)
1. Google Places API — cache-first; resolved IDs and metadata persist locally to minimize API calls
2. Yelp Fusion — food/drink ratings supplement
3. Source metadata — name, address, hours from original dataset as fallback

#### Source inventory — national (ingest once)

| Dataset | Source | What it provides | Update cadence |
|---|---|---|---|
| K–12 schools | NCES Common Core of Data | Lat/lon, enrollment, Title I status, grade span, locale code | Annual |
| Colleges / universities | IPEDS | Lat/lon for all Title IV institutions, enrollment, completion | Annual |
| Hospitals | HIFLD | Location, trauma level, bed count, ownership type | Annual |
| Public libraries | IMLS Public Library Survey | Location, hours, collection size, visit counts | Annual |
| Farmers markets | USDA National Farmers Market Directory | Location, market characteristics | Annual |
| Flood zones | FEMA NFHL | Flood zone designation polygons (also feeds Polygons layer) | Periodic (FIRM updates) |

#### Source inventory — per market (framework built once, triggered per deep-dive)

| Dataset | Source | What it provides | Notes |
|---|---|---|---|
| Transit stops | Transitland API (multi-city); MTA GTFS (NYC) | Stop locations, routes, lines, ADA status | Transitland aggregates 1,000+ US GTFS feeds; single API, parameterize by bounding box |
| POIs (restaurants, bars, cafes, grocery, parks, shopping) | Overture Places; OSM via Overpass | Point locations, names, categories, basic attributes | Query by bounding box; map to poi_categories.yaml at ingest; build framework once |
| Hotels | Overture Places; Google Places enrichment | Location, stars, rooms, brand, website | Framework already built for NYC |
| Editorial curated lists | Time Out, Eater, Infatuation, NYT, Condé Nast | Curated recommendations, rankings, editorial context | City-specific; must be sourced per market; 19 NYC scrapes live |
| Crime incidents | City open data portals | Geocoded incident-level data | NYC, Chicago, LA, SF, Seattle, Boston all publish this; standardize silver model once, apply per market |

#### Source inventory — deep-dive only

| Dataset | Source | What it provides | Notes |
|---|---|---|---|
| School attendance zones | NCES SABINS; GreatSchools | Attendance boundary polygons | Critical for Stoop Search (which school zone is this address in?); market-specific |
| Bike infrastructure | OSM (cycleway=*); city open data | Bike lane geometry, type | City-specific datasets richer than OSM; add during first deep-dive transit scoring cycle |
| Childcare / daycares | HHS Child Care Finder; state licensing | Provider locations, capacity | No clean national source; explore quality on first use |

---

### Parcels layer

**Primary table:** `dim_parcel`
**Grain:** One row per tax lot / parcel
**Key identifier:** BBL (NYC); APN (national via Regrid)
**Geometry:** Polygon stored as WKT; WGS84
**Ingestion scope:** Per market — build framework from NYC/PLUTO; Regrid for national expansion

#### What parcel tax records contain

County assessor and tax records are the upstream source that Regrid standardizes. Attributes vary by jurisdiction but the standardized schema typically includes:

**Ownership & identity**
- Owner name, owner mailing address
- Last sale price, last sale date

**Valuation**
- Assessed land value, assessed improvement (building) value, total assessed value
- Market value (where published separately from assessed value)

**Physical characteristics**
- Lot area (sq ft / acres), building square footage
- Year built, number of stories
- Number of residential units, commercial units (broken out in PLUTO)
- Building class / construction type

**Regulatory**
- Land use classification (residential, commercial, industrial, mixed-use, vacant)
- Zoning district (joined from Polygons layer at silver)
- Floor area ratio (FAR) — available in NYC PLUTO; varies nationally
- Vacancy flag (from Regrid premium or city assessor data)

**Geography**
- NTA, census tract (from centroid spatial join at silver)
- Street address, ZIP code

**Analytical use notes:**
- Last sale price + date signal undervalued land and market timing — key for ROF retail analysis
- Assessed value trends identify neighborhoods with rising land costs ahead of rental markets
- FAR and land use classification together define development capacity
- Vacancy flag is the primary filter for retail opportunity site identification

**Aggregates to Places:**
- Zoning mix per NTA (percent residential / commercial / industrial)
- Vacancy rate per NTA
- Average assessed value per NTA
- Average year built per NTA (housing stock age signal)

| Source | Market | Notes |
|---|---|---|
| NYC MapPLUTO | NYC | Lot-level geometry, zoning, year built, FAR, units (residential/commercial/office/retail split), assessed value. Free from NYC Open Data. Framework baseline. |
| Regrid | National | 150M+ US parcels, standardized schema. Free tier = geometry only; full attributes = paid. Expansion markets. |
| County assessor files | Market-specific | Raw source upstream of Regrid for some markets. Use Regrid as the standardized layer rather than processing raw assessor files directly. |

---

### Polygons layer

**Primary table:** `dim_polygon`
**Grain:** One row per zone or boundary polygon
**Key identifier:** `polygon_id` (surrogate) + `polygon_type` + `source`
**Geometry:** Polygon/multipolygon stored as WKT; WGS84

**Polygon types and their roles in the pipeline:**

| Type | Source | Scope | Role |
|---|---|---|---|
| Zoning districts | National Zoning Atlas; city planning shapefiles | Per market | Joined to Parcels at silver to attach permitted uses. Aggregates zoning mix to NTA for Places. |
| School attendance zones | NCES SABINS; GreatSchools | Deep-dive only | Point-in-polygon: which school zone does a given address fall in? Critical for Stoop Search. |
| Flood zones (NFHL) | FEMA | National (ingest once) | Joined to Parcels (parcel-level flood exposure). Aggregates flood exposure share to tract for Places Climate topic. |
| Park boundaries (baseline) | Overture | National (ingest once) | Park polygon geometry. Area contributes to green space density metric in Places. |
| Park boundaries (enriched) | City parks open data (NYC Parks, etc.) | Per market | Richer attribute data — amenities, acreage, programming. Featured markets only. |
| Neighborhood boundaries | City open data; Census TIGER | Per market | NTAs (NYC) or city-defined equivalents. The aggregation unit connecting Points/Parcels to Places. |
| Admin boundaries | TIGER/Line | National | State, county, CBSA, tract, ZCTA geometries. Foundation of the geography hierarchy. |

---

## Part 3: Source Reference Index

All data sources used across the platform, with access details.

### Federal / government (free)

| Source | URL | Primary use |
|---|---|---|
| ACS (Census Bureau) | census.gov/data/developers | Demographics, housing, economics, QoL |
| BEA Regional API | apps.bea.gov/api | GDP, income, Regional Price Parity |
| BLS LAUS | bls.gov/lau | Unemployment, labor force |
| BLS QCEW | bls.gov/cew | Industry employment and wages |
| BPS (Census Bureau) | census.gov/construction/bps | Building permits |
| CBP (County Business Patterns) | census.gov/data/datasets/time-series/econ/cbp | Establishment counts by NAICS |
| BFS (Business Formation Statistics) | census.gov/econ/bfs | New business applications |
| IRS Migration | irs.gov/statistics/soi-tax-stats-migration-data | County-to-county migration flows |
| IPEDS | nces.ed.gov/ipeds | Higher education institutions |
| NCES Common Core of Data | nces.ed.gov/ccd | K–12 school locations and attributes |
| NCES SABINS | nces.ed.gov/programs/edge/geographic/schoollocations | School attendance zone boundaries |
| HIFLD | hifld-geoplatform.opendata.arcgis.com | Hospital and infrastructure locations |
| IMLS | imls.gov/research-evaluation/data-collection/public-libraries-survey | Public library data |
| HUD CHAS | huduser.gov/portal/datasets/cp.html | Rent burden by income tier |
| HUD FMR | huduser.gov/portal/datasets/fmr.html | Fair Market Rents |
| FHFA HPI | fhfa.gov/data/hpi | Repeat-sales home price index |
| FHFA Underserved Areas | fhfa.gov/PolicyProgramsResearch/Programs/Pages/Duty-to-Serve | Underserved market designations |
| HMDA | ffiec.cfpb.gov/hmda-pub/disclosure/2023 | Mortgage lending data |
| FEMA NRI | hazards.fema.gov/nri | Natural hazard risk scores |
| FEMA NFHL | msc.fema.gov/portal/home | Flood zone designations |
| EPA EJScreen | epa.gov/ejscreen | Environmental burden indicators |
| EPA Smart Location Database | epa.gov/smartgrowth/smart-location-mapping | Built-environment indicators |
| FBI Crime Data Explorer | cde.ucr.cjis.gov | City/agency-level crime statistics (metro comparison only) |
| USDA NFMD | usda.gov/farmersmarkets | Farmers market locations |
| USDA Food Access Research Atlas | ers.usda.gov/data-products/food-access-research-atlas | Food desert designations |
| TIGER/Line | census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html | Geographic boundaries and crosswalks |
| CHR (County Health Rankings) | countyhealthrankings.org | County health outcomes and factors |
| CDC PLACES | cdc.gov/places | Tract-level health outcomes |
| FHWA | fhwa.dot.gov | Road density (supplemental) |
| BTS National Transit Map | bts.gov/national-transit-map | Quarterly GTFS compilation |

### Open data (free)

| Source | URL | Primary use |
|---|---|---|
| OpenStreetMap (via Overpass API) | overpass-api.de | POI points, roads, pedestrian infrastructure |
| Overture Maps | overturemaps.org | Buildings, places (54M POIs), road network — GeoParquet on AWS/Azure |
| Microsoft Building Footprints | github.com/microsoft/GlobalMLBuildingFootprints | ML-derived building geometry (US national) |
| National Zoning Atlas | zoningatlas.org | Digitized zoning data (33,000+ jurisdictions) |
| Transitland | transit.land | Aggregated GTFS feeds (1,000+ US agencies) |
| Mobility Database | mobilitydatabase.org | GTFS feed registry (global) |
| NYC Open Data | opendata.cityofnewyork.us | NYC-specific: LION, parks, crime, subway, PLUTO |
| NLCD (USGS) | mrlc.gov/data | National land cover (30m raster) — deferred |
| JEC Social Capital Project | jec.senate.gov/public/index.cfm/republicans/2018/4/the-geography-of-social-capital-in-america | County social capital index |

### Commercial / freemium

| Source | URL | Cost model | Primary use |
|---|---|---|---|
| Google Places API | developers.google.com/maps/documentation/places | Pay per lookup | Curated POI resolution, geocoding, ratings |
| Census Geocoder | geocoding.geo.census.gov | Free (10k batch limit) | Batch address geocoding fallback |
| Geocodio | geocod.io | ~$0.50/1k addresses | Batch geocoding at scale with Census tract enrichment |
| Regrid | regrid.com | Freemium (geometry free; attributes paid) | National parcel data |
| GreatSchools API | greatschools.org | $52/mo, 15k calls/mo | School quality ratings — deferred, market-specific on deep-dive |
| Yelp Fusion API | docs.developer.yelp.com | 500 calls/day free; commercial for bulk | Restaurant/bar ratings supplement |
| Zillow | zillow.com/research/data | Free CSV downloads | ZHVI, ZORI, inventory, days on market |
| Walk Score API | walkscore.com/professional | Freemium | Deprioritized — explore free license for Stoop Search only |
| SafeGraph | safegraph.com | Commercial license | Foot traffic — not currently in scope |
| HERE Maps | developer.here.com | Paid API | Road attributes — not currently in scope |

---

## Part 4: Ingestion Scope Rules

| Rule | What it means |
|---|---|
| **National (ingest once)** | Small, stable federal datasets. Ingest across all geographies in a single run. Update annually or on source release. Examples: NCES CCD, IPEDS, HIFLD, IMLS, FEMA NFHL. |
| **Per market (framework first)** | Larger datasets where volume scales with geography. Build the ingestion framework once, parameterized by bounding box or metro area code. Trigger per market on first deep-dive. Never pre-ingest nationally. Examples: Overture POIs, OSM, Transitland GTFS, Parcels, Zoning. |
| **Deep-dive only** | Data that requires significant sourcing effort or has high operational cost. Only ingest for featured markets where the product specifically needs it. Examples: school attendance zones, bike infrastructure, city crime incidents, childcare providers. |
| **Attribute (not standalone)** | Binary designation flags (Opportunity Zones, FHFA Underserved, FEMA flood zone share). Joined to existing tables at build time — not maintained as standalone sources. |
| **Aggregate from Points/Polygons** | Places metrics that are derived from spatial layer data. Not re-ingested from source at the Places level — computed from the Points/Polygons Gold tables. Examples: POI density, zoning mix, flood exposure share, transit stop count per NTA. |

---

## Part 5: Neighborhood Boundary Strategy

NYC uses **NTAs (Neighborhood Tabulation Areas)** — 262 named areas covering all five boroughs — as the primary neighborhood unit. For national expansion, each market needs an equivalent boundary layer.

| Market type | Recommended neighborhood unit | Source |
|---|---|---|
| NYC | NTA (262 areas) | NYC Open Data (hm78-6dwm equivalency table) |
| Other large cities | City-defined neighborhood boundaries (if published) | City open data portals |
| Markets without published boundaries | Census tracts (as fallback) | TIGER/Line |
| All markets | Census tract (for ACS metric joins) | TIGER/Line |

The neighborhood boundary layer is a prerequisite for any market deep-dive. Sourcing it is part of the market onboarding checklist.

---

## Part 6: Open Items & Decision Log

| Item | Status | Decision / next step |
|---|---|---|
| ACS broadband (B28002), disability (B18101), language (B16001) | Not yet ingested | Add to next ACS ingestion cycle |
| CBP County Business Patterns | Scope | Add alongside BFS — both are straightforward Census downloads |
| HMDA mortgage data | Scope | After FHFA work is stable; scope separately |
| Overture / OSM ingestion framework | Build when ready | Design during first true metro deep-dive; parameterize by bounding box |
| GreatSchools API | Deferred | $52/mo with 15k call limit — explore on first market deep-dive |
| CDC PLACES | Add later | CHR covers county well; add when neighborhood-level health scoring needed |
| EPA Smart Location Database | Add later | Aggregate block group → tract; 2021 vintage acceptable as baseline |
| FEMA NRI | Scope | Tract-level; strong climate risk editorial angle; priority for Sun Belt and coastal markets |
| Transportation topic | Proposed | Move commute/WFH metrics out of QoL; add EPA SLD aggregations when ready |
| Climate & Environmental Risk topic | Proposed | FEMA NRI + EJScreen + NOAA (longer term); separate from QoL |
| Neighborhood boundary equivalents | Decision needed per market | NTA works for NYC; Chicago community areas, LA neighborhood councils, others vary — needs market-specific sourcing decision |
| Walk Score API | Deprioritized | Explore free license for Stoop Search property-level display only |
| FBI UCR county-level data | Skip | ICPSR county files require non-standard FIPS crosswalk and have significant voluntary reporting gaps |
| NLCD (National Land Cover Database) | Skip | 30m raster — overkill; Overture building polygons + OSM landuse sufficient |
| Historical zoning changes | Skip | Editorial content angle, not a product data layer |