import cloudscraper  # type: ignore
import logging
import certifi
from requests import Response

logger = logging.getLogger('scraper')


class ApiRequester:
    def __init__(self):
        self.client = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            debug=False
        )

    def make_request(self, url, headers=None) -> Response:
        response = self.client.get(url, headers=headers, verify=certifi.where())
        logger.info(
            f"API Request: GET {url} | Headers: {headers} "
            f"| Response: {response.status_code} {response.text[:500]}"
        )
        return response
