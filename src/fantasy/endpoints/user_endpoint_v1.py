from fastapi import APIRouter, Body

from src.common.schemas.fantasy_schemas import UserCreate, UserLogin
from src.fantasy.service.fantasy_user_service import UserService


VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
user_service = UserService()


@router.post(
    path="/user/signup",
    tags=["Users"]
)
def user_signup(user: UserCreate = Body(...)):
    return user_service.user_signup(user)


@router.post(
    path="/user/login",
    tags=["Users"]
)
def user_login(credentials: UserLogin = Body(...)):
    return user_service.login_user(credentials)
