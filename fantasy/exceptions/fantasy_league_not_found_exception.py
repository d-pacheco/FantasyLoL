from fastapi import HTTPException
from http import HTTPStatus


class FantasyLeagueNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Fantasy League not found"
        )
