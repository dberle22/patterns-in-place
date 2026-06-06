"""Semi-manual normalization helpers for saved curated article captures."""

from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen
from urllib.parse import urljoin

from nyc_property_finder.curated_poi.web_scraping.base import ScrapedArticleConfig, ScrapedArticleRow


NOISY_TEXT_PATTERNS = (
    "sign up",
    "privacy policy",
    "terms of service",
    "open in app",
    "download app",
    "nearby restaurants",
    "nearby things to do",
)
RANKED_LINE_PATTERN = re.compile(r"^\s*(\d+)[.)-]?\s+(.+?)\s*$")
JSONLD_PATTERN = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
WANDERLOG_PLACE_HEADING_PATTERN = re.compile(
    r'<h2[^>]*>\s*(?:<span[^>]*>.*?</span>\s*)*<a[^>]+href="(?P<href>/place/details/[^"]+)"[^>]*>(?P<name>.*?)</a>\s*</h2>',
    re.IGNORECASE | re.DOTALL,
)
WANDERLOG_PLACE_BLOCK_PATTERN = re.compile(
    r'(<div id="BoardPlaceView__place-[^"]+".*?)(?=<div id="BoardPlaceView__place-|$)',
    re.IGNORECASE | re.DOTALL,
)
WANDERLOG_ADDRESS_PATTERN = re.compile(
    r'<div class="col p-0 minw-0">(?P<address>[^<]+)<span class="font-weight-bold mx-2">',
    re.IGNORECASE,
)
MICHELIN_CARD_BLOCK_PATTERN = re.compile(
    r'(<div class="card__menu selection-card[^"]*js-restaurant__list_item.*?</div>\s*<a href="[^"]+" class="link"[^>]*></a>\s*</div>)',
    re.IGNORECASE | re.DOTALL,
)
MICHELIN_NAME_PATTERN = re.compile(
    r'<h3 class="card__menu-content--title[^"]*">\s*<a href="(?P<href>[^"]+)"[^>]*>\s*(?P<name>.*?)\s*</a>\s*</h3>',
    re.IGNORECASE | re.DOTALL,
)
MICHELIN_LOCATION_PATTERN = re.compile(
    r'<div class="card__menu-footer--score pl-text">\s*(?P<location>.*?)\s*</div>',
    re.IGNORECASE | re.DOTALL,
)
MICHELIN_DETAILS_PATTERN = re.compile(
    r'<div class="card__menu-footer--score pl-text\s*">\s*(?P<details>.*?)\s*</div>',
    re.IGNORECASE | re.DOTALL,
)
NY_MAG_SWIFTYPE_CONFIG_PATTERN = re.compile(
    r'host:"(?P<host>https://[^"]+)",token:"(?P<token>[^"]+)",engine:"(?P<engine>[^"]+)"',
    re.IGNORECASE,
)
BON_APPETIT_ARTICLE_LINK_PATTERN = re.compile(
    r'<a href="(?P<href>[^"]+)"[^>]*>\s*<strong[^>]*>\s*(?P<name>.*?)\s*</strong>\s*</a>\s*<br/>\s*<em>\s*(?P<neighborhood>.*?)\s*</em>\s*<br/>',
    re.IGNORECASE | re.DOTALL,
)
BON_APPETIT_ARTICLE_LINK_ALT_PATTERN = re.compile(
    r'<strong[^>]*>\s*<a href="(?P<href>[^"]+)"[^>]*>\s*(?P<name>.*?)\s*</a>\s*</strong>\s*<br/>\s*<em>\s*(?P<neighborhood>.*?)\s*</em>\s*<br/>',
    re.IGNORECASE | re.DOTALL,
)
BON_APPETIT_ENTRY_PATTERN = re.compile(
    r"(?ms)^\s*(?P<rank>\d+)\.\s+(?P<label>[^\n]+)\n"
    r"(?P<name>[^\n]+)\n"
    r"(?P<neighborhood>[^\n]+)\n"
    r"(?P<body>.*?)(?=^\s*\d+\.\s+|\Z)"
)
TRAILING_AUTHOR_BYLINE_PATTERN = re.compile(r"\s+[--\u2014][A-Z][A-Za-z. '\u2019-]+$")
BASIC_ADDRESS_PATTERN = re.compile(
    r"\d+[A-Za-z0-9#/ -]*\s+(?:[A-Za-z0-9.'\u2019-]+\s+){0,6}"
    r"(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Dr|Drive|Ln|Lane|Way|Place|Pl|Ct|Court|Sq|Square|Broadway|Mercer|Madison)\b",
    re.IGNORECASE,
)


class SemiManualExtractionError(RuntimeError):
    """Raised when a semi-manual extraction yields too little usable data."""


@dataclass(frozen=True)
class SemiManualExtractionResult:
    """Rows and metadata from one semi-manual extraction pass."""

    rows: list[ScrapedArticleRow]
    extractor_name: str
    guidance_notes: list[str]


class SemiManualHtmlExtractor:
    """Extract list candidates from saved article HTML."""

    def __init__(self, article: ScrapedArticleConfig) -> None:
        self.article = article
        self.hints = dict(article.semi_manual_hints or {})
        self.extractor_family = str(self.hints.get("extractor_family") or "generic_html_list").strip().lower()
        self.min_candidate_rows = int(self.hints.get("min_candidate_rows") or 1)
        self.infer_item_urls = bool(self.hints.get("infer_item_urls", True))

    def extract(self, html: str) -> SemiManualExtractionResult:
        rows: list[ScrapedArticleRow] = []
        guidance_notes = [f"extractor_family={self.extractor_family}"]

        jsonld_rows = _extract_jsonld_itemlist_rows(html, self.article.article_url)
        if jsonld_rows:
            rows.extend(jsonld_rows)
            guidance_notes.append("jsonld_itemlist")

        if self.extractor_family == "wanderlog":
            wanderlog_rows = _extract_wanderlog_place_rows(
                html,
                article_url=self.article.article_url,
                infer_item_urls=self.infer_item_urls,
            )
            if wanderlog_rows:
                rows.extend(wanderlog_rows)
                guidance_notes.append("wanderlog_anchor_candidates")
        elif self.extractor_family == "michelin":
            michelin_rows = _extract_michelin_card_rows(
                html,
                article_url=self.article.article_url,
                infer_item_urls=self.infer_item_urls,
            )
            if michelin_rows:
                rows.extend(michelin_rows)
                guidance_notes.append("michelin_card_blocks")
        elif self.extractor_family == "ny_mag":
            ny_mag_rows = _extract_ny_mag_rows(
                html,
                article_url=self.article.article_url,
                listing_type=str(self.hints.get("listing_type") or "restaurant").strip().lower(),
            )
            if ny_mag_rows:
                rows.extend(ny_mag_rows)
                guidance_notes.append("ny_mag_swiftype_search")
        elif self.extractor_family == "bon_appetit":
            bon_appetit_rows = _extract_bon_appetit_article_rows(
                html,
                article_url=self.article.article_url,
                infer_item_urls=self.infer_item_urls,
            )
            if bon_appetit_rows:
                rows.extend(bon_appetit_rows)
                guidance_notes.append("bon_appetit_article_body")
        elif self.extractor_family == "vogue":
            vogue_rows = _extract_vogue_article_rows(
                html,
                article_url=self.article.article_url,
                infer_item_urls=self.infer_item_urls,
            )
            if vogue_rows:
                rows.extend(vogue_rows)
                guidance_notes.append("vogue_article_body")

        if not rows:
            generic_rows = _extract_generic_anchor_rows(
                html,
                article_url=self.article.article_url,
                infer_item_urls=self.infer_item_urls,
            )
            rows.extend(generic_rows)
            if generic_rows:
                guidance_notes.append("generic_anchor_candidates")

        cleaned_rows = _dedupe_rows(rows)
        self._validate(cleaned_rows, guidance_notes)
        return SemiManualExtractionResult(
            rows=cleaned_rows,
            extractor_name=self.extractor_family,
            guidance_notes=guidance_notes,
        )

    def _validate(self, rows: list[ScrapedArticleRow], guidance_notes: list[str]) -> None:
        if len(rows) >= self.min_candidate_rows:
            return
        notes = ", ".join(guidance_notes) if guidance_notes else "none"
        raise SemiManualExtractionError(
            "Semi-manual HTML extraction found almost nothing usable "
            f"for {self.article.publisher} / {self.article.article_slug}: "
            f"{len(rows)} candidate rows from {notes}. "
            f"Expected at least {self.min_candidate_rows}."
        )


class SemiManualTextExtractor:
    """Extract list candidates from saved article text or markdown."""

    def __init__(self, article: ScrapedArticleConfig) -> None:
        self.article = article
        self.hints = dict(article.semi_manual_hints or {})
        self.extractor_family = str(self.hints.get("extractor_family") or "generic_text_list").strip().lower()
        self.min_candidate_rows = int(self.hints.get("min_candidate_rows") or 1)

    def extract(self, text: str) -> SemiManualExtractionResult:
        rows = _extract_ranked_text_rows(text)
        guidance_notes = [f"extractor_family={self.extractor_family}", "ranked_text_lines"]
        if len(rows) < self.min_candidate_rows:
            raise SemiManualExtractionError(
                "Semi-manual text extraction found almost nothing usable "
                f"for {self.article.publisher} / {self.article.article_slug}: "
                f"{len(rows)} candidate rows from ranked_text_lines. "
                f"Expected at least {self.min_candidate_rows}."
            )
        return SemiManualExtractionResult(
            rows=rows,
            extractor_name=self.extractor_family,
            guidance_notes=guidance_notes,
        )


def build_semi_manual_rows(
    article: ScrapedArticleConfig,
    *,
    html: str | None = None,
    text: str | None = None,
) -> SemiManualExtractionResult:
    """Run the configured semi-manual extractor for one article."""

    if html:
        return SemiManualHtmlExtractor(article).extract(html)
    if text:
        return SemiManualTextExtractor(article).extract(text)
    raise ValueError("Provide html or text to build semi-manual rows.")


def preferred_input_suffix(article: ScrapedArticleConfig) -> str:
    """Return the preferred saved-capture suffix for one semi-manual article."""

    hints = article.semi_manual_hints or {}
    preferred = str(hints.get("preferred_input") or "html").strip().lower()
    return "html" if preferred == "html" else "txt"


def raw_capture_path(
    article: ScrapedArticleConfig,
    run_date: str,
    root_dir: str | Path = "data/raw/scraped/raw",
) -> Path:
    """Build the conventional raw capture path for one semi-manual article."""

    publisher_slug = _slugify(article.publisher)
    suffix = preferred_input_suffix(article)
    return Path(root_dir) / publisher_slug / f"{article.article_slug}_{run_date}.{suffix}"


def _extract_jsonld_itemlist_rows(html: str, article_url: str) -> list[ScrapedArticleRow]:
    rows: list[ScrapedArticleRow] = []
    for chunk in JSONLD_PATTERN.findall(html):
        payload = _safe_json_loads(chunk)
        for node in _iter_json_nodes(payload):
            if not isinstance(node, dict) or node.get("@type") != "ItemList":
                continue
            for item in node.get("itemListElement", []):
                if not isinstance(item, dict):
                    continue
                rank = item.get("position")
                payload_item = item.get("item", item)
                if not isinstance(payload_item, dict):
                    payload_item = {}
                item_name = _clean_text(payload_item.get("name", ""))
                item_url = _coerce_url(payload_item.get("url", ""), article_url)
                if not _is_plausible_item_name(item_name):
                    continue
                rows.append(
                    ScrapedArticleRow(
                        item_name=item_name,
                        item_rank=int(rank) if str(rank).isdigit() else None,
                        item_url=item_url,
                    )
                )
    return rows


def _extract_wanderlog_place_rows(html: str, article_url: str, infer_item_urls: bool) -> list[ScrapedArticleRow]:
    rows: list[ScrapedArticleRow] = []
    for block in WANDERLOG_PLACE_BLOCK_PATTERN.findall(html):
        match = WANDERLOG_PLACE_HEADING_PATTERN.search(block)
        if not match:
            continue
        href = _coerce_url(match.group("href"), article_url)
        item_name = _clean_text(_strip_tags(match.group("name")))
        if not _is_plausible_item_name(item_name):
            continue
        address_match = WANDERLOG_ADDRESS_PATTERN.search(block)
        raw_address = _clean_text(address_match.group("address")) if address_match else ""
        rows.append(
            ScrapedArticleRow(
                item_name=item_name,
                item_url=href if infer_item_urls else "",
                raw_address=raw_address,
            )
        )
    return rows


def _extract_generic_anchor_rows(html: str, article_url: str, infer_item_urls: bool) -> list[ScrapedArticleRow]:
    parser = _AnchorCollector(article_url=article_url)
    parser.feed(html)
    parser.close()

    rows: list[ScrapedArticleRow] = []
    for anchor in parser.anchors:
        text = _clean_text(anchor["text"])
        if not _is_plausible_item_name(text):
            continue
        rows.append(
            ScrapedArticleRow(
                item_name=text,
                item_url=anchor["href"] if infer_item_urls else "",
            )
        )
    return rows


def _extract_michelin_card_rows(html: str, article_url: str, infer_item_urls: bool) -> list[ScrapedArticleRow]:
    rows: list[ScrapedArticleRow] = []
    for block in MICHELIN_CARD_BLOCK_PATTERN.findall(html):
        name_match = MICHELIN_NAME_PATTERN.search(block)
        if not name_match:
            continue
        item_name = _clean_text(_strip_tags(name_match.group("name")))
        if not _is_plausible_item_name(item_name):
            continue
        item_url = _coerce_url(name_match.group("href"), article_url) if infer_item_urls else ""
        locations = MICHELIN_LOCATION_PATTERN.findall(block)
        details = MICHELIN_DETAILS_PATTERN.findall(block)
        raw_neighborhood = ""
        if locations:
            location_text = _clean_text(_strip_tags(locations[0]))
            raw_neighborhood = "" if location_text == "New York, NY, USA" else location_text
        raw_description = ""
        if len(details) >= 2:
            raw_description = _clean_text(_strip_tags(details[1])).replace(" · ", " - ")
        elif details:
            raw_description = _clean_text(_strip_tags(details[-1])).replace(" · ", " - ")
        rows.append(
            ScrapedArticleRow(
                item_name=item_name,
                item_url=item_url,
                raw_address="",
                raw_description=raw_description,
                raw_neighborhood=raw_neighborhood,
                raw_borough="",
            )
        )
    return rows


def _extract_ranked_text_rows(text: str) -> list[ScrapedArticleRow]:
    rows: list[ScrapedArticleRow] = []
    for line in str(text).splitlines():
        clean_line = _clean_text(line)
        if not clean_line:
            continue
        match = RANKED_LINE_PATTERN.match(clean_line)
        if not match:
            continue
        item_name = _clean_text(match.group(2))
        if not _is_plausible_item_name(item_name):
            continue
        rows.append(
            ScrapedArticleRow(
                item_name=item_name,
                item_rank=int(match.group(1)),
            )
        )
    return rows


def _extract_ny_mag_rows(html: str, article_url: str, listing_type: str) -> list[ScrapedArticleRow]:
    host, token, engine = _extract_ny_mag_swiftype_config(html)
    results = _fetch_ny_mag_listings(host=host, token=token, engine=engine, listing_type=listing_type)
    rows: list[ScrapedArticleRow] = []
    for index, result in enumerate(results, start=1):
        item_name = _clean_text(_read_swiftype_raw(result, "name"))
        if not _is_plausible_item_name(item_name):
            continue
        neighborhood = _clean_text(_read_swiftype_raw(result, "neighborhood"))
        borough = _clean_text(_read_swiftype_raw(result, "borough"))
        teaser = _clean_text(_read_swiftype_raw(result, "teaser"))
        cuisines = _read_swiftype_raw(result, "cuisines")
        bar_types = _read_swiftype_raw(result, "bar_types")
        price = _clean_text(_read_swiftype_raw(result, "price"))
        description_parts = [teaser]
        if isinstance(cuisines, list) and cuisines:
            description_parts.append(f"Cuisines: {', '.join(_clean_text(item) for item in cuisines if _clean_text(item))}")
        elif isinstance(bar_types, list) and bar_types:
            description_parts.append(f"Bar types: {', '.join(_clean_text(item) for item in bar_types if _clean_text(item))}")
        if price:
            description_parts.append(f"Price: {price}")
        rows.append(
            ScrapedArticleRow(
                item_name=item_name,
                item_rank=index,
                item_url=_coerce_url(_read_swiftype_raw(result, "canonical_url"), article_url).replace("http://", "https://"),
                raw_address="",
                raw_description=" ".join(part for part in description_parts if part).strip(),
                raw_neighborhood=neighborhood,
                raw_borough=borough,
            )
        )
    return rows


def _extract_bon_appetit_article_rows(html: str, article_url: str, infer_item_urls: bool) -> list[ScrapedArticleRow]:
    body_text = _extract_news_article_body_text(html)
    if not body_text:
        return []

    item_urls = _extract_bon_appetit_item_urls(html, article_url) if infer_item_urls else {}
    rows: list[ScrapedArticleRow] = []
    for match in BON_APPETIT_ENTRY_PATTERN.finditer(body_text):
        item_name = _clean_text(match.group("name"))
        if not _is_plausible_item_name(item_name):
            continue
        raw_neighborhood, raw_borough = _split_bon_appetit_neighborhood(match.group("neighborhood"))
        description, order_note = _split_bon_appetit_body(match.group("body"))
        raw_description_parts = [description]
        if order_note:
            raw_description_parts.append(order_note)
        rows.append(
            ScrapedArticleRow(
                item_name=item_name,
                item_rank=int(match.group("rank")),
                item_url=item_urls.get(item_name.strip().casefold(), ""),
                raw_address="",
                raw_description=" ".join(part for part in raw_description_parts if part).strip(),
                raw_neighborhood=raw_neighborhood,
                raw_borough=raw_borough,
            )
        )
    return rows


def _extract_bon_appetit_article_body_text(html: str) -> str:
    return _extract_news_article_body_text(html)


def _extract_news_article_body_text(html: str) -> str:
    for chunk in JSONLD_PATTERN.findall(html):
        payload = _safe_json_loads(chunk)
        for node in _iter_json_nodes(payload):
            if not isinstance(node, dict) or node.get("@type") != "NewsArticle":
                continue
            article_body = str(node.get("articleBody") or "")
            if article_body:
                return article_body
    return ""


def _extract_vogue_article_rows(html: str, article_url: str, infer_item_urls: bool) -> list[ScrapedArticleRow]:
    body_text = _extract_news_article_body_text(html)
    if not body_text:
        return []

    item_urls = _extract_named_anchor_urls(html, article_url) if infer_item_urls else {}
    entries = _extract_vogue_entries(body_text, item_urls)
    rows: list[ScrapedArticleRow] = []
    for entry in entries:
        item_name = entry["item_name"]
        description_lines = [_strip_vogue_trailing_promo(_strip_vogue_author_byline(line)) for line in entry["description_lines"]]
        description_lines = [line for line in description_lines if line]
        raw_description = " ".join(description_lines).strip()
        raw_addresses = entry["addresses"] or [""]
        for raw_address in raw_addresses:
            borough = _infer_borough_from_address(raw_address)
            rows.append(
                ScrapedArticleRow(
                    item_name=item_name,
                    item_rank=entry["item_rank"],
                    item_url=item_urls.get(_canonical_name_key(item_name), ""),
                    raw_address=raw_address,
                    raw_description=raw_description,
                    raw_neighborhood=entry.get("raw_neighborhood", ""),
                    raw_borough=borough,
                )
            )
    return rows


def _extract_ny_mag_swiftype_config(html: str) -> tuple[str, str, str]:
    match = NY_MAG_SWIFTYPE_CONFIG_PATTERN.search(html)
    if not match:
        raise SemiManualExtractionError("NY Mag capture did not expose Swiftype host/token/engine config.")
    return match.group("host"), match.group("token"), match.group("engine")


def _fetch_ny_mag_listings(*, host: str, token: str, engine: str, listing_type: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    page = 1
    page_size = 100
    while True:
        payload = {
            "query": "",
            "page": {"size": page_size, "current": page},
            "result_fields": {
                "name": {"raw": {}},
                "canonical_url": {"raw": {}},
                "listing_type": {"raw": {}},
                "neighborhood": {"raw": {}},
                "borough": {"raw": {}},
                "cuisines": {"raw": {}},
                "bar_types": {"raw": {}},
                "teaser": {"raw": {}},
                "price": {"raw": {}},
                "critics_rating": {"raw": {}},
            },
            "filters": {"all": [{"listing_type": listing_type}]},
            "sort": {"critics_rating": "desc"},
        }
        request = Request(
            f"{host}/api/as/v1/engines/{engine}/search",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
        except URLError as exc:
            raise SemiManualExtractionError(f"NY Mag listing fetch failed: {exc}") from exc
        payload_json = _safe_json_loads(body)
        if not isinstance(payload_json, dict):
            raise SemiManualExtractionError("NY Mag listing fetch returned invalid JSON.")
        page_results = payload_json.get("results", [])
        if not isinstance(page_results, list):
            raise SemiManualExtractionError("NY Mag listing fetch returned malformed results.")
        results.extend(result for result in page_results if isinstance(result, dict))
        meta_page = payload_json.get("meta", {}).get("page", {})
        total_pages = int(meta_page.get("total_pages") or page)
        if page >= total_pages or not page_results:
            break
        page += 1
    return results


def _extract_bon_appetit_item_urls(html: str, article_url: str) -> dict[str, str]:
    urls: dict[str, str] = {}
    for pattern in (BON_APPETIT_ARTICLE_LINK_PATTERN, BON_APPETIT_ARTICLE_LINK_ALT_PATTERN):
        for match in pattern.finditer(html):
            item_name = _clean_text(_strip_tags(match.group("name")))
            if not _is_plausible_item_name(item_name):
                continue
            urls[item_name.casefold()] = _coerce_url(match.group("href"), article_url)
    return urls


def _extract_named_anchor_urls(html: str, article_url: str) -> dict[str, str]:
    parser = _AnchorCollector(article_url=article_url)
    parser.feed(html)
    parser.close()

    urls: dict[str, str] = {}
    for anchor in parser.anchors:
        item_name = _clean_text(anchor["text"])
        if not _is_plausible_item_name(item_name):
            continue
        urls[_canonical_name_key(item_name)] = anchor["href"]
    return urls


def _extract_vogue_entries(body_text: str, item_urls: dict[str, str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    current_name = ""
    current_rank: int | None = None
    current_neighborhood = ""
    current_lines: list[str] = []
    have_started = False

    lines = [_clean_text(raw_line) for raw_line in str(body_text).splitlines()]
    for index, line in enumerate(lines):
        if not line:
            continue
        matched_name, matched_rank, matched_neighborhood = _match_vogue_entry_name(
            line,
            item_urls,
            lookahead_lines=lines[index + 1 : index + 4],
        )
        if matched_name:
            if current_name:
                entries.append(
                    _build_vogue_entry(
                        item_name=current_name,
                        item_rank=current_rank,
                        raw_neighborhood=current_neighborhood,
                        body_lines=current_lines,
                    )
                )
            current_name = matched_name
            current_rank = matched_rank
            current_neighborhood = matched_neighborhood
            current_lines = []
            have_started = True
            continue
        if have_started:
            current_lines.append(line)

    if current_name:
        entries.append(
            _build_vogue_entry(
                item_name=current_name,
                item_rank=current_rank,
                raw_neighborhood=current_neighborhood,
                body_lines=current_lines,
            )
        )
    return entries


def _match_vogue_entry_name(
    line: str,
    item_urls: dict[str, str],
    lookahead_lines: list[str] | None = None,
) -> tuple[str, int | None, str]:
    ranked_match = RANKED_LINE_PATTERN.match(line)
    if ranked_match:
        candidate_name = _clean_text(ranked_match.group(2))
        item_name, raw_neighborhood = _resolve_vogue_item_name(
            candidate_name,
            item_urls,
            lookahead_lines=lookahead_lines,
        )
        if item_name:
            return item_name, int(ranked_match.group(1)), raw_neighborhood
    item_name, raw_neighborhood = _resolve_vogue_item_name(
        line,
        item_urls,
        lookahead_lines=lookahead_lines,
    )
    return item_name, None, raw_neighborhood


def _resolve_vogue_item_name(
    value: str,
    item_urls: dict[str, str],
    lookahead_lines: list[str] | None = None,
) -> tuple[str, str]:
    key = _canonical_name_key(value)
    if key in item_urls:
        return _clean_text(value), ""
    parsed_name, raw_neighborhood = _parse_vogue_header_line(value)
    if not parsed_name:
        return "", ""
    lookahead = [_clean_text(line) for line in (lookahead_lines or []) if _clean_text(line)]
    if any(line.lower().startswith("amenities:") or line.lower().startswith("address:") for line in lookahead):
        return parsed_name, raw_neighborhood
    return "", ""


def _build_vogue_entry(
    *,
    item_name: str,
    item_rank: int | None,
    raw_neighborhood: str,
    body_lines: list[str],
) -> dict[str, Any]:
    address_lines: list[str] = []
    description_lines: list[str] = []

    address_marker_index = next((index for index, line in enumerate(body_lines) if line.lower().startswith("address:")), None)
    if address_marker_index is not None:
        description_lines = body_lines[:address_marker_index]
        raw_address = _clean_text(body_lines[address_marker_index].split(":", 1)[1] if ":" in body_lines[address_marker_index] else "")
        if _is_vogue_usable_address(raw_address):
            address_lines = [raw_address]
        elif raw_address:
            description_lines.append(f"Address note: {raw_address}")
    else:
        address_line_count = 0
        for line in body_lines:
            if _looks_like_vogue_address_line(line):
                address_line_count += 1
            else:
                break
        address_lines = [line for line in body_lines[:address_line_count] if _is_vogue_usable_address(line)]
        description_lines = body_lines[address_line_count:]

    return {
        "item_name": item_name,
        "item_rank": item_rank,
        "raw_neighborhood": raw_neighborhood,
        "addresses": address_lines,
        "description_lines": description_lines,
    }


def _parse_vogue_header_line(value: str) -> tuple[str, str]:
    text = _clean_text(value)
    if not text or "," not in text:
        return "", ""
    lowered = text.casefold()
    if lowered.startswith("amenities:") or lowered.startswith("address:"):
        return "", ""
    item_name, raw_neighborhood = text.rsplit(",", 1)
    item_name = _clean_text(item_name)
    raw_neighborhood = _clean_text(raw_neighborhood)
    if not item_name or not raw_neighborhood:
        return "", ""
    if len(raw_neighborhood.split()) > 4:
        return "", ""
    if raw_neighborhood.lower().startswith("new york"):
        return "", ""
    return item_name, raw_neighborhood


def _looks_like_vogue_address_line(value: str) -> bool:
    text = _clean_text(value)
    if not text:
        return False
    if text.lower().startswith("address:"):
        return True
    if "appointment confirmation" in text.casefold():
        return True
    if BASIC_ADDRESS_PATTERN.search(text):
        return True
    if re.search(r",\s*(?:Brooklyn|Queens|Bronx|Manhattan|Staten Island)\b", text, flags=re.IGNORECASE):
        return True
    if re.search(r",\s*NY\s+\d{5}\b", text, flags=re.IGNORECASE):
        return True
    return False


def _is_vogue_usable_address(value: str) -> bool:
    text = _clean_text(value)
    if not text:
        return False
    if "appointment confirmation" in text.casefold():
        return False
    return _looks_like_vogue_address_line(text)


def _strip_vogue_author_byline(value: str) -> str:
    return _clean_text(TRAILING_AUTHOR_BYLINE_PATTERN.sub("", value))


def _strip_vogue_trailing_promo(value: str) -> str:
    return _clean_text(re.sub(r"Mark your calendars:.*$", "", value, flags=re.IGNORECASE))


def _infer_borough_from_address(value: str) -> str:
    text = _clean_text(value)
    if not text:
        return ""
    for borough in ("Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"):
        if re.search(rf"\b{re.escape(borough)}\b", text, flags=re.IGNORECASE):
            return borough
    return ""


def _canonical_name_key(value: str) -> str:
    return (
        _clean_text(value)
        .replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .casefold()
    )


def _read_swiftype_raw(result: dict[str, Any], field_name: str) -> Any:
    field = result.get(field_name)
    if not isinstance(field, dict):
        return ""
    return field.get("raw", "")


def _split_bon_appetit_neighborhood(value: str) -> tuple[str, str]:
    clean_value = _clean_text(value)
    if not clean_value:
        return "", ""
    if "," not in clean_value:
        return clean_value, ""
    neighborhood, borough = clean_value.rsplit(",", 1)
    return _clean_text(neighborhood), _clean_text(borough)


def _split_bon_appetit_body(value: str) -> tuple[str, str]:
    cleaned = _clean_text(value)
    if not cleaned:
        return "", ""
    cleaned = re.sub(r"\s+Credits\s+Project Lead:.*$", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"\s+See all these restaurants, bars, and shops on a map.*$", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    note_match = re.search(r"✵\s*(Order|Buy):\s*(.+)$", cleaned, flags=re.IGNORECASE | re.DOTALL)
    if not note_match:
        return cleaned, ""
    description = cleaned[: note_match.start()]
    note_label = _clean_text(note_match.group(1)).capitalize()
    note_value = _clean_text(note_match.group(2))
    return _clean_text(description), f"{note_label}: {note_value}"


def _dedupe_rows(rows: list[ScrapedArticleRow]) -> list[ScrapedArticleRow]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[ScrapedArticleRow] = []
    for row in rows:
        key = (row.item_name.strip().casefold(), row.item_url.strip(), row.raw_address.strip())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def _is_plausible_item_name(value: str) -> bool:
    text = _clean_text(value)
    if len(text) < 2 or len(text) > 120:
        return False
    if "{{" in text or "}}" in text:
        return False
    if any(pattern in text.casefold() for pattern in NOISY_TEXT_PATTERNS):
        return False
    if text.casefold().startswith("best ") or text.casefold().startswith("top "):
        return False
    if sum(char.isalpha() for char in text) < 2:
        return False
    return True


def _coerce_url(value: object, article_url: str) -> str:
    href = str(value or "").strip()
    return urljoin(article_url, href) if href else ""


def _clean_text(value: object) -> str:
    text = unescape(" ".join(str(value or "").split()))
    return text.strip(" ,;")


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", str(value or ""))


def _safe_json_loads(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def _iter_json_nodes(value: Any) -> list[Any]:
    nodes: list[Any] = []
    if isinstance(value, list):
        for item in value:
            nodes.extend(_iter_json_nodes(item))
        return nodes
    if isinstance(value, dict):
        nodes.append(value)
        for item in value.values():
            nodes.extend(_iter_json_nodes(item))
    return nodes


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower())
    return cleaned.strip("_")


class _AnchorCollector(HTMLParser):
    def __init__(self, article_url: str) -> None:
        super().__init__()
        self.article_url = article_url
        self.anchors: list[dict[str, str]] = []
        self._capture_href = ""
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href") or ""
        self._capture_href = _coerce_url(href, self.article_url)
        self._text_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._capture_href:
            return
        self.anchors.append(
            {
                "href": self._capture_href,
                "text": _clean_text(" ".join(self._text_parts)),
            }
        )
        self._capture_href = ""
        self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._capture_href:
            self._text_parts.append(data)
