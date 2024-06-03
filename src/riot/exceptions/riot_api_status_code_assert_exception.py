from http import HTTPStatus
from typing import List

from ...common.exceptions.fantasy_lol_exception import FantasyLolException


class RiotApiStatusCodeAssertException(FantasyLolException):
    def __init__(self, expected: List[HTTPStatus], received: int, url: str) -> None:
        base_error_msg = "Received unexpected status code. "
        if len(expected) > 1:
            status_code_error_msg = f"Wanted one of {expected} but got {received} in {url}"
        if len(expected) == 1:
            status_code_error_msg = f"Wanted {expected[0]} but got {received} in {url}"
        else:
            status_code_error_msg = "No status code provided in logic..."
        error_msg = base_error_msg + status_code_error_msg
        super().__init__(error_msg)
