from fastapi import HTTPException
from http import HTTPStatus


class ProfessionalTeamNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Professional Team not found"
        )
