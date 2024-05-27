from copy import deepcopy
from unittest.mock import patch

from tests.test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures

from src.fantasy.util.fantasty_team_util import FantasyTeamUtil
from src.fantasy.exceptions.fantasy_draft_exception import FantasyDraftException

BASE_CRUD_PATH = 'src.db.crud'

fantasy_team_util = FantasyTeamUtil()


class TestFantasyTeamUtil(FantasyLolTestBase):
    @patch(f'{BASE_CRUD_PATH}.get_league_ids_for_player')
    def test_validate_player_from_available_league_successful(
            self, mock_get_league_ids_for_player):
        # Arrange
        player_id = "321"
        league_ids = ["1234"]
        mock_get_league_ids_for_player.return_value = league_ids
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = league_ids

        # Act and Assert
        try:
            fantasy_team_util.validate_player_from_available_league(fantasy_league, player_id)
        except FantasyDraftException:
            self.fail("Validate player from available league encountered an unexpected exception")

    @patch(f'{BASE_CRUD_PATH}.get_league_ids_for_player')
    def test_validate_player_from_available_league_player_not_in_available_league_exception(
            self, mock_get_league_ids_for_player):
        # Arrange
        player_id = "321"
        league_ids = ["1234"]
        available_league_ids = ["4321"]
        mock_get_league_ids_for_player.return_value = league_ids
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = available_league_ids

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_util.validate_player_from_available_league(fantasy_league, player_id)
        self.assertIn("Player not in available league", str(context.exception))
        self.assertNotEqual(league_ids, available_league_ids)

    @patch(f'{BASE_CRUD_PATH}.get_league_ids_for_player')
    def test_validate_player_from_available_league_no_league_ids_returned_exception(
            self, mock_get_league_ids_for_player):
        # Arrange
        player_id = "321"
        league_ids = []
        available_league_ids = ["4321"]
        mock_get_league_ids_for_player.return_value = league_ids
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = available_league_ids

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_util.validate_player_from_available_league(fantasy_league, player_id)
        self.assertIn("Player not in available league", str(context.exception))
        self.assertNotEqual(league_ids, available_league_ids)
