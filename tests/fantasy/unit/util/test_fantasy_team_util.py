from copy import deepcopy
from unittest.mock import MagicMock

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures

from src.common.schemas.riot_data_schemas import RiotLeagueID, ProPlayerID

from src.fantasy.util import FantasyTeamUtil
from src.fantasy.exceptions import FantasyDraftException


class TestFantasyTeamUtil(TestBase):
    def setUp(self):
        self.mock_db_service = MagicMock()
        self.fantasy_team_util = FantasyTeamUtil(self.mock_db_service)

    def tearDown(self):
        self.mock_db_service.reset_mock()

    def test_validate_player_from_available_league_successful(self):
        # Arrange
        player_id = ProPlayerID("321")
        league_ids = [RiotLeagueID("1234")]
        self.mock_db_service.get_league_ids_for_player.return_value = league_ids
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = league_ids

        # Act and Assert
        try:
            self.fantasy_team_util.validate_player_from_available_league(fantasy_league, player_id)
        except FantasyDraftException:
            self.fail("Validate player from available league encountered an unexpected exception")

    def test_validate_player_from_available_league_player_not_in_available_league_exception(self):
        # Arrange
        player_id = ProPlayerID("321")
        league_ids = [RiotLeagueID("1234")]
        available_league_ids = [RiotLeagueID("4321")]
        self.mock_db_service.get_league_ids_for_player.return_value = league_ids
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = available_league_ids

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            self.fantasy_team_util.validate_player_from_available_league(fantasy_league, player_id)
        self.assertIn("Player not in available league", str(context.exception))
        self.assertNotEqual(league_ids, available_league_ids)

    def test_validate_player_from_available_league_no_league_ids_returned_exception(self):
        # Arrange
        player_id = ProPlayerID("321")
        league_ids: list[RiotLeagueID] = []
        available_league_ids = [RiotLeagueID("4321")]
        self.mock_db_service.get_league_ids_for_player.return_value = league_ids
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = available_league_ids

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            self.fantasy_team_util.validate_player_from_available_league(fantasy_league, player_id)
        self.assertIn("Player not in available league", str(context.exception))
        self.assertNotEqual(league_ids, available_league_ids)
