from fastapi import HTTPException
from http import HTTPStatus


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found"
        )
