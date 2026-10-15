import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This workbook is intentionally a read-only product surface. It imports
    # only the program-owned bundle adapters; no Streamlit, DuckDB, build, or
    # live-service dependency is available at notebook load.
    from pathlib import Path
    import sys

    import marimo as mo
    import pandas as pd

    notebook_dir = Path(__file__).resolve().parent
    if str(notebook_dir) not in sys.path:
        sys.path.insert(0, str(notebook_dir))

    from site_bundle_adapter import Availability, discover_bundle, load_bundle
    from site_map_products import load_map_layer, load_map_manifest
    from site_section_registry import SECTION_REGISTRY, SectionReadiness, render_work_card

    return Availability, SECTION_REGISTRY, SectionReadiness, discover_bundle, load_bundle, load_map_layer, load_map_manifest, mo, pd, render_work_card


@app.cell
def _(mo):
    # Keep all read-only controls in one cell. They only select already-built
    # evidence and never invoke a build, service request, or database write.
    site_selector = mo.ui.text(value="jacksonville_fl_baymeadows_v0", label="Built site identifier")
    ring_selector = mo.ui.dropdown({"1 mile": 1, "3 miles": 3, "5 miles": 5}, value="3 miles", label="Reach / ring")
    map_layer_selector = mo.ui.dropdown(
        {
            "Site rings": "rings",
            "Population context": "tract_fill_pop_total",
            "Household income context": "tract_fill_median_hh_income",
            "Home value context": "tract_fill_median_home_value",
            "Education context": "tract_fill_pct_ba_plus",
            "Points of interest": "pois",
            "Road context": "roads",
            "Water-adjustment context": "severed_area",
            "Flood screening context": "flood",
        },
        value="Site rings",
        label="Map layer",
    )
    display_metric_selector = mo.ui.dropdown(
        {"Population": "population", "Household income": "income", "Home value": "home_value"},
        value="Population",
        label="Display metric",
    )
    mo.vstack([
        mo.md("# Site Intelligence workbook\nRead-only review of one completed site bundle. Values preserve the bundle's source years and provenance; unavailable evidence is never a zero."),
        mo.hstack([site_selector, ring_selector, map_layer_selector, display_metric_selector], justify="start"),
    ])
    return display_metric_selector, map_layer_selector, ring_selector, site_selector


@app.cell
def _(discover_bundle, load_bundle, load_map_manifest, site_selector):
    # Bundle discovery stops at the documented compatibility boundary. A bad
    # selection remains visible as unavailable rather than falling back to a
    # different site or materializing a replacement product.
    bundle_dir = discover_bundle(site_selector.value.strip())
    products = load_bundle(bundle_dir) if bundle_dir else None
    map_manifest = load_map_manifest(products["map_manifest"]) if products else None
    return bundle_dir, map_manifest, products


@app.cell
def _(Availability, bundle_dir, mo, products):
    if products is None:
        _output = mo.callout(
            f"No completed bundle was found for the selected identifier. The workbook did not run a build or substitute another site.",
            kind="warn",
        )
    else:
        identity = products["site_identity"]
        site = identity.data["site"] if identity.data else {}
        resolved = identity.data["resolved_site"] if identity.data else {}
        metadata = identity.metadata
        sections = products["section_status"].data["sections"]
        client_ready = [section["workbook_label"] for section in sections if section["client_eligible"]]
        deferred_count = sum(not section["client_eligible"] for section in sections)
        _output = mo.vstack([
            mo.md("## Run and site identity"),
            mo.md(
                f"**Bundle status:** `{identity.availability.value}`  \\n+**Build timestamp:** `{metadata.built_at_utc or 'unavailable'}`  \\n+**Site:** {site.get('address', 'unavailable')}  \\n+**Coordinates:** {resolved.get('lat', 'unavailable')}, {resolved.get('lon', 'unavailable')}  \\n+**Geocode provenance:** `{resolved.get('geocode_source', 'unavailable')}`  \\n+**Rings:** {site.get('rings_mi', 'unavailable')}; primary {site.get('primary_ring_mi', 'unavailable')} miles"
            ),
            mo.md(f"**Client-readiness summary:** {len(client_ready)} sections currently eligible after adapter reconciliation ({'; '.join(client_ready)}). {deferred_count} sections remain workbook-only or deferred."),
            mo.callout("Reaches are straight-line Euclidean distances. They are not routing, travel time, access, or commuting measures.", kind="warn"),
        ])
    _output
    return


@app.cell
def _(Availability, display_metric_selector, mo, pd, products):
    if products is None or products["overview"].availability is not Availability.AVAILABLE:
        _output = mo.callout("Overview is unavailable from the selected bundle.", kind="warn")
    else:
        overview = products["overview"].data
        headlines = pd.DataFrame(overview["headline_table"])
        _output = mo.vstack([
            mo.md("## Overview"),
            mo.md(f"**Selected display metric:** {display_metric_selector.value}. {overview['page_meta'].get('summary_note', 'No overview note is available.')}"),
            mo.ui.table(headlines, page_size=10),
        ])
    _output
    return


@app.cell
def _(Availability, mo, pd, products, ring_selector):
    if products is None or products["people"].availability is not Availability.AVAILABLE:
        _output = mo.callout("People and daytime context are unavailable from the selected bundle.", kind="warn")
    else:
        people = products["people"].data
        profile = pd.DataFrame(people["catchment_profile"])
        daytime = pd.DataFrame(people["daytime_population"])
        profile = profile.loc[profile["ring_mi"] == ring_selector.value]
        daytime = daytime.loc[daytime["ring_mi"] == ring_selector.value]
        _output = mo.vstack([
            mo.md("## People and daytime context"),
            mo.md("Catchment rows are apportioned evidence. Benchmark rows are shown only where the bundle declares a compatible geography and measure."),
            mo.ui.table(profile, page_size=20),
            mo.md("### Jobs and resident workers"),
            mo.ui.table(daytime, page_size=10),
        ])
    _output
    return


@app.cell
def _(Availability, mo, pd, products, ring_selector):
    if products is None or products["place"].availability is not Availability.AVAILABLE:
        _output = mo.callout("Commercial and physical context are unavailable from the selected bundle.", kind="warn")
    else:
        place = products["place"].data
        poi = pd.DataFrame(place["poi_counts"])
        traffic = pd.DataFrame(place["frontage_segments"])
        screening = pd.DataFrame(place["nri_catchment_scores"])
        _output = mo.vstack([
            mo.md("## Commercial and physical context"),
            mo.callout("POI, AADT, and environmental screening are provisional workbook evidence. They are not client-ready claims.", kind="warn"),
            mo.md("### POI mix"),
            mo.ui.table(poi.loc[poi["ring_mi"] == ring_selector.value], page_size=20),
            mo.md("### Current corridor context"),
            mo.ui.table(traffic, page_size=15),
            mo.md("### Environmental screening"),
            mo.ui.table(screening.loc[screening["ring_mi"] == ring_selector.value], page_size=10),
        ])
    _output
    return


@app.cell
def _(Availability, mo, pd, products):
    if products is None or products["market"].availability is not Availability.AVAILABLE:
        _output = mo.callout("Metro context is unavailable from the selected bundle.", kind="warn")
    else:
        market = products["market"].data
        employment = pd.DataFrame(market["employment_mix"])
        _output = mo.vstack([
            mo.md("## Metro context"),
            mo.callout("Employment mix is provisional pending unit and scale QA. Housing/rent and GDP remain withheld in the deferred ledger.", kind="warn"),
            mo.ui.table(employment, page_size=20),
        ])
    _output
    return


@app.cell
def _(Availability, mo, pd, products):
    if products is None or products["methods"].availability is not Availability.AVAILABLE:
        _output = mo.callout("Methods and QA are unavailable from the selected bundle.", kind="warn")
    else:
        methods = products["methods"].data
        _output = mo.vstack([
            mo.md("## Methods and QA"),
            mo.ui.table(pd.DataFrame(methods["coverage_diagnostic"]), page_size=10),
            mo.ui.table(pd.DataFrame(methods["source_vintages"]), page_size=20),
            mo.md("\n".join(f"- {note}" for note in methods["method_notes"])),
        ])
    _output
    return


@app.cell
def _(Availability, map_layer_selector, map_manifest, mo, load_map_layer):
    # This is the only cell that can open a heavy GeoJSON/CSV, and it receives
    # one selected identifier rather than the legacy all-layers payload.
    selected_layer = load_map_layer(map_manifest, map_layer_selector.value) if map_manifest else None
    if selected_layer is None:
        _output = mo.callout("Map manifest is unavailable; no map layer was read.", kind="warn")
    elif selected_layer.availability is not Availability.AVAILABLE:
        _output = mo.callout(f"{selected_layer.definition.reader_label} is unavailable: {selected_layer.reason}", kind="warn")
    else:
        count = len(selected_layer.data.get("features", [])) if hasattr(selected_layer.data, "get") else len(selected_layer.data)
        _output = mo.vstack([
            mo.md("## Selected map evidence"),
            mo.md(
                f"**Layer:** {selected_layer.definition.reader_label}  \\n+**Source:** {selected_layer.definition.source}  \\n+**Vintage:** {selected_layer.definition.vintage}  \\n+**Measurement:** {selected_layer.definition.measurement}  \\n+**Geometry limitation:** {selected_layer.definition.geometry_limitation}  \\n+**Selected records/features:** {count}; source size: {selected_layer.bytes_on_disk:,} bytes"
            ),
        ])
    _output
    return selected_layer,


@app.cell
def _(SECTION_REGISTRY, mo, render_work_card):
    work_cards = [render_work_card(section) for section in SECTION_REGISTRY]
    deferred = [card for card in work_cards if card is not None]
    mo.vstack([
        mo.md("## Deferred-section ledger"),
        mo.md("Provisional evidence remains workbook-only. Withheld and method-candidate sections are explicit work items, not blank charts or client claims."),
        *[mo.md(card) for card in deferred],
    ])
    return


if __name__ == "__main__":
    app.run()
