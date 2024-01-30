from unittest.mock import patch, MagicMock
import uuid

from tests.fantasy_lol_test_base import FantasyLolTestBase

from fantasylol.service.fantasy.fantasy_league_service import FantasyLeagueService
from fantasylol.schemas.fantasy_schemas import FantasyLeague
from tests.test_util import fantasy_fixtures

FANTASY_LEAGUE_SERV_PATH = 'fantasylol.service.fantasy.fantasy_league_service.FantasyLeagueService'
BASE_CRUD_PATH = 'fantasylol.db.crud'


class TestFantasyLeagueService(FantasyLolTestBase):

    @patch(f'{FANTASY_LEAGUE_SERV_PATH}.generate_new_valid_id')
    @patch(f'{BASE_CRUD_PATH}.create_fantasy_league')
    def test_create_fantasy_league(self, mock_create_fantasy_league, mock_generate_new_valid_id):
        # Arrange
        fantasy_league_id = str(uuid.uuid4())
        owner_id = str(uuid.uuid4())
        fantasy_league_create = fantasy_fixtures.fantasy_league_create_fixture
        expected_fantasy_league = FantasyLeague(
            id=fantasy_league_id,
            owner_id=owner_id,
            name=fantasy_league_create.name
        )
        mock_generate_new_valid_id.return_value = fantasy_league_id
        fantasy_league_service = FantasyLeagueService()

        # Act
        fantasy_league = fantasy_league_service.create_fantasy_league(
            owner_id, fantasy_league_create
        )

        # Assert
        self.assertEqual(expected_fantasy_league, fantasy_league)
        mock_generate_new_valid_id.assert_called_once()
        mock_create_fantasy_league.assert_called_once_with(expected_fantasy_league)

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id', side_effect=[MagicMock(), None])
    @patch('uuid.uuid4', side_effect=['id1', 'id2'])
    def test_generate_new_valid_id(self, mock_uuid4, mock_get_user_by_id):
        # Arrange
        fantasy_league_service = FantasyLeagueService()

        # Act
        generated_id = fantasy_league_service.generate_new_valid_id()

        # Assert
        self.assertEqual(generated_id, 'id2')
        mock_uuid4.assert_called()
        self.assertEqual(mock_uuid4.call_count, 2)
        mock_get_user_by_id.assert_any_call('id1')
        mock_get_user_by_id.assert_any_call('id2')
        mock_get_user_by_id.assert_called_with('id2')
