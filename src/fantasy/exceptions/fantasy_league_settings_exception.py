from fastapi import HTTPException
from http import HTTPStatus


class FantasyLeagueSettingsException(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=detail
        )
