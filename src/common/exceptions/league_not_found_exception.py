from fastapi import HTTPException
from http import HTTPStatus


class LeagueNotFoundException(HTTPException):
    def __init__(self, detail="League not found"):
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail=detail
        )
