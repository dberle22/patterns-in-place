"""Curated POI ingestion path for web-scraped sources."""

from nyc_property_finder.curated_poi.web_scraping.registry import EATER_ARTICLES, get_article, list_articles

__all__ = ["EATER_ARTICLES", "get_article", "list_articles"]
