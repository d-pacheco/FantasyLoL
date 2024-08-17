from unittest.mock import patch, MagicMock
import uuid
import copy

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueID,
    FantasyLeagueSettings,
    FantasyLeagueStatus,
    UserID
)
from src.fantasy.exceptions import FantasyLeagueNotFoundException, ForbiddenException
from src.fantasy.service import FantasyLeagueService

FANTASY_LEAGUE_SERV_PATH = 'src.fantasy.service.fantasy_league_service.FantasyLeagueService'


class TestFantasyLeagueService(TestBase):
    def setUp(self):
        self.mock_db_service = MagicMock()
        self.fantasy_league_service = FantasyLeagueService(self.mock_db_service)

    def tearDown(self):
        self.mock_db_service.reset_mock()

    @patch(f'{FANTASY_LEAGUE_SERV_PATH}.generate_new_valid_id')
    def test_create_fantasy_league(self, mock_generate_new_valid_id: MagicMock):
        # Arrange
        fantasy_league_id = FantasyLeagueID(str(uuid.uuid4()))
        owner_id = UserID(str(uuid.uuid4()))
        fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture
        expected_fantasy_league = FantasyLeague(
            id=fantasy_league_id,
            owner_id=owner_id,
            status=FantasyLeagueStatus.PRE_DRAFT,
            name=fantasy_league_settings.name
        )
        self.mock_db_service.get_fantasy_league_by_id.return_value = expected_fantasy_league
        mock_generate_new_valid_id.return_value = fantasy_league_id

        # Act
        fantasy_league = self.fantasy_league_service.create_fantasy_league(
            owner_id, fantasy_league_settings
        )

        # Assert
        self.assertEqual(expected_fantasy_league, fantasy_league)
        mock_generate_new_valid_id.assert_called_once()
        self.mock_db_service.create_fantasy_league.assert_called_once_with(expected_fantasy_league)

    @patch('uuid.uuid4', side_effect=['id1', 'id2'])
    def test_generate_new_valid_id(self, mock_uuid4: MagicMock):
        # Arrange
        mock_get_fantasy_league_by_id = MagicMock(side_effect=[MagicMock(), None])
        self.mock_db_service.get_fantasy_league_by_id = mock_get_fantasy_league_by_id

        # Act
        generated_id = self.fantasy_league_service.generate_new_valid_id()

        # Assert
        self.assertEqual(generated_id, 'id2')
        mock_uuid4.assert_called()
        self.assertEqual(mock_uuid4.call_count, 2)
        mock_get_fantasy_league_by_id.assert_any_call('id1')
        mock_get_fantasy_league_by_id.assert_any_call('id2')
        mock_get_fantasy_league_by_id.assert_called_with('id2')

    def test_get_fantasy_league_settings_successful(self):
        # Arrange
        expected_fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture

        self.mock_db_service.get_fantasy_league_by_id.return_value = fantasy_league

        owner_id = fantasy_league.owner_id
        league_id = fantasy_league.id

        # Act
        fantasy_league_settings = self.fantasy_league_service.get_fantasy_league_settings(
            owner_id, league_id
        )

        # Assert
        self.assertEqual(expected_fantasy_league_settings, fantasy_league_settings)
        self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(fantasy_league.id)

    def test_get_fantasy_league_settings_no_league_found_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = None

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.get_fantasy_league_settings(
                fantasy_league.owner_id, fantasy_league.id
            )
        self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(fantasy_league.id)

    def test_get_fantasy_league_settings_forbidden_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        owner_id = UserID(str(uuid.uuid4()))
        league_id = fantasy_league.id

        self.mock_db_service.get_fantasy_league_by_id.return_value = fantasy_league

        # Act and Assert
        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.get_fantasy_league_settings(owner_id, league_id)
        self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(league_id)

    def test_update_fantasy_league_settings_successful(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        owner_id = fantasy_league.owner_id
        league_id = fantasy_league.id

        expected_updated_league_settings = FantasyLeagueSettings(
            name="Update fantasy league",
            number_of_teams=10
        )
        expected_updated_league = copy.deepcopy(fantasy_league)
        expected_updated_league.name = expected_updated_league_settings.name
        expected_updated_league.number_of_teams = expected_updated_league_settings.number_of_teams

        self.mock_db_service.get_fantasy_league_by_id.return_value = fantasy_league
        self.mock_db_service.update_fantasy_league_settings.return_value = expected_updated_league

        # Act
        updated_settings = self.fantasy_league_service.update_fantasy_league_settings(
            owner_id, league_id, expected_updated_league_settings
        )

        # Assert
        self.assertEqual(expected_updated_league_settings, updated_settings)
        self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(league_id)
        self.mock_db_service.update_fantasy_league_settings.assert_called_once_with(
            league_id, expected_updated_league_settings
        )

    def test_update_fantasy_league_settings_league_not_found_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        owner_id = fantasy_league.owner_id
        league_id = fantasy_league.id

        updated_league_settings = FantasyLeagueSettings(
            name="Update fantasy league",
            number_of_teams=10
        )
        self.mock_db_service.get_fantasy_league_by_id.return_value = None

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.update_fantasy_league_settings(
                owner_id, league_id, updated_league_settings
            )
        self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(league_id)
        self.mock_db_service.update_fantasy_league_settings.assert_not_called()

    def test_update_fantasy_league_settings_forbidden_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        owner_id = UserID(str(uuid.uuid4()))
        league_id = fantasy_league.id

        updated_league_settings = FantasyLeagueSettings(
            name="Update fantasy league",
            number_of_teams=10
        )

        self.mock_db_service.get_fantasy_league_by_id.return_value = fantasy_league

        # Act and Assert
        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.update_fantasy_league_settings(
                owner_id, league_id, updated_league_settings
            )
        self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(league_id)
        self.mock_db_service.update_fantasy_league_settings.assert_not_called()
