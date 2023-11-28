from fantasylol.exceptions.fantasy_lol_exception import FantasyLolException

class RiotApiStatusCodeAssertException(FantasyLolException):
    def __init__(self, expected, received, url):
        self.expected = expected
        self.received = received
        self.url = url
        error_msg = f"Received unexpected status code. Wanted {self.expected} but got {self.received} in {self.url}"
        super().__init__(error_msg)