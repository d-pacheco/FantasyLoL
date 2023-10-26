from fastapi import HTTPException
from http import HTTPStatus

class InvalidQueryStringParamterException(HTTPException):
    def __init__(self, msg: str = "Invalid query string paramter sent"):
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=msg
        )