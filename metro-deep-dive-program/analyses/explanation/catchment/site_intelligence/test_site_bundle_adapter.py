"""Focused contract tests for the read-only Site Intelligence bundle adapter."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import shutil
import sys
from types import MappingProxyType


MODULE_PATH = Path(__file__).with_name("site_bundle_adapter.py")
SPEC = importlib.util.spec_from_file_location("site_bundle_adapter", MODULE_PATH)
assert SPEC and SPEC.loader
adapter = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = adapter
SPEC.loader.exec_module(adapter)

import site_map_products as maps
import site_section_registry as registry

BUNDLE = (
    Path(__file__).resolve().parents[5]
    / "metro-deep-dive/metro-area-explorer/place_intelligence/outputs/jacksonville_fl/site_artifacts"
    / "jacksonville_fl_baymeadows_v0"
)
SECOND_BUNDLE = (
    Path(__file__).resolve().parents[5]
    / "metro-deep-dive/metro-area-explorer/place_intelligence/outputs/jacksonville_fl/site_artifacts"
    / "jacksonville_fl_12187_beach_blvd_v0"
)


def test_complete_bundle_reconciles_values_and_manifest_provenance():
    """The adapter returns stored evidence without changing a client-visible value."""

    products = adapter.load_bundle(BUNDLE)
    overview_source = json.loads((BUNDLE / "overview.json").read_text())

    assert products["overview"].availability is adapter.Availability.AVAILABLE
    assert products["overview"].data["headline_table"][0]["primary_value"] == overview_source["headline_table"][0]["primary_value"]
    assert products["people"].source_years == (2023, 2024)
    assert "population_demographics" in products["people"].provenance
    for result in products.values():
        assert result.metadata.site_id == "jacksonville_fl_baymeadows_v0"
        assert result.metadata.built_at_utc == "2026-08-03T01:58:03.106705+00:00"
        assert result.metadata.manifest["completed_steps"]
    assert products["section_status"].availability is adapter.Availability.AVAILABLE
    assert len(products["section_status"].data["sections"]) == 11


def test_second_built_site_uses_the_same_complete_adapter_contract():
    """A new Jacksonville site changes only the selected bundle identifier."""

    products = adapter.load_bundle(SECOND_BUNDLE)

    assert all(result.availability is adapter.Availability.AVAILABLE for result in products.values())
    assert products["site_identity"].metadata.site_id == "jacksonville_fl_12187_beach_blvd_v0"


def test_client_brief_population_and_daytime_series_are_nonempty_for_both_sites():
    """Client-ready charts use native catchment rows, not incompatible benchmarks."""

    for bundle in (BUNDLE, SECOND_BUNDLE):
        people = adapter.load_bundle(bundle)["people"].data
        population = [row for row in people["catchment_profile"] if row["metric"] == "pop_total" and (row["benchmark_level"] is None or (isinstance(row["benchmark_level"], float) and math.isnan(row["benchmark_level"])))]

        assert len(population) == len(people["daytime_population"]) == 3
        assert all(row["value"] is not None for row in population)


def test_missing_product_is_explicitly_unavailable(tmp_path):
    """Missing files never become an empty table or a zero-valued section."""

    fixture = tmp_path / "bundle"
    shutil.copytree(BUNDLE, fixture)
    (fixture / "people.json").unlink()

    result = adapter.load_bundle(fixture)["people"]

    assert result.availability is adapter.Availability.UNAVAILABLE
    assert result.data is None
    assert "people.json" in result.reason
    assert result.metadata.site_id == "jacksonville_fl_baymeadows_v0"


def test_missing_contract_key_or_row_column_is_invalid_and_preserves_payload(tmp_path):
    """Schema drift is distinct from absence and remains inspectable for diagnosis."""

    fixture = tmp_path / "bundle"
    shutil.copytree(BUNDLE, fixture)
    path = fixture / "people.json"
    payload = json.loads(path.read_text())
    payload["metric_summary"][0].pop("source_table")
    path.write_text(json.dumps(payload))

    result = adapter.load_bundle(fixture)["people"]

    assert result.availability is adapter.Availability.INVALID
    assert "metric_summary.source_table" in result.reason
    assert result.data["site"]["site_id"] == "jacksonville_fl_baymeadows_v0"


def test_empty_required_rows_are_not_treated_as_zero(tmp_path):
    """An emitted but empty product gets an explicit empty state."""

    fixture = tmp_path / "bundle"
    shutil.copytree(BUNDLE, fixture)
    path = fixture / "market_page.json"
    payload = json.loads(path.read_text())
    payload["employment_mix"] = []
    path.write_text(json.dumps(payload))

    result = adapter.load_bundle(fixture)["market"]

    assert result.availability is adapter.Availability.EMPTY
    assert result.data["employment_mix"] == ()
    assert "empty" in result.reason


def test_discovery_uses_an_explicit_root_without_importing_legacy_app(tmp_path):
    """The temporary discovery rule accepts a declared root and remains read-only."""

    root = tmp_path / "published"
    target = root / "jacksonville_fl_baymeadows_v0"
    shutil.copytree(BUNDLE, target)

    assert adapter.discover_bundle("jacksonville_fl_baymeadows_v0", root) == target
    assert adapter.discover_bundle("not_a_site", root) is None


def test_section_registry_covers_legacy_pages_and_keeps_deferred_work_visible():
    """Every legacy page has a declared source contract and no implied promotion."""

    assert set(registry.LEGACY_PAGE_CONTRACTS) == {"overview", "people", "place", "market", "methods"}
    assert {section.status for section in registry.SECTION_REGISTRY} == set(registry.SectionReadiness)
    assert all(section.client_eligible == (section.status is registry.SectionReadiness.CLIENT_READY) for section in registry.SECTION_REGISTRY)
    card = registry.render_work_card(next(section for section in registry.SECTION_REGISTRY if section.section_id == "routed_reach"))

    assert "method_candidate" in card
    assert "not travel time" in card
    assert registry.render_work_card(registry.SECTION_REGISTRY[0]) is None


def test_map_manifest_is_lightweight_and_selected_layer_only(tmp_path):
    """A malformed unselected layer cannot break manifest-first map selection."""

    map_dir = tmp_path / "map"
    map_dir.mkdir()
    (map_dir / "rings.geojson").write_text('{"type":"FeatureCollection","features":[]}')
    (map_dir / "roads.geojson").write_text("this file is intentionally not JSON")
    metadata = adapter.BundleMetadata(tmp_path, "test_site", "2026-10-07T00:00:00+00:00", MappingProxyType({"site_id": "test_site"}))
    map_result = adapter.AdapterResult(
        "map_manifest", adapter.Availability.AVAILABLE,
        MappingProxyType({
            "site_point": (MappingProxyType({"lat": 1, "lon": 2}),),
            "view_state": MappingProxyType({"latitude": 1, "longitude": 2, "zoom": 10}),
            "tract_fill_years": MappingProxyType({}),
            "tract_fill_sources": MappingProxyType({}),
            "nfhl_service_status": "unavailable",
            "nfhl_service_error": "not built",
        }),
        None, metadata, (), (),
    )

    manifest = maps.load_map_manifest(map_result)
    rings = maps.load_map_layer(manifest, "rings")

    assert manifest is not None
    assert rings.availability is adapter.Availability.AVAILABLE
    assert next(layer for layer in manifest.layers if layer.layer_id == "roads").relative_path is not None
    assert maps.load_map_layer(manifest, "roads").availability is adapter.Availability.UNAVAILABLE


def test_display_asset_is_bounded_and_does_not_replace_source_geometry(tmp_path):
    """Client display output is a separate bounded derivative with provenance."""

    products = adapter.load_bundle(BUNDLE)
    manifest = maps.load_map_manifest(products["map_manifest"])
    source = maps.load_map_layer(manifest, "rings")
    source_features = len(source.data["features"])
    output = tmp_path / "display" / "rings.geojson"

    display = maps.write_display_geojson(source, output, max_features=2, max_bytes=100_000)

    assert display.availability is adapter.Availability.AVAILABLE
    assert output.is_file()
    assert len(display.data["features"]) == 2
    assert display.data["display_metadata"]["source_feature_count"] == source_features
    assert len(source.data["features"]) == source_features
