import cloudscraper
from typing import Dict


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
        res = self.client.get(url, headers=headers)
        res_json = res.json()
        res.close()
        return res_json
