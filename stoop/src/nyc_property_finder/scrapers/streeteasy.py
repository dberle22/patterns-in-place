"""StreetEasy scraper skeleton.

This intentionally avoids heavy scraping logic. It provides a production-shaped
interface where request/session logic and HTML parsing can be added later.
"""

from __future__ import annotations

import logging

import pandas as pd

from nyc_property_finder.scrapers.base import BasePropertyScraper

logger = logging.getLogger(__name__)


class StreetEasyScraper(BasePropertyScraper):
    """Starter StreetEasy scraper."""

    source_name = "streeteasy"

    def fetch_listings(self, search_url: str, limit: int | None = None) -> pd.DataFrame:
        """Return an empty structured dataframe for now.

        TODO: Add respectful request throttling, robots review, pagination, and
        HTML parsing after the data access approach is confirmed.
        """

        logger.info("StreetEasy scraper skeleton called for %s", search_url)
        columns = [
            "source_listing_id",
            "address",
            "lat",
            "lon",
            "price",
            "beds",
            "baths",
            "listing_type",
            "url",
        ]
        return pd.DataFrame(columns=columns)
