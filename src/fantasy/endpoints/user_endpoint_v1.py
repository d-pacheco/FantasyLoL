from classy_fastapi import Routable, get, post, put
from fastapi import Body, Depends

from src.auth import JWTBearer
from src.common.schemas.fantasy_schemas import UserCreate, UserLogin, UserID, EmailRequest
from src.fantasy.service import UserService


class UserEndpointV1(Routable):
    def __init__(self, user_service: UserService):
        super().__init__()
        self.__user_service = user_service

    @post(
        path="/user/signup",
        tags=["Users"],
        response_model=None
    )
    def user_signup(
            self,
            user: UserCreate = Body(...)
    ) -> dict:
        response_message = self.__user_service.user_signup(user)
        return {"message": response_message}

    @post(
        path="/user/login",
        tags=["Users"],
        response_model=None
    )
    def user_login(
            self,
            credentials: UserLogin = Body(...)
    ) -> dict:
        return self.__user_service.login_user(credentials)

    @put(
        path="/user/delete",
        tags=["Users"],
        dependencies=[Depends(JWTBearer())],
        status_code=204
    )
    def user_delete(
            self,
            decoded_token: dict = Depends(JWTBearer())
    ):
        user_id = UserID(decoded_token.get("user_id"))  # type: ignore
        self.__user_service.delete_user(user_id)

    @get(
        path="/user/verify-email/{token}",
        tags=["Users"],
        status_code=202
    )
    def verify_email(
            self,
            token: str
    ):
        verification_message = self.__user_service.verify_user_email(token)
        return {"message": verification_message}

    @post(
        path="/user/request-verification-email",
        tags=["Users"],
        status_code=201
    )
    def request_verification_email(
            self,
            request: EmailRequest
    ):
        user_email = request.email
        self.__user_service.request_verification_email(user_email)
        return {"message": f"A new verification email has been sent to {user_email} if it exists."}
