"""Google Takeout saved-list parsing for the Places POI workflow."""

from __future__ import annotations

from functools import lru_cache
import re
from hashlib import sha256
from pathlib import Path
from urllib.parse import unquote

import pandas as pd

from nyc_property_finder.curated_poi.google_takeout.config import DEFAULT_SEARCH_CONTEXT, SOURCE_SYSTEM
from nyc_property_finder.services.config import DEFAULT_CONFIG_DIR, load_yaml


TAKEOUT_COLUMNS = ("Title", "Note", "URL", "Tags", "Comment")


def parse_google_places_saved_list_csv(
    path: str | Path,
    search_context: str = DEFAULT_SEARCH_CONTEXT,
    source_list_name: str | None = None,
) -> pd.DataFrame:
    """Parse one Google Takeout saved-list CSV for the v2 Places pipeline."""

    path = Path(path)
    rows = _read_takeout_csv(path)
    source_list_name = source_list_name or path.stem

    # Takeout exports can omit user-metadata columns when they are empty. Add
    # them here so downstream pipeline steps always see the same contract.
    for column in TAKEOUT_COLUMNS:
        if column not in rows.columns:
            rows[column] = ""

    output = rows.loc[:, TAKEOUT_COLUMNS].copy()
    output["input_title"] = output["Title"].fillna("").astype(str).str.strip()
    # Google includes a blank example-looking row in some CSV exports; skip it
    # before creating stable source IDs.
    output = output[output["input_title"] != ""].copy()
    output["source_url"] = output["URL"].fillna("").astype(str).map(lambda value: unquote(value.strip()))
    output["note"] = output["Note"].fillna("").astype(str).str.strip()
    output["tags"] = output["Tags"].fillna("").astype(str).str.strip()
    output["comment"] = output["Comment"].fillna("").astype(str).str.strip()
    output["source_system"] = SOURCE_SYSTEM
    output["source_file"] = path.name
    output["source_list_name"] = source_list_name
    taxonomy = output.apply(
        lambda row: pd.Series(
            normalize_curated_taxonomy(
                source_file=path.name,
                source_list_name=source_list_name,
                tags=row["tags"],
                comment=row["comment"],
            )
        ),
        axis=1,
    )
    output = pd.concat([output, taxonomy], axis=1)
    output["search_query"] = output["input_title"].map(lambda title: build_search_query(title, search_context))
    output["source_record_id"] = output.apply(
        lambda row: _stable_source_record_id(
            source_system=row["source_system"],
            source_file=row["source_file"],
            source_list_name=row["source_list_name"],
            input_title=row["input_title"],
            source_url=row["source_url"],
        ),
        axis=1,
    )
    return output[
        [
            "source_record_id",
            "source_system",
            "source_file",
            "source_list_name",
            "category",
            "subcategory",
            "detail_level_3",
            "input_title",
            "note",
            "tags",
            "comment",
            "source_url",
            "search_query",
        ]
    ]


def build_search_query(
    title: str,
    search_context: str = DEFAULT_SEARCH_CONTEXT,
    address: str = "",
) -> str:
    """Build the first-pass text search query.

    When a source provides an exact address, prefer it because it materially
    improves match quality for multi-location brands and later scrape/manual
    ingestion paths.
    """

    title = " ".join(str(title).split())
    address = " ".join(str(address).split())
    search_context = " ".join(str(search_context).split())
    query_parts = [part for part in (title, address, search_context) if part]
    return " ".join(query_parts).strip()


def clean_list_category(list_name: str) -> str:
    """Convert a saved-list name into an initial category token."""

    cleaned = str(list_name).strip().lower()
    cleaned = re.sub(r"^new york\s*-\s*", "", cleaned)
    cleaned = re.sub(r"\bnyc\b", "", cleaned)
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    cleaned = cleaned.strip("_")
    return cleaned or "other"


def normalize_curated_taxonomy(
    source_file: str,
    source_list_name: str,
    tags: str = "",
    comment: str = "",
) -> dict[str, str]:
    """Assign category hierarchy for one curated source row."""

    taxonomy_config = _curated_taxonomy_config()
    file_rules = taxonomy_config.get("files", {})
    rule = file_rules.get(str(source_file).strip(), {})
    category = str(rule.get("category", "")).strip()
    subcategory = str(rule.get("subcategory", "")).strip()
    detail_level_3_tokens = _taxonomy_tokens(str(rule.get("detail_level_3", "")).strip())

    if not category:
        category = clean_list_category(source_list_name)

    tag_aliases = _taxonomy_tag_aliases(tags=tags, comment=comment)
    if rule.get("subcategory_from_tags_or_comment") and tag_aliases:
        subcategory = tag_aliases[0]
    elif not subcategory:
        subcategory = category
    if rule.get("detail_level_3_from_tags_or_comment"):
        for alias in tag_aliases:
            if alias not in detail_level_3_tokens:
                detail_level_3_tokens.append(alias)

    return {
        "category": category or "other",
        "subcategory": subcategory or "",
        "detail_level_3": "|".join(detail_level_3_tokens),
    }


def _read_takeout_csv(path: Path) -> pd.DataFrame:
    # Some Google exports include a first descriptive line before the real CSV
    # header. Try the normal header first, then a one-line offset.
    rows = pd.read_csv(path, comment=None, skip_blank_lines=True)
    if "Title" not in rows.columns:
        rows = pd.read_csv(path, skiprows=1, skip_blank_lines=True)

    if "Title" not in rows.columns:
        raise ValueError(f"Google Maps CSV missing Title column: {path}")
    return rows


@lru_cache(maxsize=1)
def _curated_taxonomy_config() -> dict[str, object]:
    config = load_yaml(DEFAULT_CONFIG_DIR / "poi_categories.yaml")
    taxonomy = config.get("curated_taxonomy", {})
    return taxonomy if isinstance(taxonomy, dict) else {}


def _taxonomy_tag_aliases(tags: str, comment: str) -> list[str]:
    aliases = _curated_taxonomy_config().get("tag_aliases", {})
    if not isinstance(aliases, dict):
        return []

    resolved: list[str] = []
    for candidate in _taxonomy_tokens(tags) + _taxonomy_tokens(comment):
        alias = aliases.get(candidate)
        if isinstance(alias, str):
            alias = alias.strip()
            if alias and alias not in resolved:
                resolved.append(alias)
    return resolved


def _taxonomy_tokens(value: str) -> list[str]:
    tokens: list[str] = []
    for raw_token in re.split(r"[;,/|]", str(value).lower()):
        cleaned = re.sub(r"[^a-z0-9]+", "_", raw_token).strip("_")
        if cleaned and cleaned not in tokens:
            tokens.append(cleaned)
    return tokens


def _stable_source_record_id(
    source_system: str,
    source_file: str,
    source_list_name: str,
    input_title: str,
    source_url: str,
) -> str:
    # The source row ID is pre-Google matching identity. It lets dry runs and
    # caches recognize the same input row before a place_id exists.
    key = "|".join(
        [
            source_system.strip().lower(),
            source_file.strip().lower(),
            source_list_name.strip().lower(),
            input_title.strip().lower(),
            source_url.strip(),
        ]
    )
    return f"src_{sha256(key.encode('utf-8')).hexdigest()[:16]}"
