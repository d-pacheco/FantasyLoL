from unittest.mock import patch, MagicMock
import uuid
import copy

from ...test_base import FantasyLolTestBase
from ...test_util import fantasy_fixtures

from fantasy.exceptions.fantasy_league_not_found_exception import FantasyLeagueNotFoundException
from fantasy.exceptions.forbidden_exception import ForbiddenException
from fantasy.service.fantasy_league_service import FantasyLeagueService
from common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueSettings,
    FantasyLeagueStatus
)

FANTASY_LEAGUE_SERV_PATH = 'fantasy.service.fantasy_league_service.FantasyLeagueService'
BASE_CRUD_PATH = 'db.crud'


class TestFantasyLeagueService(FantasyLolTestBase):

    @patch(f'{FANTASY_LEAGUE_SERV_PATH}.generate_new_valid_id')
    @patch(f'{BASE_CRUD_PATH}.create_fantasy_league')
    def test_create_fantasy_league(self, mock_create_fantasy_league, mock_generate_new_valid_id):
        # Arrange
        fantasy_league_id = str(uuid.uuid4())
        owner_id = str(uuid.uuid4())
        fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture
        expected_fantasy_league = FantasyLeague(
            id=fantasy_league_id,
            owner_id=owner_id,
            status=FantasyLeagueStatus.PRE_DRAFT,
            name=fantasy_league_settings.name
        )
        mock_generate_new_valid_id.return_value = fantasy_league_id
        fantasy_league_service = FantasyLeagueService()

        # Act
        fantasy_league = fantasy_league_service.create_fantasy_league(
            owner_id, fantasy_league_settings
        )

        # Assert
        self.assertEqual(expected_fantasy_league, fantasy_league)
        mock_generate_new_valid_id.assert_called_once()
        mock_create_fantasy_league.assert_called_once_with(expected_fantasy_league)

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id', side_effect=[MagicMock(), None])
    @patch('uuid.uuid4', side_effect=['id1', 'id2'])
    def test_generate_new_valid_id(self, mock_uuid4, mock_get_fantasy_league_by_id):
        # Arrange
        fantasy_league_service = FantasyLeagueService()

        # Act
        generated_id = fantasy_league_service.generate_new_valid_id()

        # Assert
        self.assertEqual(generated_id, 'id2')
        mock_uuid4.assert_called()
        self.assertEqual(mock_uuid4.call_count, 2)
        mock_get_fantasy_league_by_id.assert_any_call('id1')
        mock_get_fantasy_league_by_id.assert_any_call('id2')
        mock_get_fantasy_league_by_id.assert_called_with('id2')

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_get_fantasy_league_settings_successful(self, mock_get_fantasy_league_by_id):
        # Arrange
        expected_fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        mock_get_fantasy_league_by_id.return_value = fantasy_league
        owner_id = fantasy_league.owner_id
        league_id = fantasy_league.id
        fantasy_league_service = FantasyLeagueService()

        # Act
        fantasy_league_settings = fantasy_league_service.get_fantasy_league_settings(
            owner_id, league_id
        )

        # Assert
        self.assertEqual(expected_fantasy_league_settings, fantasy_league_settings)
        mock_get_fantasy_league_by_id.assert_called_once_with(league_id)

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_get_fantasy_league_settings_no_league_found_exception(
            self, mock_get_fantasy_league_by_id):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        mock_get_fantasy_league_by_id.return_value = None
        owner_id = fantasy_league.owner_id
        league_id = fantasy_league.id
        fantasy_league_service = FantasyLeagueService()

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_league_service.get_fantasy_league_settings(owner_id, league_id)
        mock_get_fantasy_league_by_id.assert_called_once_with(league_id)

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_get_fantasy_league_settings_forbidden_exception(
            self, mock_get_fantasy_league_by_id):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        mock_get_fantasy_league_by_id.return_value = fantasy_league
        owner_id = str(uuid.uuid4())
        league_id = fantasy_league.id
        fantasy_league_service = FantasyLeagueService()

        # Act and Assert
        with self.assertRaises(ForbiddenException):
            fantasy_league_service.get_fantasy_league_settings(owner_id, league_id)
        mock_get_fantasy_league_by_id.assert_called_once_with(league_id)

    @patch(f'{BASE_CRUD_PATH}.update_fantasy_league_settings')
    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_update_fantasy_league_settings_successful(
            self, mock_get_fantasy_league_by_id, mock_update_fantasy_league_settings):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        mock_get_fantasy_league_by_id.return_value = fantasy_league
        owner_id = fantasy_league.owner_id
        league_id = fantasy_league.id

        updated_league_settings = FantasyLeagueSettings(
            name="Update fantasy league",
            number_of_teams=10
        )
        expected_updated_league = copy.deepcopy(fantasy_league)
        expected_updated_league.name = updated_league_settings.name
        expected_updated_league.number_of_teams = updated_league_settings.number_of_teams
        mock_update_fantasy_league_settings.return_value = expected_updated_league

        fantasy_league_service = FantasyLeagueService()

        # Act
        updated_league = fantasy_league_service.update_fantasy_league_settings(
            owner_id, league_id, updated_league_settings
        )

        # Assert
        self.assertEqual(expected_updated_league, updated_league)
        mock_get_fantasy_league_by_id.assert_called_once_with(league_id)
        mock_update_fantasy_league_settings.assert_called_once_with(
            league_id, updated_league_settings
        )

    @patch(f'{BASE_CRUD_PATH}.update_fantasy_league_settings')
    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_update_fantasy_league_settings_league_not_found_exception(
            self, mock_get_fantasy_league_by_id, mock_update_fantasy_league_settings):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        mock_get_fantasy_league_by_id.return_value = None
        owner_id = fantasy_league.owner_id
        league_id = fantasy_league.id

        updated_league_settings = FantasyLeagueSettings(
            name="Update fantasy league",
            number_of_teams=10
        )

        fantasy_league_service = FantasyLeagueService()

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_league_service.update_fantasy_league_settings(
                owner_id, league_id, updated_league_settings
            )
        mock_get_fantasy_league_by_id.assert_called_once_with(league_id)
        mock_update_fantasy_league_settings.assert_not_called()

    @patch(f'{BASE_CRUD_PATH}.update_fantasy_league_settings')
    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_update_fantasy_league_settings_forbidden_exception(
            self, mock_get_fantasy_league_by_id, mock_update_fantasy_league_settings):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        mock_get_fantasy_league_by_id.return_value = fantasy_league
        owner_id = str(uuid.uuid4())
        league_id = fantasy_league.id

        updated_league_settings = FantasyLeagueSettings(
            name="Update fantasy league",
            number_of_teams=10
        )

        fantasy_league_service = FantasyLeagueService()

        # Act and Assert
        with self.assertRaises(ForbiddenException):
            fantasy_league_service.update_fantasy_league_settings(
                owner_id, league_id, updated_league_settings
            )
        mock_get_fantasy_league_by_id.assert_called_once_with(league_id)
        mock_update_fantasy_league_settings.assert_not_called()
