from abc import ABC, abstractmethod
from typing import Iterable


class WoolsPlatformScraper(ABC):
    """Interface Segregation Principle"""

    @abstractmethod
    def scrape_wool_info(self, wool: Iterable) -> dict | None:
        """
        Returns wool product info dict with the format of the following example:
            "info": {
              "price": 3.05,
              "availability": true,
              "needle_size": 4,
              "composition": "100% Acryl"
            }
        Returns None if no product is found"""
        ...
