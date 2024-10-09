from sqlalchemy.exc import IntegrityError

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures

from src.common.schemas.fantasy_schemas import UserID, UserAccountStatus


class TestCrudUser(TestBase):
    def test_create_user_successful(self):
        # Arrange
        user = fantasy_fixtures.user_fixture

        # Act and Assert
        user_before_create = self.db.get_user_by_id(user.id)
        self.assertIsNone(user_before_create)
        self.db.create_user(user)
        user_after_create = self.db.get_user_by_id(user.id)
        self.assertEqual(user, user_after_create)

    def test_create_user_with_existing_email_error(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)
        user_2 = fantasy_fixtures.user_2_fixture.model_copy(deep=True)
        user_2.email = user.email

        # Act and Assert
        with self.assertRaises(IntegrityError) as context:
            self.db.create_user(user_2)
        self.assertIn('UNIQUE constraint failed: users.email', str(context.exception))

    def test_create_user_with_existing_username_error(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)
        user_2 = fantasy_fixtures.user_2_fixture.model_copy(deep=True)
        user_2.username = user.username

        # Act and Assert
        with self.assertRaises(IntegrityError) as context:
            self.db.create_user(user_2)
        self.assertIn('UNIQUE constraint failed: users.username', str(context.exception))

    def test_get_user_by_id(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)

        # Act and Assert
        self.assertEqual(user, self.db.get_user_by_id(user.id))
        self.assertIsNone(self.db.get_user_by_id(UserID("123")))

    def test_get_user_by_email(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)

        # Act and Assert
        self.assertEqual(user, self.db.get_user_by_email(user.email))
        self.assertIsNone(self.db.get_user_by_email("badEmail"))

    def test_get_user_by_username(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)

        # Act and Assert
        self.assertEqual(user, self.db.get_user_by_username(user.username))
        self.assertIsNone(self.db.get_user_by_email("badUsername"))

    def test_update_user_account_status(self):
        # Arrange
        new_account_status = UserAccountStatus.DELETED
        user = fantasy_fixtures.user_fixture
        user.account_status = UserAccountStatus.ACTIVE
        self.db.create_user(user)

        # Act
        self.db.update_user_account_status(user.id, new_account_status)

        # Assert
        user_from_db = self.db.get_user_by_id(user.id)
        self.assertEqual(user.id, user_from_db.id)
        self.assertEqual(new_account_status, user_from_db.account_status)
