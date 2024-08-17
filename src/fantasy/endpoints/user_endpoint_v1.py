from fastapi import APIRouter, Body, Depends

from src.common.schemas.fantasy_schemas import UserCreate, UserLogin
from src.db.database_service import db_service
from src.fantasy.service import UserService


VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
user_service = UserService(db_service)


def get_user_service() -> UserService:
    return user_service


@router.post(
    path="/user/signup",
    tags=["Users"],
    response_model=None
)
def user_signup(
        user: UserCreate = Body(...),
        service: UserService = Depends(get_user_service)
) -> dict:
    return service.user_signup(user)


@router.post(
    path="/user/login",
    tags=["Users"],
    response_model=None
)
def user_login(
        credentials: UserLogin = Body(...),
        service: UserService = Depends(get_user_service)
) -> dict:
    return service.login_user(credentials)
