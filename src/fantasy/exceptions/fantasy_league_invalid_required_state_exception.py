from fastapi import HTTPException
from http import HTTPStatus


class FantasyLeagueInvalidRequiredStateException(HTTPException):
    def __init__(self, fantasy_league_id, current_state, required_states):
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Invalid fantasy league state: Fantasy league ({fantasy_league_id}) is"
                   f"currently in state {current_state}, but is required to be in "
                   f"one of the required states: {required_states}"
        )
