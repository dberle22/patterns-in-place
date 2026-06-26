# Source Spec: BLS OEWS

## 1. Overview

- Source: U.S. Bureau of Labor Statistics
- Program: Occupational Employment and Wage Statistics (OEWS)
- Access pattern in current first-pass scope: public BLS downloadable spreadsheets plus the stable `download.bls.gov/pub/time.series/oe/` text-family metadata; no API key required
- Current verified release surface as of `June 22, 2026`: `May 2025` metro, state, national, and all-data downloads are linked from the OEWS tables page
- Native geographies in the public cross-industry releases: national, state, metropolitan area, and nonmetropolitan area
- Scope in Foundations: state plus metro-first occupational employment and wage percentiles, with `state` and `cbsa` as the canonical first-pass managed geographies and nonmetro rows staged for later modeling if we decide to expose them
- Documentation goal: confirm the live OEWS download surface, current file shape, suppression behavior, and the narrowest viable first-pass staging strategy before writing ETL

OEWS fills the occupation-side labor-market gap that QCEW and LAUS do not address. QCEW gives industry employment and pay by employer industry. OEWS gives the occupational mix inside labor markets: how many nurses, software developers, or truck drivers a metro has, and what those occupations earn across the wage distribution.

This is a topic-level child spec for the BLS family. It intentionally reuses the provider-level BLS operating pattern already documented in [source__bls.md](./source__bls.md): cache public BLS download artifacts locally, keep staging source-faithful, and defer canonical geography harmonization and analytical rollups to Silver.

---

## 2. Coverage Matrix

| Topic group | Staging family contracts | Silver outputs | Gold outputs |
| --- | --- | --- | --- |
| BLS OEWS state, metro, and nonmetro occupational estimates | [../layers/staging/staging__bls_oews.md](../layers/staging/staging__bls_oews.md) | `silver.bls_oews` | `gold.economics_occupation_wide` |

---

## 3. Source Contract

- Provider: U.S. Bureau of Labor Statistics
- OEWS home: `https://www.bls.gov/oes/`
- OEWS tables page: `https://www.bls.gov/oes/tables.htm`
- Current metro HTML release page: `https://www.bls.gov/oes/2025/may/oessrcma.htm`
- Current state HTML release page: `https://www.bls.gov/oes/2025/may/oessrcst.htm`
- Current metro XLSX ZIP path linked from the tables page: `https://www.bls.gov/oes/special-requests/oesm25ma.zip`
- Current state XLSX ZIP path linked from the tables page: `https://www.bls.gov/oes/special-requests/oesm25st.zip`
- Current technical notes: `https://www.bls.gov/oes/current/oes_tec.htm`
- Current FAQ: `https://www.bls.gov/oes/oes_ques.htm`
- Additional OEWS datasets: `https://www.bls.gov/oes/additional.htm`
- Stable OEWS text-series root: `https://download.bls.gov/pub/time.series/oe/`
- Current general metadata file: `https://download.bls.gov/pub/time.series/oe/oe.txt`
- Current footnote mapping: `https://download.bls.gov/pub/time.series/oe/oe.footnote`
- Current SOC major groups: `https://www.bls.gov/soc/2018/major_groups.htm`
- Authentication: none

**What we verified**

- The live OEWS tables page was last modified on `May 15, 2026` and now exposes `May 2025` downloads for national, state, metro/nonmetro, and all-data files.
- The current metro HTML page is `May 2025 Metropolitan and Nonmetropolitan Area Occupational Employment and Wage Estimates`.
- The tables page links the metro XLSX download to `https://www.bls.gov/oes/special-requests/oesm25ma.zip`.
- BLS states in the FAQ that downloading Excel spreadsheets is the only comprehensive way to access all years and all OEWS variables.
- The stable `download.bls.gov/pub/time.series/oe/` family remains available and documents canonical `area_code`, `occupation_code`, datatype, and footnote mappings for OEWS.

**Important operational note**

The downloadable state and metro/nonmetro XLSX workbooks are the right first-pass ingest surface for Track `24.2`, not the HTML tables and not the OEWS query tool:

- HTML does not expose all OEWS variables, including percentile wages.
- The query tool only serves the most recent year and does not expose the full variable set.
- The downloadable spreadsheet paths are the comprehensive cross-industry releases that match the Track `24` scope.

---

## 4. Native File Shape

OEWS publishes both presentation-layer tables and structured download artifacts.

**Relevant public surfaces**

| Surface | What it is | Best use in Foundations |
| --- | --- | --- |
| Metro HTML page | linked area-by-area tables for one release year | human QA only |
| Metro XLSX ZIP | cross-industry metro/nonmetro all-data spreadsheet for one release year | canonical first-pass staging input |
| `download.bls.gov` text family | normalized OEWS series, code maps, and footnotes | metadata QA and code-reference support |

**Observed download structure**

- The current metro download is distributed as a ZIP at `oesm25ma.zip`.
- The tables page maintains a stable yearly pattern for metro/nonmetro XLSX downloads across recent vintages (`May 2019` through `May 2025` are all still linked).
- BLS also maintains a separate `All data` download and a stable text-series directory for OEWS metadata.

**Expected metro spreadsheet row shape**

The Track `24` first-pass staging contract should expect one row per `release_year + area_code + occ_code` cross-industry estimate, with the metro spreadsheet carrying at least the core columns already called out in the roadmap:

- `area_code`
- `area_title`
- `occ_code`
- `occ_title`
- `group`
- `tot_emp` or equivalent employment count field
- hourly percentile fields including:
  - `h_pct10`
  - `h_pct25`
  - `h_median`
  - `h_pct75`
  - `h_pct90`
- annual wage fields where published
- mean wage fields where published
- relative standard error / suppression / release-note fields where published

The exact spreadsheet headers should be preserved verbatim in staging once `24.2` lands the file, but for `24.1` the key confirmed point is the shape: area x occupation cross-industry rows with employment plus wage distribution measures.

**How the text-series family complements the spreadsheet**

The `oe.txt` metadata confirms the provider's canonical coding pieces:

- `area_code`: unique geography identifier
- `occupation_code`: unique occupation identifier
- `datatype_code`: identifies measure type
- `footnote_code`: identifies special release notes such as unreleased estimates

That text family is not a substitute for the metro spreadsheet when we need all percentile fields in one wide row, but it is useful for QA and for preserving the official footnote dictionary.

---

## 5. Historical Coverage

**Verified release history from current FAQ and tables page**

- OEWS annual estimates are available from `1997` to present.
- Metropolitan area cross-industry data are available:
  - `1997-2004` under older metro definitions
  - `2005-2014` under the 2000 census-based OMB definitions
  - `2015-2018` under the 2010 census-based OMB definitions
  - `2019-present` under the 2018 SOC transition and current recent release structure
- Nonmetropolitan area data are available from `2006` onward.

**Important comparability caveats from BLS**

BLS explicitly does not encourage OEWS as a clean time series because comparability is affected by:

- the three-year pooled sample design
- occupational classification changes
- industry classification changes
- geographic definition changes
- methodology changes, including the model-based estimation approach

For the first-pass Foundations ingest, that means a recent-history backfill such as `2019+` is more defensible than a full-history backfill.

**Most important current breakpoints**

- `May 2019` and `May 2020` are hybrid years spanning the `2010` and `2018` SOC systems.
- `May 2021` is the first release based entirely on the `2018` SOC.
- `May 2018` is the year OEWS stopped publishing metropolitan divisions and moved the large split metros to MSA-level-only output.

That makes `2021+` the cleanest first-pass comparability window, while `2019-2020` are still reasonable to stage if we want COVID-period context and explicitly document the hybrid SOC boundary.

---

## 6. Recommended First-Pass Scope

The narrowest high-value first pass is smaller than the full OEWS surface:

1. Use the annual metro/nonmetro XLSX download as the canonical ingest artifact.
2. Stage all published metro and nonmetro rows source-faithfully.
3. Model state and metropolitan rows into the first-pass Silver contract.
4. Normalize state `area` codes to canonical state FIPS and metro `area` codes to canonical `cbsa_code` in Silver.
5. Keep one row per `geo_id + year + soc_code`.
6. Carry employment and the wage distribution measures needed for archetype and opportunity analysis.
7. Stage nonmetro rows source-faithfully even if the first modeled Silver table stays focused on `state` and `cbsa`.
8. Backfill recent years only, with `2021+` as the cleanest minimum window and `2019+` acceptable if we want explicit pre/post-COVID context.

**Why state + metro first**

- The source does not publish county rows, so state is the next-best direct higher geography to preserve alongside metros.
- State rows are directly published and are cheap to stage and model.
- Metro rows align directly with the repo's canonical `cbsa` geography strategy.
- Cross-state MSAs are already handled by the published metro definitions, which is preferable to rebuilding occupation totals from counties with no county OEWS equivalent in scope here.

**Why keep nonmetro in staging**

- The source file publishes metro and nonmetro together.
- Staging should remain source-faithful.
- We may later decide to expose nonmetro analytical outputs without rewriting the ingest.

**Why `2021+` is the cleanest default**

- It avoids the hybrid `2010` / `2018` SOC years.
- It keeps all modeled rows inside the fully `2018 SOC` era.
- It still gives a usable recent panel for benchmarking and Gold rollups.

---

## 7. Recommended SOC Rollup Strategy

Track `24.1` also asked us to verify the occupation-group rollup path for archetype work.

**STEM**

- BLS already publishes official OEWS STEM auxiliary datasets on the `Additional OEWS data sets` page.
- Those files are the safest official reference for a managed `is_stem` flag or `stem_definition` helper table.
- Recommendation: reuse the published BLS STEM set rather than inventing a repo-only STEM classification from scratch.

**Management / service / production archetype buckets**

BLS does not publish one official archetype rollup for these broader framing buckets. The right first-pass approach is to define them in Foundations using the official `2018 SOC` major groups.

Recommended first-pass bucket logic:

| Foundations bucket | Recommended major-group basis | Notes |
| --- | --- | --- |
| `management_professional` | `11`, `13`, `15`, `17`, `19`, `23`, `27`, `29` | repo-defined analytical bucket combining management with high-skill professional groups |
| `service` | `21`, `31`, `33`, `35`, `37`, `39` | repo-defined service-facing bucket |
| `production_transportation` | `45`, `47`, `49`, `51`, `53` | repo-defined goods movement / physical production bucket |
| `other` | `25`, `41`, `43` plus residual nonbucketed codes | catch-all for education, sales, office support, and any rows we do not intentionally map elsewhere |

This grouping is a Foundations analytical convention, not an official BLS release taxonomy. The official input it relies on is the SOC major-group structure itself.

**Recommendation for implementation**

- Persist the raw `occ_code` and a derived `soc_major_group` in staging or Silver.
- Build a small maintained mapping table for the Foundations bucket assignment.
- Treat STEM as a separate overlay rather than forcing it into the mutually exclusive archetype buckets, because the BLS STEM set cuts across multiple major groups.

---

## 8. Suppression And Footnote Handling

OEWS unreleased estimates need explicit documentation because they affect both totals and interpretation.

**What BLS says**

- BLS may withhold an employment or wage estimate because of confidentiality or quality standards.
- If one estimate is available and the paired estimate is not, the occupation can still appear with the unavailable value footnoted `Estimate not released.`
- If neither employment nor wage can be published, the occupation may not appear at all.
- Major-group and all-occupation totals can therefore exceed the sum of separately published detailed occupations.

**Verified official footnote map**

The current `oe.footnote` file includes:

- `1`: detailed occupations do not sum to totals; self-employed excluded
- `2`: annual wages derived from hourly wages where applicable
- `3`: relative standard error note
- `4`: some occupations report only hourly or only annual wages depending on pay practice
- `5`: top-coded wage, equal to or greater than `$115.00` hourly or `$239,200` annually
- `8`: `Estimate not released.`

**Staging rule**

- Preserve every published footnote / note field exactly as delivered.
- Do not coerce unreleased values to zero.
- Do not force occupational sums to match major-group or all-occupation totals.

---

## 9. Staging To Silver

Recommended first-pass handoff:

1. Read the metro/nonmetro spreadsheet rows from `staging.bls_oews`.
2. Preserve the source occupation code and title.
3. Filter to state and metro rows for the initial managed Silver output.
4. Normalize state `area` codes to canonical state FIPS and metro `area` codes to canonical `cbsa_code`.
5. Keep wage percentile fields and employment as the core analytical payload.
6. Add a derived SOC major-group code from the first two digits of `occ_code`.
7. Add the Foundations archetype bucket mapping and the STEM overlay in Silver.
8. Compute location quotient in Silver or Gold against the national occupational distribution.

Preferred first-pass Silver columns:

- `geo_level`
- `geo_id`
- `geo_name`
- `year`
- `soc_code`
- `soc_title`
- `soc_major_group`
- `employment`
- `employment_rse_pct` if present
- `wage_hourly_p10`
- `wage_hourly_p25`
- `wage_hourly_median`
- `wage_hourly_p75`
- `wage_hourly_p90`
- annual analogs where present
- `is_stem`
- `occupation_bucket`
- `source_footnote_codes`

---

## 10. Data Quality Expectations

- Verify uniqueness at `release_year + area_code + occ_code` in staging.
- Verify that metro and nonmetro rows are distinguishable from the source geography fields before filtering to metro in Silver.
- Verify that major-group and all-occupation totals are not naively summed alongside detailed occupations; the FAQ explicitly warns this causes double counting.
- Watch for unreleased detailed occupations that appear as missing wage or employment fields but still belong inside major-group totals.
- Document wage top-coding and occupations that publish only hourly or only annual wages.
- Treat `2019-2020` as hybrid SOC years and flag them explicitly if included.

---

## 11. Operational Notes

- Staging entrypoint: `foundations/etl/staging/get_bls_oews.R`
- Staging contract: `foundations/data_dictionary/layers/staging/staging__bls_oews.md`
- Silver entrypoint: `foundations/etl/silver/bls_oews_silver.R`
- Gold destination: `gold.economics_occupation_wide`
- Reused BLS-family strategy:
  - cache public BLS artifacts locally
  - keep staging source-faithful
  - do canonical geography normalization and analytical bucketing in Silver

---

## 12. Known Gaps

- The exact metro spreadsheet header names still need to be preserved from the landed workbook during `24.2`; this spec confirms the shape and required field families, not the final staging column names.
- BLS's published STEM datasets solve the official STEM definition question, but we still need to decide whether Foundations wants one pinned BLS STEM definition or a small versioned helper table that can support multiple definitions later.
- The recommended management/service/production buckets are analytical repo conventions built from official SOC major groups, not official BLS aggregates.
- OEWS is not designed as a clean short-interval time series, so any later Gold product should emphasize structure and benchmarking more than year-over-year change claims.

## 13. Source References

Official BLS references used for this OEWS source spec:
- https://www.bls.gov/oes/tables.htm
- https://www.bls.gov/oes/2025/may/oessrcma.htm
- https://www.bls.gov/oes/current/oes_tec.htm
- https://www.bls.gov/oes/oes_ques.htm
- https://www.bls.gov/oes/additional.htm
- https://download.bls.gov/pub/time.series/oe/
- https://download.bls.gov/pub/time.series/oe/oe.txt
- https://download.bls.gov/pub/time.series/oe/oe.footnote
- https://www.bls.gov/soc/2018/major_groups.htm
