from unittest.mock import patch, MagicMock

from tests.test_base import TestBase, BASE_CRUD_PATH
from tests.test_util import fantasy_fixtures

from src.fantasy.exceptions import UserAlreadyExistsException, InvalidUsernameOrPasswordException
from src.fantasy.service import UserService
from src.auth import token_response

BASE_USER_SERVICE_PATH = 'src.fantasy.service.fantasy_user_service.UserService'
SIGN_JWT_PATH = 'src.fantasy.service.fantasy_user_service.sign_jwt'


class UserServiceTest(TestBase):

    @patch(f'{BASE_USER_SERVICE_PATH}.validate_username_and_email')
    @patch(f'{BASE_USER_SERVICE_PATH}.create_new_user')
    @patch(f'{BASE_CRUD_PATH}.create_user')
    def test_user_signup(
            self,
            mock_create_user: MagicMock,
            mock_create_new_user: MagicMock,
            mock_validate_username_and_email: MagicMock):
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
            self, mock_get_user_by_email: MagicMock, mock_get_user_by_username: MagicMock):
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
            self, mock_get_user_by_email: MagicMock, mock_get_user_by_username: MagicMock):
        # Arrange
        user_service = UserService()
        user_username = 'existingUser'
        user_email = 'newEmail@example.com'

        # Act and Assert
        with self.assertRaises(UserAlreadyExistsException) as context:
            user_service.validate_username_and_email(
                username=user_username, email=user_email
            )
        self.assertIn('Username already in use', str(context.exception))
        mock_get_user_by_username.assert_called_once_with(user_username)
        mock_get_user_by_email.assert_not_called()

    @patch(f'{BASE_CRUD_PATH}.get_user_by_username', return_value=None)
    @patch(f'{BASE_CRUD_PATH}.get_user_by_email', return_value=MagicMock())
    def test_validate_username_and_email_exception_email_in_use(
            self, mock_get_user_by_email: MagicMock, mock_get_user_by_username: MagicMock):
        # Arrange
        user_service = UserService()
        user_username = 'newUser'
        user_email = 'existingEmail@example.com'

        # Act and Assert
        with self.assertRaises(UserAlreadyExistsException) as context:
            user_service.validate_username_and_email(
                username=user_username, email=user_email
            )
        self.assertIn('Email already in use', str(context.exception))
        mock_get_user_by_username.assert_called_once_with(user_username)
        mock_get_user_by_email.assert_called_once_with(user_email)

    @patch(f'{BASE_USER_SERVICE_PATH}.generate_new_valid_id')
    @patch(f'{BASE_USER_SERVICE_PATH}.hash_password')
    def test_create_new_user(
            self, mock_hash_password: MagicMock, mock_generate_new_valid_id: MagicMock):
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
    def test_generate_new_valid_id(self, mock_uuid4: MagicMock, mock_get_user_by_id: MagicMock):
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
    def test_hash_password(self, mock_hashpw: MagicMock, mock_gensalt: MagicMock):
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

    @patch(SIGN_JWT_PATH)
    @patch(f'{BASE_CRUD_PATH}.get_user_by_username')
    def test_user_login_successful(
            self, mock_get_user_by_username: MagicMock, mock_sign_jwt: MagicMock):
        # Arrange
        user = fantasy_fixtures.user_fixture
        mock_get_user_by_username.return_value = user
        mock_token_response = token_response("mock-token")
        mock_sign_jwt.return_value = mock_token_response
        user_service = UserService()

        # Act
        token = user_service.login_user(fantasy_fixtures.user_login_fixture)

        # Assert
        mock_get_user_by_username.assert_called_once_with(user.username)
        mock_sign_jwt.assert_called_once_with(user.id)
        self.assertEqual(mock_token_response, token)

    @patch(f'{BASE_CRUD_PATH}.get_user_by_username', return_value=None)
    def test_user_login_invalid_username(self, mock_get_user_by_username: MagicMock):
        # Arrange
        user_login = fantasy_fixtures.user_login_fixture
        user_service = UserService()

        # Act and Assert
        with self.assertRaises(InvalidUsernameOrPasswordException) as context:
            user_service.login_user(user_login)

        self.assertIn("Invalid username/password", str(context.exception.detail))
        mock_get_user_by_username.assert_called_once_with(user_login.username)

    @patch(f'{BASE_CRUD_PATH}.get_user_by_username')
    def test_user_login_invalid_password(self, mock_get_user_by_username: MagicMock):
        # Arrange
        user = fantasy_fixtures.user_fixture
        mock_get_user_by_username.return_value = user
        user_login = fantasy_fixtures.user_login_fixture.model_copy(deep=True)
        user_login.password = "badPassword"
        user_service = UserService()

        # Act and Assert
        with self.assertRaises(InvalidUsernameOrPasswordException) as context:
            user_service.login_user(user_login)

        self.assertIn("Invalid username/password", str(context.exception.detail))
        mock_get_user_by_username.assert_called_once_with(user_login.username)
