"""RentHop scraper placeholder."""

from __future__ import annotations

import pandas as pd

from nyc_property_finder.scrapers.base import BasePropertyScraper


class RentHopScraper(BasePropertyScraper):
    """Starter RentHop scraper."""

    source_name = "renthop"

    def fetch_listings(self, search_url: str, limit: int | None = None) -> pd.DataFrame:
        """Return an empty dataframe until scraping logic is implemented."""

        return pd.DataFrame()
