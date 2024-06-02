from fastapi import HTTPException
from http import HTTPStatus


class ForbiddenException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN
        )
