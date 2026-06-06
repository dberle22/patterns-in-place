"""Configuration constants for public baseline POI ingestion."""

from __future__ import annotations

from pathlib import Path

from nyc_property_finder.services.config import PROJECT_ROOT

SOURCE_SYSTEM_MTA_GTFS = "mta_gtfs"
SOURCE_SYSTEM_NYC_OPEN_DATA = "nyc_open_data"
SOURCE_SYSTEM_OSM = "osm"
SOURCE_SYSTEM_GBFS = "gbfs"
SOURCE_SYSTEM_NYPL_API = "nypl_api"
SOURCE_SYSTEM_HAND_ENTRY = "hand_entry"

DEFAULT_RAW_PUBLIC_POI_DIR = PROJECT_ROOT / "data" / "raw" / "public_poi"
DEFAULT_MTA_SUBWAY_GTFS_PATH = PROJECT_ROOT / "data" / "raw" / "transit" / "gtfs_subway.zip"

SNAPSHOT_DIRS = {
    "mta_subway": DEFAULT_RAW_PUBLIC_POI_DIR / "mta_subway",
    "mta_bus": DEFAULT_RAW_PUBLIC_POI_DIR / "mta_bus",
    "citi_bike": DEFAULT_RAW_PUBLIC_POI_DIR / "citi_bike",
    "ferry_path": DEFAULT_RAW_PUBLIC_POI_DIR / "ferry_path",
    "nyc_open_data": DEFAULT_RAW_PUBLIC_POI_DIR / "nyc_open_data",
    "osm": DEFAULT_RAW_PUBLIC_POI_DIR / "osm",
    "nypl": DEFAULT_RAW_PUBLIC_POI_DIR / "nypl",
}

DIM_PUBLIC_POI_COLUMNS = [
    "poi_id",
    "source_system",
    "source_id",
    "category",
    "subcategory",
    "name",
    "address",
    "lat",
    "lon",
    "attributes",
    "snapshotted_at",
]

NORMALIZED_SOURCE_COLUMNS = [
    "source_system",
    "source_id",
    "category",
    "subcategory",
    "name",
    "address",
    "lat",
    "lon",
    "attributes",
]

CATEGORY_SLUGS = {
    "subway_station",
    "subway_entrance",
    "subway_line",
    "bus_stop",
    "citi_bike_station",
    "ferry_terminal",
    "path_station",
    "bike_lane",
    "park",
    "dog_run",
    "playground",
    "public_library",
    "post_office",
    "public_school",
    "farmers_market",
    "hospital",
    "urgent_care",
    "pharmacy",
    "grocery_store",
    "laundromat",
    "dry_cleaner",
    "gym",
    "hotel",
    "bank",
    "atm",
    "hardware_store",
    "landmark",
    "museum_institutional",
    "public_art",
}


def ensure_snapshot_dirs(base_dir: str | Path = DEFAULT_RAW_PUBLIC_POI_DIR) -> dict[str, Path]:
    """Create and return the expected public POI raw snapshot directories."""

    base_path = Path(base_dir)
    dirs = {
        name: base_path / path.relative_to(DEFAULT_RAW_PUBLIC_POI_DIR)
        for name, path in SNAPSHOT_DIRS.items()
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs
