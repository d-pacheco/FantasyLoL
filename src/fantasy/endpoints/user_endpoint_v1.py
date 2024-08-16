from fastapi import APIRouter, Body

from src.common.schemas.fantasy_schemas import UserCreate, UserLogin
from src.db.database_config import DatabaseConfig
from src.db.database_connection_provider import DatabaseConnectionProvider
from src.db.database_service import DatabaseService
from src.fantasy.service import UserService


VERSION = "v1"
router = APIRouter(prefix=f"/{VERSION}")
user_service = UserService(
    DatabaseService(
        DatabaseConnectionProvider(
            DatabaseConfig(database_url="sqlite:///./fantasy-league-of-legends.db")
        )
    )
)


@router.post(
    path="/user/signup",
    tags=["Users"]
)
def user_signup(user: UserCreate = Body(...)) -> dict:
    return user_service.user_signup(user)


@router.post(
    path="/user/login",
    tags=["Users"]
)
def user_login(credentials: UserLogin = Body(...)) -> dict:
    return user_service.login_user(credentials)
