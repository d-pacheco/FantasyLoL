from fastapi import HTTPException
from http import HTTPStatus


class FantasyUnavailableException(HTTPException):
    def __init__(self, detail):
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=detail
        )
