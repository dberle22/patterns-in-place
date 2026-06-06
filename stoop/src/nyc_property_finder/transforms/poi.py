"""POI parsing and normalization helpers."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from hashlib import sha256
from pathlib import Path
from urllib.parse import unquote

import pandas as pd


DEFAULT_KEYWORD_TAXONOMY_RULES = {
    # Food & Drink — specific first to avoid false matches on broad terms
    "pizza": {"category": "restaurants", "subcategory": "pizza", "keywords": ["pizza"]},
    "bakeries": {
        "category": "bakeries",
        "subcategory": "bakeries",
        "keywords": ["bakery", "pastry", "patisserie"],
    },
    "sandwiches": {"category": "restaurants", "subcategory": "sandwiches", "keywords": ["sandwich"]},
    "coffee_shops": {
        "category": "coffee_shops",
        "subcategory": "coffee_shops",
        "keywords": ["coffee", "cafe", "espresso"],
    },
    "chinese_cuisine": {
        "category": "restaurants",
        "subcategory": "chinese",
        "keywords": ["chinese", "dim sum", "cantonese"],
    },
    "japanese_cuisine": {
        "category": "restaurants",
        "subcategory": "japanese",
        "keywords": ["japanese", "sushi", "ramen", "izakaya"],
    },
    "specialty_grocery": {
        "category": "specialty_grocery",
        "subcategory": "specialty_grocery",
        "keywords": ["speciality", "specialty", "gourmet"],
    },
    # food_markets before groceries — both can match "market"
    "food_markets": {
        "category": "food_markets",
        "subcategory": "food_markets",
        "keywords": ["market", "food hall"],
    },
    "restaurants": {"category": "restaurants", "subcategory": "restaurants", "keywords": ["restaurant", "diner", "food"]},
    "bars": {"category": "bars", "subcategory": "bars", "keywords": ["bar", "brewery", "pub", "cocktail"]},
    # Culture & Entertainment
    "bookstores": {"category": "bookstores", "subcategory": "bookstores", "keywords": ["bookstore", "books"]},
    "record_stores": {"category": "record_stores", "subcategory": "record_stores", "keywords": ["record", "vinyl"]},
    "museums": {"category": "museums", "subcategory": "museums", "keywords": ["museum", "gallery"]},
    "movie_theaters": {
        "category": "movie_theaters",
        "subcategory": "movie_theaters",
        "keywords": ["cinema", "movie", "theater"],
    },
    "music_venues": {
        "category": "music_venues",
        "subcategory": "music_venues",
        "keywords": ["venue", "concert", "music", "jazz"],
    },
    # Everyday & Outdoor
    "groceries": {"category": "groceries", "subcategory": "groceries", "keywords": ["grocery", "supermarket"]},
    "shopping": {"category": "shopping", "subcategory": "shopping", "keywords": ["shop", "store", "mall"]},
    "parks": {"category": "parks", "subcategory": "parks", "keywords": ["park", "garden", "playground"]},
}


def infer_taxonomy_from_text(
    text: str,
    keyword_taxonomy_rules: dict[str, object] | None = None,
) -> dict[str, str]:
    """Infer a category/subcategory pair from free text using ordered rules."""

    rules = _coerce_keyword_taxonomy_rules(keyword_taxonomy_rules)
    clean_text = str(text).lower()
    for rule in rules.values():
        keywords = rule.get("keywords", [])
        if any(keyword in clean_text for keyword in keywords):
            return {
                "category": str(rule.get("category", "")).strip() or "other",
                "subcategory": str(rule.get("subcategory", "")).strip(),
            }
    return {"category": "other", "subcategory": ""}


def normalize_category(name: str, category_keywords: dict[str, object] | None = None) -> str:
    """Map a place name into a coarse category."""

    return infer_taxonomy_from_text(name, category_keywords)["category"]


def category_from_list_name(list_name: str, category_keywords: dict[str, object] | None = None) -> str:
    """Map a Google Maps list name into a coarse POI category."""

    clean_name = list_name.lower().replace("new york - ", "").replace("nyc", "")
    return infer_taxonomy_from_text(clean_name, category_keywords)["category"]


def parse_google_maps_csv(path: str | Path) -> pd.DataFrame:
    """Parse a Google Maps saved-list CSV with title/link records."""

    path = Path(path)
    rows = pd.read_csv(path, comment=None, skip_blank_lines=True)
    if "Title" not in rows.columns:
        rows = pd.read_csv(path, skiprows=1, skip_blank_lines=True)

    if "Title" not in rows.columns:
        raise ValueError(f"Google Maps CSV missing Title column: {path}")

    source_list_name = path.stem
    output = rows.rename(columns={"Title": "name", "URL": "url", "Note": "note"}).copy()
    output["source_list_name"] = source_list_name
    output["name"] = output["name"].fillna("").astype(str).str.strip()
    output = output[output["name"] != ""].copy()
    if "url" not in output.columns:
        output["url"] = ""
    output["url"] = output["url"].fillna("").astype(str).map(unquote)
    output["lat"] = pd.NA
    output["lon"] = pd.NA
    return output[["name", "source_list_name", "url", "lat", "lon"]]


def parse_google_maps_json(path: str | Path) -> pd.DataFrame:
    """Parse a minimal Google Maps JSON export.

    Google exports vary by product/version, so this accepts either a list of
    places or a mapping with a ``places`` key.
    """

    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)

    places = data.get("places", data) if isinstance(data, dict) else data
    rows: list[dict[str, object]] = []
    for place in places:
        location = place.get("location", {})
        lat = place.get("lat", location.get("lat"))
        lon = place.get("lon", place.get("lng", location.get("lng")))
        rows.append(
            {
                "name": place.get("name", ""),
                "source_list_name": place.get("list_name", place.get("source_list_name", "google_maps")),
                "lat": lat,
                "lon": lon,
            }
        )
    return pd.DataFrame(rows)


def parse_google_maps_kml(path: str | Path) -> pd.DataFrame:
    """Parse placemarks from a KML file."""

    tree = ET.parse(path)
    root = tree.getroot()
    namespace_match = re.match(r"\{.*\}", root.tag)
    namespace = namespace_match.group(0) if namespace_match else ""
    rows: list[dict[str, object]] = []

    for placemark in root.iter(f"{namespace}Placemark"):
        name_node = placemark.find(f"{namespace}name")
        coordinates_node = placemark.find(f".//{namespace}coordinates")
        if coordinates_node is None or not coordinates_node.text:
            continue
        lon, lat, *_ = coordinates_node.text.strip().split(",")
        rows.append(
            {
                "name": name_node.text if name_node is not None else "",
                "source_list_name": "google_maps",
                "lat": float(lat),
                "lon": float(lon),
            }
        )

    return pd.DataFrame(rows)


def normalize_poi_dataframe(
    dataframe: pd.DataFrame,
    category_keywords: dict[str, object] | None = None,
) -> pd.DataFrame:
    """Clean and categorize POI records."""

    output = dataframe.copy()
    output["name"] = output["name"].fillna("").astype(str).str.strip()
    output["source_list_name"] = output.get("source_list_name", "google_maps")
    output["source_list_name"] = output["source_list_name"].fillna("google_maps").astype(str).str.strip()
    output["lat"] = pd.to_numeric(output["lat"], errors="coerce")
    output["lon"] = pd.to_numeric(output["lon"], errors="coerce")
    output = output.dropna(subset=["lat", "lon"])
    def resolve_category(row: pd.Series) -> str:
        list_match = infer_taxonomy_from_text(row["source_list_name"], category_keywords)
        if list_match["category"] != "other":
            return list_match["category"]
        return infer_taxonomy_from_text(row["name"], category_keywords)["category"]

    output["category"] = output.apply(resolve_category, axis=1)
    output["poi_id"] = output.apply(
        lambda row: _stable_poi_id(row["name"], row["lat"], row["lon"]),
        axis=1,
    )
    return output[["poi_id", "name", "category", "source_list_name", "lat", "lon"]]


def _coerce_keyword_taxonomy_rules(
    keyword_taxonomy_rules: dict[str, object] | None,
) -> dict[str, dict[str, object]]:
    if not keyword_taxonomy_rules:
        return DEFAULT_KEYWORD_TAXONOMY_RULES

    normalized: dict[str, dict[str, object]] = {}
    for rule_name, raw_rule in keyword_taxonomy_rules.items():
        if isinstance(raw_rule, dict):
            keywords = raw_rule.get("keywords", [])
            normalized[rule_name] = {
                "category": str(raw_rule.get("category", "")).strip(),
                "subcategory": str(raw_rule.get("subcategory", "")).strip(),
                "keywords": [str(keyword).lower() for keyword in keywords if str(keyword).strip()],
            }
            continue
        if isinstance(raw_rule, list):
            # Backward compatibility for the old `categories:` config shape.
            normalized[rule_name] = {
                "category": str(rule_name).strip(),
                "subcategory": str(rule_name).strip(),
                "keywords": [str(keyword).lower() for keyword in raw_rule if str(keyword).strip()],
            }
    return normalized or DEFAULT_KEYWORD_TAXONOMY_RULES


def _stable_poi_id(name: str, lat: float, lon: float) -> str:
    """Generate a deterministic POI id."""

    key = f"{name.strip().lower()}|{round(lat, 6)}|{round(lon, 6)}"
    return f"poi_{sha256(key.encode('utf-8')).hexdigest()[:16]}"
