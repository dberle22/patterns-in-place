"""Normalization helpers for curated POI web scraping."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from nyc_property_finder.curated_poi.web_scraping.base import (
    ScrapedArticleConfig,
    ScrapedArticleRow,
    normalize_article_rows,
)


NORMALIZED_SCRAPE_COLUMNS = [
    "source_record_id",
    "source_system",
    "source_file",
    "publisher",
    "article_slug",
    "article_title",
    "article_url",
    "source_list_name",
    "capture_mode",
    "parser_name",
    "category",
    "subcategory",
    "detail_level_3",
    "item_rank",
    "item_name",
    "item_url",
    "raw_address",
    "raw_description",
    "raw_neighborhood",
    "raw_borough",
    "scraped_at",
    "input_title",
    "note",
    "tags",
    "comment",
    "source_url",
    "search_query",
]


def build_normalized_scrape_dataframe(
    article: ScrapedArticleConfig,
    rows: list[ScrapedArticleRow],
    source_file: str = "",
    scraped_at: datetime | None = None,
) -> pd.DataFrame:
    """Build a reviewable normalized CSV dataframe for one scraped article."""

    normalized = normalize_article_rows(
        article=article,
        rows=rows,
        source_file=source_file,
        scraped_at=scraped_at,
    )
    return pd.DataFrame([row.to_dict() for row in normalized], columns=NORMALIZED_SCRAPE_COLUMNS)


def write_normalized_scrape_csv(frame: pd.DataFrame, path: str | Path) -> Path:
    """Persist one normalized scrape dataframe."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return output_path


def read_normalized_scrape_csv(path: str | Path) -> pd.DataFrame:
    """Read one normalized scrape CSV back into the shared contract."""

    frame = pd.read_csv(path, dtype=str).fillna("")
    for column in NORMALIZED_SCRAPE_COLUMNS:
        if column not in frame.columns:
            frame[column] = ""
    return frame[NORMALIZED_SCRAPE_COLUMNS]
