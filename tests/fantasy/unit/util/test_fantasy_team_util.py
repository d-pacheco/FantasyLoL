from copy import deepcopy
from unittest.mock import patch

from tests.test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures

from src.db.models import FantasyLeagueDraftOrderModel, FantasyTeamModel

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

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_current_week')
    def test_all_teams_fully_drafted_true(self, mock_get_all_fantasy_teams_for_current_week):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        fantasy_teams = [
            create_fantasy_team_model(fantasy_league.id, str(user_id), fantasy_league.current_week)
            for user_id in range(fantasy_league.number_of_teams)
        ]
        mock_get_all_fantasy_teams_for_current_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertTrue(all_teams_fully_drafted)
        self.assertEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        mock_get_all_fantasy_teams_for_current_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_current_week')
    def test_all_teams_fully_drafted_too_few_fantasy_teams(
            self, mock_get_all_fantasy_teams_for_current_week):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        fantasy_teams = [
            create_fantasy_team_model(fantasy_league.id, str(user_id), fantasy_league.current_week)
            for user_id in range(fantasy_league.number_of_teams - 1)
        ]
        mock_get_all_fantasy_teams_for_current_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertNotEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        mock_get_all_fantasy_teams_for_current_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_current_week')
    def test_all_teams_fully_drafted_too_many_fantasy_teams(
            self, mock_get_all_fantasy_teams_for_current_week):
        # !!!!!!!!!  THIS SHOULD NEVER HAPPEN  !!!!!!!!!!
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        fantasy_teams = [
            create_fantasy_team_model(fantasy_league.id, str(user_id), fantasy_league.current_week)
            for user_id in range(fantasy_league.number_of_teams + 1)
        ]
        mock_get_all_fantasy_teams_for_current_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertNotEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        mock_get_all_fantasy_teams_for_current_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_current_week')
    def test_all_teams_fully_drafted_team_missing_top_player(
            self, mock_get_all_fantasy_teams_for_current_week):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        fantasy_teams = [
            create_fantasy_team_model(fantasy_league.id, str(user_id), fantasy_league.current_week)
            for user_id in range(fantasy_league.number_of_teams - 1)
        ]
        missing_top_player_team = create_fantasy_team_model(
            fantasy_league.id, "123", fantasy_league.current_week, set_top_player_id=False
        )
        fantasy_teams.append(missing_top_player_team)
        mock_get_all_fantasy_teams_for_current_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.assertEqual(missing_top_player_team.top_player_id, None)
        mock_get_all_fantasy_teams_for_current_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_current_week')
    def test_all_teams_fully_drafted_team_missing_jungle_player(
            self, mock_get_all_fantasy_teams_for_current_week):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        fantasy_teams = [
            create_fantasy_team_model(fantasy_league.id, str(user_id), fantasy_league.current_week)
            for user_id in range(fantasy_league.number_of_teams - 1)
        ]
        missing_jungle_player_team = create_fantasy_team_model(
            fantasy_league.id, "123", fantasy_league.current_week, set_jungle_player_id=False
        )
        fantasy_teams.append(missing_jungle_player_team)
        mock_get_all_fantasy_teams_for_current_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.assertEqual(missing_jungle_player_team.jungle_player_id, None)
        mock_get_all_fantasy_teams_for_current_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_current_week')
    def test_all_teams_fully_drafted_team_missing_mid_player(
            self, mock_get_all_fantasy_teams_for_current_week):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        fantasy_teams = [
            create_fantasy_team_model(fantasy_league.id, str(user_id), fantasy_league.current_week)
            for user_id in range(fantasy_league.number_of_teams - 1)
        ]
        missing_mid_player_team = create_fantasy_team_model(
            fantasy_league.id, "123", fantasy_league.current_week, set_mid_player_id=False
        )
        fantasy_teams.append(missing_mid_player_team)
        mock_get_all_fantasy_teams_for_current_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.assertEqual(missing_mid_player_team.mid_player_id, None)
        mock_get_all_fantasy_teams_for_current_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_current_week')
    def test_all_teams_fully_drafted_team_missing_adc_player(
            self, mock_get_all_fantasy_teams_for_current_week):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        fantasy_teams = [
            create_fantasy_team_model(fantasy_league.id, str(user_id), fantasy_league.current_week)
            for user_id in range(fantasy_league.number_of_teams - 1)
        ]
        missing_adc_player_team = create_fantasy_team_model(
            fantasy_league.id, "123", fantasy_league.current_week, set_adc_player_id=False
        )
        fantasy_teams.append(missing_adc_player_team)
        mock_get_all_fantasy_teams_for_current_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.assertEqual(missing_adc_player_team.adc_player_id, None)
        mock_get_all_fantasy_teams_for_current_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_current_week')
    def test_all_teams_fully_drafted_team_missing_support_player(
            self, mock_get_all_fantasy_teams_for_current_week):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        fantasy_teams = [
            create_fantasy_team_model(fantasy_league.id, str(user_id), fantasy_league.current_week)
            for user_id in range(fantasy_league.number_of_teams - 1)
        ]
        missing_support_player_team = create_fantasy_team_model(
            fantasy_league.id, "123", fantasy_league.current_week, set_support_player_id=False
        )
        fantasy_teams.append(missing_support_player_team)
        mock_get_all_fantasy_teams_for_current_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.assertEqual(missing_support_player_team.support_player_id, None)
        mock_get_all_fantasy_teams_for_current_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )


def create_fantasy_team_model(
        fantasy_league_id: str,
        user_id: str,
        week: int,
        set_top_player_id: bool = True,
        set_jungle_player_id: bool = True,
        set_mid_player_id: bool = True,
        set_adc_player_id: bool = True,
        set_support_player_id: bool = True) -> FantasyTeamModel:
    return FantasyTeamModel(
        fantasy_league_id=fantasy_league_id,
        user_id=user_id,
        week=week,
        top_player_id=f"topId{user_id}" if set_top_player_id else None,
        jungle_player_id=f"jungleId{user_id}" if set_jungle_player_id else None,
        mid_player_id=f"midId{user_id}" if set_mid_player_id else None,
        adc_player_id=f"adcId{user_id}" if set_adc_player_id else None,
        support_player_id=f"supportId{user_id}" if set_support_player_id else None,
    )
