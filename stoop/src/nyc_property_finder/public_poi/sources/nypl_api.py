"""NYPL API public POI source adapter."""

from __future__ import annotations

import json
import shutil
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from nyc_property_finder.public_poi.config import (
    NORMALIZED_SOURCE_COLUMNS,
    SNAPSHOT_DIRS,
    SOURCE_SYSTEM_NYPL_API,
)

NYPL_LIBRARIES_URL = "https://refinery.nypl.org/api/nypl/ndo/v0.1/locations/libraries"


def fetch_snapshot(output_dir: str | Path = SNAPSHOT_DIRS["nypl"]) -> Path:
    """Download today's NYPL Refinery libraries snapshot."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    today = datetime.now(UTC).strftime("%Y%m%d")
    path = output_path / f"nypl_locations_{today}.json"
    if path.exists():
        return path

    query = urllib.parse.urlencode({"page[size]": 200, "page[number]": 1})
    url = f"{NYPL_LIBRARIES_URL}?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": "nyc-property-finder/0.1"})
    with urllib.request.urlopen(request, timeout=90) as response, path.open("wb") as file:
        shutil.copyfileobj(response, file)
    return path


def load(snapshot_path: str | Path) -> pd.DataFrame:
    """Load NYPL Refinery library rows into normalized POI records."""

    with Path(snapshot_path).open("r", encoding="utf-8") as file:
        payload = json.load(file)

    rows = []
    for record in payload.get("data", []):
        attributes = record.get("attributes", {})
        address = attributes.get("address") or {}
        lat = pd.to_numeric(address.get("latitude"), errors="coerce")
        lon = pd.to_numeric(address.get("longitude"), errors="coerce")
        if pd.isna(lat) or pd.isna(lon):
            continue

        rows.append(
            {
                "source_system": SOURCE_SYSTEM_NYPL_API,
                "source_id": f"public_library:nypl:{record.get('id', '')}",
                "category": "public_library",
                "subcategory": "nypl",
                "name": (
                    attributes.get("full-name")
                    or attributes.get("short-name")
                    or "NYPL Branch"
                ),
                "address": _address_value(address),
                "lat": float(lat),
                "lon": float(lon),
                "attributes": _attributes_value(attributes),
            }
        )

    if not rows:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)
    return pd.DataFrame(rows).drop_duplicates(subset=["source_id"])[NORMALIZED_SOURCE_COLUMNS]


def _address_value(address: dict[str, Any]) -> str:
    parts = [
        address.get("address1"),
        address.get("address2"),
        address.get("city"),
        address.get("region"),
        address.get("postal-code"),
    ]
    return " ".join(str(part).strip() for part in parts if part and str(part).strip())


def _attributes_value(attributes: dict[str, Any]) -> str:
    main_uri = attributes.get("main-uri") or attributes.get("about-uri") or {}
    if not isinstance(main_uri, dict):
        main_uri = {}
    return json.dumps(
        {
            "accessibility": attributes.get("accessibility") or None,
            "location_type": attributes.get("location-type") or None,
            "phone": attributes.get("phone") or None,
            "slug": attributes.get("slug") or None,
            "symbol": attributes.get("symbol") or None,
            "url": main_uri.get("full-uri") or None,
        },
        sort_keys=True,
    )
