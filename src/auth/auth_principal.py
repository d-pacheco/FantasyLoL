from pydantic import BaseModel

from src.common.schemas.fantasy_schemas import UserID


class AuthPrincipal(BaseModel):
    user_id: UserID
    permissions: list[str]
