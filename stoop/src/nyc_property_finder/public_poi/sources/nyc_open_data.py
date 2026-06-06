"""NYC Open Data public POI source adapter."""

from __future__ import annotations

import json
import shutil
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import geopandas as gpd
import pandas as pd

from nyc_property_finder.public_poi.config import (
    NORMALIZED_SOURCE_COLUMNS,
    SNAPSHOT_DIRS,
    SOURCE_SYSTEM_NYC_OPEN_DATA,
)

SOCRATA_EXPORTS = {
    "grocery_stores": {
        "dataset_id": "9a8c-vfzj",
        "domain": "data.ny.gov",
        "filename": "grocery_stores",
    },
    "dcwp_issued_licenses": {
        "dataset_id": "w7w3-xahh",
        "domain": "data.cityofnewyork.us",
        "filename": "dcwp_issued_licenses",
    },
    "bike_lanes": {
        "dataset_id": "mzxg-pwib",
        "domain": "data.cityofnewyork.us",
        "filename": "bike_lanes",
    },
    "parks": {
        "dataset_id": "enfh-gkve",
        "domain": "data.cityofnewyork.us",
        "filename": "parks",
    },
    "dog_runs": {
        "dataset_id": "hxx3-bwgv",
        "domain": "data.cityofnewyork.us",
        "filename": "dog_runs",
    },
    "playgrounds": {
        "dataset_id": "j55h-3upk",
        "domain": "data.cityofnewyork.us",
        "filename": "playgrounds",
    },
    "bpl_libraries": {
        "dataset_id": "feuq-due4",
        "domain": "data.cityofnewyork.us",
        "filename": "bpl_libraries",
    },
    "qpl_branches": {
        "dataset_id": "kh3d-xhq7",
        "domain": "data.cityofnewyork.us",
        "filename": "qpl_branches",
    },
    "public_schools": {
        "dataset_id": "r2nx-nhxe",
        "domain": "data.cityofnewyork.us",
        "filename": "public_schools",
    },
    "farmers_markets": {
        "dataset_id": "8vwk-6iz2",
        "domain": "data.cityofnewyork.us",
        "filename": "farmers_markets",
    },
    "facilities": {
        "dataset_id": "ji82-xba5",
        "domain": "data.cityofnewyork.us",
        "filename": "facilities",
    },
    "individual_landmarks": {
        "dataset_id": "buis-pvji",
        "domain": "data.cityofnewyork.us",
        "filename": "individual_landmarks",
    },
    "historic_districts": {
        "dataset_id": "skyk-mpzq",
        "domain": "data.cityofnewyork.us",
        "filename": "historic_districts",
    },
    "dcla_cultural_organizations": {
        "dataset_id": "u35m-9t32",
        "domain": "data.cityofnewyork.us",
        "filename": "dcla_cultural_organizations",
    },
    "public_art": {
        "dataset_id": "2pg3-gcaa",
        "domain": "data.cityofnewyork.us",
        "filename": "public_art",
    },
}

NYC_COUNTIES = {"BRONX", "KINGS", "NEW YORK", "QUEENS", "RICHMOND"}

PARK_TYPECATEGORY_ALLOWLIST = {
    "Garden",
    "Neighborhood Park",
    "Flagship Park",
    "Triangle/Plaza",
    "Jointly Operated Playground",
}

SUPERMARKET_NAME_PATTERNS = (
    "SUPERMARKET",
    "FOOD BAZAAR",
    "FOODTOWN",
    "KEY FOOD",
    "CTOWN",
    "C TOWN",
    "FINE FARE",
    "FOOD UNIVERSE",
    "IDEAL FOOD BASKET",
    "BRAVO",
    "ASSOCIATED",
    "WESTSIDE MARKET",
    "WEST SIDE MARKET",
    "WHOLE FOODS",
    "TRADER JOE",
    "WEGMANS",
    "H MART",
    "ALDI",
    "LIDL",
    "FAIRWAY",
    "MORTON WILLIAMS",
    "GRISTEDES",
    "DAGOSTINO",
    "D'AGOSTINO",
    "MET FOOD",
    "SHOP FAIR",
    "SHOPRITE",
    "STOP & SHOP",
)

SUPERMARKET_EXCLUDE_PATTERNS = (
    "PHARMACY",
    "CVS",
    "WALGREENS",
    "DUANE READE",
    "RITE AID",
    "DOLLAR",
    "FAMILY DOLLAR",
    "DOLLAR TREE",
    "GAS",
    "MART",
    "7-ELEVEN",
    "SEVEN ELEVEN",
    "SMOKE",
    "TOBACCO",
    "VAPE",
    "WINE",
    "LIQUOR",
)

DCWP_ACTIVE_STATUSES = {"ACTIVE", "READY FOR RENEWAL"}
HOSPITAL_FACTYPES = {"ACUTE CARE HOSPITAL", "HOSPITAL"}
DCLA_MUSEUM_DISCIPLINES = {"BOTANICAL", "MUSEUM", "SCIENCE", "ZOO"}


def fetch_snapshot(
    dataset_key: str,
    output_dir: str | Path = SNAPSHOT_DIRS["nyc_open_data"],
    limit: int = 50000,
) -> Path:
    """Download today's GeoJSON snapshot for a configured NYC Open Data dataset."""

    if dataset_key not in SOCRATA_EXPORTS:
        raise ValueError(f"Unknown NYC Open Data dataset key: {dataset_key}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    today = datetime.now(UTC).strftime("%Y%m%d")
    dataset = SOCRATA_EXPORTS[dataset_key]
    path = output_path / f"{dataset['filename']}_{today}.geojson"
    if not path.exists():
        query = urllib.parse.urlencode({"$limit": limit})
        domain = dataset.get("domain", "data.cityofnewyork.us")
        url = f"https://{domain}/resource/{dataset['dataset_id']}.geojson?{query}"
        request = urllib.request.Request(url, headers={"User-Agent": "nyc-property-finder/0.1"})
        with urllib.request.urlopen(request, timeout=90) as response, path.open("wb") as file:
            shutil.copyfileobj(response, file)
    return path


def fetch_json_snapshot(
    dataset_key: str,
    output_dir: str | Path = SNAPSHOT_DIRS["nyc_open_data"],
    limit: int = 50000,
) -> Path:
    """Download today's JSON snapshot for a configured Socrata dataset."""

    if dataset_key not in SOCRATA_EXPORTS:
        raise ValueError(f"Unknown NYC Open Data dataset key: {dataset_key}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    today = datetime.now(UTC).strftime("%Y%m%d")
    dataset = SOCRATA_EXPORTS[dataset_key]
    path = output_path / f"{dataset['filename']}_{today}.json"
    if not path.exists():
        query = urllib.parse.urlencode({"$limit": limit})
        domain = dataset.get("domain", "data.cityofnewyork.us")
        url = f"https://{domain}/resource/{dataset['dataset_id']}.json?{query}"
        request = urllib.request.Request(url, headers={"User-Agent": "nyc-property-finder/0.1"})
        with urllib.request.urlopen(request, timeout=90) as response, path.open("wb") as file:
            shutil.copyfileobj(response, file)
    return path


def load_bike_lanes(snapshot_path: str | Path) -> pd.DataFrame:
    """Load NYC DOT bicycle route features as centroid POI rows."""

    routes = gpd.read_file(snapshot_path)
    if routes.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    routes = routes.loc[~routes.geometry.isna()].copy()
    projected = routes.to_crs(2263)
    centroids = projected.geometry.centroid.to_crs(4326)
    routes["lat"] = centroids.y
    routes["lon"] = centroids.x
    routes["source_id_value"] = routes.apply(_bike_lane_source_id, axis=1)
    routes["name_value"] = routes.apply(_bike_lane_name, axis=1)

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "bike_lane:" + routes["source_id_value"].astype(str),
            "category": "bike_lane",
            "subcategory": routes.apply(
                _first_present_value,
                axis=1,
                candidates=_facility_candidates(),
            ),
            "name": routes["name_value"],
            "address": "",
            "lat": routes["lat"],
            "lon": routes["lon"],
            "attributes": routes.apply(_bike_lane_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_parks(snapshot_path: str | Path) -> pd.DataFrame:
    """Load NYC Parks property polygons as centroid POI rows."""

    parks = gpd.read_file(snapshot_path)
    if parks.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    parks = parks.loc[~parks.geometry.isna()].copy()
    parks["typecategory_value"] = parks.apply(
        _first_present_value,
        axis=1,
        candidates=("typecategory", "type_category"),
    )
    parks = parks.loc[parks["typecategory_value"].isin(PARK_TYPECATEGORY_ALLOWLIST)].copy()
    if parks.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    parks = _add_centroid_coordinates(parks)
    parks["source_id_value"] = parks.apply(_park_source_id, axis=1)
    parks["name_value"] = parks.apply(_park_name, axis=1)

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "park:" + parks["source_id_value"].astype(str),
            "category": "park",
            "subcategory": parks["typecategory_value"],
            "name": parks["name_value"],
            "address": parks.apply(_address_value, axis=1),
            "lat": parks["lat"],
            "lon": parks["lon"],
            "attributes": parks.apply(_park_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_dog_runs(snapshot_path: str | Path) -> pd.DataFrame:
    """Load NYC Parks dog run features as POI rows."""

    dog_runs = gpd.read_file(snapshot_path)
    if dog_runs.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    dog_runs = dog_runs.loc[~dog_runs.geometry.isna()].copy()
    dog_runs = _add_centroid_coordinates(dog_runs)
    dog_runs["source_id_value"] = dog_runs.apply(_dog_run_source_id, axis=1)
    dog_runs["name_value"] = dog_runs.apply(_dog_run_name, axis=1)

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "dog_run:" + dog_runs["source_id_value"].astype(str),
            "category": "dog_run",
            "subcategory": "",
            "name": dog_runs["name_value"],
            "address": dog_runs.apply(_address_value, axis=1),
            "lat": dog_runs["lat"],
            "lon": dog_runs["lon"],
            "attributes": dog_runs.apply(_dog_run_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_playgrounds(snapshot_path: str | Path) -> pd.DataFrame:
    """Load NYC Parks playground/children's play area features as POI rows."""

    playgrounds = gpd.read_file(snapshot_path)
    if playgrounds.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    playgrounds = playgrounds.loc[~playgrounds.geometry.isna()].copy()
    playgrounds = _add_centroid_coordinates(playgrounds)
    playgrounds["source_id_value"] = playgrounds.apply(_playground_source_id, axis=1)
    playgrounds["name_value"] = playgrounds.apply(_playground_name, axis=1)

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "playground:" + playgrounds["source_id_value"].astype(str),
            "category": "playground",
            "subcategory": playgrounds.apply(
                _first_present_value,
                axis=1,
                candidates=("type", "asset_type", "play_area_type", "category"),
            ),
            "name": playgrounds["name_value"],
            "address": playgrounds.apply(_address_value, axis=1),
            "lat": playgrounds["lat"],
            "lon": playgrounds["lon"],
            "attributes": playgrounds.apply(_playground_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_grocery_stores(snapshot_path: str | Path) -> pd.DataFrame:
    """Load supermarket-style NYC grocery stores from NYS retail food stores."""

    stores = _read_json_records(snapshot_path)
    if stores.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    stores = stores.loc[stores.apply(_is_nyc_retail_food_store, axis=1)].copy()
    stores = stores.loc[stores.apply(_is_supermarket_baseline, axis=1)].copy()
    stores = stores.loc[stores.apply(_has_valid_lat_lon, axis=1)].copy()
    if stores.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    stores["source_id_value"] = stores.apply(_grocery_source_id, axis=1)
    stores["name_value"] = stores.apply(_grocery_name, axis=1)

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "grocery_store:" + stores["source_id_value"].astype(str),
            "category": "grocery_store",
            "subcategory": "supermarket",
            "name": stores["name_value"],
            "address": stores.apply(_grocery_address, axis=1),
            "lat": stores.apply(_lat_value, axis=1),
            "lon": stores.apply(_lon_value, axis=1),
            "attributes": stores.apply(_grocery_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_laundromats(snapshot_path: str | Path) -> pd.DataFrame:
    """Load laundromats from DCWP issued-license snapshots."""

    return _load_dcwp_businesses(
        snapshot_path,
        category="laundromat",
        legacy_industry_code="110",
        current_category_allowlist=("LAUNDRIES", "INDUSTRIAL LAUNDRY"),
        name_patterns=("LAUNDROMAT", "LAUNDRY", "WASH & FOLD", "WASH AND FOLD"),
    )


def load_dry_cleaners(snapshot_path: str | Path) -> pd.DataFrame:
    """Load dry cleaners from DCWP issued-license snapshots."""

    return _load_dcwp_businesses(
        snapshot_path,
        category="dry_cleaner",
        legacy_industry_code="113",
        current_category_allowlist=("INDUSTRIAL LAUNDRY", "INDUSTRIAL LAUNDRY DELIVERY"),
        name_patterns=("DRY CLEAN", "CLEANERS", "CLEANER", "TAILOR"),
    )


def load_bpl_branches(snapshot_path: str | Path) -> pd.DataFrame:
    """Load Brooklyn Public Library branches from the NYC Open Data library layer."""

    libraries = _read_tabular_records(snapshot_path)
    if libraries.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    libraries = libraries.loc[
        libraries.apply(_first_present_value, axis=1, candidates=("system",)).str.upper()
        == "BPL"
    ].copy()
    libraries = libraries.loc[libraries.apply(_has_valid_point, axis=1)].copy()
    if libraries.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    libraries["source_id_value"] = libraries.apply(_library_source_id, axis=1)
    libraries = libraries.drop_duplicates(subset=["source_id_value"])

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "public_library:bpl:" + libraries["source_id_value"].astype(str),
            "category": "public_library",
            "subcategory": "bpl",
            "name": libraries.apply(_library_name, axis=1),
            "address": libraries.apply(_library_address, axis=1),
            "lat": libraries.apply(_point_lat_value, axis=1),
            "lon": libraries.apply(_point_lon_value, axis=1),
            "attributes": libraries.apply(_bpl_library_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_qpl_branches(snapshot_path: str | Path) -> pd.DataFrame:
    """Load Queens Public Library branches from a static CSV or Socrata JSON snapshot."""

    libraries = _read_tabular_records(snapshot_path)
    if libraries.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    libraries = libraries.loc[libraries.apply(_has_valid_point, axis=1)].copy()
    if libraries.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    libraries["source_id_value"] = libraries.apply(_qpl_source_id, axis=1)
    libraries = libraries.drop_duplicates(subset=["source_id_value"])

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "public_library:qpl:" + libraries["source_id_value"].astype(str),
            "category": "public_library",
            "subcategory": "qpl",
            "name": libraries.apply(_library_name, axis=1),
            "address": libraries.apply(_qpl_address, axis=1),
            "lat": libraries.apply(_point_lat_value, axis=1),
            "lon": libraries.apply(_point_lon_value, axis=1),
            "attributes": libraries.apply(_qpl_library_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_public_schools(snapshot_path: str | Path) -> pd.DataFrame:
    """Load open public school locations from DOE school snapshots."""

    schools = _read_json_records(snapshot_path)
    if schools.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    schools = schools.loc[schools.apply(_is_open_public_school, axis=1)].copy()
    schools = schools.loc[schools.apply(_has_valid_point, axis=1)].copy()
    if schools.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    schools["fiscal_year_numeric"] = pd.to_numeric(schools.get("fiscal_year"), errors="coerce")
    schools = schools.sort_values("fiscal_year_numeric").drop_duplicates(
        subset=["location_code"],
        keep="last",
    )

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "public_school:" + schools.apply(_school_source_id, axis=1),
            "category": "public_school",
            "subcategory": schools.apply(
                _first_present_value,
                axis=1,
                candidates=("location_category_description", "location_type_description"),
            ),
            "name": schools.apply(_school_name, axis=1),
            "address": schools.apply(_school_address, axis=1),
            "lat": schools.apply(_point_lat_value, axis=1),
            "lon": schools.apply(_point_lon_value, axis=1),
            "attributes": schools.apply(_school_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_farmers_markets(snapshot_path: str | Path) -> pd.DataFrame:
    """Load NYC farmers markets from DOHMH market snapshots."""

    markets = _read_json_records(snapshot_path)
    if markets.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    markets = markets.loc[markets.apply(_has_valid_lat_lon, axis=1)].copy()
    markets["year_numeric"] = pd.to_numeric(markets.get("year"), errors="coerce")
    latest_year = markets["year_numeric"].max()
    if pd.notna(latest_year):
        markets = markets.loc[markets["year_numeric"] == latest_year].copy()
    if markets.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    markets["source_id_value"] = markets.apply(_farmers_market_source_id, axis=1)
    markets = markets.drop_duplicates(subset=["source_id_value"])

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "farmers_market:" + markets["source_id_value"].astype(str),
            "category": "farmers_market",
            "subcategory": markets.apply(_farmers_market_subcategory, axis=1),
            "name": markets.apply(_farmers_market_name, axis=1),
            "address": markets.apply(_farmers_market_address, axis=1),
            "lat": markets.apply(_lat_value, axis=1),
            "lon": markets.apply(_lon_value, axis=1),
            "attributes": markets.apply(_farmers_market_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_hospitals(snapshot_path: str | Path) -> pd.DataFrame:
    """Load hospital facilities from the current DCP Facilities Database."""

    facilities = _read_json_records(snapshot_path)
    if facilities.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    facilities = facilities.loc[facilities.apply(_is_general_hospital, axis=1)].copy()
    facilities = facilities.loc[facilities.apply(_has_valid_lat_lon, axis=1)].copy()
    if facilities.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    facilities["source_id_value"] = facilities.apply(_facility_source_id, axis=1)
    facilities = facilities.drop_duplicates(subset=["source_id_value"])

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "hospital:" + facilities["source_id_value"].astype(str),
            "category": "hospital",
            "subcategory": facilities.apply(
                _first_present_value,
                axis=1,
                candidates=("factype", "facsubgrp"),
            ),
            "name": facilities.apply(_facility_name, axis=1),
            "address": facilities.apply(_facility_address, axis=1),
            "lat": facilities.apply(_lat_value, axis=1),
            "lon": facilities.apply(_lon_value, axis=1),
            "attributes": facilities.apply(_facility_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_individual_landmarks(snapshot_path: str | Path) -> pd.DataFrame:
    """Load LPC individual landmark site polygons as centroid POI rows."""

    landmarks = gpd.read_file(snapshot_path)
    if landmarks.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    landmarks = landmarks.loc[~landmarks.geometry.isna()].copy()
    landmarks = _add_centroid_coordinates(landmarks)
    landmarks["source_id_value"] = landmarks.apply(_landmark_source_id, axis=1)
    landmarks = landmarks.drop_duplicates(subset=["source_id_value"])

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "landmark:individual:" + landmarks["source_id_value"].astype(str),
            "category": "landmark",
            "subcategory": landmarks.apply(
                _first_present_value,
                axis=1,
                candidates=("landmarkty", "lpc_sitest"),
            ),
            "name": landmarks.apply(_landmark_name, axis=1),
            "address": landmarks.apply(_landmark_address, axis=1),
            "lat": landmarks["lat"],
            "lon": landmarks["lon"],
            "attributes": landmarks.apply(_landmark_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_historic_districts(snapshot_path: str | Path) -> pd.DataFrame:
    """Load LPC historic district polygons as centroid POI rows."""

    districts = gpd.read_file(snapshot_path)
    if districts.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    districts = districts.loc[~districts.geometry.isna()].copy()
    districts = _add_centroid_coordinates(districts)
    districts["source_id_value"] = districts.apply(_historic_district_source_id, axis=1)
    districts = districts.drop_duplicates(subset=["source_id_value"])

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "landmark:historic_district:" + districts["source_id_value"].astype(str),
            "category": "landmark",
            "subcategory": "historic_district",
            "name": districts.apply(_historic_district_name, axis=1),
            "address": "",
            "lat": districts["lat"],
            "lon": districts["lon"],
            "attributes": districts.apply(_historic_district_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_dcla_museums(snapshot_path: str | Path) -> pd.DataFrame:
    """Load institutional museum-like organizations from DCLA cultural organizations."""

    organizations = _read_json_records(snapshot_path)
    if organizations.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    organizations = organizations.loc[organizations.apply(_is_dcla_museum, axis=1)].copy()
    organizations = organizations.loc[organizations.apply(_has_valid_lat_lon, axis=1)].copy()
    if organizations.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    organizations["source_id_value"] = organizations.apply(_dcla_source_id, axis=1)
    organizations = organizations.drop_duplicates(subset=["source_id_value"])

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "museum_institutional:" + organizations["source_id_value"].astype(str),
            "category": "museum_institutional",
            "subcategory": organizations.apply(_dcla_museum_subcategory, axis=1),
            "name": organizations.apply(_dcla_name, axis=1),
            "address": organizations.apply(_dcla_address, axis=1),
            "lat": organizations.apply(_lat_value, axis=1),
            "lon": organizations.apply(_lon_value, axis=1),
            "attributes": organizations.apply(_dcla_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def load_public_art(snapshot_path: str | Path) -> pd.DataFrame:
    """Load public outdoor artwork from the Public Design Commission inventory."""

    artworks = _read_json_records(snapshot_path)
    if artworks.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    artworks = artworks.loc[artworks.apply(_has_valid_lat_lon, axis=1)].copy()
    if artworks.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    artworks["source_id_value"] = artworks.apply(_public_art_source_id, axis=1)
    artworks = artworks.drop_duplicates(subset=["source_id_value"])

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": "public_art:" + artworks["source_id_value"].astype(str),
            "category": "public_art",
            "subcategory": artworks.apply(
                _first_present_value,
                axis=1,
                candidates=("artwork_type1", "artwork_type2"),
            ),
            "name": artworks.apply(_public_art_name, axis=1),
            "address": artworks.apply(_public_art_address, axis=1),
            "lat": artworks.apply(_lat_value, axis=1),
            "lon": artworks.apply(_lon_value, axis=1),
            "attributes": artworks.apply(_public_art_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def _add_centroid_coordinates(features: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    features = features.copy()
    if features.crs is None:
        features = features.set_crs(4326)
    projected = features.to_crs(2263)
    centroids = projected.geometry.centroid.to_crs(4326)
    features["lat"] = centroids.y
    features["lon"] = centroids.x
    return features


def _read_json_records(snapshot_path: str | Path) -> pd.DataFrame:
    with Path(snapshot_path).open("r", encoding="utf-8") as file:
        records = json.load(file)
    if not records:
        return pd.DataFrame()
    if not isinstance(records, list):
        raise ValueError(f"Expected a Socrata JSON array at {snapshot_path}")
    return pd.DataFrame(records)


def _read_tabular_records(snapshot_path: str | Path) -> pd.DataFrame:
    path = Path(snapshot_path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, dtype=str).fillna("")
    return _read_json_records(path)


def _library_source_id(row: pd.Series) -> str:
    return _first_present_value(row, ("bin", "bbl", "name")) or str(row.name)


def _qpl_source_id(row: pd.Series) -> str:
    return _first_present_value(row, ("bin", "bbl", "name")) or str(row.name)


def _library_name(row: pd.Series) -> str:
    return _first_present_value(row, ("name", "branch", "facname")) or "Public Library"


def _library_address(row: pd.Series) -> str:
    parts = [
        _first_present_value(row, ("housenum",)),
        _first_present_value(row, ("streetname",)),
        _first_present_value(row, ("city",)),
        _first_present_value(row, ("zip", "postcode")),
    ]
    return " ".join(part for part in parts if part)


def _qpl_address(row: pd.Series) -> str:
    parts = [
        _first_present_value(row, ("address", "location_1_address")),
        _first_present_value(row, ("city", "location_1_city")),
        _first_present_value(row, ("postcode", "location_1_zip")),
    ]
    return " ".join(part for part in parts if part)


def _bpl_library_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "bbl": _first_present_value(row, ("bbl",)) or None,
            "bin": _first_present_value(row, ("bin",)) or None,
            "system": _first_present_value(row, ("system",)) or None,
            "url": _first_present_value(row, ("url",)) or None,
        },
        sort_keys=True,
    )


def _qpl_library_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "bbl": _first_present_value(row, ("bbl",)) or None,
            "bin": _first_present_value(row, ("bin",)) or None,
            "phone": _first_present_value(row, ("phone",)) or None,
            "system": "QPL",
        },
        sort_keys=True,
    )


def _is_open_public_school(row: pd.Series) -> bool:
    status = _first_present_value(row, ("status_descriptions", "status"))
    if status and not status.upper().startswith("OPEN"):
        return False
    managed_by = _first_present_value(row, ("managed_by_name",))
    if managed_by and managed_by.upper() not in {"DOE", "NYCDOE"}:
        return False
    return True


def _school_source_id(row: pd.Series) -> str:
    return _first_present_value(
        row,
        ("location_code", "ats_system_code", "beds_number"),
    ) or str(row.name)


def _school_name(row: pd.Series) -> str:
    return _first_present_value(row, ("location_name", "school_name")) or (
        f"Public school {row.get('location_code', row.name)}"
    )


def _school_address(row: pd.Series) -> str:
    parts = [
        _first_present_value(row, ("primary_address_line_1", "location_1_address")),
        _first_present_value(row, ("location_1_city",)),
        _first_present_value(row, ("state_code", "location_1_state")),
        _first_present_value(row, ("location_1_zip",)),
    ]
    return " ".join(part for part in parts if part)


def _school_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "beds_number": _first_present_value(row, ("beds_number",)) or None,
            "fiscal_year": _first_present_value(row, ("fiscal_year",)) or None,
            "grades": _first_present_value(row, ("grades_final_text", "grades_text")) or None,
            "location_type": _first_present_value(row, ("location_type_description",)) or None,
            "managed_by": _first_present_value(row, ("managed_by_name",)) or None,
            "nta": _first_present_value(row, ("nta",)) or None,
        },
        sort_keys=True,
    )


def _farmers_market_source_id(row: pd.Series) -> str:
    parts = [
        _first_present_value(row, ("year",)),
        _first_present_value(row, ("marketname",)),
        _first_present_value(row, ("streetaddress",)),
    ]
    return ":".join(part for part in parts if part) or str(row.name)


def _farmers_market_name(row: pd.Series) -> str:
    return _first_present_value(row, ("marketname", "name")) or "Farmers Market"


def _farmers_market_address(row: pd.Series) -> str:
    parts = [
        _first_present_value(row, ("streetaddress",)),
        _first_present_value(row, ("borough",)),
    ]
    return " ".join(part for part in parts if part)


def _farmers_market_subcategory(row: pd.Series) -> str:
    if _bool_or_none(_first_present_value(row, ("open_year_round",))) is True:
        return "year_round"
    return "seasonal"


def _farmers_market_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "accepts_ebt": _bool_or_none(_first_present_value(row, ("accepts_ebt",))),
            "borough": _first_present_value(row, ("borough",)) or None,
            "days_operation": _first_present_value(row, ("daysoperation",)) or None,
            "hours_operations": _first_present_value(row, ("hoursoperations",)) or None,
            "open_year_round": _bool_or_none(_first_present_value(row, ("open_year_round",))),
            "year": _first_present_value(row, ("year",)) or None,
        },
        sort_keys=True,
    )


def _is_general_hospital(row: pd.Series) -> bool:
    factype = _first_present_value(row, ("factype",)).upper()
    if factype not in HOSPITAL_FACTYPES:
        return False
    facsubgrp = _first_present_value(row, ("facsubgrp",)).upper()
    return facsubgrp == "HOSPITALS AND CLINICS"


def _facility_source_id(row: pd.Series) -> str:
    return _first_present_value(row, ("uid", "bin", "bbl", "facname")) or str(row.name)


def _facility_name(row: pd.Series) -> str:
    return _first_present_value(row, ("facname", "opname")) or "Hospital"


def _facility_address(row: pd.Series) -> str:
    parts = [
        _first_present_value(row, ("address",)),
        _first_present_value(row, ("city",)),
        _first_present_value(row, ("zipcode",)),
    ]
    return " ".join(part for part in parts if part)


def _facility_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "facility_domain": _first_present_value(row, ("facdomain",)) or None,
            "facility_group": _first_present_value(row, ("facgroup",)) or None,
            "facility_subgroup": _first_present_value(row, ("facsubgrp",)) or None,
            "facility_type": _first_present_value(row, ("factype",)) or None,
            "operator": _first_present_value(row, ("opname",)) or None,
            "oversight_agency": _first_present_value(row, ("overagency",)) or None,
        },
        sort_keys=True,
    )


def _landmark_source_id(row: pd.Series) -> str:
    return _first_present_value(row, ("lpc_lpnumb", "objectid", "bbl", "lpc_name")) or str(row.name)


def _landmark_name(row: pd.Series) -> str:
    return _first_present_value(row, ("lpc_name", "name")) or (
        f"Landmark {row.get('source_id_value', row.name)}"
    )


def _landmark_address(row: pd.Series) -> str:
    return _first_present_value(row, ("address", "lpc_sitede"))


def _landmark_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "alternate_name": _first_present_value(row, ("lpc_altern",)) or None,
            "bbl": _first_present_value(row, ("bbl",)) or None,
            "borough": _first_present_value(row, ("borough",)) or None,
            "designation_date": _first_present_value(row, ("desdate",)) or None,
            "landmark_type": _first_present_value(row, ("landmarkty",)) or None,
            "lpc_number": _first_present_value(row, ("lpc_lpnumb",)) or None,
            "report_url": _first_present_value(row, ("url_report",)) or None,
            "site_status": _first_present_value(row, ("lpc_sitest",)) or None,
        },
        sort_keys=True,
    )


def _historic_district_source_id(row: pd.Series) -> str:
    return _first_present_value(row, ("lp_number", "area_name", "objectid")) or str(row.name)


def _historic_district_name(row: pd.Series) -> str:
    return _first_present_value(row, ("area_name", "name")) or (
        f"Historic district {row.get('source_id_value', row.name)}"
    )


def _historic_district_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "borough": _first_present_value(row, ("borough",)) or None,
            "calendar_date": _first_present_value(row, ("caldate",)) or None,
            "current": _first_present_value(row, ("current_", "current")) or None,
            "designation_date": _first_present_value(row, ("desdate",)) or None,
            "extension": _first_present_value(row, ("extension",)) or None,
            "lp_number": _first_present_value(row, ("lp_number",)) or None,
            "status": _first_present_value(row, ("status_of_", "last_actio")) or None,
        },
        sort_keys=True,
    )


def _is_dcla_museum(row: pd.Series) -> bool:
    discipline = _first_present_value(row, ("discipline",)).upper()
    return discipline in DCLA_MUSEUM_DISCIPLINES


def _dcla_source_id(row: pd.Series) -> str:
    return _first_present_value(row, ("bin", "bbl", "organization_name")) or str(row.name)


def _dcla_name(row: pd.Series) -> str:
    return _first_present_value(row, ("organization_name", "name")) or (
        f"DCLA institution {row.get('source_id_value', row.name)}"
    )


def _dcla_address(row: pd.Series) -> str:
    parts = [
        _first_present_value(row, ("address",)),
        _first_present_value(row, ("city",)),
        _first_present_value(row, ("state",)),
        _first_present_value(row, ("postcode", "zip")),
    ]
    return " ".join(part for part in parts if part)


def _dcla_museum_subcategory(row: pd.Series) -> str:
    discipline = _first_present_value(row, ("discipline",)).lower()
    return discipline.replace("/", "_").replace(" ", "_")


def _dcla_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "bbl": _first_present_value(row, ("bbl",)) or None,
            "bin": _first_present_value(row, ("bin",)) or None,
            "borough": _first_present_value(row, ("borough",)) or None,
            "community_board": _first_present_value(row, ("community_board",)) or None,
            "council_district": _first_present_value(row, ("council_district",)) or None,
            "discipline": _first_present_value(row, ("discipline",)) or None,
            "main_phone": _first_present_value(row, ("main_phone",)) or None,
            "nta": _first_present_value(row, ("nta",)) or None,
        },
        sort_keys=True,
    )


def _public_art_source_id(row: pd.Series) -> str:
    parts = [
        _first_present_value(row, ("title",)),
        _first_present_value(row, ("location_name", "address")),
        str(_lat_value(row) or ""),
        str(_lon_value(row) or ""),
    ]
    return ":".join(part for part in parts if part) or str(row.name)


def _public_art_name(row: pd.Series) -> str:
    return _first_present_value(row, ("title", "name")) or (
        f"Public art {row.get('source_id_value', row.name)}"
    )


def _public_art_address(row: pd.Series) -> str:
    parts = [
        _first_present_value(row, ("location_name",)),
        _first_present_value(row, ("address",)),
        _first_present_value(row, ("city",)),
        _first_present_value(row, ("zip_code", "postcode")),
    ]
    return " ".join(part for part in parts if part)


def _public_art_attributes(row: pd.Series) -> str:
    artist_parts = [
        _first_present_value(row, ("primary_artist_first",)),
        _first_present_value(row, ("primary_artist_middle",)),
        _first_present_value(row, ("primary_artist_last",)),
    ]
    artist = " ".join(part for part in artist_parts if part and part.upper() != "NULL")
    return json.dumps(
        {
            "acquisition": _nullish_to_none(_first_present_value(row, ("acquisition",))),
            "artist": artist or None,
            "artwork_type1": _nullish_to_none(_first_present_value(row, ("artwork_type1",))),
            "artwork_type2": _nullish_to_none(_first_present_value(row, ("artwork_type2",))),
            "borough": _nullish_to_none(_first_present_value(row, ("borough",))),
            "date_created": _nullish_to_none(_first_present_value(row, ("date_created",))),
            "date_dedicated": _nullish_to_none(_first_present_value(row, ("date_dedicated",))),
            "location_name": _nullish_to_none(_first_present_value(row, ("location_name",))),
            "managing_city_agency": _nullish_to_none(
                _first_present_value(row, ("managing_city_agency",))
            ),
            "material": _nullish_to_none(_first_present_value(row, ("material",))),
        },
        sort_keys=True,
    )


def _bike_lane_source_id(row: pd.Series) -> str:
    for column in ("segmentid", "segment_id", "objectid", "id"):
        value = row.get(column)
        if pd.notna(value) and str(value):
            return str(value)
    return str(row.name)


def _bike_lane_name(row: pd.Series) -> str:
    route_name = _first_present_value(row, _route_name_candidates())
    return route_name or f"Bike lane {row.get('source_id_value', row.name)}"


def _bike_lane_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "route_name": _first_present_value(row, _route_name_candidates()) or None,
            "facility_type": _first_present_value(row, _facility_candidates()) or None,
            "segment_id": _bike_lane_source_id(row),
        },
        sort_keys=True,
    )


def _park_source_id(row: pd.Series) -> str:
    for column in ("gispropnum", "gis_prop_num", "propnum", "objectid", "globalid", "id"):
        value = row.get(column)
        if pd.notna(value) and str(value).strip():
            return str(value).strip()
    return str(row.name)


def _park_name(row: pd.Series) -> str:
    name = _first_present_value(row, ("signname", "parkname", "name", "name311"))
    return name or f"Park {row.get('source_id_value', row.name)}"


def _park_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "gispropnum": _first_present_value(
                row,
                ("gispropnum", "gis_prop_num", "propnum"),
            )
            or None,
            "acres": _numeric_or_none(_first_present_value(row, ("acres", "gisacres"))),
            "typecategory": row.get("typecategory_value") or None,
        },
        sort_keys=True,
    )


def _dog_run_source_id(row: pd.Series) -> str:
    for column in ("dogrun_id", "dog_run_id", "objectid", "globalid", "gispropnum", "id"):
        value = row.get(column)
        if pd.notna(value) and str(value).strip():
            return str(value).strip()
    prop_id = _first_present_value(row, ("prop_id", "propid", "gispropnum"))
    name = _dog_run_name(row)
    if prop_id or name:
        return f"{prop_id}:{name}".strip(":")
    return str(row.name)


def _dog_run_name(row: pd.Series) -> str:
    name = _first_present_value(
        row,
        ("name", "dog_run_name", "dogrunname", "dog_run", "site_name", "signname"),
    )
    return name or f"Dog run {row.get('source_id_value', row.name)}"


def _dog_run_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "on_leash": _bool_or_none(
                _first_present_value(row, ("on_leash", "onleash", "leash_status"))
            ),
            "fenced": _bool_or_none(_first_present_value(row, ("fenced", "is_fenced"))),
            "gispropnum": _first_present_value(
                row,
                ("gispropnum", "gis_prop_num", "prop_id", "propid"),
            )
            or None,
        },
        sort_keys=True,
    )


def _playground_source_id(row: pd.Series) -> str:
    for column in (
        "playground_id",
        "playarea_id",
        "objectid",
        "globalid",
        "gispropnum",
        "id",
    ):
        value = row.get(column)
        if pd.notna(value) and str(value).strip():
            return str(value).strip()
    prop_id = _first_present_value(row, ("prop_id", "propid", "gispropnum"))
    name = _playground_name(row)
    if prop_id or name:
        return f"{prop_id}:{name}".strip(":")
    return str(row.name)


def _playground_name(row: pd.Series) -> str:
    name = _first_present_value(
        row,
        ("name", "name311", "playground_name", "playarea_name", "site_name", "signname"),
    )
    return name or f"Playground {row.get('source_id_value', row.name)}"


def _playground_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "gispropnum": _first_present_value(
                row,
                ("gispropnum", "gis_prop_num", "prop_id", "propid"),
            )
            or None,
            "type": _first_present_value(
                row,
                ("type", "asset_type", "play_area_type", "category"),
            )
            or None,
        },
        sort_keys=True,
    )


def _is_nyc_retail_food_store(row: pd.Series) -> bool:
    county = str(row.get("county", "")).strip().upper()
    if county in NYC_COUNTIES:
        return True
    city = str(row.get("city", "")).strip().upper()
    return city in {"BRONX", "BROOKLYN", "NEW YORK", "STATEN ISLAND"}


def _is_supermarket_baseline(row: pd.Series) -> bool:
    name = f"{row.get('dba_name', '')} {row.get('entity_name', '')}".upper()
    square_footage = _numeric_or_none(row.get("square_footage"))
    has_supermarket_name = any(pattern in name for pattern in SUPERMARKET_NAME_PATTERNS)
    is_large_store = square_footage is not None and square_footage >= 5000
    is_excluded = any(pattern in name for pattern in SUPERMARKET_EXCLUDE_PATTERNS)
    return (has_supermarket_name or is_large_store) and not is_excluded


def _grocery_source_id(row: pd.Series) -> str:
    return _first_present_value(row, ("license_number", "entity_name", "dba_name")) or str(row.name)


def _grocery_name(row: pd.Series) -> str:
    return _first_present_value(row, ("dba_name", "entity_name")) or (
        f"Grocery store {row.get('source_id_value', row.name)}"
    )


def _grocery_address(row: pd.Series) -> str:
    parts = [
        _first_present_value(row, ("street_number",)),
        _first_present_value(row, ("street_name",)),
        _first_present_value(row, ("address_line_2",)),
        _first_present_value(row, ("city",)),
        _first_present_value(row, ("state",)),
        _first_present_value(row, ("zip_code",)),
    ]
    return " ".join(part for part in parts if part)


def _grocery_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "county": _first_present_value(row, ("county",)) or None,
            "estab_type": _first_present_value(row, ("estab_type",)) or None,
            "license_number": _first_present_value(row, ("license_number",)) or None,
            "operation_type": _first_present_value(row, ("operation_type",)) or None,
            "square_footage": _numeric_or_none(row.get("square_footage")),
        },
        sort_keys=True,
    )


def _load_dcwp_businesses(
    snapshot_path: str | Path,
    category: str,
    legacy_industry_code: str,
    current_category_allowlist: tuple[str, ...],
    name_patterns: tuple[str, ...],
) -> pd.DataFrame:
    licenses = _read_json_records(snapshot_path)
    if licenses.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    licenses = licenses.loc[licenses.apply(_is_dcwp_category_match, axis=1, args=(
        legacy_industry_code,
        current_category_allowlist,
        name_patterns,
    ))].copy()
    licenses = licenses.loc[licenses.apply(_is_active_dcwp_license, axis=1)].copy()
    licenses = licenses.loc[licenses.apply(_has_valid_lat_lon, axis=1)].copy()
    if licenses.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    licenses["source_id_value"] = licenses.apply(_dcwp_source_id, axis=1)
    licenses["name_value"] = licenses.apply(_dcwp_name, axis=1)
    licenses = licenses.drop_duplicates(subset=["source_id_value"])

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_NYC_OPEN_DATA,
            "source_id": category + ":" + licenses["source_id_value"].astype(str),
            "category": category,
            "subcategory": licenses.apply(_dcwp_subcategory, axis=1),
            "name": licenses["name_value"],
            "address": licenses.apply(_dcwp_address, axis=1),
            "lat": licenses.apply(_lat_value, axis=1),
            "lon": licenses.apply(_lon_value, axis=1),
            "attributes": licenses.apply(_dcwp_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def _is_dcwp_category_match(
    row: pd.Series,
    legacy_industry_code: str,
    current_category_allowlist: tuple[str, ...],
    name_patterns: tuple[str, ...],
) -> bool:
    industry_code = _first_present_value(row, ("industry", "industry_code"))
    if industry_code == legacy_industry_code:
        return True

    business_category = _first_present_value(row, ("business_category", "industry_description"))
    if business_category.upper() in current_category_allowlist:
        name = f"{row.get('dba_trade_name', '')} {row.get('business_name', '')}".upper()
        return any(pattern in name for pattern in name_patterns)
    return False


def _is_active_dcwp_license(row: pd.Series) -> bool:
    status = _first_present_value(row, ("license_status", "status"))
    if not status:
        return True
    return status.upper() in DCWP_ACTIVE_STATUSES


def _dcwp_source_id(row: pd.Series) -> str:
    candidates = ("license_nbr", "license_number", "business_unique_id")
    return _first_present_value(row, candidates) or str(row.name)


def _dcwp_name(row: pd.Series) -> str:
    return _first_present_value(row, ("dba_trade_name", "business_name")) or (
        f"DCWP business {row.get('source_id_value', row.name)}"
    )


def _dcwp_subcategory(row: pd.Series) -> str:
    return _first_present_value(row, ("business_category", "industry_description", "industry"))


def _dcwp_address(row: pd.Series) -> str:
    parts = [
        _first_present_value(row, ("address_building", "building")),
        _first_present_value(row, ("address_street_name", "street")),
        _first_present_value(row, ("address_city", "city")),
        _first_present_value(row, ("address_state", "state")),
        _first_present_value(row, ("address_zip", "zip")),
    ]
    return " ".join(part for part in parts if part)


def _dcwp_attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "business_category": _first_present_value(row, ("business_category",)) or None,
            "business_unique_id": _first_present_value(row, ("business_unique_id",)) or None,
            "license_expiration_date": _first_present_value(row, ("lic_expir_dd",)) or None,
            "license_status": _first_present_value(row, ("license_status",)) or None,
            "license_type": _first_present_value(row, ("license_type",)) or None,
        },
        sort_keys=True,
    )


def _has_valid_lat_lon(row: pd.Series) -> bool:
    lat = _lat_value(row)
    lon = _lon_value(row)
    return lat is not None and lon is not None and lat != 0 and lon != 0


def _has_valid_point(row: pd.Series) -> bool:
    lat = _point_lat_value(row)
    lon = _point_lon_value(row)
    return lat is not None and lon is not None and lat != 0 and lon != 0


def _lat_value(row: pd.Series) -> float | None:
    value = row.get("latitude")
    if value is not None and str(value).strip():
        return _numeric_or_none(value)
    point = (
        row.get("georeference")
        or row.get("location")
        or row.get("location_1")
        or row.get("the_geom")
    )
    if isinstance(point, dict):
        latitude = point.get("latitude")
        if latitude is not None and str(latitude).strip():
            return _numeric_or_none(latitude)
        coordinates = point.get("coordinates")
        if isinstance(coordinates, list) and len(coordinates) >= 2:
            return _numeric_or_none(coordinates[1])
    return None


def _lon_value(row: pd.Series) -> float | None:
    value = row.get("longitude")
    if value is not None and str(value).strip():
        return _numeric_or_none(value)
    point = (
        row.get("georeference")
        or row.get("location")
        or row.get("location_1")
        or row.get("the_geom")
    )
    if isinstance(point, dict):
        longitude = point.get("longitude")
        if longitude is not None and str(longitude).strip():
            return _numeric_or_none(longitude)
        coordinates = point.get("coordinates")
        if isinstance(coordinates, list) and len(coordinates) >= 2:
            return _numeric_or_none(coordinates[0])
    return None


def _point_lat_value(row: pd.Series) -> float | None:
    return _lat_value(row)


def _point_lon_value(row: pd.Series) -> float | None:
    return _lon_value(row)


def _first_present_value(row: pd.Series, candidates: tuple[str, ...]) -> str:
    for column in candidates:
        value = row.get(column)
        if pd.notna(value) and str(value).strip():
            return str(value).strip()
    return ""


def _address_value(row: pd.Series) -> str:
    return _first_present_value(
        row,
        (
            "address",
            "location",
            "location_description",
            "cross_streets",
            "streetname",
        ),
    )


def _numeric_or_none(value: object) -> float | None:
    if value is None or not str(value).strip():
        return None
    cleaned = str(value).strip().replace(",", "")
    numeric = pd.to_numeric(cleaned, errors="coerce")
    if pd.isna(numeric):
        return None
    return float(numeric)


def _nullish_to_none(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() in {"NULL", "N/A", "NA", "NONE"}:
        return None
    return text


def _bool_or_none(value: object) -> bool | None:
    if value is None or not str(value).strip():
        return None
    normalized = str(value).strip().lower()
    if normalized in {"true", "t", "yes", "y", "1"}:
        return True
    if normalized in {"false", "f", "no", "n", "0"}:
        return False
    return None


def _route_name_candidates() -> tuple[str, ...]:
    return ("street", "stname_lab", "streetname", "route_name", "name", "boro")


def _facility_candidates() -> tuple[str, ...]:
    return ("facilitycl", "facility_class", "facility_type", "tf_facilit", "bikedir")
