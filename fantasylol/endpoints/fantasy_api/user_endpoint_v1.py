from fastapi import APIRouter, Body

from fantasylol.schemas.fantasy_schemas import UserCreate
from fantasylol.service.fantasy_user_service import UserService


VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
user_service = UserService()


@router.post(
    path="/user/signup",
    tags=["Users"]
)
def user_signup(user: UserCreate = Body(...)):
    return user_service.user_signup(user)
