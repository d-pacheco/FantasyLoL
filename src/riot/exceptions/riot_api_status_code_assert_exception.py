from ...common.exceptions.fantasy_lol_exception import FantasyLolException


class RiotApiStatusCodeAssertException(FantasyLolException):
    def __init__(self, expected: int, received: int, url: str) -> None:
        expected = expected
        received = received
        url = url
        error_msg = f"Received unexpected status code. " \
                    f"Wanted {expected} but got {received} in {url}"
        super().__init__(error_msg)
