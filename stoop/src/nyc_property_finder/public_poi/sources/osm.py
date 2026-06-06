"""OpenStreetMap public POI source adapter."""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

import pandas as pd

from nyc_property_finder.public_poi.config import (
    NORMALIZED_SOURCE_COLUMNS,
    SNAPSHOT_DIRS,
    SOURCE_SYSTEM_OSM,
)

OVERPASS_URLS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
)
NYC_BBOX = (40.4774, -74.2591, 40.9176, -73.7004)

OSM_EXPORTS = {
    "pharmacies": {
        "filename": "nyc_pharmacies",
        "category": "pharmacy",
        "tag_key": "amenity",
        "tag_value": "pharmacy",
    },
    "banks": {
        "filename": "nyc_banks",
        "category": "bank",
        "tag_key": "amenity",
        "tag_value": "bank",
    },
    "atms": {
        "filename": "nyc_atms",
        "category": "atm",
        "tag_key": "amenity",
        "tag_value": "atm",
    },
    "hardware_stores": {
        "filename": "nyc_hardware_stores",
        "category": "hardware_store",
        "tag_key": "shop",
        "tag_value": "hardware",
    },
    "post_offices": {
        "filename": "nyc_post_offices",
        "category": "post_office",
        "tag_key": "amenity",
        "tag_value": "post_office",
    },
    "urgent_care": {
        "filename": "nyc_urgent_care",
        "category": "urgent_care",
        "tag_key": "amenity",
        "tag_value": "clinic",
    },
    "gyms": {
        "filename": "nyc_gyms",
        "category": "gym",
        "tag_key": "leisure",
        "tag_value": "fitness_centre",
    },
    "hotels": {
        "filename": "nyc_hotels",
        "category": "hotel",
        "tag_key": "tourism",
        "tag_value": "hotel",
    },
}

URGENT_CARE_INCLUDE_PATTERN = re.compile(
    r"\b("
    r"urgent|immediate|walk[- ]?in|citymd|afc|gohealth|medrite|medrite|"
    r"modern\s*md|modernmd|pm pediatrics?|pm pediatric urgent|kamin|kamin|"
    r"chai care|centers urgent|statcare|prompt[- ]?md|prohealth urgent|"
    r"pro health.*urgent|optum urgent|mi doctor|midoctor|nao medical|"
    r"quality first urgent|first response urgent|healthneed urgent|"
    r"forest urgent|friendly urgent|proxi medical urgent|ny doctors urgent|"
    r"new york doctors urgent|mount sinai urgent|atlantic health urgent|"
    r"nj doctors urgent|lamd medical group and urgent care"
    r")\b",
    re.IGNORECASE,
)
URGENT_CARE_EXCLUDE_PATTERN = re.compile(
    r"\b("
    r"laborator(y|ies)|lab\b|dialysis|kidney|radiology|imaging|surgery|"
    r"surgical|dermatology|skin specialists|acupuncture|dental|dentist|"
    r"orthodont|podiatr|vein|vascular|cancer|oncology|cardiac|cardiology|"
    r"gastro|gi\b|obstetrics|gynecology|women'?s health|fertility|"
    r"reproductive|rehab|rehabilitation|physical therapy|pain management|"
    r"massage|spa|veterinary|optical|eye surgery|retina"
    r")\b",
    re.IGNORECASE,
)
NYC_URGENT_CARE_CITY_NAMES = {
    "bronx",
    "brooklyn",
    "new york",
    "queens",
    "staten island",
}
NYC_URGENT_CARE_ZIP_PREFIXES = (
    "100",
    "101",
    "102",
    "103",
    "104",
    "111",
    "112",
    "113",
    "114",
    "116",
)


def fetch_snapshot(dataset_key: str, output_dir: str | Path = SNAPSHOT_DIRS["osm"]) -> Path:
    """Download today's Overpass snapshot for a configured OSM category."""

    if dataset_key not in OSM_EXPORTS:
        raise ValueError(f"Unknown OSM dataset key: {dataset_key}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    today = datetime.now(UTC).strftime("%Y%m%d")
    export = OSM_EXPORTS[dataset_key]
    path = output_path / f"{export['filename']}_{today}.geojson"
    if path.exists():
        return path

    query = _overpass_query(export["tag_key"], export["tag_value"])
    payload = urllib.parse.urlencode({"data": query}).encode("utf-8")
    feature_collection = _fetch_overpass_feature_collection(payload, export)
    with path.open("w", encoding="utf-8") as file:
        json.dump(feature_collection, file, sort_keys=True)
    return path


def load(snapshot_path: str | Path, dataset_key: str) -> pd.DataFrame:
    """Load a configured OSM GeoJSON snapshot into normalized POI rows."""

    if dataset_key not in OSM_EXPORTS:
        raise ValueError(f"Unknown OSM dataset key: {dataset_key}")

    with Path(snapshot_path).open("r", encoding="utf-8") as file:
        feature_collection = json.load(file)
    features = feature_collection.get("features", [])
    if not features:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    export = OSM_EXPORTS[dataset_key]
    rows = []
    for feature in features:
        properties = feature.get("properties", {})
        if dataset_key == "urgent_care" and not _is_urgent_care_feature(properties):
            continue
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [])
        if len(coordinates) < 2:
            continue
        lon = pd.to_numeric(coordinates[0], errors="coerce")
        lat = pd.to_numeric(coordinates[1], errors="coerce")
        if pd.isna(lat) or pd.isna(lon):
            continue

        rows.append(
            {
                "source_system": SOURCE_SYSTEM_OSM,
                "source_id": f"{export['category']}:{properties.get('osm_id', '')}",
                "category": export["category"],
                "subcategory": properties.get("tag_value", ""),
                "name": _feature_name(properties, export["category"]),
                "address": _feature_address(properties),
                "lat": float(lat),
                "lon": float(lon),
                "attributes": _feature_attributes(properties),
            }
        )

    if not rows:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)
    return pd.DataFrame(rows).drop_duplicates(subset=["source_id"])[NORMALIZED_SOURCE_COLUMNS]


def _is_urgent_care_feature(properties: dict[str, Any]) -> bool:
    """Keep only clinic rows that look like urgent/immediate care providers."""

    if not _is_nyc_feature_or_unknown(properties):
        return False

    search_text = " ".join(
        str(properties.get(key, ""))
        for key in ("name", "brand", "operator", "network", "website")
    )
    if not URGENT_CARE_INCLUDE_PATTERN.search(search_text):
        return False
    return not URGENT_CARE_EXCLUDE_PATTERN.search(search_text)


def _is_nyc_feature_or_unknown(properties: dict[str, Any]) -> bool:
    city = str(properties.get("addr:city", "")).strip().lower()
    if city and city not in NYC_URGENT_CARE_CITY_NAMES:
        return False

    postcode = str(properties.get("addr:postcode", "")).strip()
    postcode_match = re.search(r"\d{5}", postcode)
    if postcode_match and not postcode_match.group(0).startswith(NYC_URGENT_CARE_ZIP_PREFIXES):
        return False

    return True


def _overpass_query(tag_key: str, tag_value: str) -> str:
    south, west, north, east = NYC_BBOX
    bbox = f"{south},{west},{north},{east}"
    return f"""
    [out:json][timeout:180];
    (
      node["{tag_key}"="{tag_value}"]({bbox});
      way["{tag_key}"="{tag_value}"]({bbox});
      relation["{tag_key}"="{tag_value}"]({bbox});
    );
    out center tags;
    """


def _fetch_overpass_feature_collection(
    payload: bytes,
    export: dict[str, str],
) -> dict[str, Any]:
    errors = []
    for index, url in enumerate(OVERPASS_URLS):
        if index > 0:
            time.sleep(2)
        request = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "nyc-property-finder/0.1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                elements = json.load(response).get("elements", [])
                return _elements_to_feature_collection(elements, export)
        except (HTTPError, URLError, TimeoutError) as exc:
            errors.append(f"{url}: {exc}")

    message = "; ".join(errors)
    raise RuntimeError(f"All Overpass endpoints failed for {export['category']}: {message}")


def _elements_to_feature_collection(
    elements: list[dict[str, Any]],
    export: dict[str, str],
) -> dict[str, Any]:
    features = []
    for element in elements:
        coordinates = _element_coordinates(element)
        if coordinates is None:
            continue
        tags = element.get("tags", {})
        osm_type = str(element.get("type", ""))
        osm_id = str(element.get("id", ""))
        properties = {
            "osm_type": osm_type,
            "osm_id": f"{osm_type}/{osm_id}",
            "tag_key": export["tag_key"],
            "tag_value": export["tag_value"],
            **tags,
        }
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": coordinates},
                "properties": properties,
            }
        )
    return {"type": "FeatureCollection", "features": features}


def _element_coordinates(element: dict[str, Any]) -> list[float] | None:
    if "lon" in element and "lat" in element:
        return [float(element["lon"]), float(element["lat"])]
    center = element.get("center")
    if isinstance(center, dict) and "lon" in center and "lat" in center:
        return [float(center["lon"]), float(center["lat"])]
    return None


def _feature_name(properties: dict[str, Any], category: str) -> str:
    for key in ("name", "brand", "operator"):
        value = properties.get(key)
        if value:
            return str(value)
    return category.replace("_", " ").title()


def _feature_address(properties: dict[str, Any]) -> str:
    house_number = str(properties.get("addr:housenumber", "")).strip()
    street = str(properties.get("addr:street", "")).strip()
    city = str(properties.get("addr:city", "")).strip()
    postcode = str(properties.get("addr:postcode", "")).strip()
    return " ".join(part for part in (house_number, street, city, postcode) if part)


def _feature_attributes(properties: dict[str, Any]) -> str:
    retained = {
        key: value
        for key, value in properties.items()
        if key
        in {
            "amenity",
            "brand",
            "network",
            "opening_hours",
            "operator",
            "osm_id",
            "osm_type",
            "shop",
            "tourism",
            "website",
        }
    }
    return json.dumps(retained, sort_keys=True)
