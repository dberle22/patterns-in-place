# Source Spec: Census Geography Backbone

## Purpose

This source supplies the authoritative 2020 block registry, Census ZCTA and
Place membership, tract-vintage harmonization inputs, and governed geometry.

## Approved bundle

- 2020 PL 94-171 block population and housing-unit records;
- 2020 Place Block Assignment Files, with name lookup tables only when labels
  are needed, and the national 2020 ZCTA-to-block relationship file;
- 2010-to-2020 Census block relationship files for historical allocation;
- the 2020 tract relationship file for land-area intersections; and
- TIGER/Line (analysis) and Census cartographic boundary (display) files.

Files are acquired and staged one state at a time. The block registry stores
tabular IDs, memberships, counts, and areas; it never stores block polygons.

## Key limitations

The 2020 tract relationship file does not contain population or housing-unit
counts. Population and housing weights must be calculated from block-level
relationships and decennial counts. Census ZCTAs are decennial areal units and
must never be substituted with USPS ZIP codes.
