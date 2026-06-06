"""Publication-specific web scrapers."""

from __future__ import annotations

from collections.abc import Callable

from nyc_property_finder.curated_poi.web_scraping.base import ScrapedArticleConfig, ScrapedArticleRow
from nyc_property_finder.curated_poi.web_scraping.publications.eater import parse_article as parse_eater_article
from nyc_property_finder.curated_poi.web_scraping.publications.timeout import parse_article as parse_timeout_article


ArticleParser = Callable[[str, ScrapedArticleConfig], list[ScrapedArticleRow]]

PARSER_REGISTRY: dict[str, ArticleParser] = {
    "eater": parse_eater_article,
    "timeout": parse_timeout_article,
}


def get_parser(parser_name: str) -> ArticleParser:
    """Return the registered parser callable for one parser family."""

    parser = PARSER_REGISTRY.get(str(parser_name).strip().lower())
    if parser is None:
        raise KeyError(f"Unknown parser: {parser_name!r}")
    return parser
