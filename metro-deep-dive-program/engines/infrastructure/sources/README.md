# Infrastructure Source Inventory

This directory holds declarative, market-parameterized source configurations.
The Epic 2 OSM baseline is declared in
[osm_infrastructure.yml](osm_infrastructure.yml), with its legacy evidence in
[the audit notes](../NOTES.md). It points to cached PBF source assets and the
cached GeoPackages used for local feature reads; both are checksummed at run
time and remain outside Git.

A future source declaration must identify the provider, source release or
dated snapshot, source asset URI and checksum where available, acquisition
partition/query, governed boundary identity and vintage, CRS, and row
accounting. Do not place downloaded PBFs, GeoPackages, or other source caches
here.

Official or specialist sources may be added only for a named consumer and
comparison rationale. They do not replace OSM by default.
