import uuid
import bcrypt

from ...auth import sign_jwt

from ...common.schemas.fantasy_schemas import UserCreate, User, UserLogin, UserID

from ...db import crud

from ..exceptions import UserAlreadyExistsException, InvalidUsernameOrPasswordException



class UserService:

    def user_signup(self, user_create: UserCreate) -> dict:
        self.validate_username_and_email(user_create.username, user_create.email)
        user = self.create_new_user(user_create)
        crud.create_user(user)
        return sign_jwt(user.id)

    @staticmethod
    def validate_username_and_email(username: str, email: str) -> None:
        if crud.get_user_by_username(username):
            raise UserAlreadyExistsException("Username already in use")
        if crud.get_user_by_email(email):
            raise UserAlreadyExistsException("Email already in use")

    def create_new_user(self, user_create: UserCreate) -> User:
        new_id = self.generate_new_valid_id()
        hashed_password = self.hash_password(user_create.password)

        return User(
            id=new_id,
            username=user_create.username,
            email=user_create.email,
            password=hashed_password
        )

    @staticmethod
    def generate_new_valid_id() -> UserID:
        while True:
            new_id = UserID(str(uuid.uuid4()))
            if not crud.get_user_by_id(new_id):
                break
        return new_id

    @staticmethod
    def hash_password(password) -> bytes:
        salt = bcrypt.gensalt()
        pw_bytes = str.encode(password)
        return bcrypt.hashpw(pw_bytes, salt)

    @staticmethod
    def login_user(user_credentials: UserLogin) -> dict:
        user = crud.get_user_by_username(user_credentials.username)
        if user is None:
            raise InvalidUsernameOrPasswordException()

        passwords_match = bcrypt.checkpw(
            user_credentials.password.encode(), user.password
        )
        if not passwords_match:
            raise InvalidUsernameOrPasswordException()

        return sign_jwt(user.id)
