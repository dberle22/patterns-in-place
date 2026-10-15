import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This fixed configuration is the only brief input. It deliberately has no
    # UI controls: exports must be reproducible and client-safe by default.
    import os

    BRIEF_CONFIG = {
        "site_id": os.environ.get("SITE_INTELLIGENCE_BRIEF_SITE_ID", "jacksonville_fl_baymeadows_v0"),
        "title": os.environ.get("SITE_INTELLIGENCE_BRIEF_TITLE", "Site Intelligence Brief"),
        "audience": os.environ.get("SITE_INTELLIGENCE_BRIEF_AUDIENCE", "Client review"),
        "client_section_ids": ("catchment_profile", "daytime_context"),
        "featured_metric": "pop_total",
    }
    return (BRIEF_CONFIG,)


@app.cell
def _():
    from pathlib import Path
    import sys

    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    notebook_dir = Path(__file__).resolve().parent
    if str(notebook_dir) not in sys.path:
        sys.path.insert(0, str(notebook_dir))
    from site_bundle_adapter import Availability, discover_bundle, load_bundle
    from site_map_products import load_map_layer, load_map_manifest
    from site_section_registry import SECTION_REGISTRY, SectionReadiness

    return Availability, SECTION_REGISTRY, SectionReadiness, discover_bundle, go, load_bundle, load_map_layer, load_map_manifest, mo, pd, px


@app.cell
def _(BRIEF_CONFIG, discover_bundle, load_bundle, load_map_manifest):
    # Read a completed artifact bundle only. Exporting this notebook never runs
    # a build, contacts a live service, or opens DuckDB.
    bundle_dir = discover_bundle(BRIEF_CONFIG["site_id"])
    products = load_bundle(bundle_dir) if bundle_dir else None
    map_manifest = load_map_manifest(products["map_manifest"]) if products else None
    return bundle_dir, map_manifest, products


@app.cell
def _(BRIEF_CONFIG, SECTION_REGISTRY, SectionReadiness):
    configured = set(BRIEF_CONFIG["client_section_ids"])
    client_sections = [section for section in SECTION_REGISTRY if section.section_id in configured]
    assert {section.section_id for section in client_sections} == configured
    assert all(section.status is SectionReadiness.CLIENT_READY and section.client_eligible for section in client_sections)
    return (client_sections,)


@app.cell
def _(Availability, BRIEF_CONFIG, client_sections, mo, products):
    if products is None:
        _brief_header = mo.callout("The configured completed site bundle is unavailable. No substitute site was used.", kind="warn")
    else:
        identity = products["site_identity"]
        site = identity.data["site"]
        resolved = identity.data["resolved_site"]
        _brief_header = mo.vstack([
            mo.md(f"# {BRIEF_CONFIG['title']}\n\n**Audience:** {BRIEF_CONFIG['audience']}"),
            mo.md(
                f"## Site and catchment orientation\n\n**Site:** {site['address']}  \\n+**Coordinates:** {resolved['lat']}, {resolved['lon']}  \\n+**Configured reaches:** {site['rings_mi']} miles; primary reach: {site['primary_ring_mi']} miles  \\n+**Bundle build:** {identity.metadata.built_at_utc}  \\n+**Included evidence:** {', '.join(section.workbook_label for section in client_sections)}"
            ),
            mo.callout("The reach is a straight-line Euclidean proximity area. It is not a travel-time, routing, access, or commuting measure.", kind="warn"),
        ])
    _brief_header
    return


@app.cell
def _(Availability, BRIEF_CONFIG, mo, pd, products, px):
    if products is None or products["people"].availability is not Availability.AVAILABLE:
        _people_output = mo.callout("Client-eligible people evidence is unavailable.", kind="warn")
    else:
        profile = pd.DataFrame(products["people"].data["catchment_profile"])
        # Legacy catchment rows use a null benchmark level; named levels are
        # comparison rows. Retain only the native catchment evidence rather
        # than treating a multi-tract total as a tract-like benchmark.
        featured = profile.loc[(profile["metric"] == BRIEF_CONFIG["featured_metric"]) & profile["benchmark_level"].isna()].copy()
        _population_chart = px.bar(featured, x="ring_mi", y="value", title="Population in straight-line reach", labels={"ring_mi": "Reach (miles)", "value": "Apportioned population"})
        _people_output = mo.vstack([
            mo.md("## People in range\nPopulation is apportioned from contributing tracts using the declared areal method. It is not a count of observed residents inside a routing area."),
            mo.ui.plotly(_population_chart),
            mo.md(f"**Source:** {', '.join(products['people'].provenance)}. **Years:** {', '.join(map(str, products['people'].source_years))}."),
        ])
    _people_output
    return


@app.cell
def _(Availability, mo, pd, products, px):
    if products is None or products["people"].availability is not Availability.AVAILABLE:
        _daytime_output = mo.callout("Client-eligible daytime evidence is unavailable.", kind="warn")
    else:
        daytime = pd.DataFrame(products["people"].data["daytime_population"])
        _daytime_chart = px.bar(daytime, x="ring_mi", y=["jobs_total", "workers_total"], barmode="group", title="Jobs and resident workers by reach", labels={"ring_mi": "Reach (miles)", "value": "Apportioned count", "variable": "Measure"})
        _daytime_output = mo.vstack([
            mo.md("## Daytime context\nJobs are workplace jobs located in the reach; workers are reach residents who report working. Both are apportioned tract evidence, not observed trips or commuting flows."),
            mo.ui.plotly(_daytime_chart),
            mo.md("**Source:** legacy Place Intelligence daytime population product; the retained bundle rows identify their 2023 vintage."),
        ])
    _daytime_output
    return


@app.cell
def _(Availability, go, load_map_layer, map_manifest, mo):
    # The brief uses one small, self-contained orientation map and no basemap
    # service. The only geometry read is the selected rings layer.
    rings = load_map_layer(map_manifest, "rings") if map_manifest else None
    if rings is None or rings.availability is not Availability.AVAILABLE:
        _map_output = mo.callout("The orientation map is unavailable from the selected bundle.", kind="warn")
    else:
        figure = go.Figure()
        for feature in rings.data["features"]:
            geometry = feature.get("geometry", {})
            coordinates = geometry.get("coordinates", [])
            polygon = coordinates[0] if geometry.get("type") == "Polygon" else []
            if polygon:
                x_values, y_values = zip(*polygon)
                figure.add_trace(go.Scatter(x=x_values, y=y_values, mode="lines", fill="toself", name=f"{feature.get('properties', {}).get('ring_mi', 'Reach')} mile reach"))
        figure.update_layout(title="Straight-line catchment orientation", xaxis_title="Longitude", yaxis_title="Latitude", showlegend=True)
        _map_output = mo.vstack([
            mo.md("## Catchment orientation map"),
            mo.ui.plotly(figure),
            mo.md(f"**Layer:** {rings.definition.reader_label}. **Source:** {rings.definition.source}. **Vintage:** {rings.definition.vintage}. **Limitation:** {rings.definition.geometry_limitation}"),
        ])
    _map_output
    return


@app.cell
def _(Availability, mo, products):
    if products is None or products["methods"].availability is not Availability.AVAILABLE:
        _appendix = mo.callout("Methods and provenance appendix is unavailable.", kind="warn")
    else:
        methods = products["methods"].data
        _appendix = mo.vstack([
            mo.md("## Methods, sources, and limitations"),
            mo.md("This brief excludes provisional commercial/physical and market sections, all withheld sections, raw diagnostics, and local paths."),
            mo.md("### Source vintages"),
            mo.ui.table([dict(row) for row in methods["source_vintages"]], page_size=30),
            mo.md("### Method notes\n" + "\n".join(f"- {note}" for note in methods["method_notes"])),
        ])
    _appendix
    return


if __name__ == "__main__":
    app.run()
