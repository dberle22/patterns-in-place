# Engines

`engines/` holds reusable systems that support multiple analyses or issues.

Each engine folder should usually contain:

- `README.md` for scope and purpose
- `NOTES.md` for audit notes, current references, and open questions
- `CONTRACT.md` for expected inputs, outputs, grain, and caveats
- a notebook or build file once the engine is opened

Engines are built on call, then promoted only when reuse is real.

## Governed geometry handoff

Spatial consumers discover governed geometry through
`mart_geography.geometry_catalog` and must request an explicit geometry role.
`geo.places_analysis` is the national 2024 Census TIGER/Line Place product for
point assignment and line/polygon overlays; it is distinct from cartographic
display geometry. State and CBSA analytical products are also available.
County, tract, and ZCTA analytical geometry remain deferred until a named
spatial operation requires them.
