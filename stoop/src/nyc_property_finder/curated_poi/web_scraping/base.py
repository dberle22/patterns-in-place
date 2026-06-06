"""Shared contracts for curated POI web scraping."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
import re
from typing import Any


DEFAULT_SEARCH_CONTEXT = "New York, NY"


@dataclass(frozen=True)
class ScrapedArticleConfig:
    """Locked metadata for one curated article source."""

    publisher: str
    article_slug: str
    article_title: str
    article_url: str
    source_list_name: str
    category: str
    subcategory: str
    detail_level_3: str = ""
    capture_mode: str = "parser"
    parser_name: str = ""
    status: str = "planned"
    semi_manual_hints: dict[str, Any] | None = None


@dataclass(frozen=True)
class ScrapedArticleRow:
    """One pre-normalized place mention extracted from article content."""

    item_name: str
    item_rank: int | None = None
    item_url: str = ""
    raw_address: str = ""
    raw_description: str = ""
    raw_neighborhood: str = ""
    raw_borough: str = ""


@dataclass(frozen=True)
class NormalizedScrapedRow:
    """Normalized scrape row ready for QA review and later resolve steps."""

    source_record_id: str
    source_system: str
    source_file: str
    publisher: str
    article_slug: str
    article_title: str
    article_url: str
    source_list_name: str
    capture_mode: str
    parser_name: str
    category: str
    subcategory: str
    detail_level_3: str
    item_rank: int | None
    item_name: str
    item_url: str
    raw_address: str
    raw_description: str
    raw_neighborhood: str
    raw_borough: str
    scraped_at: str
    input_title: str
    note: str
    tags: str
    comment: str
    source_url: str
    search_query: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def normalized_output_path(
    article: ScrapedArticleConfig,
    run_date: str,
    root_dir: str | Path = "data/raw/scraped/normalized",
) -> Path:
    """Build the conventional normalized scrape CSV path."""

    filename = (
        f"{_slugify(article.category)}_{_slugify(article.publisher)}_"
        f"{article.article_slug}_{run_date}.csv"
    )
    return Path(root_dir) / filename


def build_search_query(
    title: str,
    raw_address: str = "",
    raw_neighborhood: str = "",
    search_context: str = DEFAULT_SEARCH_CONTEXT,
) -> str:
    """Build a Places search query for one scraped source row."""

    clean_address = " ".join(str(raw_address).split())
    clean_neighborhood = " ".join(str(raw_neighborhood).split())
    parts = [
        " ".join(str(title).split()),
        clean_address,
        clean_neighborhood if not clean_address else "",
        " ".join(str(search_context).split()),
    ]
    return " ".join(part for part in parts if part).strip()


def build_source_record_id(article: ScrapedArticleConfig, row: ScrapedArticleRow) -> str:
    """Create a stable source-row ID before Places resolution exists."""

    key = "|".join(
        [
            article.publisher.strip().lower(),
            article.article_slug.strip().lower(),
            article.article_url.strip(),
            row.item_name.strip().lower(),
            row.raw_address.strip().lower(),
        ]
    )
    return f"src_{sha256(key.encode('utf-8')).hexdigest()[:16]}"


def normalize_article_rows(
    article: ScrapedArticleConfig,
    rows: list[ScrapedArticleRow],
    source_file: str = "",
    scraped_at: datetime | None = None,
    search_context: str = DEFAULT_SEARCH_CONTEXT,
) -> list[NormalizedScrapedRow]:
    """Normalize publication-specific rows into the shared scrape contract."""

    timestamp = (scraped_at or datetime.now(UTC)).isoformat()
    normalized: list[NormalizedScrapedRow] = []
    for row in rows:
        clean_name = " ".join(str(row.item_name).split()).strip()
        clean_address = " ".join(str(row.raw_address).split()).strip(" ,;")
        clean_description = " ".join(str(row.raw_description).split()).strip()
        source_url = row.item_url or article.article_url
        normalized.append(
            NormalizedScrapedRow(
                source_record_id=build_source_record_id(article, row),
                source_system="web_scrape",
                source_file=source_file,
                publisher=article.publisher,
                article_slug=article.article_slug,
                article_title=article.article_title,
                article_url=article.article_url,
                source_list_name=article.source_list_name,
                capture_mode=article.capture_mode,
                parser_name=article.parser_name,
                category=article.category,
                subcategory=article.subcategory,
                detail_level_3=article.detail_level_3,
                item_rank=row.item_rank,
                item_name=clean_name,
                item_url=row.item_url,
                raw_address=clean_address,
                raw_description=clean_description,
                raw_neighborhood=" ".join(str(row.raw_neighborhood).split()).strip(),
                raw_borough=" ".join(str(row.raw_borough).split()).strip(),
                scraped_at=timestamp,
                input_title=clean_name,
                note=clean_address,
                tags="",
                comment=clean_description,
                source_url=source_url,
                search_query=build_search_query(
                    title=clean_name,
                    raw_address=clean_address,
                    raw_neighborhood=" ".join(str(row.raw_neighborhood).split()).strip(),
                    search_context=search_context,
                ),
            )
        )
    return normalized


def split_multi_location_address(raw_address: str) -> list[str]:
    """Split obvious multi-address strings into one row per location candidate."""

    value = " ".join(str(raw_address).split()).strip(" ,;")
    if not value:
        return [""]

    normalized = re.sub(r"\s+(?:and|&)\s+", " | ", value, flags=re.IGNORECASE)
    normalized = normalized.replace(";", " | ")
    parts = [part.strip(" ,;") for part in normalized.split("|")]
    deduped: list[str] = []
    for part in parts:
        if part and part not in deduped:
            deduped.append(part)
    return deduped or [value]


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower())
    return cleaned.strip("_")
