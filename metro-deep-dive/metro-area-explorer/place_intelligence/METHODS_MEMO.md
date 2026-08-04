# Place Intelligence Methods Memo

Date: Saturday, August 1, 2026

Purpose: this memo is the Phase 1 stop-gate handoff for Place Intelligence. It is written for clarity first. The goal is that you can read this, understand what we actually built in D1-D3, understand what we chose not to build, and hand any open questions to a new agent without needing to reverse-engineer the code from scratch.

## What Shipped In Phase 1

Phase 1 produced four main method blocks:

1. Geocode the site and resolve it to a tract.
2. Build straight-line catchment rings and apportion tract data into those rings.
3. Build D2 catchment metrics and benchmark rows from governed Gold tables.
4. Build D3 daytime/population/POI/barrier context, including both:
   - baseline straight-line rings
   - water-adjusted companion rings for river-severed cases

The most important files are:

- `metro-deep-dive/metro-area-explorer/place_intelligence/geocode.py`
- `metro-deep-dive/metro-area-explorer/place_intelligence/apportion.py`
- `metro-deep-dive/metro-area-explorer/place_intelligence/site_prep.py`
- `metro-deep-dive/metro-area-explorer/place_intelligence/ingest_jax_overture.py`
- `metro-deep-dive/metro-area-explorer/place_intelligence/ingest_jax_osmextract.R`
- `metro-deep-dive/metro-area-explorer/place_intelligence/promote_jax_osmextract.py`
- `metro-deep-dive/metro-area-explorer/place_intelligence/decisions.md`

## 1. Apportionment: Areal vs. Dasymetric

### Short version

- Areal apportionment says: if 20% of a tract's area falls inside a ring, assign 20% of that tract's count to the ring.
- Dasymetric apportionment says: do not assume people are spread evenly across all land in the tract. Use another spatial layer, like buildings or land use, to estimate where population is more likely to be.

### Which one did we actually ship?

We shipped **areal apportionment** in v0.

We did **not** ship dasymetric apportionment.

That distinction matters. Dasymetric mapping is the more attractive long-term method for small catchments because it is usually better at avoiding obviously uninhabited land. But we explicitly timeboxed that spike in the build plan, and we cut it for v0 because our existing Overture pipeline was built around `theme=places`, not building footprints. In other words: dasymetric was methodologically attractive, but not cheap enough to add cleanly within the Phase 1 box.

### Why dasymetric still matters

For one-mile rings, the main failure mode of areal interpolation is that tracts are treated as internally uniform. That is rarely true. Population is concentrated in residential parcels, buildings, and developable land, not in waterways, highways, or industrial yards. Dasymetric weighting tries to correct that.

The clean mental model is:

- Areal: "population density is uniform inside each source polygon"
- Dasymetric: "population density varies, and we can approximate that variation using an ancillary layer"

### Why we did not choose dasymetric in this build

We did not reject dasymetric on principle. We rejected it for scope and plumbing reasons:

1. The current Overture ingest path was already working for `places`.
2. Building footprints were not a one-line parameter flip in the current pipeline.
3. The build plan explicitly allowed cutting the dasymetric spike if it was not cheap.
4. We wanted a transparent v0 method that was easy to test and explain.

### The actual method we used

The actual D1 method is:

1. Build non-overlapping projected ring bands around the site.
2. Pull tract geometry for the market from DuckDB.
3. Intersect each ring band with each tract that touches it.
4. Compute `weight = intersect_area / tract_area`.
5. Use those weights to aggregate tract metrics into ring metrics.

This is the core code in `apportion.py`:

```python
def build_rings(lat: float, lon: float, rings_mi: list[int]) -> gpd.GeoDataFrame:
    sorted_rings = _validate_rings(rings_mi)
    site = gpd.GeoDataFrame(
        [{"lat": float(lat), "lon": float(lon)}],
        geometry=[Point(float(lon), float(lat))],
        crs=WGS84_CRS,
    )
    projected_crs = site.estimate_utm_crs()
    site_projected = site.to_crs(projected_crs)
    point = site_projected.geometry.iloc[0]

    rows: list[dict] = []
    previous_buffer = None
    for ring_mi in sorted_rings:
        outer_buffer = point.buffer(ring_mi * METERS_PER_MILE)
        ring_geometry = outer_buffer if previous_buffer is None else outer_buffer.difference(previous_buffer)
        rows.append({"ring_mi": ring_mi, "geometry": ring_geometry})
        previous_buffer = outer_buffer

    return gpd.GeoDataFrame(rows, geometry="geometry", crs=projected_crs)
```

How that works:

- We start in WGS84 because the site coordinates are lat/lon.
- We immediately project into a local UTM CRS because buffering in degrees would be wrong.
- We create 1, 3, and 5 mile buffers.
- We convert those into **bands**, not nested circles, because D1 weights need to sum sensibly across rings.

This is the weighting step:

```python
def apportion_weights(rings: gpd.GeoDataFrame, market_id: str) -> pd.DataFrame:
    market_tracts = _load_market_tracts(str(market_id))
    tracts_projected = market_tracts.to_crs(rings.crs)

    rows: list[dict] = []
    for ring in rings.sort_values("ring_mi").itertuples(index=False):
        ring_geom = ring.geometry
        intersecting = tracts_projected.loc[tracts_projected.geometry.intersects(ring_geom)].copy()
        intersecting["intersect_geometry"] = intersecting.geometry.intersection(ring_geom)
        intersecting["intersect_area"] = intersecting["intersect_geometry"].area
        intersecting["tract_area"] = intersecting.geometry.area
        intersecting["weight"] = intersecting["intersect_area"] / intersecting["tract_area"]
```

How that works:

- `intersects` is the selection rule. We do not require the tract centroid to fall inside the ring.
- We compute the actual geometry overlap.
- We compute the share of the tract that lies in the ring.
- That share becomes the weight.

This is the aggregation step:

```python
def apportion(metric_series: pd.Series, weight_table: pd.DataFrame, kind: Literal["extensive", "intensive"], method: str | None = None) -> pd.Series:
    values = metric_series.rename("metric_value").rename_axis("tract_geoid").reset_index()
    merged = weight_table.merge(values, on="tract_geoid", how="inner")

    if kind == "extensive":
        result = merged.assign(weighted_value=merged["metric_value"] * merged["weight"]).groupby(
            ["ring_mi"], sort=True
        )["weighted_value"].sum()
        return result.astype(float)

    numerator = merged.assign(weighted_value=merged["metric_value"] * merged["weight"]).groupby(
        ["ring_mi"], sort=True
    )["weighted_value"].sum()
    denominator = merged.groupby(["ring_mi"], sort=True)["weight"].sum()
    return (numerator / denominator).astype(float)
```

How that works:

- For **extensive** metrics like population and jobs, we weight and sum.
- For **intensive** metrics like rates, we compute a weighted mean.
- For median-like metrics, the code refuses to proceed unless the caller explicitly allows approximation.

### A note on medians

Medians are awkward under areal apportionment. A weighted average of tract medians is not a true median of the ring population. We put in a code guard so the method cannot silently pretend otherwise.

That guard is here:

```python
if kind == "intensive" and _is_median_metric(metric_name) and method != "approximate":
    raise ValueError(
        f"Metric '{metric_name or '<unnamed>'}' looks median-like and requires method='approximate'."
    )
```

### What to read next on apportionment

Recommended references:

- Goodchild, M. F., & Lam, N. S.-N. (1980). *Areal interpolation: a variant of the traditional spatial problem.*  
  https://asu.elsevierpure.com/en/publications/areal-interpolation-a-variant-of-the-traditional-spatial-problem/

- Mennis, J. (2009). *Dasymetric Mapping for Estimating Population in Small Areas.*  
  https://doi.org/10.1111/j.1749-8198.2009.00220.x

- Mennis, J., & Hultgren, T. (2006). *Intelligent Dasymetric Mapping and Its Application to Areal Interpolation.*  
  https://doi.org/10.1559/152304006779077309

- Comber, A., Zeng, W., Brunsdon, C., et al. (2019). *Spatial interpolation using areal features: A review of methods and opportunities using new forms of data with coded illustrations.*  
  https://doi.org/10.1111/gec3.12465

- U.S. Census Bureau working paper on interpolation caution: *Improving Estimates of Neighborhood Change with Constant Tract Boundaries.*  
  https://www.census.gov/library/working-papers/2022/adrm/CES-WP-22-16.html

## 2. D2 Catchment Metrics and Benchmarks

D2 is less conceptually novel, but it matters because it formalized how the rings talk to the Gold layer.

The pattern is:

1. Query governed tract metrics from Gold.
2. Use the D1 weight table to aggregate them into ring values.
3. Pull benchmark rows from the same query path, not from a separate lookup table.
4. Compute CBSA tract percentiles for the primary ring.

This is important because it means D2 is traceable. The ring value and the benchmark rows come from the same warehouse path, so we are not comparing unlike things by accident.

One unresolved item remains conceptually important: the median-handling decision deserves a fuller writeup if we revisit D2. The guard exists, but a fully satisfying median strategy was not the star of this build.

## 3. POIs: Ingestion and Classification

### What sources we used

We used two spatial sources in D3:

- **Overture Places** for POIs
- **OSM / osmextract** for infrastructure and waterways

The POI source was Overture. The infrastructure source was OSM.

That separation is deliberate:

- Overture is better for establishments and taxonomy-rich POIs.
- OSM is better for networks, roads, rail, and waterways.

### Overture ingestion

The Jacksonville Overture entrypoint is `ingest_jax_overture.py`.

Core code:

```python
overture_frame, overture_layers, overture_notes = fetch_overture_pois(
    market_id=MARKET_ID,
    bbox=bbox,
    extract_date=extract_date,
    overture_path=args.overture_path,
)

_write_parquet(overture_frame, OUTPUT_DIR / "overture_pois.parquet")
```

How that worked:

1. Derive the Jacksonville bbox from tract geometry if no manual bbox is passed.
2. Query the Overture `places` theme.
3. Write the result to `outputs/jacksonville_fl/overture_pois.parquet`.
4. Merge layer metadata into the shared spatial manifest.

Observed Jacksonville count during validation:

- `107,489` Overture POIs

That count is useful as a sanity check. It tells us the ingest was not silently empty.

### OSM infrastructure ingestion

The Jacksonville OSM ingest uses `osmextract` through `ingest_jax_osmextract.R`, then the cached GeoPackage is normalized with `promote_jax_osmextract.py`.

The R-side query logic was:

```r
line_query <- paste(
  "SELECT * FROM lines",
  "WHERE highway IN ('motorway','motorway_link','trunk','trunk_link',",
  "'primary','primary_link','secondary','secondary_link','tertiary','tertiary_link')",
  "OR railway IN ('rail','light_rail','subway')",
  "OR waterway IN ('river','canal')"
)
```

And the Python normalizer mapped raw OSM tags to our D3 groups here:

```python
def _classify_layer_group(row: pd.Series) -> str:
    if highway in {"motorway", "motorway_link", "trunk", "trunk_link"}:
        return "highways"
    if highway in {"primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link"}:
        return "major_roads"
    if railway in {"rail", "light_rail", "subway"}:
        return "rail"
    if waterway in {"river", "canal"} or natural == "water" or water in {"river", "canal", "reservoir", "lake"}:
        return "water"
```

Observed Jacksonville normalized counts during validation:

- `25,431` line features
- `36` point features
- `20,201` polygon features
- line breakdown: `15,926` major roads, `7,227` highways, `1,632` rail, `646` water
- polygon breakdown: `19,892` water polygons

### How POI classification worked

We did not reuse substring matching. We wrote a governed allowlist classifier in `site_prep.py`.

First, we defined the category sets:

```python
COMPETITIVE_CATEGORY_VALUES = {
    "department_store", "shopping_center", "retail", "retail_store",
    "mall", "clothing_store", "shoe_store", "discount_store",
    "home_improvement_store", "furniture_store", "electronics_store",
}

COMPLEMENTARY_CATEGORY_VALUES = {
    "grocery_store", "supermarket", "specialty_grocery_store",
    "international_grocery_store", "pharmacy", "drugstore", "gym",
    "fitness_center", "quick_service_restaurant", "fast_food_restaurant",
    "coffee_shop", "bank", "atm", "bank_or_credit_union",
}

ANCHOR_CATEGORY_VALUES = {
    "hospital", "medical_center", "outpatient_care_facility",
    "university", "college", "school", "civic", "government_office",
    "courthouse", "airport", "port", "warehouse", "logistics",
}
```

Then we established field priority:

```python
def _ordered_category_candidates(row: pd.Series) -> list[str]:
    raw_values: list[str] = []
    for key in ("basic_category", "taxonomy_primary"):
        raw_values.extend(_normalize_category_values(row.get(key)))

    hierarchy_value = row.get("taxonomy_hierarchy")
    if isinstance(hierarchy_value, list):
        for item in hierarchy_value:
            raw_values.extend(_normalize_category_values(item))
    else:
        raw_values.extend(_normalize_category_values(hierarchy_value))

    raw_values.extend(_normalize_category_values(row.get("primary_category")))
```

Then classification itself:

```python
def classify_poi(row: pd.Series) -> str | None:
    category_candidates = _ordered_category_candidates(row)
    if any(category in ANCHOR_CATEGORY_VALUES for category in category_candidates):
        return "anchor"
    if any(category in COMPLEMENTARY_CATEGORY_VALUES for category in category_candidates):
        return "complementary"
    if any(category in COMPETITIVE_CATEGORY_VALUES for category in category_candidates):
        return "competitive"
    return None
```

How to read this:

1. Normalize the candidate category strings to lowercase tokens.
2. Check Overture fields in a deliberate order:
   - `basic_category`
   - `taxonomy_primary`
   - `taxonomy_hierarchy`
   - `primary_category`
3. If any anchor token appears anywhere in that ordered candidate list, classify as `anchor`.
4. Otherwise check complementary.
5. Otherwise check competitive.
6. Otherwise return `None`.

This means the classifier is both:

- explicit
- auditable

That was the point. It is not trying to be clever NLP. It is trying to be governable.

### How POI counts were computed

We did not apportion POIs by tract. We counted them directly by point-in-ring.

```python
def count_pois_in_rings(site: Site, cumulative_rings: gpd.GeoDataFrame | None = None) -> pd.DataFrame:
    rings = cumulative_rings if cumulative_rings is not None else _build_cumulative_rings(lat, lon, site.rings_mi)
    pois = _load_overture_pois(site.market_id)
    pois["poi_class"] = pois.apply(classify_poi, axis=1)
    pois = pois.loc[pois["poi_class"].notna()].copy()
    pois = pois.to_crs(rings.crs)

    for ring in rings.itertuples(index=False):
        within_ring = pois.loc[pois.geometry.within(ring.geometry)].copy()
```

That is the correct choice for points. POIs are already point features, so tract interpolation would have been the wrong operation.

## 4. Density and Clustering: What We Did Not Yet Build

### Status

We did **not** ship a formal density or clustering model in Phase 1.

That means:

- no kernel density estimate
- no DBSCAN/HDBSCAN store-cluster detection
- no Ripley's K
- no nearest-neighbor concentration score
- no street-network retail fabric classifier

What we do have is:

- ring-level POI counts
- category splits
- road context
- barriers

That is useful context, but it is not a formal concentration method.

### Why this still matters

If you want Place Intelligence to say more than "there are 468 anchors/competitors/complementaries in 3 miles," then clustering is the next real method frontier.

The most useful question is not "are there many POIs?" but:

- are they dispersed
- are they corridor-shaped
- are they concentrated into nodes
- is the site itself inside the cluster or just near one

### Suggested literature review

I would frame the clustering literature in three buckets.

#### Bucket A: Retail agglomeration as a business/marketing concept

Use this if the question is: "Why do stores cluster, and when does clustering help?"

Recommended:

- Kuduvalli Manjunath et al. (2025). *Systematic literature review on retail agglomeration marketing.*  
  https://www.emerald.com/insight/content/doi/10.1108/MIP-11-2023-0593/full/html

- Teller & Schnedlitz (2011). *Drivers of Agglomeration Effects in Retailing – the Shopping Mall Tenant’s Perspective.*  
  https://doi.org/10.1080/0267257X.2011.617708

#### Bucket B: Point-pattern analysis as a spatial statistics method

Use this if the question is: "Are these points clustered relative to a null pattern, and at what distance scales?"

Recommended:

- Ripley's K overviews and extensions:
  - Wiegand & Moloney discussion of K/g-function concepts  
    https://doi.org/10.1111/j.1365-2745.2006.01113.x
  - Accessible explanation of K-function estimation  
    https://pmc.ncbi.nlm.nih.gov/articles/PMC5642986/

#### Bucket C: Retail-specific spatial morphology

Use this if the question is: "How do I go from points to retail districts, corridors, and fabrics?"

Recommended:

- *Retail Fabric Assessment: Describing retail patterns within urban space.*  
  https://www.sciencedirect.com/science/article/pii/S0264275118309387

### My recommendation for the next experiment

If we continue this work, I would not start with a fancy clustering algorithm. I would start with a staged approach:

1. Compute simple POI density per ring and per square mile.
2. Compute nearest-neighbor distance summaries by POI class.
3. Add a scale-sensitive clustering diagnostic such as Ripley's K or pair-correlation.
4. Only then consider a production cluster detector like DBSCAN/HDBSCAN.

Why:

- Density is easy to explain.
- Nearest-neighbor distance is easy to QA.
- Ripley's K tells you whether clustering exists and at what radius.
- DBSCAN is useful, but parameter-sensitive and easier to misuse if you have not already studied the scale structure.

### Questions for the next agent

- Do we want to measure clustering in Euclidean space or along the street network?
- Are we clustering all POIs, or just competitive retail?
- Is the question "how dense is this environment?" or "is there a coherent node here?"
- Should clustering be descriptive only, or should it feed the node typology?

## 5. Barriers, Waterways, and the Dual-Ring Decision

### What we learned

The biggest lesson from Jacksonville was:

**the water geometry existed, but the first interpretation was wrong.**

The St. Johns was not missing from the data. The problem was that raw OSM water polygons produced a noisy barrier surface full of small fragments. That made the barrier logic hard to trust.

We fixed that by:

1. treating named river line features as the primary water barrier objects
2. optionally attaching nearby water surface geometry
3. computing barrier summaries against those consolidated features

### The barrier thresholds we carried forward

Current constants in `site_prep.py`:

```python
D3_BARRIER_SPACING_THRESHOLD_MI = 1.0
D3_SITE_CARD_SEVERED_POP_SHARE_THRESHOLD = 0.2
```

Interpretation:

- Highway/rail are only suspicious as true barriers when crossing spacing is wider than about a mile.
- A severed population share has to get fairly large before it should be elevated to the site card.

### How barrier detection worked

The core D3 barrier function is:

```python
def compute_barrier_flags(site: Site, weight_table: pd.DataFrame, cumulative_rings: gpd.GeoDataFrame | None = None) -> pd.DataFrame:
    rings = cumulative_rings if cumulative_rings is not None else _build_cumulative_rings(lat, lon, site.rings_mi)
    lines = _load_osm_lines(site.market_id)
    polygons = _load_osm_polygons(site.market_id)
    ring_population = _compute_cumulative_weighted_population(site.market_id, weight_table, site.rings_mi)
    barriers = _prepare_barrier_features(lines, polygons, rings.crs)
    crossing_network = _prepare_crossing_network(lines, rings.crs)
```

Then for each ring and each barrier:

```python
crossing_count, spacing_mi = _compute_crossing_spacing(barrier_geom, barrier.barrier_type, crossing_network)
qualified = barrier.barrier_type == "water" or (
    spacing_mi is not None and spacing_mi > D3_BARRIER_SPACING_THRESHOLD_MI
)
severed_area_share, far_side_geom = _compute_severed_area_share(ring.geometry, barrier_geom, site_point)
severed_pop_share = _compute_severed_population_share(
    ring_mi=int(ring.ring_mi),
    far_side_geom=far_side_geom,
    ring_population=ring_population,
)
```

How to read this:

1. Build candidate barriers from OSM roads, rail, and water.
2. Count crossings where the road network intersects the barrier.
3. Compute the average spacing between crossings.
4. Water qualifies by default.
5. Highway and rail only qualify when spacing is wide enough to be meaningful.
6. Split the ring geometry against the barrier.
7. Compute how much area and weighted population are on the far side.

### Why the dual-ring approach was the right move

You suggested keeping both a no-barrier ring and a barrier-aware version. That was the right call.

We implemented that in `build_ring_variants()`:

```python
def build_ring_variants(site: Site, weight_table: pd.DataFrame, cumulative_rings: gpd.GeoDataFrame | None = None, barrier_summary: pd.DataFrame | None = None) -> dict[str, Any]:
    baseline_rings = cumulative_rings if cumulative_rings is not None else _build_cumulative_rings(lat, lon, site.rings_mi)
    ...
    adjusted_geom = ring.geometry
    for barrier_name in ring_barrier_rows["feature_name"].dropna().unique().tolist():
        ...
        _, far_side_geom = _compute_severed_area_share(ring.geometry, barrier_geom, site_point)
        adjusted_geom = adjusted_geom.difference(far_side_geom)
```

That means D3 now carries:

- baseline rings: the simple first-pass geometry
- water-adjusted rings: the same rings with severed far-side areas removed

### What we saw in Jacksonville

For `1 E Independent Dr, Jacksonville, FL 32202`:

- 3-mile baseline ring lost about `35.8%` of its area in the water-adjusted version
- 5-mile baseline ring lost about `41.5%`

For `3832 Baymeadows Road, Jacksonville, FL 32217`:

- almost no change until a negligible 5-mile adjustment

That is exactly the kind of contrast we wanted:

- downtown Jacksonville is a river-distorted catchment
- Baymeadows mostly is not

### Tradeoffs: using barriers vs. not using barriers

#### If we do not use barriers

Benefits:

- simple
- fast
- easy to explain
- easy to compare across sites

Costs:

- can badly overstate practical reach in river-constrained places
- especially misleading for Jacksonville

#### If we use barriers aggressively

Benefits:

- more spatially honest
- better for teaching why some rings are unrealistic

Costs:

- method becomes more complex
- more opportunities for geometry noise
- can look too "precise" given we are still not doing routed travel times

### My current view

The current dual-ring solution is a good v0 compromise:

- keep the baseline ring as the canonical simple catchment
- add the water-adjusted ring as the cautionary companion
- do not pretend this is a full network-access model

This is especially important because the copy note is true:

we are still doing straight-line geography, not route-based accessibility.

### Related reading on water and access

- *What prevents people accessing urban bluespaces? A qualitative study.*  
  https://doi.org/10.1016/j.ufug.2019.02.013

- Recent road-water accessibility example in commercial catchments:  
  https://www.sciencedirect.com/science/article/abs/pii/S2213624X26001641

I would not treat those as direct methodological blueprints for our code, but they are useful for thinking about how waterways can shape real accessibility beyond simple Euclidean distance.

## 6. Other Important Pieces

### Geocoding

We used the Census geocoder, recorded provenance, and preferred local tract point-in-polygon when there was disagreement.

Why that matters:

- geocoding is not just "get a lat/lon"
- the tract assignment is what anchors D1, D2, and D3

### Node typology

The D3 node typology is intentionally a simple v0 heuristic mirroring the Industry D4 pattern. It is a summarized interpretation layer, not a learned model.

That means:

- useful for quick reading
- not yet a deeply parameterized ontology

### What remains unresolved

The biggest open questions for a future agent are:

1. Should D1 move from areal to dasymetric weighting?
2. Should D3 add a formal density/clustering method?
3. Should D3 eventually replace water-adjusted Euclidean rings with true routed travel-time or network reach?
4. Should the node typology incorporate cluster structure instead of only ring counts and infrastructure signals?

## 7. Suggested Next Questions For A New Agent

If you open a fresh thread with a new agent, these are good prompts:

1. "Prototype dasymetric weighting for Place Intelligence using a buildings layer and compare it to the current areal results for the Jacksonville test sites."
2. "Design a retail density/clustering module for D3 and recommend whether to start with nearest-neighbor metrics, Ripley's K, or DBSCAN."
3. "Evaluate whether the current water-adjusted rings should remain a companion view or become the default view for river-adjacent Jacksonville sites."
4. "Propose a better median-handling strategy for D2 and test it on median income and median home value."
5. "Review the POI allowlists and propose any changes for grocery, healthcare, banking, or institutional anchors."

## 8. Bottom Line

The core Phase 1 methodological choices were:

- geocode the site and resolve it cleanly
- use projected straight-line ring bands
- ship **areal** apportionment, not dasymetric
- keep POI classification explicit and auditable
- use Overture for POIs and OSM for infrastructure
- treat waterways as important enough to justify a second, barrier-aware ring view
- stop short of claiming a full accessibility model or a formal clustering model

That is a coherent v0. It is not the final word. But it is teachable, testable, and honest about what it is.
