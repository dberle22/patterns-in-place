"""Tests for Place Intelligence site configuration loading."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "metro-area-explorer"
    / "place_intelligence"
    / "site_prep.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("place_intelligence_site_prep", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def pi_site_prep():
    return _load_module()


def test_load_site_round_trips_required_fields_and_defaults(tmp_path, pi_site_prep):
    site_path = tmp_path / "site.yaml"
    site_path.write_text(
        "\n".join(
            [
                'site_id: "example_site"',
                'address: "123 Main Street, Jacksonville, FL"',
                "lat:",
                "lon:",
                'geocode_source: "pending_geocode"',
                'market_id: "27260"',
                'asset_type: "retail"',
            ]
        ),
        encoding="utf-8",
    )

    site = pi_site_prep.load_site(str(site_path))

    assert site.site_id == "example_site"
    assert site.address == "123 Main Street, Jacksonville, FL"
    assert site.lat is None
    assert site.lon is None
    assert site.geocode_source == "pending_geocode"
    assert site.market_id == "27260"
    assert site.asset_type == "retail"
    assert site.rings_mi == [1, 3, 5]
    assert site.primary_ring_mi == 3


def test_load_site_raises_clear_error_for_missing_required_field(tmp_path, pi_site_prep):
    site_path = tmp_path / "site.yaml"
    site_path.write_text(
        "\n".join(
            [
                'site_id: "example_site"',
                "lat:",
                "lon:",
                'geocode_source: "pending_geocode"',
                'market_id: "27260"',
                'asset_type: "retail"',
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing required field: address"):
        pi_site_prep.load_site(str(site_path))


def test_load_site_parses_manual_coordinates_and_custom_rings(tmp_path, pi_site_prep):
    site_path = tmp_path / "site.yaml"
    site_path.write_text(
        "\n".join(
            [
                'site_id: "example_site"',
                'address: "123 Main Street, Jacksonville, FL"',
                "lat: 30.2219",
                "lon: -81.6267",
                'geocode_source: "manual_override"',
                'market_id: "27260"',
                'asset_type: "mixed"',
                "rings_mi: [2, 4, 6]",
                "primary_ring_mi: 4",
            ]
        ),
        encoding="utf-8",
    )

    site = pi_site_prep.load_site(str(site_path))

    assert site.lat == pytest.approx(30.2219)
    assert site.lon == pytest.approx(-81.6267)
    assert site.asset_type == "mixed"
    assert site.rings_mi == [2, 4, 6]
    assert site.primary_ring_mi == 4


def test_collect_imports_for_place_intelligence_files(pi_site_prep):
    assert pi_site_prep.Site.__name__ == "Site"


def test_list_site_configs_discovers_both_jacksonville_configs(pi_site_prep):
    site_configs = pi_site_prep.list_site_configs()
    site_names = sorted(path.name for path in site_configs)

    assert "site_jacksonville_v0.yaml" in site_names
    assert "site_jacksonville_downtown_v0.yaml" in site_names

    downtown_path = next(path for path in site_configs if path.name == "site_jacksonville_downtown_v0.yaml")
    downtown_site = pi_site_prep.load_site(str(downtown_path))

    assert downtown_site.site_id == "jacksonville_fl_downtown_v0"
    assert downtown_site.geocode_source == "manual_override"
    assert downtown_site.primary_ring_mi == 3
