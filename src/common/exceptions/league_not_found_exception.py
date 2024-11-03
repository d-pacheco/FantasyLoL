from fastapi import HTTPException
from http import HTTPStatus

from src.common.schemas.riot_data_schemas import RiotLeagueID


class LeagueNotFoundException(HTTPException):
    def __init__(self, league_id: RiotLeagueID):
        error_msg = f"Riot league with ID {league_id} not found"
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail=error_msg
        )
