# Source Spec: BFS (Business Formation Statistics)

## 1. Overview

- Source: U.S. Census Bureau
- Program: Business Formation Statistics (BFS)
- Access pattern in current Track 12 scope: public annual county XLSX workbook plus public monthly BFS release files for broader series coverage; no key required
- Current county annual release as of `June 9, 2026`: years `2005-2024`, released `June 11, 2025`
- Native geography in current first-pass file: county
- Scope in Foundations: a mixed-grain BFS analytical layer where Silver can retain monthly BFS series where Census publishes them, while county and county-derived CBSA annual business-application metrics flow to Gold
- Documentation goal: define the real shape of the annual county file and set a simple ingest architecture that does not overpromise fields the source does not actually contain

The key practical finding is that the annual county BFS file is much narrower than the broader monthly BFS product family. The annual county workbook contains only Business Applications (`BA`) by county and year. It does not include county-level HBA, WBA, CBA, or business formation (`BF*`) series, so those richer series must come from separate monthly BFS files if we want them in Silver.

## 2. Coverage Matrix

| Topic group | Staging family contracts | Silver outputs | Gold outputs |
| --- | --- | --- | --- |
| BFS annual county business applications | planned `staging__bfs.md` | planned `silver.bfs` | planned annual Gold promotion for county / CBSA / state |
| BFS monthly national / state / regional application + formation series | same provider family, staged as a second BFS feed when implemented | planned `silver.bfs` | staged and silvered only; not promoted directly to Gold monthly |

This spec now treats BFS as a two-surface source family:
- annual county BA for county / CBSA / state annual business-dynamics metrics
- monthly BFS series for richer trend coverage in Silver only

## 3. Source Contract

- Provider: U.S. Census Bureau
- BFS about page: `https://www.census.gov/econ/bfs/about_the_data.html`
- BFS data page: `https://www.census.gov/econ/bfs/data.html`
- Annual county data page: `https://www.census.gov/econ/bfs/data/county.html`
- Current annual county workbook: `https://www.census.gov/econ/bfs/xlsx/bfs_county_apps_annual.xlsx`
- County data dictionary: `https://www.census.gov/econ/bfs/pdf/bfs_county_data_dictionary.pdf`
- BFS main data page for monthly release assets: `https://www.census.gov/econ/bfs/data.html`
- Authentication: none

**What we verified**

- Census says annual county BFS data start in `2005` and are released annually about 6 months after year-end.
- The current annual county file is an Excel workbook, not a CSV.
- The county data page labels the workbook specifically as "Business Applications by County."
- The county data dictionary shows the workbook carries geography columns plus `BA2005` through `BA2024`.
- The broader BFS program includes monthly BA / HBA / WBA / CBA and formation series, but Census describes those as monthly products and separately notes that annual county BFS contains Business Application data by county.

**Observed workbook shape**

The live workbook currently has one sheet named `County Data`.

The meaningful header row begins on row 3:
- `State`
- `County`
- `County Code`
- `state_fips`
- `county_fips`
- `BA2005`
- `BA2006`
- ...
- `BA2024`

Sample data row pattern:
- `AL`, `Autauga County`, `01001`, `01`, `001`, then one annual business-application count per year column

**Recommended ingestion path**

1. Download the annual county workbook directly for county business applications.
2. Read the `County Data` sheet.
3. Skip the first two title / disclosure rows.
4. Pivot `BA2005` ... `BA2024` into a long county-year table.
5. Add a second BFS staging feed for monthly released BFS series when we implement the richer Silver contract.
6. Treat annual county BA and monthly BFS series as sibling staging surfaces under one provider family rather than trying to force them into one raw file shape.

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- planned `../../etl/staging/get_bfs.R`

## 4. Staging Shape

Preferred first-pass staging output:
- `staging.bfs_county`
- one row per `county_fips + year`
- no need to preserve the original wide workbook structure after raw read

Preferred follow-on staging output for richer Silver coverage:
- `staging.bfs_monthly`
- one row per published `geo_level + geo_id + period_month + series_code`
- limited to the monthly BFS files that expose BA / HBA / WBA / CBA and formation series

**Recommended normalized staging contract**

| Column | Type | Description |
| --- | --- | --- |
| `year` | INTEGER | Calendar year derived from the `BA####` column name |
| `state_abbr` | VARCHAR | Two-letter state abbreviation from `State` |
| `county_name` | VARCHAR | County display name |
| `county_fips` | VARCHAR | Five-digit county FIPS from `County Code` |
| `state_fips` | VARCHAR | Two-digit state FIPS |
| `county_fips_3` | VARCHAR | Three-digit county code from `county_fips` source column |
| `business_applications` | DOUBLE | Annual business applications count for the county-year |
| `series_code` | VARCHAR | Fixed value `BA` for clarity in downstream joins |
| `source_file` | VARCHAR | Raw workbook identifier such as `bfs_county_apps_annual.xlsx` |

This county annual staging contract is intentionally small. The source does not justify a wider county table.

If we add the monthly BFS release files, `staging.bfs_monthly` should use a normalized shape such as:

| Column | Type | Description |
| --- | --- | --- |
| `period` | DATE or VARCHAR | Monthly period identifier |
| `year` | INTEGER | Calendar year |
| `geo_level` | VARCHAR | Published geography level such as `us`, `region`, `state` |
| `geo_id` | VARCHAR | Geography key |
| `series_code` | VARCHAR | BFS series code such as `BA`, `HBA`, `WBA`, `CBA`, `BF4Q`, `BF8Q`, `PBF4Q`, `PBF8Q` |
| `adjustment` | VARCHAR | Seasonal-adjustment flag if present |
| `value` | DOUBLE | Published BFS value |
| `source_file` | VARCHAR | Raw monthly BFS file identifier |

## 5. Staging To Silver

Preferred first-pass Silver output:
- `silver.bfs`
- one normalized long table that can hold both monthly and annual BFS rows
- county annual rows pass through directly from the annual county workbook
- `cbsa` and `state` annual rows are derived from counties
- monthly rows are retained where Census publishes them natively, but they are not forced onto county / CBSA if the source does not support that geography

Handoff pattern:
1. Read `staging.bfs_county`.
2. Standardize county keys and years.
3. Roll county annual rows to `cbsa` using `silver.xwalk_cbsa_county`.
4. Roll county annual rows to `state` using `silver.xwalk_county_state`.
5. Read `staging.bfs_monthly` when the monthly feed is implemented and append those rows into the same normalized Silver contract.
6. Compute annual rate metrics from annual county-derived rows only.

Recommended Silver fields:
- `geo_level`
- `geo_id`
- `period_type` such as `annual` or `monthly`
- `period`
- `year`
- `series_code`
- `series_label`
- `value`
- optional annual-only derived fields for county / CBSA / state BA rows:
  - `business_applications`
  - `business_applications_yoy_pct`
  - `business_application_rate_per_1000_establishments`

Recommended denominator for the annual rate:
- use CBP all-sector establishments (`naics = '------'`) as the denominator
- publish the rate as `business_application_rate_per_1000_establishments`

This is the clearest business-base intensity metric and pairs naturally with the CBP track.

## 6. Transformation Notes

### Simple architecture recommendation

The simplest correct architecture is:

1. One raw workbook download.
2. One county-year long staging table.
3. One normalized Silver table that can hold county annual rows plus richer monthly BFS series.
4. One annual-only Gold enrichment that treats BFS as a business-applications signal.

That is enough to support platform metrics like local entrepreneurial activity while still leaving room for richer monthly BFS analysis in Silver.

### Important source limitation

The current county annual workbook does **not** provide:
- high-propensity applications (`HBA`)
- planned-wage applications (`WBA`)
- corporate applications (`CBA`)
- business formations within 4 or 8 quarters (`BF4Q`, `BF8Q`)
- NAICS-sector county detail

Those series live in other BFS product families, primarily monthly national / state / regional files.

### Gold promotion rule

Gold should stay annual-only for BFS.

That means:
- promote annual county rows directly
- promote annual county-derived CBSA and state rows
- do not push monthly BFS rows into Gold
- if a monthly series is ever summarized into Gold, it should first be annualized explicitly

### Interpretation note

BFS business applications are not the same thing as new employer establishments. They are leading indicators based on EIN applications. That makes BFS conceptually complementary to CBP and QCEW rather than a substitute for them.

## 7. Data Quality Expectations

| Check | What to verify |
| --- | --- |
| County key completeness | `county_fips` stays zero-padded text |
| Row uniqueness | uniqueness at `county_fips + year + series_code` |
| Year coverage | all years `2005-2024` are present after pivot |
| Workbook header stability | title rows are skipped correctly and the data starts on the expected header row |
| County-equivalent handling | Louisiana parishes, Alaska county-equivalents, Virginia independent cities, and Connecticut planning regions are preserved exactly as published |
| Rollup stability | county-derived state totals reconcile to simple state sums |

## 8. Operational Notes

- The annual county workbook is small, about `496 KB`, so this is one of the lightest ingestion tracks in the plan.
- Census explicitly notes county-equivalent behavior and geographic-boundary reference dates in the county data dictionary; that should be preserved in staging notes rather than normalized away silently.
- Because the workbook is annual and already wide by year, the ETL should pivot to long immediately instead of materializing one column per year in DuckDB.
- Monthly BFS belongs in a sibling staging family and shared Silver contract, not in the county annual workbook contract.
- The preferred annual intensity denominator is CBP all-sector establishments, which means annual BFS Gold should depend on the stabilized CBP path.

## 9. Known Gaps

- County / CBSA monthly BFS is not source-native in the verified annual county file; if we want monthly Silver at those geographies, we will need to decide whether that should remain state-and-above only or whether we should avoid presenting implied county monthly coverage entirely.
- Track 12.3 still needs to be rewritten from "county/state CSV" into the agreed two-surface BFS ingest path.
- `business_application_rate_per_1000_establishments` is the preferred Gold metric name, but we still need to confirm the exact CBP join year logic when a source updates on a different annual schedule.

## 10. Source References

- https://www.census.gov/econ/bfs/about_the_data.html
- https://www.census.gov/econ/bfs/data.html
- https://www.census.gov/econ/bfs/data/county.html
- https://www.census.gov/econ/bfs/xlsx/bfs_county_apps_annual.xlsx
- https://www.census.gov/econ/bfs/pdf/bfs_county_data_dictionary.pdf
