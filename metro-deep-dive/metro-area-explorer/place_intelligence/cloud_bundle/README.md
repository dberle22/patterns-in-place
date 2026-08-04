# Cloud Bundle

This folder is the publish-ready artifact root for the Place Intelligence Streamlit app.

Rules:
- `cloud_bundle/` is read-only at app runtime.
- The app automatically prefers `cloud_bundle/site_artifacts/<site_id>/` when it exists.
- Local development can still read from the larger `outputs/.../site_artifacts/<site_id>/` tree.
- `map/flood.geojson` is intentionally excluded from the cloud bundle because it dominates bundle size and the app no longer uses flood geometry as an interactive map layer.

Build the bundle:

```bash
.venv312/bin/python metro-deep-dive/metro-area-explorer/place_intelligence/build_cloud_bundle.py
```

What gets copied:
- page-contract JSONs: `overview.json`, `people.json`, `place.json`, `market_page.json`, `methods.json`
- minimal site metadata: `site.json`, `resolved_site.json`, `manifest.json`
- map assets still used by the app: `meta.json`, `rings.geojson`, `roads.geojson`, `poi_rows.csv`, `severed_area.geojson`, `water_adjusted_rings.geojson`, and the tract-fill GeoJSONs
- a copy of the source site YAML under `cloud_bundle/site_configs/`

Expected deployment shape:

```text
cloud_bundle/
  README.md
  site_configs/
    site_jacksonville_v0.yaml
  site_artifacts/
    jacksonville_fl_baymeadows_v0/
      manifest.json
      overview.json
      people.json
      place.json
      market_page.json
      methods.json
      ...
```

Recommended Streamlit Cloud entrypoint:

```text
metro-deep-dive/metro-area-explorer/place_intelligence/app.py
```

Optional override:
- Set `PLACE_INTELLIGENCE_ARTIFACT_ROOT` if you want the app to read published site bundles from another directory. The app expects `<artifact_root>/<site_id>/manifest.json`.
