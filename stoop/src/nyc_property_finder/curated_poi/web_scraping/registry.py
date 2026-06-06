"""Article registry for curated POI web scraping."""

from __future__ import annotations

from functools import lru_cache

from nyc_property_finder.curated_poi.web_scraping.base import ScrapedArticleConfig
from nyc_property_finder.services.config import DEFAULT_CONFIG_DIR, load_yaml


@lru_cache(maxsize=1)
def _article_registry() -> tuple[ScrapedArticleConfig, ...]:
    payload = load_yaml(DEFAULT_CONFIG_DIR / "curated_scrape_articles.yaml")
    articles = payload.get("articles", [])
    if not isinstance(articles, list):
        raise ValueError("curated_scrape_articles.yaml must contain an 'articles' list.")

    output: list[ScrapedArticleConfig] = []
    for item in articles:
        if not isinstance(item, dict):
            raise ValueError("Each scraped article config must be a mapping.")
        output.append(ScrapedArticleConfig(**item))
    return tuple(output)


EATER_ARTICLES: tuple[ScrapedArticleConfig, ...] = tuple(
    article for article in _article_registry() if article.publisher.lower() == "eater"
)


ARTICLE_REGISTRY: tuple[ScrapedArticleConfig, ...] = _article_registry()


def list_articles(publisher: str | None = None) -> list[ScrapedArticleConfig]:
    """Return registered scrape articles, optionally filtered by publisher."""

    if publisher is None:
        return list(ARTICLE_REGISTRY)
    target = publisher.strip().lower()
    return [article for article in ARTICLE_REGISTRY if article.publisher.lower() == target]


def get_article(publisher: str, article_slug: str) -> ScrapedArticleConfig:
    """Resolve one article config from the registry."""

    target_publisher = publisher.strip().lower()
    target_slug = article_slug.strip().lower()
    for article in ARTICLE_REGISTRY:
        if article.publisher.lower() == target_publisher and article.article_slug.lower() == target_slug:
            return article
    raise KeyError(f"Unknown scrape article: publisher={publisher!r}, article_slug={article_slug!r}")


def get_article_by_slug(article_slug: str) -> ScrapedArticleConfig:
    """Resolve one article config by slug across publishers."""

    target_slug = article_slug.strip().lower()
    matches = [article for article in ARTICLE_REGISTRY if article.article_slug.lower() == target_slug]
    if not matches:
        raise KeyError(f"Unknown scrape article slug: {article_slug!r}")
    if len(matches) > 1:
        raise KeyError(f"Article slug is not unique across publishers: {article_slug!r}")
    return matches[0]
