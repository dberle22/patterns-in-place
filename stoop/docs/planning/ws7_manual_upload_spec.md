# WS7 Manual Upload Spec

Last updated: 2026-04-29

## Goal

Define the exact contributor-facing spreadsheet contract for curated POI manual
uploads, plus the normalization rules needed to convert that sheet into a
reviewable machine-readable batch for downstream dedupe, Places resolution, and
canonical merge work.

This spec is intentionally limited to the intake template and reader contract.
It does not define Google Sheets integration, Places API enrichment, or the
canonical merge implementation.

---

## Scope

WS7 covers:

- one shared spreadsheet template that can be used in Excel or Google Sheets
- one reader that accepts `.xlsx` or `.csv`
- one normalization pass that emits a consistent manual-upload dataframe

WS7 does not cover:

- article scraping
- semi-manual extractor logic
- Google Places matching behavior changes
- canonical merge policy changes beyond producing the expected staging shape

---

## Template design

The template should have two tabs when used as a spreadsheet:

1. `manual_poi_upload`
2. `instructions`

If exported to CSV, only the `manual_poi_upload` tab matters.

### Required columns

These fields must be present as headers and must be populated on every kept
row unless otherwise noted.

| Column | Required | Type | Description | Example |
| --- | --- | --- | --- | --- |
| `item_name` | yes | text | Venue or place name as the contributor knows it | `Le Bernardin` |
| `category` | yes | text | Locked top-level curated category | `restaurants` |
| `subcategory` | yes | text | Stable second-level filter bucket | `french` |

### Recommended columns

These fields should be included in the template and should usually be filled
when the contributor knows the value.

| Column | Required | Type | Description | Example |
| --- | --- | --- | --- | --- |
| `raw_address` | no | text | Street address or best known address string | `155 W 51st St, New York, NY 10019` |
| `item_url` | no | text | Official site, listing page, Instagram, or other place-specific URL | `https://www.le-bernardin.com/` |
| `raw_neighborhood` | no | text | Human-readable neighborhood hint | `Midtown West` |
| `raw_borough` | no | text | Borough hint | `Manhattan` |
| `detail_level_3` | no | text | Optional third-level descriptor | `omakase` |
| `source_list_name` | no | text | Name of the contributor’s list or theme | `Best special-occasion dinners` |
| `submitter_notes` | no | text | Freeform notes for QA or later review | `Excellent for anniversaries; add jacket dress-code note later` |

### Optional provenance columns

These fields should be available in the template because they are useful for
review, but they are not required for a valid row.

| Column | Required | Type | Description | Example |
| --- | --- | --- | --- | --- |
| `source_url` | no | text | URL where the place was discovered, if different from `item_url` | `https://example.com/best-date-night-restaurants` |
| `input_title` | no | text | Original source title if different from the final place name | `Le Bernardin - NYC` |
| `tags` | no | text | Comma-separated contributor tags | `special occasion, tasting menu, seafood` |
| `comment` | no | text | Longer structured comment field if the user prefers it over `submitter_notes` | `Known for seafood tasting menu` |
| `submitter_name` | no | text | Human submitter name or initials | `DB` |
| `batch_name` | no | text | Shared name for the uploaded batch | `nyc_restaurants_round_1` |

### System columns

These columns should not be manually edited by contributors in the first
version. The reader will create them later during normalization.

- `source_record_id`
- `source_system`
- `source_file`
- `search_query`
- `uploaded_at`
- `ingest_batch_id`

---

## Final template headers

The first version of the template should contain exactly these columns in this
order:

1. `item_name`
2. `category`
3. `subcategory`
4. `raw_address`
5. `item_url`
6. `raw_neighborhood`
7. `raw_borough`
8. `detail_level_3`
9. `source_list_name`
10. `submitter_notes`
11. `source_url`
12. `input_title`
13. `tags`
14. `comment`
15. `submitter_name`
16. `batch_name`

This order keeps the high-signal contributor fields first while preserving the
metadata we need for QA and downstream matching.

---

## Contributor rules

- One row should represent one physical place candidate.
- If a place has multiple locations, each location should be entered as its own
  row.
- `category` and `subcategory` should use the project taxonomy, not ad hoc
  labels.
- If the contributor does not know the exact address, leave `raw_address`
  blank rather than guessing.
- If the contributor has only one useful URL, prefer putting it in `item_url`.
- `submitter_notes` should be plain-language notes, not machine-formatted data.

---

## Template validation rules

The reader should apply these rules before outputting normalized rows.

### Header validation

- The file must contain all required columns.
- Missing optional columns should be created and filled with blank strings.
- Extra unknown columns may be preserved for audit, but they should not block
  ingestion in v1.

### Row filtering

- Completely blank rows should be dropped.
- Rows with blank `item_name` should fail validation.
- Rows with blank `category` should fail validation.
- Rows with blank `subcategory` should fail validation.

### Value cleanup

- Trim surrounding whitespace on all text fields.
- Collapse repeated internal whitespace to single spaces.
- Convert Excel `NaN` / empty cells to `""`.
- Preserve contributor punctuation and casing except for whitespace cleanup.

### Soft warnings

These should not block normalization, but they should be surfaced in QA output.

- missing `raw_address`
- missing both `item_url` and `source_url`
- `raw_borough` not in `Manhattan`, `Brooklyn`, `Queens`, `Bronx`, `Staten Island`
- `category` or `subcategory` not found in the locked taxonomy
- duplicate rows within the same upload batch based on normalized
  `item_name + raw_address + source_list_name`

---

## Normalized output contract

The manual-upload reader should emit one normalized dataframe with the
following columns.

| Column | Populate from | Notes |
| --- | --- | --- |
| `source_record_id` | system-generated | Stable per-row ID from upload metadata + item identity |
| `source_system` | constant | `manual_upload` |
| `source_file` | system-generated | Input filename or sheet export name |
| `publisher` | blank | Keep blank in v1 for pure manual uploads |
| `article_slug` | blank | Keep blank in v1 |
| `article_title` | blank | Keep blank in v1 |
| `article_url` | blank | Keep blank in v1 |
| `source_list_name` | template | If blank, fallback to `batch_name`, else `manual_upload` |
| `capture_mode` | constant | `manual_upload` |
| `parser_name` | constant | blank |
| `category` | template | required |
| `subcategory` | template | required |
| `detail_level_3` | template | optional |
| `item_rank` | blank | no rank in v1 |
| `item_name` | template | required |
| `item_url` | template | optional |
| `raw_address` | template | optional |
| `raw_description` | template | build from `submitter_notes` or `comment` |
| `raw_neighborhood` | template | optional |
| `raw_borough` | template | optional |
| `scraped_at` | system-generated | upload normalization timestamp; name kept for schema compatibility |
| `input_title` | template | fallback to `item_name` |
| `note` | template | prefer `submitter_notes`, else `raw_address` |
| `tags` | template | optional text field, not parsed in v1 |
| `comment` | template | prefer `comment`, else `submitter_notes` |
| `source_url` | template | fallback to `item_url` |
| `search_query` | system-generated | built from item name + address or neighborhood + `New York, NY` |

### Search query rule

Use the same general pattern already used by the scrape pipeline:

- `item_name`
- `raw_address` if present
- otherwise `raw_neighborhood` if present
- `New York, NY`

Examples:

- `Le Bernardin 155 W 51st St, New York, NY 10019 New York, NY`
- `Le Bernardin Midtown West New York, NY`
- `Le Bernardin New York, NY`

---

## Mapping rules

### `raw_description`

Populate as:

1. `submitter_notes` if present
2. else `comment`
3. else `""`

### `note`

Populate as:

1. `submitter_notes` if present
2. else `raw_address` if present
3. else `""`

### `comment`

Populate as:

1. `comment` if present
2. else `submitter_notes` if present
3. else `""`

### `source_list_name`

Populate as:

1. `source_list_name` if present
2. else `batch_name` if present
3. else `manual_upload`

### `input_title`

Populate as:

1. `input_title` if present
2. else `item_name`

### `source_url`

Populate as:

1. `source_url` if present
2. else `item_url`
3. else `""`

---

## Reader behavior

The v1 reader should:

1. accept `.xlsx` and `.csv`
2. read the `manual_poi_upload` tab for spreadsheet inputs
3. normalize headers into the exact expected column names
4. add any missing optional columns as blanks
5. validate required fields
6. emit a normalized dataframe in the shared downstream shape
7. write a QA-friendly CSV copy for review before any enrich or merge step

The v1 reader should not:

- call Google APIs directly
- write canonical tables directly
- infer taxonomy from free text
- split multi-location rows automatically unless we explicitly add that later

---

## Google Sheets compatibility notes

To keep later Google Sheets setup simple:

- use plain lowercase snake_case headers from day one
- avoid formulas as required fields
- avoid dropdowns that write display labels different from stored values
- keep taxonomy validation values aligned exactly with canonical category names
- reserve the first row for headers only

---

## Open decisions for review

These are the only design questions that still need your sign-off before build:

1. Should `source_list_name` remain optional with fallback to `batch_name`, or
   should we make it required?
2. Do you want `submitter_notes` and `comment` as separate fields in v1, or
   should we simplify to one notes field?
3. Should `raw_borough` be free text in v1 or constrained to the five borough
   names only?

My recommendation:

- keep `source_list_name` optional in v1
- keep both `submitter_notes` and `comment`, but document `submitter_notes` as
  the main human-facing field
- keep `raw_borough` free text with a QA warning instead of a hard failure

