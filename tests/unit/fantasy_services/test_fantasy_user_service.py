from unittest.mock import patch, MagicMock

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures

from fantasylol.exceptions.user_already_exists_exception import UserAlreadyExistsException
from fantasylol.service.fantasy_user_service import UserService

BASE_USER_SERVICE_PATH = 'fantasylol.service.fantasy_user_service.UserService'
BASE_CRUD_PATH = 'fantasylol.db.crud'


class UserServiceTest(FantasyLolTestBase):

    @patch(f'{BASE_USER_SERVICE_PATH}.validate_username_and_email')
    @patch(f'{BASE_USER_SERVICE_PATH}.create_new_user')
    @patch(f'{BASE_CRUD_PATH}.create_user')
    def test_user_signup(
            self, mock_create_user, mock_create_new_user, mock_validate_username_and_email):
        # Arrange
        create_user_fixture = fantasy_fixtures.user_create_fixture
        mock_create_new_user.return_value = fantasy_fixtures.user_fixture
        user_service = UserService()

        # Act
        user_service.user_signup(create_user_fixture)

        # Assert
        mock_validate_username_and_email.assert_called_once_with(
            create_user_fixture.username, create_user_fixture.email
        )
        mock_create_new_user.assert_called_once_with(create_user_fixture)
        mock_create_user.assert_called_once_with(fantasy_fixtures.user_fixture)

    @patch(f'{BASE_CRUD_PATH}.get_user_by_username', return_value=None)
    @patch(f'{BASE_CRUD_PATH}.get_user_by_email', return_value=None)
    def test_validate_username_and_email_no_error_thrown(
            self, mock_get_user_by_email, mock_get_user_by_username):
        # Arrange
        user_service = UserService()

        # Act
        user_service.validate_username_and_email(
            username='new_user', email='newuser@example.com'
        )

        # Assert
        mock_get_user_by_username.assert_called_once_with('new_user')
        mock_get_user_by_email.assert_called_once_with('newuser@example.com')

    @patch(f'{BASE_CRUD_PATH}.get_user_by_username', return_value=MagicMock())
    @patch(f'{BASE_CRUD_PATH}.get_user_by_email', return_value=None)
    def test_validate_username_and_email_exception_username_in_use(
            self, mock_get_user_by_email, mock_get_user_by_username):
        # Arrange
        user_service = UserService()

        # Act and Assert
        with self.assertRaises(UserAlreadyExistsException) as context:
            user_service.validate_username_and_email(
                username='existinguser', email='newuser@example.com'
            )

        self.assertIn('Username already in use', str(context.exception))
        mock_get_user_by_username.assert_called_once_with('existinguser')
        mock_get_user_by_email.assert_not_called()

    @patch(f'{BASE_CRUD_PATH}.get_user_by_username', return_value=None)
    @patch(f'{BASE_CRUD_PATH}.get_user_by_email', return_value=MagicMock())
    def test_validate_username_and_email_exception_email_in_use(
            self, mock_get_user_by_email, mock_get_user_by_username):
        # Arrange
        user_service = UserService()

        # Act and Assert
        with self.assertRaises(UserAlreadyExistsException) as context:
            user_service.validate_username_and_email(
                username='newuser', email='existinguser@example.com'
            )

        self.assertIn('Email already in use', str(context.exception))
        mock_get_user_by_username.assert_called_once_with('newuser')
        mock_get_user_by_email.assert_called_once_with('existinguser@example.com')

    @patch(f'{BASE_USER_SERVICE_PATH}.generate_new_valid_id')
    @patch(f'{BASE_USER_SERVICE_PATH}.hash_password')
    def test_create_new_user(self, mock_hash_password, mock_generate_new_valid_id):
        # Arrange
        user_create_fixture = fantasy_fixtures.user_create_fixture
        user_fixture = fantasy_fixtures.user_fixture
        mock_hash_password.return_value = user_fixture.password
        mock_generate_new_valid_id.return_value = user_fixture.id
        user_service = UserService()

        # Act
        new_user = user_service.create_new_user(user_create_fixture)

        # Assert
        self.assertEqual(user_fixture, new_user)
        mock_hash_password.assert_called_once_with(user_create_fixture.password)
        mock_generate_new_valid_id.assert_called_once()

    @patch(f'{BASE_CRUD_PATH}.get_user_by_id', side_effect=[MagicMock(), None, None, None])
    @patch('uuid.uuid4', side_effect=['id1', 'id2', 'id3', 'id4'])
    def test_generate_new_valid_id(self, mock_uuid4, mock_get_user_by_id):
        # Arrange
        user_service = UserService()

        # Act
        generated_id = user_service.generate_new_valid_id()

        # Assert
        self.assertEqual(generated_id, 'id2')
        mock_uuid4.assert_called()
        self.assertEqual(mock_uuid4.call_count, 2)
        mock_get_user_by_id.assert_any_call('id1')
        mock_get_user_by_id.assert_any_call('id2')
        mock_get_user_by_id.assert_called_with('id2')

    @patch('bcrypt.gensalt', return_value=b'$2b$12$abcdefghijklmnopqrstuv')
    @patch('bcrypt.hashpw', return_value=b'hashed_password')
    def test_hash_password(self, mock_hashpw, mock_gensalt):
        # Arrange
        user_service = UserService()
        password = "secure_password"

        # Act
        hashed_password = user_service.hash_password(password)

        # Assert
        self.assertEqual(hashed_password, b'hashed_password')
        mock_gensalt.assert_called_once()
        mock_hashpw.assert_called_once_with(
            password.encode('utf-8'), b'$2b$12$abcdefghijklmnopqrstuv'
        )
