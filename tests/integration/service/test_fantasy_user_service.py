import bcrypt
import uuid
import copy

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures
from tests.test_util import db_util

from fantasylol.exceptions.user_already_exists_exception import UserAlreadyExistsException
from fantasylol.schemas import fantasy_schemas
from fantasylol.service.fantasy_user_service import UserService


class UserServiceIntegrationTest(FantasyLolTestBase):
    def test_user_signup_successful(self):
        # Arrange
        user_create_fixture = fantasy_fixtures.user_create_fixture
        user_service = UserService()

        # Act
        user_service.user_signup(user_create_fixture)

        # Assert
        user_model_from_db = db_util.get_user_by_username(user_create_fixture.username)
        self.assertIsNotNone(user_model_from_db)
        user_from_db = fantasy_schemas.User.model_validate(user_model_from_db)
        self.assertTrue(uuid.UUID(user_from_db.id, version=4))
        self.assertEqual(user_from_db.username, user_create_fixture.username)
        self.assertEqual(user_from_db.email, user_create_fixture.email)
        self.assertTrue(bcrypt.checkpw(
            str.encode(user_create_fixture.password), str.encode(user_from_db.password)
        ))

    def test_user_signup_username_already_in_use_exception(self):
        # Arrange
        modified_user_create = copy.deepcopy(fantasy_fixtures.user_create_fixture)
        modified_user_create.email = "random_email@email.com"
        user_fixture = fantasy_fixtures.user_fixture
        db_util.create_user(user_fixture)
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
        db_util.create_user(user_fixture)
        user_service = UserService()

        # Act and Assert
        with self.assertRaises(UserAlreadyExistsException) as context:
            user_service.user_signup(modified_user_create)

        self.assertIn('Email already in use', str(context.exception))
