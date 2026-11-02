# POI Engine

The POI Engine prepares governed, analysis-ready **place points**. Its first
consumer is Richmond Q4 Daily-needs access; Corridor Intelligence and Internal
Structure are the next planned consumers. It does not define an amenity basket,
calculate access, model barriers, or identify structural candidates. Corridor
Intelligence may aggregate eligible governed categories as membership evidence
without changing POI's source classifications.

Start with:

- [Build plan](POI_ENGINE_BUILD_PLAN.md)
- [Contract](CONTRACT.md)
- [Audit notes](NOTES.md)
- [Richmond POI data shape](DATA_SHAPE.md)
- [Source inventory](sources/README.md)
- [Taxonomy workflow](taxonomy/README.md)
- [QA outputs](qa/README.md)

## Current state

Epics 1–5 are complete for Richmond and Jacksonville. The engine acquires a
source-faithful cache, normalizes source identity and provenance, applies the
first governed taxonomy mapping, and assigns retained points to governed tract,
county, and Census Place geometry with QA. Place results are direct analytical
point assignments; `no_census_place` and boundary ambiguity remain visible.
First-analysis adoption remains open.

All 27 New York CBSAs and the state's non-CBSA counties are published as of
2026-11-02, along with a separate OSM anchor table.

## Running markets

Declare the market in [sources/overture_places.yml](sources/overture_places.yml),
then build its local artifacts. The runner resumes unfinished steps, stops on a
failure, and never writes to the warehouse:

```sh
.venv-marimo/bin/python metro-deep-dive-program/engines/poi/run_poi_markets.py --markets hudson_ny
```

Its order is acquire, normalize, classify, taxonomy profile, taxonomy validation,
assign. Review the results, then publish:

```sh
.venv-marimo/bin/python metro-deep-dive-program/engines/poi/publish_poi_append.py --market hudson_ny
```

`publish_poi_append.py` refuses a market that already has rows, while
`publish_poi_mart.py` replaces them. Publishing needs the warehouse free of
other connections.

`SYNTH-NY` in `cbsa_code` marks the New York counties in no CBSA. It is
synthetic and joins to no real CBSA. The New York-Newark CBSA includes its NJ
counties, so statewide queries filter on county assignment `geo_id LIKE '36%'`.

**Raw counts overstate some markets.** Marts keep every source record, including
likely junk and closed places, and these vary a lot by market. No table or query
filters them yet. A review is pending, starting from this candidate filter:

```sql
try_cast(json_extract_string(source_attributes, '$.confidence') AS DOUBLE) >= 0.3
AND coalesce(json_extract_string(source_attributes, '$.operating_status'), '') <> 'permanently_closed'
AND mapping_status = 'mapped'
```

The evidence and open questions are in [the audit notes](NOTES.md), and the review
is tracked in the [NY build plan](../../issues/ny_state/NY_STATEWIDE_DATA_BUILD_PLAN.md).

`build_osm_anchors.py` and `publish_osm_anchors.py` build `mart_poi.poi_osm_anchor`:
rail stations, subway entrances, ferry terminals and bus stations from OSM, in
New York only. They stay separate from Overture records and are not merged.

## Ownership

- Geography supplies authoritative market boundaries, tract geometry,
  point-in-polygon rules, and boundary vintages.
- This engine owns source-place identity, source provenance, source taxonomy,
  governed category mappings, point assignments, and place QA.
- Q4 owns its daily-needs basket and access calculation.
- Infrastructure owns physical line and polygon features; a place anchor does
  not merge with an infrastructure footprint by default.

Stable code or tables move to `foundations/` only after two consumers use the
same interface unchanged.
