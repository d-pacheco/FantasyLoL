import uuid
import bcrypt
from typing import List, Optional
import secrets

from src.auth import sign_jwt, Permissions
from src.common.schemas.fantasy_schemas import (
    UserCreate,
    User,
    UserLogin,
    UserID,
    UserAccountStatus
)
from src.db.database_service import DatabaseService
from src.fantasy.exceptions import (
    UserAlreadyExistsException,
    InvalidUsernameOrPasswordException,
    UserVerificationException
)
from .email_verification_service import EmailVerificationService

DEFAULT_PERMISSIONS = [Permissions.FANTASY_READ, Permissions.FANTASY_WRITE, Permissions.RIOT_READ]


class UserService:
    def __init__(
            self,
            database_service: DatabaseService,
            email_verification_service: EmailVerificationService = EmailVerificationService()
    ):
        self.db = database_service
        self.email_verification_service = email_verification_service

    def user_signup(self, user_create: UserCreate) -> str:
        self.validate_username_and_email(user_create.username, user_create.email)
        verification_token = self.send_verification_email_to_user(user_create.email)
        user = self.create_new_user(user_create, DEFAULT_PERMISSIONS, verification_token)
        self.db.create_user(user)

        successful_signup_msg = f"""
        Email verification sent to {user.email}. Please verify email before logging in.
        Check your spam or junk inbox for verification email.
        """
        return successful_signup_msg

    def validate_username_and_email(self, username: str, email: str) -> None:
        valid_account_status = [UserAccountStatus.ACTIVE, UserAccountStatus.PENDING_VERIFICATION]

        user_by_username = self.db.get_user_by_username(username)
        if user_by_username and user_by_username.account_status in valid_account_status:
            raise UserAlreadyExistsException("Username already in use")

        user_by_email = self.db.get_user_by_email(email)
        if user_by_email and user_by_email.account_status in valid_account_status:
            raise UserAlreadyExistsException("Email already in use")

    def create_new_user(
            self,
            user_create: UserCreate,
            permissions: List[Permissions],
            verification_token: Optional[str] = None
    ) -> User:
        new_id = self.generate_new_valid_id()
        hashed_password = self.hash_password(user_create.password)

        user = User(
            id=new_id,
            username=user_create.username,
            email=user_create.email,
            password=hashed_password,
            account_status=UserAccountStatus.PENDING_VERIFICATION,
            verified=False,
            verification_token=verification_token
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

        if not user.verified:
            raise UserVerificationException("You must verify your email before logging in.")

        passwords_match = bcrypt.checkpw(
            user_credentials.password.encode(), user.password
        )
        if not passwords_match:
            raise InvalidUsernameOrPasswordException()

        return sign_jwt(user.id, user.get_permissions())

    def delete_user(self, user_id: UserID) -> None:
        self.db.update_user_account_status(user_id, UserAccountStatus.DELETED)

    def request_verification_email(self, user_email: str) -> None:
        user = self.db.get_user_by_email(user_email)
        if user is None or user.verified:
            return
        verification_token = self.send_verification_email_to_user(user.email)
        self.db.update_user_verification_token(user.id, verification_token)

    def verify_user_email(self, verification_token: str) -> str:
        user = self.db.get_user_by_verification_token(verification_token)
        if user is None:
            raise UserVerificationException("The verification token is either invalid or expired")

        self.db.update_user_verified(user.id, True)
        self.db.update_user_account_status(user.id, UserAccountStatus.ACTIVE)
        self.db.update_user_verification_token(user.id, None)
        success_message = f"Email {user.email} has been verified successfully."
        return success_message

    def send_verification_email_to_user(self, user_email: str) -> str:
        verification_token = self.generate_verification_token()
        email_sent_successfully = self.email_verification_service.send_verification_email(
            user_email,
            verification_token
        )
        if not email_sent_successfully:
            raise UserVerificationException("Invalid email address provided.")
        return verification_token

    @staticmethod
    def generate_verification_token(length=256) -> str:
        return secrets.token_hex(length // 2)
