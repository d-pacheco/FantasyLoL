from fastapi import HTTPException
from http import HTTPStatus


class UserVerificationException(HTTPException):
    def __init__(self, message) -> None:
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=message
        )
