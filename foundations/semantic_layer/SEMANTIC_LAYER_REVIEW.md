# Semantic Layer Review

**Status:** Active
**Updated:** 2026-10-17

A review of `foundations/semantic_layer/` against how other semantic layers are built: dbt (MetricFlow), Cube, Looker (LookML), Snowflake semantic views, Databricks Genie and the Open Semantic Interchange (OSI) spec. It covers what we do well, where we fall short, what to change, and what not to copy.

This is a point-in-time review: the counts below were measured on 2026-10-14 and won't be updated. Track the recommended work in [foundations/ROADMAP.md](../ROADMAP.md), not here.

---

## 1. Overall read

The layer follows the core industry pattern. It is a set of YAML files under version control that act as the contract between the warehouse and every product, with tables, metrics, joins and geography described separately. Its rules for grain and joins are stricter than most setups, and its metadata (caveats, polarity, display names) suits an LLM consumer well.

The main gap is **enforcement**. dbt and Cube check their definitions on every build and generate SQL from them. Ours are mostly documentation that nothing checks. As a result:

- the catalogs have drifted from the warehouse and from each other;
- information the catalogs lack has been hard-coded into the chatbot parser instead.

The fix is not to adopt another tool. It is to add a small validator, give metrics more structure, and reorganise the files around tables.

---

## 2. How our files map to standard concepts

| Our file | Industry equivalent | Fit |
|---|---|---|
| `table_catalog.yml` | dbt semantic model / Cube cube / LookML view | Good: grain, primary key and time field are declared |
| `metric_catalog.yml` | dbt metrics / Cube measures | Partial: each metric points at a column but has no type, aggregation rule or structured formula |
| `join_catalog.yml` + `geography_catalog.yml` | Entities, relationships, a shared dimension hierarchy | Strong |
| `question_catalog.yml` | dbt saved queries / Snowflake Cortex Analyst "verified queries" / Databricks Genie example SQL | Good, and ahead of most setups |
| `query_templates.yml`, `chart_rules.yml` | App or BI configuration, usually not part of the semantic layer itself | Fine to keep here, but it is app config |
| `intelligence_catalog.yml` | Model metadata, closer to an ML model registry | Unusual but sensible |
| `theme_catalog.yml` | Folders / groups / topics | Fine, but it repeats the intelligence topic hierarchy |
| `points_catalog.yml` | — | A placeholder; nothing to compare yet |

### How other tools split their files

Splitting a semantic layer across files is standard. The usual split is **one file per table**, holding everything about that table, not one file per kind of definition as we do now:

- **dbt:** each model's YAML holds its semantic model (entities, dimensions, measures) and usually the metrics built on it.
- **Cube:** one file per cube, with its measures, dimensions and joins together.
- **LookML:** one view file per table, plus explore files that define the joins.

What stays in separate files in those tools is what spans tables: joins, shared dimension hierarchies (our geography) and saved or verified questions.

---

## 3. What we do better than most

- **Grain and join safety.** `no_implicit_rollups`, `zcta_weighted_rollups_disallowed` and `benchmark_rows_are_not_fact_rows` guard against fan-out and unsafe geographic rollups, a failure many dbt projects only find in production.
- **Geography as a first-class dimension.** Hierarchy ranks, boundary vintages and approved rollup paths go further than most semantic layers go even for time.
- **Metadata an LLM can use.** Caveats, polarity, display names and unit formats are the descriptions that dbt and Snowflake now recommend for AI consumers.
- **Questions as verified examples.** Pairing natural-language questions with structured query plans is the pattern Snowflake and Databricks built into their text-to-SQL products.

---

## 4. Gaps, in priority order

### Gap 1: Nothing validates the catalogs, and they have drifted

Measured on 2026-10-14:

- **59 of 243 metrics** point at five tables that `table_catalog.yml` never declares: `health_wide` (36), `social_fabric_wide` (10), `housing_market_wide` (7), `transport_built_form_sld` (4) and `food_access_wide` (2). All five exist in `gold` in the warehouse. The catalog is behind, not the warehouse.
- **112 metrics in total** point at a column that `table_catalog.yml` doesn't list. This includes the 59 above, plus metrics on declared tables whose column lists are incomplete; `economics_industry_wide` alone is missing 21.
- **36 metric descriptions** differ from the description of the same column in `table_catalog.yml`.

`graph_builder.py` builds a graph from the YAML but checks nothing. dbt (`dbt parse`) and Cube both fail the build when a reference doesn't resolve.

### Gap 2: Columns are described in two places

`table_catalog.yml` and `metric_catalog.yml` both describe the same columns, which is where the 36 mismatches come from. In dbt a measure is declared once and metrics reference it.

### Gap 3: Metrics have no type, so the missing information ends up in code

MetricFlow types every metric as `simple`, `ratio`, `derived`, `cumulative` or `conversion`, each with structured inputs. Ours have no type:

- 34 metrics carry a `formula` that is free text the system can't run, e.g. `'1 - sum(share_i^2)'` or `'annualized_median_rent / per_capita_income_proxy'`.
- Nothing links a growth metric (e.g. `pop_growth_5yr`) to its base metric (`pop_total`) or window (5 years).

Because the catalog lacks these links, `publisher/chatbot/intent/parser.py` (`_normalize_provider_plan` and `_precomputed_growth_override`) hard-codes three things:

- the base metric for each growth metric;
- table names such as `economics_income_wide` and `population_demographics`;
- a default year of 2024.

That contradicts the README's statement that nothing downstream hard-codes table or metric definitions.

### Gap 4: No rules for how metrics aggregate

Every major semantic layer declares how a measure aggregates: `sum`, `average`, `count_distinct`, or not at all (non-additive). Our gold tables are already aggregated to geography × year, so this matters less for queries at the stored grain. It matters a lot for:

- **rollups:** `pop_total` can be summed from counties to a CBSA; `median_age` and `pct_ba_plus` cannot;
- **the LLM parser:** it needs to know whether a value may be summed or averaged.

Today the only protection is a blanket ban (`no_implicit_rollups`).

### Gap 5: Metrics carry no time or vintage information

Geographies record their boundary vintages; metrics don't record:

- which years are available, or the latest year;
- the source period (ACS 1-year vs 5-year, where "year" means the end of a 5-year window).

That is why the parser falls back to a hard-coded 2024.

The intelligence marts (`mart_intelligence.intelligence_*`) have no year column and no `as_of` or model-version field either. When a frame is recalibrated, the old scores are replaced with no record of which version a product was showing.

### Gap 6: The LLM consumer is under-served

The chatbot parser is the main consumer, but no catalog has a `synonyms` field. Snowflake semantic views, LookML and Genie all treat synonyms as basic. "Rent burden", "cost-burdened renters" and "housing cost stress" should all resolve to the same metric without the LLM guessing.

### Gap 7: The topic hierarchy is maintained in two places

The topics in `theme_catalog.yml` largely mirror the frame topics in `intelligence_catalog.yml`. The README's maintenance steps ("update topic membership to match calibrated structure") keep them in sync by hand, and they have drifted:

| | Theme topics | Frame topics | Shared IDs | Topics only in one file | Theme-only metrics within shared topics |
|---|---|---|---|---|---|
| Character | 11 | 11 | 10 | `population_size_and_growth` (theme), `household_structure` (frame) | 4 |
| Livability | 16 | 18 | 16 | `built_form_proxy`, `housing_slack` (frame) | 10 |
| Opportunity | 18 | 18 | 17 | `social_capital_signal` (theme), `intergenerational_mobility_proxy` (frame) | 18 |

Some of the difference is intended: the theme catalog keeps metrics the models dropped because they are still worth querying. Some of it is drift.

### Gap 8: Lower priority

- `status` is `active` on all 243 metrics, so it doesn't currently distinguish anything. Certification levels or a deprecation path would matter once metrics start being retired.
- Owner and access-control fields, which dbt and Looker have, don't matter with one maintainer.
- **Portability:** the OSI spec now has a first published version, backed by Snowflake, dbt Labs and others. It models datasets, metrics, dimensions and relationships much as we already do, so writing an exporter later would be cheap. That isn't a reason to restructure now.

---

## 5. Recommendations

### R1: Write a validator (fixes gap 1)

A Python script of roughly 150 lines, run as a pre-commit hook and from `visualize`:

1. **Structure:** Pydantic schemas for each catalog's entries, so a missing or misspelled field fails loudly.
2. **References between catalogs:** every `metric_id`, `source_table`, `template_id`, `default_chart`, topic and geography level a file mentions must exist in the file that defines it.
3. **Against the warehouse:** every `source_table` and `source_column` must exist in DuckDB (`information_schema`). This step is skipped with a warning when the database isn't built locally.
4. **Topic drift (after R4):** theme topics must resolve to intelligence topics.

Fix what it flags, starting with the five undeclared tables.

### R2: Give metrics a type and structured inputs (fixes gap 3)

Add `metric_type` and replace free-text formulas with references to other metrics:

```yaml
- metric_id: pop_growth_5yr
  metric_type: growth
  base_metric: pop_total
  window_years: 5

- metric_id: rent_to_income
  metric_type: ratio
  numerator: annualized_median_rent
  denominator: per_capita_income_proxy

- metric_id: diversity_index
  metric_type: derived
  formula_note: 1 - sum(share_i^2) over race/ethnicity shares   # for documentation only; computed in ETL
```

Then delete the hard-coded growth mappings and table names from `parser.py` and read them from the catalog.

### R3: Add aggregation and time fields (fixes gaps 4 and 5)

```yaml
- metric_id: pop_total
  additivity: additive                 # additive | non_additive | weighted
  available_years: [2012, 2024]        # first and last year
  source_period: acs_5yr
```

- `weighted` takes a weight metric, e.g. `weighted_by: pop_total` for a share.
- With additivity declared, `no_implicit_rollups` can be relaxed to "additive metrics may roll up along approved geography paths".
- The parser's default year comes from `available_years` instead of the literal 2024.
- Each frame in `intelligence_catalog.yml` gets `model_version` and `as_of`, and the marts carry them as columns.

### R4: Make theme topics reference intelligence topics (fixes gap 7)

Don't merge the two files: they do different jobs.

- **`intelligence_catalog.yml`** is a scoring-model spec. It is CBSA-only, carries weights, polarity and model roles, and changes on every recalibration.
- **`theme_catalog.yml`** is navigation. It spans every geography level and deliberately keeps metrics the models dropped.

Merging would tie the navigation to each recalibration and put model fields on topics that aren't part of any model. Instead, let intelligence own the topic hierarchy and have theme topics point at it:

```yaml
- topic_id: housing_burden
  intelligence_topic: livability.affordability.housing_burden   # metrics inherited from the frame
  additional_metrics: [median_gross_rent]                       # navigation-only extras
```

Topics with no frame equivalent (e.g. `population_size_and_growth`) keep a plain `metrics` list. The validator checks that every `intelligence_topic` resolves.

### R5: Reorganise into one file per table (fixes gap 2)

Merge `table_catalog.yml` and `metric_catalog.yml` the way dbt and Cube do, one file per table:

```
semantic_layer/
  semantic_models/
    housing_core_wide.yml        # grain, keys, geo fields, then this table's metrics
    population_demographics.yml
    ...
  metrics/
    derived.yml                  # metrics built from more than one table
  join_catalog.yml               # stays separate: spans tables
  geography_catalog.yml          # stays separate: shared dimension
  intelligence_catalog.yml
  theme_catalog.yml
  question_catalog.yml
  query_templates.yml
  chart_rules.yml
```

- Each column is described once, on its metric. A column that isn't a metric (a key or name field) gets name and type only.
- A single file would be about 5,000 lines, so one file per table is easier to work in.
- **Readers will break.** By a search on 2026-10-14, about a dozen files read these catalogs directly, including:
  - `publisher/chatbot/query/catalogs.py` and `publisher/chatbot/intent/parser.py`
  - `area-explorer/shared/catalog.py` and `area-explorer/app/explorer_utils.py`
  - the phase 2–4 `*_catalog_audit.R` and phase 6 scripts in `exploration/intelligence_framework/`
  - `foundations/visual_library/chart_engine_py/`

  Have `graph_builder.load_catalogs()` combine the per-table files back into the current `tables` / `metrics` shape, so readers can move over one at a time. Re-run the validator after each step.

### R6: Add synonyms (fixes gap 6)

Add a `synonyms` list to metrics and geography levels, and include it in what the parser sends the LLM. This is cheap and should make question resolution more reliable.

### Suggested order

1. **R1:** the validator, then fix what it flags.
2. **R2 and R3:** metric types, aggregation and time fields; remove the hard-coded parser logic.
3. **R6:** synonyms (independent; can happen any time).
4. **R5:** reorganise into one file per table, behind the combining loader.
5. **R4:** theme topics reference intelligence topics.

R1 comes first because every later step changes the catalogs, and the validator is what catches the breakage.

---

## 6. What not to copy

### Don't adopt dbt or MetricFlow to get validation

This was considered and rejected:

- **dbt has to own the tables.** A dbt semantic model points at a dbt model through `ref()`. Our gold tables are built by R and Python loaders, so we'd need a dbt-duckdb project of pass-through models (`select * from gold.x`) just to have something to reference.
- **It would validate only what MetricFlow understands.** The catalogs would be rewritten in MetricFlow's format. Polarity, caveats, geography rules, the frame models and the question catalog would go into free-form `meta` fields, which it doesn't check.
- **Its query engine doesn't fit our data.** MetricFlow aggregates event-level data when a query runs; our marts are already at geography × year grain.
- **Our readers wouldn't change.** The parser, Area Explorer and the R scripts read our YAML, not MetricFlow output.

**Revisit if** the ETL itself moves into dbt. At that point the dbt semantic layer comes almost for free.

### Don't copy the full MetricFlow structure

Measures, entities and time spines are designed for event tables. Take the discipline instead: typed metrics, declared aggregation, validation on every build, and one definition per concept.

---

## Sources

- [About MetricFlow (dbt docs)](https://docs.getdbt.com/docs/build/about-metricflow.md)
- [Metric properties (dbt docs)](https://docs.getdbt.com/reference/metric-properties.md)
- [OSI specs finalized (Snowflake)](https://www.snowflake.com/en/blog/open-semantic-interchanges-specs-finalized/)
- [The OSI spec updates (dbt Labs)](https://www.getdbt.com/blog/the-osi-spec-updates)
- [OSI April 2026 community update](https://ossie.apache.org/updates/osi-april-2026-community-update/)
