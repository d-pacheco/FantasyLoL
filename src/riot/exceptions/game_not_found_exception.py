from fastapi import HTTPException
from http import HTTPStatus


class GameNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Game not found"
        )
