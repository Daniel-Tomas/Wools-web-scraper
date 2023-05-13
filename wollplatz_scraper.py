import re
import json
from typing import Iterable

import requests

from bs4 import BeautifulSoup
from requests import Response

from wools_platform_scraper import WoolsPlatformScraper


class WollplatzScraper(WoolsPlatformScraper):

    def scrape_wool_info(self, wool: Iterable) -> dict | None:
        """Get the info of the first product found in the platform. Returns None if no product is  found"""
        search_term = ' '.join(wool)
        product_link_response = self._crawl_product_link(search_term)
        product_link = self._parse_product_link(product_link_response)
        if product_link is None:
            return None

        product_page_response = self._crawl_product_page(product_link)
        product_info = self._parse_product_page(product_page_response)

        return product_info

    @staticmethod
    def _crawl_product_link(search_term: str) -> Response:
        """Imitates browser search request"""

        params = {
            'type': 'suggest',
            'searchQuery': search_term,
            'filterInitiated': 'false',
            'triggerFilter': '',
            'triggerFilterValue': '',
            'triggerFilterIndex': '',
            'filtersShowAll': 'false',
            'enableFiltersShowAll': 'false',
            'filterValuesShowAll': '',
            'securedFiltersHash': 'false',
            'sortBy': '0',
            'offset': '0',
            'limit': '16',
            'requestIndex': '0',
            'url': '/',
            'sid': '144952626.1794940112.1683024014.1683749831.1683789247.13',
            'snowplow[domain_userid]': 'c6a1994d-02cd-439a-8201-02611f1eb0d9',
            'snowplow[domain_sessionidx]': '1',
            'snowplow[domain_sessionid]': '89acb24b-4a35-438b-83b4-db80bc833caf',
            'index': 'collection:19572',
            'view': '44898be26662b0df',
            'account': 'SQ-119572-1',
            '_': '1683791444885',
        }
        # Search request can be optimized
        response = requests.get('https://dynamic.sooqr.com/suggest/script/', params=params)
        return response

    def _parse_product_link(self, product_link_response: Response) -> str | None:
        """Get link of the first result. Returns None if no product is  found"""

        search_response_dict = self._extract_json_from_response_str(product_link_response.content.decode())
        results_panel = search_response_dict['resultsPanel']
        if results_panel['numberOfResults'] == 0:
            return None

        soup = BeautifulSoup(results_panel['html'], 'html.parser')

        # Finds first product in the product result list
        product_link = soup.find(class_='productlist-imgholder')['href']
        return product_link

    @staticmethod
    def _extract_json_from_response_str(response_str: str) -> dict:
        """Extract dict with search results"""
        pattern = r'searchCallback\.sendSearchQueryByScriptCompleted\(({.*})\);'
        match = re.search(pattern, response_str)

        json_str = match.group(1)
        data = json.loads(json_str)

        return data

    @staticmethod
    def _crawl_product_page(product_link: str) -> Response:
        return requests.get(product_link)

    def _parse_product_page(self, product_page_response: Response) -> dict:
        product_page_html = product_page_response.content.decode()
        product_page_soup = BeautifulSoup(product_page_html, 'html.parser')

        price = self._parse_price(product_page_soup)
        availability = self._parse_availability(product_page_soup)
        needle_size = self._parse_needle_size(product_page_soup)
        composition = self._parse_composition(product_page_soup)

        return {
            'price': price,
            'availability': availability,
            'needle_size': needle_size,
            'composition': composition
        }

    @staticmethod
    def _parse_price(product_page_soup: BeautifulSoup) -> float:
        """
        The price is parsed from the <div id="ContentPlaceHolder1_pnlPDetailBuyHolder">,
        and specifically from the <span class="product-price-amount"> within that div.
        """
        price_str = product_page_soup.find(id='ContentPlaceHolder1_pnlPDetailBuyHolder') \
            .find(class_='product-price-amount').text
        price = float(price_str.replace(',', '.'))
        return price

    @staticmethod
    def _parse_availability(product_page_soup: BeautifulSoup) -> bool:
        """
        The availability status is parsed from the <meta itemprop="availability"> tag,
        specifically from the 'content' attribute of that tag.
        """
        availability_tag = product_page_soup.find(itemprop='availability')
        availability_content_str = availability_tag['content'].lower()

        availability = None
        if 'in' in availability_content_str:
            availability = True
        elif 'out' in availability_content_str:
            availability = False
        else:
            raise ValueError('Availability value not expected')

        return availability

    @staticmethod
    def _parse_needle_size(product_page_soup: BeautifulSoup) -> int:
        """
        The needle size is parsed from a <tr> tag containing the text 'Nadelstärke',
        and specifically from the next <td> tag after the 'Nadelstärke' tag
        """
        needle_size_tag = product_page_soup.find('td', string=re.compile('Nadelstärke', re.IGNORECASE)) \
            .find_next_sibling('td')
        needle_size = int(needle_size_tag.text.split()[0])
        return needle_size

    @staticmethod
    def _parse_composition(product_page_soup: BeautifulSoup) -> str:
        """
        The composition is parsed from a <tr> tag containing the text 'Zusammenstellung',
        and specifically from the next <td> tag after the 'Zusammenstellung' tag.
        """
        composition_tag = product_page_soup.find('td', string=re.compile('Zusammenstellung', re.IGNORECASE)) \
            .find_next_sibling('td')
        composition = composition_tag.text
        return composition
