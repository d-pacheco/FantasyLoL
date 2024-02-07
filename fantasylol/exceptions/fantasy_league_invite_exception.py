from fastapi import HTTPException
from http import HTTPStatus


class FantasyLeagueInviteException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invite exceeds maximum players for the league"
        )
