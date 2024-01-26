from fastapi import HTTPException
from http import HTTPStatus


class UserAlreadyExistsException(HTTPException):
    def __init__(self, detail):
        super().__init__(
            status_code=HTTPStatus.CONFLICT,
            detail=detail
        )
