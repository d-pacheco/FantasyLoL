from copy import deepcopy
from unittest.mock import patch

from tests.test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures

from src.db.models import FantasyLeagueDraftOrderModel

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

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_draft_order')
    def test_is_users_position_to_draft_true(self, mock_get_fantasy_league_draft_order):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        users_draft_position = FantasyLeagueDraftOrderModel(
            fantasy_league_id=fantasy_league.id,
            user_id=user.id,
            position=1
        )
        draft_order = [
            users_draft_position,
            FantasyLeagueDraftOrderModel(
                fantasy_league_id=fantasy_league.id,
                user_id="someOtherUser",
                position=2
            )
        ]
        mock_get_fantasy_league_draft_order.return_value = draft_order

        # Act
        is_turn_to_draft = fantasy_team_util.is_users_position_to_draft(fantasy_league, user.id)

        # Assert
        self.assertTrue(is_turn_to_draft)
        self.assertEqual(fantasy_league.current_draft_position, users_draft_position.position)
        mock_get_fantasy_league_draft_order.assert_called_once_with(fantasy_league.id)

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_draft_order')
    def test_is_users_position_to_draft_false(self, mock_get_fantasy_league_draft_order):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_draft_fixture)
        fantasy_league.current_draft_position = 2
        users_draft_position = FantasyLeagueDraftOrderModel(
            fantasy_league_id=fantasy_league.id,
            user_id=user.id,
            position=1
        )
        draft_order = [
            users_draft_position,
            FantasyLeagueDraftOrderModel(
                fantasy_league_id=fantasy_league.id,
                user_id="someOtherUser",
                position=2
            )
        ]
        mock_get_fantasy_league_draft_order.return_value = draft_order

        # Act
        is_turn_to_draft = fantasy_team_util.is_users_position_to_draft(fantasy_league, user.id)

        # Assert
        self.assertFalse(is_turn_to_draft)
        self.assertNotEqual(fantasy_league.current_draft_position, users_draft_position.position)
        mock_get_fantasy_league_draft_order.assert_called_once_with(fantasy_league.id)

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_draft_order')
    def test_is_users_position_to_draft_no_user_draft_position_found_exception(
            self, mock_get_fantasy_league_draft_order):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_draft_fixture)
        fantasy_league.current_draft_position = 1
        users_draft_position = FantasyLeagueDraftOrderModel(
            fantasy_league_id=fantasy_league.id,
            user_id=user.id,
            position=1
        )
        draft_order = [
            users_draft_position,
            FantasyLeagueDraftOrderModel(
                fantasy_league_id=fantasy_league.id,
                user_id="someOtherUser",
                position=2
            )
        ]
        mock_get_fantasy_league_draft_order.return_value = draft_order

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_util.is_users_position_to_draft(fantasy_league, "notFoundUserId")
        self.assertIn("Could not find draft position", str(context.exception))
        mock_get_fantasy_league_draft_order.assert_called_once_with(fantasy_league.id)
