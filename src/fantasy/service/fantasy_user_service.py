import uuid
import bcrypt
from typing import List

from src.auth import sign_jwt, FantasyPermissions, RiotPermissions
from src.common.schemas.fantasy_schemas import UserCreate, User, UserLogin, UserID
from src.db.database_service import DatabaseService
from src.fantasy.exceptions import UserAlreadyExistsException, InvalidUsernameOrPasswordException

DEFAULT_PERMISSIONS = [FantasyPermissions.READ, FantasyPermissions.WRITE, RiotPermissions.READ]


class UserService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def user_signup(self, user_create: UserCreate) -> dict:
        self.validate_username_and_email(user_create.username, user_create.email)
        user = self.create_new_user(user_create, DEFAULT_PERMISSIONS)
        self.db.create_user(user)
        return sign_jwt(user.id, DEFAULT_PERMISSIONS)

    def validate_username_and_email(self, username: str, email: str) -> None:
        if self.db.get_user_by_username(username):
            raise UserAlreadyExistsException("Username already in use")
        if self.db.get_user_by_email(email):
            raise UserAlreadyExistsException("Email already in use")

    def create_new_user(self, user_create: UserCreate, permissions: List[str]) -> User:
        new_id = self.generate_new_valid_id()
        hashed_password = self.hash_password(user_create.password)

        user = User(
            id=new_id,
            username=user_create.username,
            email=user_create.email,
            password=hashed_password
        )
        user.set_permissions(permissions)
        return user

    def generate_new_valid_id(self) -> UserID:
        while True:
            new_id = UserID(str(uuid.uuid4()))
            if not self.db.get_user_by_id(new_id):
                break
        return new_id

    @staticmethod
    def hash_password(password) -> bytes:
        salt = bcrypt.gensalt()
        pw_bytes = str.encode(password)
        return bcrypt.hashpw(pw_bytes, salt)

    def login_user(self, user_credentials: UserLogin) -> dict:
        user = self.db.get_user_by_username(user_credentials.username)
        if user is None:
            raise InvalidUsernameOrPasswordException()

        passwords_match = bcrypt.checkpw(
            user_credentials.password.encode(), user.password
        )
        if not passwords_match:
            raise InvalidUsernameOrPasswordException()

        return sign_jwt(user.id, user.get_permissions())
