from fastapi import HTTPException
from http import HTTPStatus


class InvalidUsernameOrPasswordException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid username/password"
        )
