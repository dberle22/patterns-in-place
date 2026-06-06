"""Base scraper interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BasePropertyScraper(ABC):
    """Contract for listing scrapers."""

    source_name: str

    @abstractmethod
    def fetch_listings(self, search_url: str, limit: int | None = None) -> pd.DataFrame:
        """Fetch listings and return a raw dataframe."""
