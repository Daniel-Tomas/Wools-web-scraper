import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit

from wollplatz_scraper import WollplatzScraper
from wools_platform_scraper import WoolsPlatformScraper


@dataclass
class Platform:
    name: str
    scraper_class: type(WoolsPlatformScraper)


class WoolsScrapingOrchestrator:
    """Open/Closed Principle:
        New platforms can be added without modifying the existing code
    Dependency Inversion Principle:
        High-level modules (this class) do not depend on low-level modules (e.g. WollplatzScraper),
        both depend on abstractions (abstract class WoolsPlatformScraper) """

    # TODO: Likely repeated webpage names, they will probably appear here and in the scrapers classes
    #  Proposed solution: create a class in a new python file to store shared variables
    WEBSITE_BY_URL = {
        'wollplatz.de': Platform('Wollplatz', WollplatzScraper),
    }

    def execute(self, wools_to_scrape: list[Iterable], websites_to_scrape: list[str]) -> None:
        self.store_wools_info(self.get_wools_info_from_websites(wools_to_scrape, websites_to_scrape))

    def get_wools_info_from_websites(self, wools: list[Iterable], websites_urls: list[str]) -> dict:
        if any(len(wool) != 2 for wool in wools):
            raise ValueError('Wools must have to elements, brand and model')

        cleaned_websites_url = self._get_cleaned_websites_url(websites_urls)
        platforms_to_scrape = [platform_to_scrape for website_url_to_scrape in cleaned_websites_url if
                               (platform_to_scrape := self.WEBSITE_BY_URL.get(website_url_to_scrape)) is not None]

        wools_info = []
        for wool in wools:
            offered_in_platforms = []
            for website in platforms_to_scrape:
                # If some web scraping execution fails, the rest can continue
                try:
                    wool_info = website.scraper_class().scrape_wool_info(wool)
                except Exception as e:
                    print(e, file=sys.stderr)
                    continue

                if wool_info is None:
                    continue

                offered_in_platforms.append({'platform': website.name,
                                             'info': wool_info})

            brand, model = wool
            wools_info.append({'brand': brand,
                               'model:': model,
                               'offeredInPlatforms': offered_in_platforms})

        return {'wools': wools_info}

    @staticmethod
    def store_wools_info(wools: dict) -> None:
        # Storage logic separated to easily change it in the future if necessary
        with open(Path(__file__).parent / 'wools.json', 'w') as file:
            json.dump(wools, file)

    @staticmethod
    def _get_cleaned_websites_url(websites_urls: list[str]) -> list[str]:
        """
        Clean websites url keeping only the website netloc without the www subdomain
        (http://netloc/path;parameters?query=argument#fragment)
        """

        def clean_website_url(website_url: str) -> str:
            return urlsplit(website_url).netloc.removeprefix('www.')

        return [clean_website_url(website_url) for website_url in websites_urls]


if __name__ == '__main__':
    websites_to_scrape = ['https://www.wollplatz.de/', ]
    wools_to_scrape = [('DMC', 'Natura XL'), ('Drops', 'Safran'), ('Drops', 'Baby Merino Mix'),
                       ('Hahn', 'Alpacca Speciale'), ('Stylecraft', 'Special double knit')]

    scraper_orchestrator = WoolsScrapingOrchestrator()
    scraper_orchestrator.execute(wools_to_scrape, websites_to_scrape)
