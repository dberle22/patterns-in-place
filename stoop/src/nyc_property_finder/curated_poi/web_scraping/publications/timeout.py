"""Time Out list-feature parser for curated POI article scraping."""

from __future__ import annotations

from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
import re
from urllib.parse import urljoin

from nyc_property_finder.curated_poi.web_scraping.base import ScrapedArticleConfig, ScrapedArticleRow


RANKED_TITLE_PATTERN = re.compile(r"^\s*(\d+)\.\s*(.+?)\s*$", re.DOTALL)


@dataclass
class _Tile:
    item_name: str = ""
    item_rank: int | None = None
    item_url: str = ""
    tags: list[str] = field(default_factory=list)
    description_parts: list[str] = field(default_factory=list)


class _TimeOutHTMLParser(HTMLParser):
    def __init__(self, article_url: str) -> None:
        super().__init__()
        self.article_url = article_url
        self.rows: list[ScrapedArticleRow] = []

        self._in_primary_zone = False
        self._primary_zone_seen = False
        self._zone_depth = 0

        self._current_tile: _Tile | None = None
        self._tile_depth = 0

        self._in_tile_title = False
        self._title_parts: list[str] = []
        self._current_tile_link = ""

        self._in_tag_section = False
        self._in_tag_item = False
        self._tag_parts: list[str] = []

        self._in_summary = False
        self._summary_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)

        if (
            not self._primary_zone_seen
            and tag == "div"
            and attrs_dict.get("data-zone-name") == "large_list"
            and attrs_dict.get("data-testid") == "zone-large-list_testID"
        ):
            self._in_primary_zone = True
            self._primary_zone_seen = True
            self._zone_depth = 1
            return

        if self._in_primary_zone and tag == "div":
            self._zone_depth += 1

        if not self._in_primary_zone:
            return

        if tag == "article" and attrs_dict.get("data-testid") == "tile-zone-large-list_testID":
            self._current_tile = _Tile()
            self._tile_depth = 1
            return

        if self._current_tile is None:
            return

        self._tile_depth += 1

        if tag == "a" and attrs_dict.get("data-testid") == "tile-link_testID" and not self._current_tile_link:
            href = (attrs_dict.get("href") or "").strip()
            if href:
                self._current_tile_link = urljoin(self.article_url, href)
            return

        if tag == "h3" and attrs_dict.get("data-testid") == "tile-title_testID":
            self._in_tile_title = True
            self._title_parts = []
            return

        if tag == "section" and attrs_dict.get("data-testid") == "tags_testID":
            self._in_tag_section = True
            return

        if self._in_tag_section and tag == "li":
            classes = set((attrs_dict.get("class") or "").split())
            if any(cls.startswith("_tag_") for cls in classes):
                self._in_tag_item = True
                self._tag_parts = []
            return

        if attrs_dict.get("data-testid") == "summary_testID":
            self._in_summary = True
            self._summary_parts = []

    def handle_endtag(self, tag: str) -> None:
        if not self._in_primary_zone:
            return

        if self._current_tile is not None:
            if self._in_tile_title and tag == "h3":
                self._commit_title()
                self._in_tile_title = False
                self._title_parts = []
                self._tile_depth = max(0, self._tile_depth - 1)
                return

            if self._in_tag_item and tag == "li":
                tag_text = _clean_text(" ".join(self._tag_parts))
                if tag_text:
                    self._current_tile.tags.append(tag_text)
                self._in_tag_item = False
                self._tag_parts = []
                self._tile_depth = max(0, self._tile_depth - 1)
                return

            if self._in_tag_section and tag == "section":
                self._in_tag_section = False
                self._tile_depth = max(0, self._tile_depth - 1)
                return

            if self._in_summary and tag == "div":
                description = _clean_text(" ".join(self._summary_parts))
                if description:
                    self._current_tile.description_parts.append(description)
                self._in_summary = False
                self._summary_parts = []
                self._tile_depth = max(0, self._tile_depth - 1)
                return

            if tag == "article":
                self._commit_tile()
                self._tile_depth = 0
                self._zone_depth = max(0, self._zone_depth - 1)
                return

            self._tile_depth = max(0, self._tile_depth - 1)

        if tag == "div":
            self._zone_depth -= 1
            if self._zone_depth <= 0:
                self._in_primary_zone = False
                self._zone_depth = 0

    def handle_data(self, data: str) -> None:
        if self._current_tile is None:
            return
        if self._in_tile_title:
            self._title_parts.append(data)
            return
        if self._in_tag_item:
            self._tag_parts.append(data)
            return
        if self._in_summary:
            self._summary_parts.append(data)

    def _commit_title(self) -> None:
        if self._current_tile is None:
            return
        title = _clean_text(" ".join(self._title_parts))
        if not title:
            return
        match = RANKED_TITLE_PATTERN.match(title)
        if match:
            self._current_tile.item_rank = int(match.group(1))
            self._current_tile.item_name = _clean_text(match.group(2))
            return
        self._current_tile.item_name = title

    def _commit_tile(self) -> None:
        if self._current_tile is None:
            return
        item_name = _clean_text(self._current_tile.item_name)
        if not item_name:
            self._current_tile = None
            return

        description = _clean_text(" ".join(self._current_tile.description_parts))
        tags = [_clean_text(tag) for tag in self._current_tile.tags if _clean_text(tag)]
        raw_neighborhood = tags[-1] if len(tags) >= 2 else ""
        self.rows.append(
            ScrapedArticleRow(
                item_name=item_name,
                item_rank=self._current_tile.item_rank,
                item_url=self._current_tile_link,
                raw_address="",
                raw_description=description,
                raw_neighborhood=raw_neighborhood,
                raw_borough="",
            )
        )
        self._current_tile = None
        self._current_tile_link = ""
        self._in_tile_title = False
        self._title_parts = []
        self._in_tag_section = False
        self._in_tag_item = False
        self._tag_parts = []
        self._in_summary = False
        self._summary_parts = []


def parse_article(html: str, article: ScrapedArticleConfig) -> list[ScrapedArticleRow]:
    """Parse one Time Out list-feature article into reviewable source rows."""

    parser = _TimeOutHTMLParser(article.article_url)
    parser.feed(html)
    parser.close()
    return parser.rows


def _clean_text(value: str) -> str:
    cleaned = unescape(" ".join(str(value).split()))
    return cleaned.strip(" ,;")
