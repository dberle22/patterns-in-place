# Map 2 Ingestion Review

**Status:** Done
**Updated:** 2026-10-18

Map 2's bounded input ingestion is complete. The notebook section remains
unchanged and waits for Dan's data review. This is a dated record of the inputs,
validation and remaining visual decisions, not approval of the final map.

## Inputs available

| Input | Result | Provenance / QA |
|---|---|---|
| OSM infrastructure | 179,751 valid, uniquely identified serving features: 152,269 roads, 21,368 rail and 6,114 water-network features | [Consumer handoff](what_ny_is/data/map2_infrastructure_handoff.json), [independent input QA](what_ny_is/data/map2_ingestion_qa.json) |
| Canal Corporation centerline | 20 valid LineStrings; Erie route is one continuous line, about 337.78 miles | [Download manifest](what_ny_is/data/map2_reference_manifest.json) |
| Adirondack Park | One valid APA blue-line polygon, about 5.824 million acres | Download manifest; `what_ny_is/data/adirondack_park.geojson` |
| Catskill Park | One valid DEC blue-line polygon, about 696,707 acres | DEC's current `dil_reference/MapServer/8`; `what_ny_is/data/catskill_park.geojson` |
| Landmarks and ports | All 30 planned landmarks plus seven ports; all 37 coordinates inside NY; all retained for review | [Landmark CSV](what_ny_is/reference/landmarks.csv), [coordinate sources](what_ny_is/reference/landmark_sources.json) |
| Principal cities | 22 NY principal-city points across 13 metros, unique at CBSA × Place | Independently executed [SQL](what_ny_is/sql/ny_principal_cities.sql) |

The source PBF is Geofabrik's dated `new-york-261017.osm.pbf`, 497,738,989
bytes, verified against the provider's MD5. The approximately 4 GB GeoPackage
passes SQLite integrity checks and contains 2,174,756 lines, 5,092,046 polygons
and 4,180,281 points in EPSG:4326. Those are raw cache objects, not a governed
statewide POI product. Both raw files remain ignored under
`engines/infrastructure/outputs/new_york_state/raw/`.

The source run is `osm-infrastructure-36-snapshot-2026-10-17-426e6bab853f`.
It selects 180,497 core features, excludes 733 outside the governed state
boundary, and acquires 179,764 uniquely identified features. Validation retains
179,751 and preserves 13 in the rejection artifact: six boundary-touching
points and seven geometry collections, which the serving contract does not
accept as lines or polygons. No features require geometry repair. All acquired
features receive an existing core mapping; none are unmapped or ambiguous.

The published Parquet is about 91 MB and is resolved by the consumer handoff,
not copied into the issue or warehouse. All serving rows declare state `36`,
the 2023 analytical boundary and EPSG:5070 for metric QA. Their interchange
geometry remains longitude/latitude. Independent checks verify valid,
nonempty geometry, unique identities, NY intersection, reference checksums
and state-boundary containment to submillimeter numerical precision.

## Ports and named-site choices

The approved five are NY/NJ's NY side, Albany–Rensselaer, Oswego, Buffalo and
Ogdensburg. Coeymans and Rochester are additional review candidates.

- NY/NJ uses Howland Hook on Staten Island. Buffalo uses a hand-placed
  Gateway Metroport marker from its operator's published location map.
- Ogdensburg uses the terminal operator's coordinates. Wikipedia's port
  authority redirect leads to the international bridge, so it was not used.
- Rochester represents its terminal/marina complex at the Genesee River mouth.
  Its inclusion does not imply freight activity comparable to the other ports.
- Waterford uses the Lock E2 lockhouse as the eastern gateway to the flight.
  Bethlehem Steel uses the Library of Congress's Lackawanna plant coordinate.
  Tubman uses NPS's South Street home/visitor-center coordinate. These choices
  avoid substituting a municipality or another site with a similar name.
- Adirondack, Catskill and Finger Lakes CSV coordinates are label anchors.
  The two parks' actual areas come from their official polygons. No Finger
  Lakes regional polygon is asserted. Park boundaries include public and
  private land; they are not state-owned-land footprints.

Every row records its coordinate source and interpretation in
`landmark_sources.json`. `overture_id` is empty: there is no statewide Overture
run or new `mart_poi` materialization in this scope.

## Read before building the notebook

**The planned Thruway operator predicate returns zero rows.** Among 14,452
motorway features, 14,445 have no operator tag; the other seven name NYC DOT
or the Port Authority. There are 2,204 motorway features with one of four
Thruway names: New York State Thruway (1,743), Niagara Thruway (245), New England
Thruway (142) and Berkshire Connector (74). The planned fallback therefore
needs explicit name/ref rules checked against the official Thruway system
map, including the Cross-Westchester Expressway and bridge approaches. Do not
substitute all of I-87 or I-90. Raw names, refs and tags are preserved.

For main-line rail, 6,855 `railway=rail` features have `usage=main`; another
6,334 have no usage tag. Select the explicit main-line evidence for the draft,
and disclose the source tagging limit rather than treating missing usage as
proof of a non-main-line route. These are physical features, not a routable
or complete transport network.

The canal layer totals about 533.78 miles across all routes, lake stretches
and spurs; this is not the official 524-mile system mileage. Credit NYS Canal
Corporation and preserve the note that the service declares no license text.
Credit OpenStreetMap contributors for OSM data, with Geofabrik as extract
provider. Source URLs, pull timestamps and file checksums are in the manifests.

Next: review these inputs with Dan, then implement build-plan step 7. The
landmark/port cut, NYC clustering, visual layers, exports and Carto remain
pending. The existing notebook and its earlier visuals have not been edited.

## Shared-engine changes and verification

- Added explicit state-boundary support while preserving CBSA defaults and
  older manifests. State runs record the geometry's 2023 vintage rather than
  the identity backbone's 2020 vintage.
- Retained GDAL polygon-way IDs through `osm_way_id`, with a `way:` namespace
  that cannot collide with existing relation IDs. This avoids rejecting 843
  identity-complete water polygons found by the initial NY dry run.
- Made longitude/latitude order explicit in metric area transformations and
  cached acquisition stages in connection-local temporary tables to avoid
  repeated statewide adapter scans. Warehouse connections remain read-only.
- Added the NY source declaration, reproducible R adapter builder, state field
  in the handoff and corresponding contract documentation.
- Seven focused regression tests pass. Python compilation, R parsing, the
  unchanged notebook's `marimo check`, and `git diff --check` pass. Live
  normalization of both legacy markets still returns `cbsa`; Richmond's
  existing consumer handoff passes the updated field verification.

Run the focused tests from the repo root:

```sh
.venv-marimo/bin/python -m unittest discover \
  -s metro-deep-dive-program/engines/infrastructure/qa -p 'test_*.py'
```

The acquire → normalize → validate → publish CLI commands use
`.venv-marimo/bin/python`, the existing engine scripts and
`--market new_york_state`, in sequence. Do not overwrite the completed source
run merely to read it; the notebook should consume the verified handoff.
