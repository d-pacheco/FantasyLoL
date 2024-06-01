from fastapi import HTTPException
from http import HTTPStatus


class DraftOrderException(HTTPException):
    def __init__(self, detail) -> None:
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=detail
        )
