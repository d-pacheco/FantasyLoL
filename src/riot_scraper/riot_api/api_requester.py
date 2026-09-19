import cloudscraper  # type: ignore
import logging
import certifi
from requests import Response

logger = logging.getLogger("scraper.api")


class ApiRequester:
    def __init__(self):
        self.client = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "desktop": True}, debug=False
        )

    # (connect timeout, read timeout) in seconds. Without this, a stalled Riot
    # connection blocks the scraper thread indefinitely, wedging the match job
    # (APScheduler max_instances=1) with no completion log and no error.
    REQUEST_TIMEOUT = (10, 30)

    def make_request(self, url, headers=None) -> Response:
        response = self.client.get(
            url, headers=headers, verify=certifi.where(), timeout=self.REQUEST_TIMEOUT
        )
        logger.info(
            f"API Request: GET {url} | Headers: {headers} "
            f"| Response: {response.status_code} {response.text[:500]}"
        )
        return response
