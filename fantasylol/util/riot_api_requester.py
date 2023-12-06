import cloudscraper
from http import HTTPStatus
from typing import Dict

from fantasylol.exceptions.riot_api_status_code_assert_exception import \
    RiotApiStatusCodeAssertException


class RiotApiRequester:
    def __init__(self):
        RIOT_API_KEY = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"
        self.client = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            debug=False
        )
        self.default_headers = {
            "Origin": "https://lolesports.com",
            "Referrer": "https://lolesports.com",
            "x-api-key": RIOT_API_KEY
        }

    def make_request(self, url, headers=None) -> Dict:
        if headers is None:
            headers = self.default_headers
        response = self.client.get(url, headers=headers)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        response.close()
        return res_json
