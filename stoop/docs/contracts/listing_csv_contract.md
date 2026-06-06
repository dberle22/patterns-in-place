# Manual Listing CSV Contract

This is the Sprint 1 contract for manually building the first property listing
file. It is designed to be easy to maintain by hand while still supporting
listing cards, map display, scoring, and detail review.

## File Location

Default path: `data/raw/property_listings.csv`

Recommended source label: `manual_csv`

The raw file is local runtime data and should not be committed if it contains
real listing links, addresses, or notes.

## MVP Collection Pattern

- The first file can mix rentals and sales, with a rental lean.
- The first manual sources are expected to be StreetEasy and Zillow links/facts.
- The user will gather listings manually; the pipeline should normalize and
  validate the file.
- `no_fee` is part of the MVP CSV because broker fees are important for rental
  affordability.
- `days_on_market` is deferred until scraper or adapter data makes it easier to
  maintain consistently.
- Listing images are post-MVP. For now, collect only the source URL.

## Required Columns For Ingestion

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `address` | string | yes | Display address or source listing title. |
| `lat` | double | yes after geocoding | WGS84 latitude. Can be blank in the raw CSV only if a geocoding step fills it before scoring. |
| `lon` | double | yes after geocoding | WGS84 longitude. Can be blank in the raw CSV only if a geocoding step fills it before scoring. |
| `price` | number | yes | Monthly rent for rentals; asking price for sales. |
| `beds` | number | yes | Use `0` for studio. |
| `baths` | number | yes | Half baths allowed, for example `1.5`. |
| `listing_type` | string | yes | Allowed values: `rental`, `sale`. |
| `no_fee` | boolean | yes for rentals | Important rental affordability field. Use blank for sales when not applicable. |
| `url` | string | strongly recommended | Source listing URL. |

## Strongly Recommended Columns

| Column | Type | Notes |
| --- | --- | --- |
| `source` | string | Provider or workflow label. If omitted, pipeline can use `manual_csv`. |
| `source_listing_id` | string | Listing ID from source when available. Improves dedupe stability. |
| `neighborhood_label` | string | Source-provided neighborhood label. |
| `borough` | string | Useful before geography assignment is complete. |
| `unit` | string | Unit/apartment label. |
| `sqft` | number | Interior square footage. |
| `available_date` | date | ISO `YYYY-MM-DD` preferred. |
| `broker_fee` | string | Keep as text because sources vary. |
| `amenities` | string | JSON array text preferred, for example `["laundry","elevator"]`. |
| `description` | string | Short source description or notes. |
| `active` | boolean | Defaults to `true` for rows in the current manual file. |
| `source_updated_at` | timestamp | Listed/updated timestamp when available. |
| `coordinate_quality` | string | Allowed values: `exact_address`, `approximate`, `geocoded`, `source_provided`, `unknown`. |
| `geocoded_from_address` | boolean | True when coordinates were generated from address text. |
| `geocode_source` | string | Geocoder used, for example `nyc_geosearch`, `nyc_geoclient`, or `manual`. |

## Validation Rules

- `listing_type` must be `rental` or `sale`.
- Rental rows should include `no_fee` as `true` or `false`; sale rows may leave
  it blank.
- `price` must be greater than `0`.
- `beds` and `baths` must be greater than or equal to `0`.
- `lat` and `lon` are required for the normalized listing table and property
  context scoring.
- Raw CSV rows may omit `lat` and `lon` when a valid address is available, but
  those rows must be geocoded before they can appear on the map or receive
  spatial scores.
- Rows that still lack coordinates after geocoding should be rejected or
  quarantined.
- Approximate coordinates are acceptable for MVP when exact addresses are not
  available, but `coordinate_quality` should make that clear.
- Coordinates should fall inside the NYC MVP bounding box:
  `lat 40.45-40.95`, `lon -74.30--73.65`.
- `url` should be present for all real listings unless the row is a synthetic
  fixture.
- Duplicate rows should collapse to one `property_id`, preferring the latest
  `source_updated_at` or latest ingested row.
- Rental and sale listings can live in the same file, but the app should avoid
  ranking them as directly comparable value opportunities in MVP.

## Example Rows

```csv
source,source_listing_id,address,unit,lat,lon,price,beds,baths,listing_type,no_fee,url,neighborhood_label,borough,sqft,available_date,broker_fee,amenities,description,active,source_updated_at,coordinate_quality,geocoded_from_address,geocode_source
streeteasy_saved,se-12345,"123 Example St","4B",40.6872,-73.9901,4200,2,1,rental,true,https://example.com/listing/12345,"Boerum Hill",Brooklyn,850,2026-05-01,none,"[""laundry"",""dishwasher""]","Sunny two bedroom near transit",true,2026-04-15T10:30:00Z,exact_address,false,source_provided
zillow_saved,z-98765,"456 Sample Ave","",,,875000,1,1,sale,,https://example.com/listing/98765,"Hell's Kitchen",Manhattan,690,,unknown,"[""elevator"",""doorman""]","One bedroom condo near multiple lines",true,2026-04-14T09:00:00Z,unknown,true,nyc_geosearch
```

## First-Pass Manual Source Ideas

- Saved listing links from StreetEasy and Zillow, with facts copied into the CSV
  for personal use.
- Later manual sources can include RentHop, Realtor.com, Compass, or brokerage
  pages if useful.
- Broker-provided listing spreadsheets or emails converted into the CSV
  contract.
- Personal shortlist exports from marketplaces when the site provides an export
  or shareable listing data.
- Manually geocoded listing addresses from public map tools, reviewed before
  ingest.
- Address-only rows geocoded through an explicit local step, with unmatched rows
  quarantined for review.
- Synthetic fixture rows for tests and demos when real listing data should not
  be shared.

## Geocoding Notes

Geocoding converts a listing address into latitude and longitude so the app can
put the listing on the map, assign it to a tract/NTA, compute nearest subway
distance, and count nearby personal POIs. The normalized
`property_explorer_gold.dim_property_listing` table still needs coordinates,
but a raw CSV row can start with address only if the pipeline adds a geocoding
stage before map/scoring.

The geocoding step should:

- Read rows with an address but missing `lat`/`lon`.
- Send the address to a configured geocoder or use a manually prepared geocode
  lookup.
- Write matched coordinates plus match quality/source to
  `data/interim/geocoding/listing_geocodes.csv`.
- Quarantine unmatched or low-confidence rows for review instead of silently
  placing them on the map.

Good candidate sources are NYC GeoSearch for simple forward geocoding and NYC
Geoclient/Geoservice for more official NYC address handling.

## Resolved Sprint 1 Choices

1. The first file can mix rentals and sales, leaning toward rentals.
2. First manual sources are StreetEasy and Zillow.
3. `image_url` is post-MVP; source URL is enough for MVP.
4. Approximate coordinates are acceptable, but address-based rows are preferred.
5. Keyword POI categories are enough for MVP; manual overrides are post-MVP.
6. `no_fee` is part of the rental CSV contract.
7. `days_on_market` is deferred until scraper/adapter data exists.

## Remaining Open Questions

1. Which exact geocoding provider should Sprint 2 use first if `lat`/`lon` are
   missing?
