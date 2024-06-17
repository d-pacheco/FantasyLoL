import bcrypt
import uuid
import copy

from tests.test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures

from src.db import crud

from src.fantasy.exceptions.user_already_exists_exception import UserAlreadyExistsException
from src.fantasy.exceptions.invalid_username_password_exception import \
    InvalidUsernameOrPasswordException
from src.common.schemas import fantasy_schemas
from src.fantasy.service.fantasy_user_service import UserService


class UserServiceIntegrationTest(FantasyLolTestBase):
    def test_user_signup_successful(self):
        # Arrange
        user_create_fixture = fantasy_fixtures.user_create_fixture
        user_service = UserService()

        # Act
        user_service.user_signup(user_create_fixture)

        # Assert
        user_model_from_db = crud.get_user_by_username(user_create_fixture.username)
        self.assertIsNotNone(user_model_from_db)
        user_from_db = fantasy_schemas.User.model_validate(user_model_from_db)
        self.assertTrue(uuid.UUID(user_from_db.id, version=4))
        self.assertEqual(user_from_db.username, user_create_fixture.username)
        self.assertEqual(user_from_db.email, user_create_fixture.email)
        self.assertTrue(bcrypt.checkpw(
            str.encode(user_create_fixture.password), user_from_db.password
        ))

    def test_user_signup_username_already_in_use_exception(self):
        # Arrange
        modified_user_create = copy.deepcopy(fantasy_fixtures.user_create_fixture)
        modified_user_create.email = "random_email@email.com"
        user_fixture = fantasy_fixtures.user_fixture
        crud.create_user(user_fixture)
        user_service = UserService()

        # Act and Assert
        with self.assertRaises(UserAlreadyExistsException) as context:
            user_service.user_signup(modified_user_create)

        self.assertIn('Username already in use', str(context.exception))

    def test_user_signup_email_already_in_use_exception(self):
        # Arrange
        modified_user_create = copy.deepcopy(fantasy_fixtures.user_create_fixture)
        modified_user_create.username = "randomUsername"
        user_fixture = fantasy_fixtures.user_fixture
        crud.create_user(user_fixture)
        user_service = UserService()

        # Act and Assert
        with self.assertRaises(UserAlreadyExistsException) as context:
            user_service.user_signup(modified_user_create)

        self.assertIn('Email already in use', str(context.exception))

    def test_user_login_successful(self):
        # Arrange
        login_credentials = fantasy_fixtures.user_login_fixture
        crud.create_user(fantasy_fixtures.user_fixture)
        user_service = UserService

        # Act
        login_response = user_service.login_user(login_credentials)

        # Assert
        self.assertIsInstance(login_response, dict)
        self.assertIn("access_token", login_response)

    def test_user_login_invalid_username(self):
        # Arrange
        login_credentials = copy.deepcopy(fantasy_fixtures.user_login_fixture)
        login_credentials.username = "badUsername"
        crud.create_user(fantasy_fixtures.user_fixture)
        user_service = UserService()

        # Act and Assert
        with self.assertRaises(InvalidUsernameOrPasswordException) as context:
            user_service.login_user(login_credentials)
        self.assertIn("Invalid username/password", str(context.exception.detail))

    def test_user_login_invalid_password(self):
        # Arrange
        login_credentials = copy.deepcopy(fantasy_fixtures.user_login_fixture)
        login_credentials.password = "badPassword"
        crud.create_user(fantasy_fixtures.user_fixture)
        user_service = UserService()

        # Act and Assert
        with self.assertRaises(InvalidUsernameOrPasswordException) as context:
            user_service.login_user(login_credentials)
        self.assertIn("Invalid username/password", str(context.exception.detail))
