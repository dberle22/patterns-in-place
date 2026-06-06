"""Eater map/list parser for curated POI article scraping."""

from __future__ import annotations

from dataclasses import dataclass, replace
from html import unescape
from html.parser import HTMLParser
import json
import re
from urllib.parse import urlparse

from nyc_property_finder.curated_poi.web_scraping.base import (
    ScrapedArticleConfig,
    ScrapedArticleRow,
    split_multi_location_address,
)


ADDRESS_LINE_PATTERN = re.compile(
    r"(?:Location|Address)\s+(.*?)(?=(?:Why we love it|Why it matters|What to order)\s*:|$)",
    re.IGNORECASE,
)
DESCRIPTION_LINE_PATTERN = re.compile(
    r"(?:Why we love it|Why it matters|What to order)\s*:?[\s-]*(.*?)(?=$)",
    re.IGNORECASE,
)
NEXT_DATA_PATTERN = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.DOTALL)


@dataclass
class _Section:
    title: str
    section_id: str
    text_parts: list[str]


class _EaterHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.jsonld_chunks: list[str] = []
        self._capture_jsonld = False
        self._current_heading_id = ""
        self._current_heading_text_parts: list[str] = []
        self._current_section: _Section | None = None
        self.sections: dict[str, dict[str, str]] = {}
        self._heading_depth = 0
        self._current_text_target: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "script" and attrs_dict.get("type") == "application/ld+json":
            self._capture_jsonld = True
            return

        if tag in {"h1", "h2", "h3", "h4"}:
            self._commit_open_heading()
            self._close_open_section()
            self._heading_depth += 1
            self._current_heading_id = (attrs_dict.get("id") or "").strip()
            self._current_heading_text_parts = []
            self._current_text_target = self._current_heading_text_parts
            return

        if tag == "p" and self._current_section is not None:
            self._current_text_target = self._current_section.text_parts

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._capture_jsonld:
            self._capture_jsonld = False
            return

        if tag in {"h1", "h2", "h3", "h4"} and self._heading_depth:
            self._heading_depth -= 1
            if self._heading_depth == 0:
                self._commit_open_heading()
            self._current_text_target = None
            return

        if tag == "p":
            self._current_text_target = None

    def handle_data(self, data: str) -> None:
        if self._capture_jsonld:
            self.jsonld_chunks.append(data)
            return
        if self._current_text_target is not None:
            cleaned = data.strip()
            if cleaned:
                self._current_text_target.append(cleaned)

    def close(self) -> None:
        super().close()
        self._commit_open_heading()
        self._close_open_section()

    def _commit_open_heading(self) -> None:
        if not self._current_heading_id:
            self._current_heading_text_parts = []
            return
        title = " ".join(self._current_heading_text_parts).strip()
        if not title:
            self._current_heading_id = ""
            self._current_heading_text_parts = []
            return
        self._current_section = _Section(title=title, section_id=self._current_heading_id, text_parts=[])
        self._current_heading_id = ""
        self._current_heading_text_parts = []

    def _close_open_section(self) -> None:
        if self._current_section is None:
            return
        section_text = " ".join(self._current_section.text_parts)
        section = {
            "title": self._current_section.title,
            "address": _extract_address(section_text),
            "description": _extract_description(section_text),
        }
        self.sections[self._current_section.section_id] = section
        self.sections.setdefault(_slugify(self._current_section.title), section)
        self._current_section = None


def parse_article(html: str, article: ScrapedArticleConfig) -> list[ScrapedArticleRow]:
    """Parse one Eater article into split, reviewable source rows."""

    parser = _EaterHTMLParser()
    parser.feed(html)
    parser.close()
    items = _extract_items_from_jsonld(parser.jsonld_chunks)
    next_data_sections = _extract_sections_from_next_data(html)
    rows: list[ScrapedArticleRow] = []

    for item in items:
        section = next_data_sections.get(_slug_from_item_url(item.get("item_url", ""))) or parser.sections.get(
            _slug_from_item_url(item.get("item_url", ""))
        )
        if not section:
            section = next_data_sections.get(_slugify(item.get("name", ""))) or parser.sections.get(
                _slugify(item.get("name", ""))
            )
        section = section or {}
        base_row = ScrapedArticleRow(
            item_name=item.get("name", ""),
            item_rank=item.get("rank"),
            item_url=item.get("item_url", ""),
            raw_address=section.get("address", ""),
            raw_description=section.get("description", ""),
            raw_neighborhood=section.get("neighborhood", ""),
            raw_borough=section.get("borough", ""),
        )
        rows.extend(_expand_multi_address_row(base_row))
    return rows


def _extract_items_from_jsonld(chunks: list[str]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for chunk in chunks:
        payload = _safe_json_loads(chunk)
        for data in _iter_json_nodes(payload):
            if not isinstance(data, dict) or data.get("@type") != "ItemList":
                continue
            for item in data.get("itemListElement", []):
                if not isinstance(item, dict):
                    continue
                place = item.get("item", {})
                if not isinstance(place, dict):
                    place = {}
                name = str(place.get("name", "") or "").strip()
                item_url = str(place.get("url", "") or "").strip()
                if not name:
                    continue
                rank = item.get("position")
                records.append(
                    {
                        "rank": int(rank) if isinstance(rank, int) or str(rank).isdigit() else None,
                        "name": name,
                        "item_url": item_url,
                    }
                )
    return records


def _extract_address(section_text: str) -> str:
    text = unescape(" ".join(str(section_text).split()))
    match = ADDRESS_LINE_PATTERN.search(text)
    if match:
        return match.group(1).strip(" ,;")
    return ""


def _extract_description(section_text: str) -> str:
    text = unescape(" ".join(str(section_text).split()))
    match = DESCRIPTION_LINE_PATTERN.search(text)
    if match:
        return match.group(1).strip(" ,;")
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return sentences[0].strip(" ,;") if sentences and sentences[0] else ""


def _extract_sections_from_next_data(html: str) -> dict[str, dict[str, str]]:
    match = NEXT_DATA_PATTERN.search(html)
    if not match:
        return {}

    payload = _safe_json_loads(match.group(1))
    if not isinstance(payload, dict):
        return {}

    map_points = _find_map_points(payload)
    sections: dict[str, dict[str, str]] = {}
    for point in map_points:
        if not isinstance(point, dict):
            continue
        slug = _extract_point_slug(point)
        if not slug:
            continue
        title = str(point.get("name", "") or "").strip()
        description = _extract_point_description(point)
        address = str(point.get("address", "") or "").strip()
        neighborhood = _extract_point_neighborhood(point)
        borough = _extract_point_borough(point)
        section = {
            "title": title,
            "address": address,
            "description": description,
            "neighborhood": neighborhood,
            "borough": borough,
        }
        sections[slug] = section
        if title:
            sections.setdefault(_slugify(title), section)
    return sections


def _expand_multi_address_row(row: ScrapedArticleRow) -> list[ScrapedArticleRow]:
    addresses = split_multi_location_address(row.raw_address)
    if addresses == [""] or len(addresses) == 1:
        return [row]
    return [replace(row, raw_address=address) for address in addresses]


def _slug_from_item_url(item_url: str) -> str:
    parsed = urlparse(item_url)
    return parsed.fragment.strip()


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", str(value).strip().lower())
    return cleaned.strip("-")


def _find_map_points(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, dict):
        if "mapPoints" in payload and isinstance(payload["mapPoints"], list):
            points = payload["mapPoints"]
            return [point for point in points if isinstance(point, dict)]
        for value in payload.values():
            found = _find_map_points(value)
            if found:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _find_map_points(value)
            if found:
                return found
    return []


def _extract_point_slug(point: dict[str, object]) -> str:
    venue = point.get("venue", {})
    if isinstance(venue, dict):
        slug = str(venue.get("slug", "") or "").strip()
        if slug:
            return slug
    item_url = str(point.get("url", "") or "").strip()
    return _slug_from_item_url(item_url)


def _extract_point_description(point: dict[str, object]) -> str:
    descriptions = point.get("description", [])
    if isinstance(descriptions, list):
        for candidate in descriptions:
            if isinstance(candidate, dict):
                plaintext = str(candidate.get("plaintext", "") or "").strip()
                if plaintext:
                    return plaintext
                html = str(candidate.get("html", "") or "").strip()
                if html:
                    return unescape(re.sub(r"<[^>]+>", " ", html)).strip()
    return ""


def _extract_point_neighborhood(point: dict[str, object]) -> str:
    venue = point.get("venue", {})
    if isinstance(venue, dict):
        return str(venue.get("neighborhood", "") or "").strip()
    return ""


def _extract_point_borough(point: dict[str, object]) -> str:
    venue = point.get("venue", {})
    if isinstance(venue, dict):
        return str(venue.get("borough", "") or "").strip()
    return ""


def _safe_json_loads(value: str) -> object:
    try:
        return json.loads(value)
    except Exception:
        return None


def _iter_json_nodes(payload: object) -> list[object]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    return [payload]
