from unittest.mock import MagicMock
import bcrypt
import uuid

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures

from src.common.schemas.fantasy_schemas import User, UserAccountStatus
from src.fantasy.exceptions import (
    UserAlreadyExistsException,
    InvalidUsernameOrPasswordException,
    UserVerificationException
)
from src.fantasy.service import UserService


class UserServiceIntegrationTest(TestBase):
    def setUp(self):
        super().setUp()
        self.mock_email_verification_service = MagicMock()
        self.user_service = UserService(self.db, self.mock_email_verification_service)

    def tearDown(self):
        super().tearDown()
        self.mock_email_verification_service.reset_mock()

    def test_user_signup_successful(self):
        # Arrange
        user_create_fixture = fantasy_fixtures.user_create_fixture
        self.mock_email_verification_service.send_verification_email.return_value = True

        # Act
        response_message = self.user_service.user_signup(user_create_fixture)

        # Assert
        self.assertIn(user_create_fixture.email, response_message)
        user_from_db = self.db.get_user_by_username(user_create_fixture.username)
        self.assertIsNotNone(user_from_db)
        user_from_db = User.model_validate(user_from_db)
        self.assertTrue(uuid.UUID(user_from_db.id, version=4))
        self.assertEqual(user_from_db.username, user_create_fixture.username)
        self.assertEqual(user_from_db.email, user_create_fixture.email)
        self.assertTrue(bcrypt.checkpw(
            str.encode(user_create_fixture.password), user_from_db.password
        ))
        self.assertFalse(user_from_db.verified)
        self.assertIsNotNone(user_from_db.verification_token)

    def test_user_signup_username_already_in_use_exception(self):
        # Arrange
        modified_user_create = fantasy_fixtures.user_create_fixture.model_copy(deep=True)
        modified_user_create.email = "random_email@email.com"
        user_fixture = fantasy_fixtures.user_fixture
        self.db.create_user(user_fixture)

        # Act and Assert
        with self.assertRaises(UserAlreadyExistsException) as context:
            self.user_service.user_signup(modified_user_create)

        self.assertIn('Username already in use', str(context.exception))

    def test_user_signup_email_already_in_use_exception(self):
        # Arrange
        modified_user_create = fantasy_fixtures.user_create_fixture.model_copy(deep=True)
        modified_user_create.username = "randomUsername"
        user_fixture = fantasy_fixtures.user_fixture
        self.db.create_user(user_fixture)

        # Act and Assert
        with self.assertRaises(UserAlreadyExistsException) as context:
            self.user_service.user_signup(modified_user_create)

        self.assertIn('Email already in use', str(context.exception))

    def test_user_login_successful(self):
        # Arrange
        login_credentials = fantasy_fixtures.user_login_fixture
        user = fantasy_fixtures.user_fixture.model_copy(deep=True)
        user.verified = True
        self.db.create_user(user)

        # Act
        login_response = self.user_service.login_user(login_credentials)

        # Assert
        self.assertIsInstance(login_response, dict)
        self.assertIn("access_token", login_response)

    def test_user_login_user_not_verified(self):
        # Arrange
        login_credentials = fantasy_fixtures.user_login_fixture
        user = fantasy_fixtures.user_fixture.model_copy(deep=True)
        user.verified = False
        self.db.create_user(user)

        # Act and Assert
        with self.assertRaises(UserVerificationException) as context:
            self.user_service.login_user(login_credentials)
        self.assertIn("verify your email before logging in", str(context.exception.detail))

    def test_user_login_invalid_username(self):
        # Arrange
        login_credentials = fantasy_fixtures.user_login_fixture.model_copy(deep=True)
        login_credentials.username = "badUsername"
        self.db.create_user(fantasy_fixtures.user_fixture)

        # Act and Assert
        with self.assertRaises(InvalidUsernameOrPasswordException) as context:
            self.user_service.login_user(login_credentials)
        self.assertIn("Invalid username/password", str(context.exception.detail))

    def test_user_login_invalid_password(self):
        # Arrange
        login_credentials = fantasy_fixtures.user_login_fixture.model_copy(deep=True)
        login_credentials.password = "badPassword"
        user = fantasy_fixtures.user_fixture.model_copy(deep=True)
        user.verified = True
        self.db.create_user(user)

        # Act and Assert
        with self.assertRaises(InvalidUsernameOrPasswordException) as context:
            self.user_service.login_user(login_credentials)
        self.assertIn("Invalid username/password", str(context.exception.detail))

    def test_verify_user_email_successful(self):
        # Arrange
        user_verification_token = "123456789"
        user = fantasy_fixtures.user_fixture.model_copy(deep=True)
        user.account_status = UserAccountStatus.PENDING_VERIFICATION
        user.verified = False
        user.verification_token = user_verification_token
        self.db.create_user(user)

        # Act
        response_message = self.user_service.verify_user_email(user_verification_token)

        # Assert
        self.assertIn(f"{user.email} has been verified successfully", response_message)
        user_from_db = self.db.get_user_by_username(user.username)
        self.assertIsNotNone(user_from_db)
        user_from_db = User.model_validate(user_from_db)
        self.assertTrue(user_from_db.verified)
        self.assertIsNone(user_from_db.verification_token)
        self.assertEqual(user_from_db.account_status, UserAccountStatus.ACTIVE)

    def test_verify_user_email_bad_verification_token(self):
        # Arrange
        user_verification_token = "123456789"
        user = fantasy_fixtures.user_fixture.model_copy(deep=True)
        user.account_status = UserAccountStatus.PENDING_VERIFICATION
        user.verified = False
        user.verification_token = user_verification_token
        self.db.create_user(user)

        # Act
        with self.assertRaises(UserVerificationException) as context:
            self.user_service.verify_user_email("badVerificationToken")
        self.assertIn("token is either invalid or expired", str(context.exception.detail))
