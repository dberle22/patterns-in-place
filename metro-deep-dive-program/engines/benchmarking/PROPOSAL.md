# Benchmarking Engine Proposal

**Drafted:** 2026-09-03
**Build sequence step:** `4`
**Primary build location:** `metro-deep-dive-program/engines/benchmarking/`

## 1. Why open this engine now

The first real trigger is narrow and concrete:

- `Act 1` needs a fingerprint percentile table
- `Act 2` already names a shared benchmark comparison layer as reusable method
- the program doc already expects one benchmarking function whose signature can
  support `national`, `division`, `state`, and `peer_set` comparisons

So the right move is not a broad analytics framework. It is a small, reusable
comparison engine that starts with one query path and expands only when the
same contract is needed again.

## 2. Recommendation in one sentence

Build the Benchmarking engine as a query-first layer that takes a long KPI
surface plus a comparison-set definition and returns a benchmark table with
target value, comparator summary, rank, percentile, and comparison deltas.

## 2.1 DuckDB recommendation

Yes: this should be a new DuckDB schema that downstream notebooks can call
directly.

Recommended schema name:

- `mart_benchmarking`

Why this is the right shape:

- benchmarking is a reusable serving layer, not just notebook glue
- the same comparison outputs should feed Position, Explanation, and Thematic
  analyses
- materializing the comparison sets once keeps region/division/state logic out
  of downstream notebooks
- later peer-set support can slot into the same schema without changing the
  consumer contract

## 3. Core design choice

Prefer **benchmark-ready query surfaces** over a Python-heavy helper library.

Why:

- most downstream consumers already read DuckDB tables or SQL query outputs
- comparison logic is easier to inspect when it stays close to the data
- the first consumers are notebook and issue-builder workflows, not a web app
- this keeps the engine aligned with the repo's marts-and-methods framing

Python can still help orchestrate query execution or light validation, but the
benchmark contract should be legible in SQL first.

## 4. Inputs the engine should treat as canonical

### Geography spine

Use `gold.dim_geo` as the canonical geography dimension for:

- `geo_level`
- `geo_id`
- readable names and labels
- `division`, `region`, `state`, and parent lookup
- metro-vs-micro filtering

This engine should not reinvent geography joins in each analysis.

### Peer spine

Use the Intelligence Framework peer outputs as the canonical peer source for
metro benchmarking:

- `cross_frame` peers as the default peer set
- frame-specific peers as optional alternate sets later

The Benchmarking engine should consume a peer-membership surface; it should not
own cosine-similarity generation itself.

### Metric spine

Consume long metric surfaces from upstream analyses or marts, with a minimal
shape like:

- `metric_id`
- `metric_label`
- `geo_level`
- `geo_id`
- `year`
- `value`
- `value_direction` where needed (`higher_is_better`, `lower_is_better`,
  `neutral`)
- `source_name`
- `vintage_note`

The metric surface can come from the Intelligence Framework, theme marts, or
question-specific prep. The Benchmarking engine should not own metric
calculation.

## 5. Recommended outputs

### Output A: comparison-set membership surface

One reusable table or query that answers:

- what is the comparison set?
- who belongs to it?
- why do they belong to it?

Suggested grain:

- `target_geo_level`
- `target_geo_id`
- `comparison_set_id`
- `comparison_set_type`
- `member_geo_level`
- `member_geo_id`
- `member_rank`
- `membership_source`

Recommended first comparison types:

- `national`
- `region`
- `division`
- `state`
- `peer_set`

Recommended later types:

- `nearby_metros`
- `same_cluster`
- `custom`

Recommended first materialized tables:

- `mart_benchmarking.benchmark_sets`
- `mart_benchmarking.benchmark_set_members`

### Output B: benchmark result surface

One standard benchmark result surface per target geography, metric, year, and
comparison set.

Suggested grain:

- `target_geo_level`
- `target_geo_id`
- `metric_id`
- `year`
- `comparison_set_id`

Suggested fields:

- target metadata: `target_geo_name`, `metric_label`
- denominator context: `comparison_n`
- target value: `target_value`
- comparator summaries: `comparison_mean`, `comparison_median`,
  `comparison_min`, `comparison_max`
- position metrics: `rank_asc`, `rank_desc`, `percentile_rank`
- gap metrics: `delta_from_mean`, `delta_from_median`,
  `pct_diff_from_mean`
- standardization metrics: `z_score` when denominator is large enough
- provenance: `comparison_set_type`, `membership_source`, `source_name`,
  `vintage_note`

This becomes the common output for profile tables, peer tables, Act 2 component
tables, and later Act 3 dynamic comparisons.

Current implementation choice:

- compute this surface on demand in one shared Python package
- do not materialize `benchmark_results` unless repeated downstream usage
  proves the size tradeoff is worth it

### Output C: metric catalog

One metadata table that describes how a metric should be interpreted in a
benchmarking context.

Recommended first materialized table:

- `mart_benchmarking.benchmark_metric_catalog`

Suggested fields:

- `metric_id`
- `metric_label`
- `metric_family`
- `metric_type`
- `unit`
- `value_direction`
- `preferred_summary_stat`
- `is_higher_better`
- `source_name`
- `default_year_behavior`
- `notes`

## 6. First implementation slice

The first slice should stay small.

### Scope now

- support `cbsa` target geographies only
- support `national` comparison first
- accept a long KPI surface produced from the Act 1 profile queries
- compute percentile rank and simple rank cleanly
- expose denominator explicitly

### Do not build yet

- tract, ZCTA, or place benchmarking
- distance-based nearby metros
- weighted peer averages
- composite scores inside the benchmarking engine
- automatic metric direction inversion

Those can come later if a named consumer actually needs them.

## 7. Query pattern to standardize

The engine should standardize a pattern like:

`target geography`
-> `metric surface`
-> `comparison set members`
-> `filtered comparison values`
-> `rank / percentile / summary stats`
-> `benchmark result rows`

In practice, the engine likely needs:

- a reusable SQL template for comparison-set membership
- a reusable SQL template for benchmark stats from a long metric table
- optional thin wrappers per consumer that map local field names into the
  benchmark contract

## 8. Comparison methods we should support

These methods solve different questions. We should not force one method to do
everything.

### Method 1: percentile rank

Best for:

- Act 1 fingerprint tables
- fast reader-facing interpretation
- cross-metric comparability

Strengths:

- easy to read
- stable across different units
- works well for scorecards

Caveats:

- hides distance between places
- can overstate tiny differences around the middle

### Method 2: delta from benchmark mean or median

Best for:

- Act 2 explanation tables
- “above or below peers/division” reads
- questions where magnitude matters more than ordinal position

Recommendation:

- use `median` for skewed metrics like prices, rents, and densities
- use `mean` where additive interpretation is more natural

### Method 3: z-score within comparison set

Best for:

- flagging stronger outliers
- screening candidate findings
- comparing how unusual a market is within peers or region

Caveats:

- less reader-friendly
- unstable on small peer sets
- sensitive to skew unless transformed upstream

### Method 4: rank plus gap pair

Best for:

- featured peer comparisons
- “where does this market sit, and by how much?”

This is often more informative than percentile alone.

### Method 5: trend-relative comparison

Later, for Act 3:

- benchmark current growth or change against peers/division/national
- compare level and change separately
- treat “high level, falling” and “mid level, rising” as distinct reads

This likely reuses the same benchmark result contract with `metric_id`
representing a change metric rather than a level metric.

## 9. Recommended benchmark hierarchy by act

### Act 1

Default comparison:

- `national`

Optional support:

- `peer_set` for featured peer tables

Reason:

- Act 1 is mainly identity and placement
- national percentiles are the cleanest baseline

### Act 2

Default comparisons:

- `national`
- `division`
- `peer_set`

Conditional comparison:

- `state` when the question is policy or institutional
- `nearby_metros` when the question is regional competition

Reason:

- Act 2 needs more than one baseline because “unusual nationally” and
  “unusual for its region” are different claims

### Act 3

Default comparisons:

- `division`
- `peer_set`

Reason:

- dynamics are more meaningful when we ask whether the market is converging
  with or diverging from relevant peers and region

### Act 4

Default comparisons:

- national tract or zone baseline once the geography stack exists
- within-market baseline for zone composition reads

Reason:

- internal structure requires different denominators than metro-level acts

## 10. How `dim_geo` should enter the build

`gold.dim_geo` should support:

- target-market metadata lookup
- division and state membership for comparison sets
- filtering to metro rows for CBSA benchmarking
- readable names in output tables

What it should not be asked to do yet:

- nearby-metro distance logic
- place and ZCTA hierarchy logic that the geography engine has not settled

Those should wait for the Geography engine to formalize them.

## 11. How the peer set should enter the build

The peer set should be materialized as a reusable comparison membership
surface, not embedded ad hoc inside each query.

Recommended first behavior:

- default peer source = cross-frame top peers from
  `mart_intelligence.intelligence_cross_frame`
- include target market as a separate target row, not as a peer member
- preserve `member_rank` so top-5 and top-10 views can be derived without new
  logic

Recommended later behavior:

- support `character`, `livability`, and `opportunity` frame peer sets
- support curated peer subsets chosen at the issue layer without breaking the
  base contract

## 12. Implementation shape inside `engines/benchmarking/`

Recommended initial contents:

- `README.md`
- `NOTES.md`
- `CONTRACT.md`
- `PROPOSAL.md`
- `queries/benchmark_sets.sql`
- `queries/benchmark_set_members_national.sql`
- `queries/benchmark_set_members_region.sql`
- `queries/benchmark_set_members_division.sql`
- `queries/benchmark_set_members_state.sql`
- `benchmark_engine.py` during engine development, then a shared package home
  under `foundations/`
- optional thin notebook or QA script once the first consumer is wired

The first implementation can begin with only one or two of those queries if
that is enough for the profile consumer.

## 13. Risks to design around now

### Small denominators

Peer sets of `5` or `10` are useful, but percentile and z-score behavior
should state the denominator clearly.

### Mixed vintages

The engine should carry source and vintage fields forward so we do not compare
different years invisibly.

### Metric direction

Some metrics are “lower is better,” but not all benchmarking is evaluative.
Direction should be metadata, not hidden inversion.

### Skewed distributions

Highly skewed metrics should prefer median and percentile surfaces over raw
mean comparisons unless the analysis explicitly wants means.

### Repeated bespoke SQL

If each analysis invents its own peer and region filters, the engine has
failed. The main goal is to stop that drift.

## 14. Proposed build order

1. Write the benchmark contract around one long metric surface and one
   comparison-set surface.
2. Build `national` CBSA comparison first for the Act 1 fingerprint consumer.
3. Add `division` CBSA comparison next, using `gold.dim_geo`.
4. Add `peer_set` comparison next, using Intelligence Framework peer outputs.
5. Only then decide whether a materialized benchmark-results mart is
   warranted, based on repeated reuse.

## 15. Bottom-line recommendation

We should build this engine around **standard benchmark result logic**, not
around bespoke notebook logic and not around one giant precomputed mart on day
one.

That gives us:

- a clean Act 1 percentile path now
- a reusable Act 2 comparison layer next
- a natural extension into Act 3 dynamic benchmarking later
- a clear boundary between geography membership, peer membership, metric
  calculation, and benchmark comparison

## 16. Concrete first-pass schema proposal

For the current implementation, I recommend four materialized tables plus one
shared package layer.

### Table 1: `mart_benchmarking.benchmark_metric_catalog`

Purpose:

- register the benchmarkable metrics and how they should be interpreted

Grain:

- `1 row per metric_id`

Key fields:

- `metric_id`
- `metric_label`
- `metric_family`
- `metric_type`
- `unit`
- `value_direction`
- `preferred_summary_stat`
- `source_schema`
- `source_table`
- `source_column`
- `notes`

Metric families we should expect:

- `population`
- `housing`
- `income_wages`
- `industry`
- `labor`
- `mobility`
- `health_environment`
- `framework_scores`
- `market_structure`

Metric types we should expect:

- `level`
- `share`
- `rate`
- `index`
- `change`
- `rank`
- `percentile`

### Table 2: `mart_benchmarking.benchmark_sets`

Purpose:

- define the reusable comparison sets that exist independently of any one
  metric

Grain:

- `1 row per comparison_set_id`

Key fields:

- `comparison_set_id`
- `comparison_set_type`
- `target_geo_level`
- `target_geo_id`
- `comparison_label`
- `comparison_description`
- `comparison_year_scope`
- `membership_source`

Expected first rows:

- one `national` set per target CBSA
- one `region` set per target CBSA
- one `division` set per target CBSA
- one `state` set per target CBSA when state membership is unambiguous

### Table 3: `mart_benchmarking.benchmark_set_members`

Purpose:

- materialize which geographies belong to each comparison set

Grain:

- `1 row per comparison_set_id + member_geo_level + member_geo_id`

Key fields:

- `comparison_set_id`
- `comparison_set_type`
- `target_geo_level`
- `target_geo_id`
- `member_geo_level`
- `member_geo_id`
- `member_geo_name`
- `member_rank`
- `member_role`
- `membership_source`

Expected first behavior:

- `national` includes all metro CBSA rows in the benchmark universe
- `region` includes all metro CBSA rows in the target's Census region
- `division` includes all metro CBSA rows in the target's Census division
- `state` includes all metro CBSA rows in the target's state when a single
  parent state exists

### Package layer: shared benchmarking API

Purpose:

- calculate benchmark summaries and member-level comparison rows on demand from
  the materialized metric and membership tables

Recommended first functions:

- `list_comparison_sets(...)`
- `get_target_metric_surface(...)`
- `benchmark_metric(...)`
- `benchmark_metric_bundle(...)`

### Query surfaces to expose

Recommended first query files:

- `queries/profile_fingerprint_benchmarks.sql`
- `queries/profile_peer_set_members.sql`
- package-level benchmark calls for summary and member outputs

These should read from `mart_benchmarking` and the shared package rather than
recomputing comparison logic inline.
