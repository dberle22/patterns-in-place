"""Tests for Place Intelligence geocoding and tract resolution."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


SITE_PREP_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "metro-area-explorer"
    / "place_intelligence"
    / "site_prep.py"
)
GEOCODE_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "metro-area-explorer"
    / "place_intelligence"
    / "geocode.py"
)


def _load_site_prep_module():
    spec = importlib.util.spec_from_file_location("place_intelligence_site_prep", SITE_PREP_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_geocode_module():
    site_prep_module = _load_site_prep_module()
    sys.modules["site_prep"] = site_prep_module
    spec = importlib.util.spec_from_file_location("place_intelligence_geocode", GEOCODE_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture(scope="module")
def pi_geocode():
    return _load_geocode_module()


def test_geocode_address_returns_parsed_result(monkeypatch, pi_geocode):
    def _fake_urlopen(_url):
        return _FakeResponse(
            {
                "result": {
                    "input": {
                        "benchmark": {"benchmarkName": "Public_AR_Current"},
                        "vintage": {"vintageName": "Current_Current"},
                    },
                    "addressMatches": [
                        {
                            "matchedAddress": "3832 BAYMEADOWS RD, JACKSONVILLE, FL, 32217",
                            "coordinates": {"x": -81.616679103522, "y": 30.217618577902},
                            "geographies": {"Census Tracts": [{"GEOID": "12031016603"}]},
                        }
                    ],
                }
            }
        )

    monkeypatch.setattr(pi_geocode, "urlopen", _fake_urlopen)

    result = pi_geocode.geocode_address("3832 Baymeadows Road, Jacksonville, FL 32217")

    assert result.lat == pytest.approx(30.217618577902)
    assert result.lon == pytest.approx(-81.616679103522)
    assert result.matched_address == "3832 BAYMEADOWS RD, JACKSONVILLE, FL, 32217"
    assert result.match_type == "address_range"
    assert result.tract_geoid == "12031016603"
    assert result.geocode_source == "census_geocoder:Public_AR_Current:Current_Current"


def test_resolve_site_geocode_uses_manual_override_without_calling_geocoder(monkeypatch, pi_geocode):
    site = pi_geocode.Site(
        site_id="jacksonville_fl_baymeadows_v0",
        address="3832 Baymeadows Road, Jacksonville, FL 32217",
        lat=30.2176,
        lon=-81.6167,
        geocode_source="pending_geocode",
        market_id="27260",
        asset_type="retail",
        rings_mi=[1, 3, 5],
        primary_ring_mi=3,
    )

    def _fail_geocode(_address):
        raise AssertionError("geocode_address should not run when manual coordinates are present")

    monkeypatch.setattr(pi_geocode, "geocode_address", _fail_geocode)
    monkeypatch.setattr(pi_geocode, "resolve_tract_from_coordinates", lambda lon, lat: "12031016603")

    result = pi_geocode.resolve_site_geocode(site)

    assert result.lat == pytest.approx(30.2176)
    assert result.lon == pytest.approx(-81.6167)
    assert result.match_type == "manual_override"
    assert result.tract_geoid == "12031016603"
    assert result.geocode_source == "manual_override"


def test_geocode_address_raises_clear_error_on_no_match(monkeypatch, pi_geocode):
    monkeypatch.setattr(
        pi_geocode,
        "urlopen",
        lambda _url: _FakeResponse({"result": {"addressMatches": []}}),
    )

    with pytest.raises(
        ValueError,
        match="Census geocoder returned no match for address: Missing Address, Jacksonville, FL",
    ):
        pi_geocode.geocode_address("Missing Address, Jacksonville, FL")


def test_resolve_site_geocode_prefers_spatial_tract_when_lookup_disagrees(monkeypatch, pi_geocode):
    site = pi_geocode.Site(
        site_id="jacksonville_fl_baymeadows_v0",
        address="3832 Baymeadows Road, Jacksonville, FL 32217",
        lat=None,
        lon=None,
        geocode_source="pending_geocode",
        market_id="27260",
        asset_type="retail",
        rings_mi=[1, 3, 5],
        primary_ring_mi=3,
    )

    monkeypatch.setattr(
        pi_geocode,
        "geocode_address",
        lambda _address: pi_geocode.GeocodeResult(
            lat=30.217618577902,
            lon=-81.616679103522,
            matched_address="3832 BAYMEADOWS RD, JACKSONVILLE, FL, 32217",
            match_type="address_range",
            tract_geoid="99999999999",
            geocode_source="census_geocoder:Public_AR_Current:Current_Current",
        ),
    )
    monkeypatch.setattr(pi_geocode, "resolve_tract_from_coordinates", lambda lon, lat: "12031016603")

    result = pi_geocode.resolve_site_geocode(site)

    assert result.tract_geoid == "12031016603"
    assert result.geocode_source.endswith(":tract_corrected_by_spatial_join")


@pytest.mark.integration
def test_geocode_address_live_smoke(pi_geocode):
    result = pi_geocode.geocode_address("3832 Baymeadows Road, Jacksonville, FL 32217")

    assert result.tract_geoid == "12031016603"
    assert result.match_type == "address_range"
    assert "census_geocoder:" in result.geocode_source
