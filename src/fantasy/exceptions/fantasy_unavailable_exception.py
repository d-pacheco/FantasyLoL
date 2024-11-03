from fastapi import HTTPException
from http import HTTPStatus

from src.common.schemas.riot_data_schemas import RiotLeagueID


class FantasyUnavailableException(HTTPException):
    def __init__(self, league_id: RiotLeagueID) -> None:
        error_msg = f"Riot league with ID {league_id} not available to be used in Fantasy Leagues"
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=error_msg
        )
