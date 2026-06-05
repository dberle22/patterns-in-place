# BLS QCEW Industry Inventory

## Current Status

- This note has now been turned into a reproducible mapping asset:
  - [`../../etl/reference/bls_qcew_industry_map.csv`](../../etl/reference/bls_qcew_industry_map.csv)
  - built by [`../../etl/reference/build_bls_qcew_industry_map.R`](../../etl/reference/build_bls_qcew_industry_map.R)
- The generated mapping currently contains `2,660` published industry members across the `2010–2024` annual archives.
- The year-to-year changes matter because the published QCEW code universe shifts across NAICS vintages:
  - `2010`: `2,363` codes
  - `2011–2016`: `2,244` codes
  - `2017–2021`: `2,231` codes
  - `2022–2024`: `2,159` codes

## What The Raw Annual ZIP Contains

- Tested source: `2010_annual_by_industry.zip`
- Raw structure: one ZIP per year, with one CSV member per published industry code
- Member count in the 2010 annual ZIP: `2,363` CSV files
- Geography coverage in the raw members is broader than county-only:
  - total-industry member includes state rows (`agglvl_code` `50`, `51`, `96`) and county rows (`70`, `71`)
  - non-total industry members include state rows (`54`) and county rows (`74`)
- Current ingestion design should therefore be thought of as:
  - raw source has state + county coverage
  - staging should keep both state and county rows for the annual ingest path

## Recommended Modeling Direction

- Keep all exported industry members in `staging`
- Add a mapping layer in `silver` that preserves the raw code and adds metadata describing how the code should be interpreted
- Keep the extra QCEW fields that already exist in the source files:
  - `lq_*`
  - `oty_*`

## Proposed Metadata Columns For The Silver Mapping

| Column | Purpose |
| --- | --- |
| `industry_code` | Raw BLS member code from the ZIP member and row payload |
| `industry_title` | Human-readable title from the source |
| `code_type` | One of `total`, `supersector_aggregate`, `naics_compound_sector`, `naics_sector`, `naics_subsector`, `naics_industry_group`, `naics_industry`, `naics_national_industry`, `unclassified` |
| `code_length` | Character length of the code after preserving hyphens |
| `is_aggregate` | Boolean flag for non-leaf grouped members |
| `aggregate_components` | Delimited list of the higher-level codes that appear to compose the aggregate, when known |
| `keep_in_staging` | Boolean, expected to be `TRUE` for all published members we ingest |
| `keep_in_silver_canonical` | Boolean flag for the subset we want in the main analytical Silver contract |
| `silver_rollup_family` | Optional grouped family label such as `goods_producing`, `trade_transport_utilities`, `financial_activities` |
| `notes` | Free-text caveats or confirmation needs |

## Recommended High-Signal Code Table

This is the most important first-pass table for the Silver mapping layer. The component lists below are inferred from the member titles and should be confirmed against BLS supersector definitions before hard-coding.

| Industry code | Industry title | Code type | Aggregate components | Suggested Silver treatment |
| --- | --- | --- | --- | --- |
| `10` | Total, all industries | `total` |  | Keep |
| `11` | Agriculture, forestry, fishing and hunting | `naics_sector` |  | Keep |
| `21` | Mining, quarrying, and oil and gas extraction | `naics_sector` |  | Keep |
| `22` | Utilities | `naics_sector` |  | Keep |
| `23` | Construction | `naics_sector` |  | Keep |
| `31-33` | Manufacturing | `naics_compound_sector` | `31`, `32`, `33` | Keep |
| `42` | Wholesale trade | `naics_sector` |  | Keep |
| `44-45` | Retail trade | `naics_compound_sector` | `44`, `45` | Keep |
| `48-49` | Transportation and warehousing | `naics_compound_sector` | `48`, `49` | Keep |
| `51` | Information | `naics_sector` |  | Keep |
| `52` | Finance and insurance | `naics_sector` |  | Keep |
| `53` | Real estate and rental and leasing | `naics_sector` |  | Keep |
| `54` | Professional and technical services | `naics_sector` |  | Keep |
| `55` | Management of companies and enterprises | `naics_sector` |  | Keep |
| `56` | Administrative and waste services | `naics_sector` |  | Keep |
| `61` | Educational services | `naics_sector` |  | Keep |
| `62` | Health care and social assistance | `naics_sector` |  | Keep |
| `71` | Arts, entertainment, and recreation | `naics_sector` |  | Keep |
| `72` | Accommodation and food services | `naics_sector` |  | Keep |
| `81` | Other services, except public administration | `naics_sector` |  | Keep |
| `92` | Public administration | `naics_sector` |  | Keep |
| `99` | Unclassified | `unclassified` |  | Keep in staging, optional in canonical Silver |
| `101` | Goods-producing | `supersector_aggregate` | `11`, `21`, `23`, `31-33` | Keep as optional aggregate |
| `102` | Service-providing | `supersector_aggregate` | Confirm before hard-coding | Keep as optional aggregate |
| `1011` | Natural resources and mining | `supersector_aggregate` | `11`, `21` | Keep as optional aggregate |
| `1012` | Construction | `supersector_aggregate` | `23` | Usually redundant with `23` |
| `1013` | Manufacturing | `supersector_aggregate` | `31-33` | Usually redundant with `31-33` |
| `1021` | Trade, transportation, and utilities | `supersector_aggregate` | `22`, `42`, `44-45`, `48-49` | Good Silver rollup candidate |
| `1022` | Information | `supersector_aggregate` | `51` | Redundant with `51` |
| `1023` | Financial activities | `supersector_aggregate` | `52`, `53` | Good Silver rollup candidate |
| `1024` | Professional and business services | `supersector_aggregate` | `54`, `55`, `56` | Good Silver rollup candidate |
| `1025` | Education and health services | `supersector_aggregate` | `61`, `62` | Good Silver rollup candidate |
| `1026` | Leisure and hospitality | `supersector_aggregate` | `71`, `72` | Good Silver rollup candidate |
| `1027` | Other services | `supersector_aggregate` | `81` | Usually redundant with `81` |
| `1028` | Public administration | `supersector_aggregate` | `92` | Usually redundant with `92` |
| `1029` | Unclassified | `supersector_aggregate` | `99` | Usually redundant with `99` |

## What Else Exists In The Raw ZIP

Examples of additional published member levels that show up in the annual ZIP and should be preserved if we keep the raw member universe in staging:

- `3`-digit subsectors such as:
  - `111` Crop production
  - `221` Utilities
  - `236` Construction of buildings
  - `423` Merchant wholesalers, durable goods
  - `511` Publishing industries, except internet
  - `621` Ambulatory health care services
  - `721` Accommodation
  - `921` Executive, legislative and general government
- `4`-digit groups such as:
  - `1011` Natural resources and mining
  - `2211` Power generation and supply
  - `5411` Legal services
  - `6211` Offices of physicians
  - `7221` Full-service restaurants
  - `8111` Automotive repair and maintenance
- still-deeper `5`- and `6`-digit NAICS-style members and a final unclassified ladder like `999`, `9999`, `99999`, `999999`

## Answer To The Geography Question

The raw annual ZIP does **not** only contain county data.

What is present in the raw files:

- state rows
- county rows
- ownership-specific variants of both
- total-covered and government-specific variants for some members

What the current ingestion script does:

- filters to county rows only
- keeps all ownership rolled up to `own_code = 0`
- keeps all establishment sizes rolled up to `size_code = 0`
- keeps annual rows only (`qtr = A`)

So the current county-only behavior is a modeling choice, not a source limitation.

## Current Staging Footprint

After the full annual singlefile backfill for `2010–2024`, the source-faithful staging landings are:

- `staging.bls_qcew_county`: `43,342,060` rows
- `staging.bls_qcew_state`: `2,073,926` rows
- Combined staged rows: `45,415,986`
- Distinct published `industry_code` values retained across the full annual range: `2,660`
