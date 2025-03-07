from copy import deepcopy
from unittest.mock import MagicMock

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeagueDraftOrder,
    FantasyTeam,
    UserID
)
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

    def test_is_users_position_to_draft_true(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture.model_copy()
        fantasy_league.current_draft_position = 1
        user_draft_position = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=user.id, position=1
        )
        other_user_draft_position = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=UserID("someOtherUser"), position=2
        )
        draft_order = [user_draft_position, other_user_draft_position]
        self.mock_db_service.get_fantasy_league_draft_order.return_value = draft_order

        # Act
        is_turn_to_draft = self.fantasy_team_util.is_users_position_to_draft(
            fantasy_league, user.id)

        # Assert
        self.assertTrue(is_turn_to_draft)
        self.assertEqual(fantasy_league.current_draft_position, user_draft_position.position)
        self.mock_db_service.get_fantasy_league_draft_order.assert_called_once_with(
            fantasy_league.id)

    def test_is_users_position_to_draft_false(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture.model_copy()
        fantasy_league.current_draft_position = 2
        user_draft_position = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=user.id, position=1
        )
        other_user_draft_position = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=UserID("someOtherUser"), position=2
        )
        draft_order = [user_draft_position, other_user_draft_position]
        self.mock_db_service.get_fantasy_league_draft_order.return_value = draft_order

        # Act
        is_turn_to_draft = self.fantasy_team_util.is_users_position_to_draft(
            fantasy_league, user.id)

        # Assert
        self.assertFalse(is_turn_to_draft)
        self.assertNotEqual(fantasy_league.current_draft_position, user_draft_position.position)
        self.mock_db_service.get_fantasy_league_draft_order.assert_called_once_with(
            fantasy_league.id)

    def test_is_users_position_to_draft_no_user_draft_position_found_exception(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_draft_fixture)
        fantasy_league.current_draft_position = 1
        user_draft_position = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=user.id, position=1
        )
        other_user_draft_position = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=UserID("someOtherUser"), position=2
        )
        draft_order = [user_draft_position, other_user_draft_position]
        self.mock_db_service.get_fantasy_league_draft_order.return_value = draft_order

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            self.fantasy_team_util.is_users_position_to_draft(
                fantasy_league, UserID("notFoundUserId"))
        self.assertIn("Could not find draft position", str(context.exception))
        self.mock_db_service.get_fantasy_league_draft_order.assert_called_once_with(
            fantasy_league.id)

    def test_all_teams_fully_drafted_true(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        assert fantasy_league.current_week is not None, "current_week should not be None"
        fantasy_teams = [
            create_fantasy_team(
                fantasy_league.id, UserID(str(user_id)), fantasy_league.current_week
            )
            for user_id in range(fantasy_league.number_of_teams)
        ]
        self.mock_db_service.get_all_fantasy_teams_for_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = self.fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertTrue(all_teams_fully_drafted)
        self.assertEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.mock_db_service.get_all_fantasy_teams_for_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    def test_all_teams_fully_drafted_too_few_fantasy_teams(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        assert fantasy_league.current_week is not None, "current_week should not be None"
        fantasy_teams = [
            create_fantasy_team(
                fantasy_league.id, UserID(str(user_id)), fantasy_league.current_week
            )
            for user_id in range(fantasy_league.number_of_teams - 1)
        ]
        self.mock_db_service.get_all_fantasy_teams_for_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = self.fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertNotEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.mock_db_service.get_all_fantasy_teams_for_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    def test_all_teams_fully_drafted_too_many_fantasy_teams(self):
        # !!!!!!!!!  THIS SHOULD NEVER HAPPEN  !!!!!!!!!!
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        assert fantasy_league.current_week is not None, "current_week should not be None"
        fantasy_teams = [
            create_fantasy_team(
                fantasy_league.id, UserID(str(user_id)), fantasy_league.current_week
            )
            for user_id in range(fantasy_league.number_of_teams + 1)
        ]
        self.mock_db_service.get_all_fantasy_teams_for_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = self.fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertNotEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.mock_db_service.get_all_fantasy_teams_for_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    def test_all_teams_fully_drafted_team_missing_top_player(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        assert fantasy_league.current_week is not None, "current_week should not be None"
        fantasy_teams = [
            create_fantasy_team(
                fantasy_league.id, UserID(str(user_id)), fantasy_league.current_week
            )
            for user_id in range(fantasy_league.number_of_teams - 1)
        ]
        missing_top_player_team = create_fantasy_team(
            fantasy_league.id, UserID("123"), fantasy_league.current_week, set_top_player_id=False
        )
        fantasy_teams.append(missing_top_player_team)
        self.mock_db_service.get_all_fantasy_teams_for_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = self.fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.assertEqual(missing_top_player_team.top_player_id, None)
        self.mock_db_service.get_all_fantasy_teams_for_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    def test_all_teams_fully_drafted_team_missing_jungle_player(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        assert fantasy_league.current_week is not None, "current_week should not be None"
        fantasy_teams = [
            create_fantasy_team(
                fantasy_league.id, UserID(str(user_id)), fantasy_league.current_week
            )
            for user_id in range(fantasy_league.number_of_teams - 1)
        ]
        missing_jungle_player_team = create_fantasy_team(
            fantasy_league.id,
            UserID("123"),
            fantasy_league.current_week,
            set_jungle_player_id=False
        )
        fantasy_teams.append(missing_jungle_player_team)
        self.mock_db_service.get_all_fantasy_teams_for_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = self.fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.assertEqual(missing_jungle_player_team.jungle_player_id, None)
        self.mock_db_service.get_all_fantasy_teams_for_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    def test_all_teams_fully_drafted_team_missing_mid_player(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        assert fantasy_league.current_week is not None, "current_week should not be None"
        fantasy_teams = [
            create_fantasy_team(
                fantasy_league.id, UserID(str(user_id)), fantasy_league.current_week
            )
            for user_id in range(fantasy_league.number_of_teams - 1)
        ]
        missing_mid_player_team = create_fantasy_team(
            fantasy_league.id, UserID("123"), fantasy_league.current_week, set_mid_player_id=False
        )
        fantasy_teams.append(missing_mid_player_team)
        self.mock_db_service.get_all_fantasy_teams_for_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = self.fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.assertEqual(missing_mid_player_team.mid_player_id, None)
        self.mock_db_service.get_all_fantasy_teams_for_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    def test_all_teams_fully_drafted_team_missing_adc_player(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        assert fantasy_league.current_week is not None, "current_week should not be None"
        fantasy_teams = [
            create_fantasy_team(
                fantasy_league.id, UserID(str(user_id)), fantasy_league.current_week
            )
            for user_id in range(fantasy_league.number_of_teams - 1)
        ]
        missing_adc_player_team = create_fantasy_team(
            fantasy_league.id, UserID("123"), fantasy_league.current_week, set_adc_player_id=False
        )
        fantasy_teams.append(missing_adc_player_team)
        self.mock_db_service.get_all_fantasy_teams_for_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = self.fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.assertEqual(missing_adc_player_team.adc_player_id, None)
        self.mock_db_service.get_all_fantasy_teams_for_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )

    def test_all_teams_fully_drafted_team_missing_support_player(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        assert fantasy_league.current_week is not None, "current_week should not be None"
        fantasy_teams = [
            create_fantasy_team(
                fantasy_league.id, UserID(str(user_id)), fantasy_league.current_week
            )
            for user_id in range(fantasy_league.number_of_teams - 1)
        ]
        missing_support_player_team = create_fantasy_team(
            fantasy_league.id,
            UserID("123"),
            fantasy_league.current_week,
            set_support_player_id=False
        )
        fantasy_teams.append(missing_support_player_team)
        self.mock_db_service.get_all_fantasy_teams_for_week.return_value = fantasy_teams

        # Act
        all_teams_fully_drafted = self.fantasy_team_util.all_teams_fully_drafted(fantasy_league)

        # Assert
        self.assertFalse(all_teams_fully_drafted)
        self.assertEqual(fantasy_league.number_of_teams, len(fantasy_teams))
        self.assertEqual(missing_support_player_team.support_player_id, None)
        self.mock_db_service.get_all_fantasy_teams_for_week.assert_called_once_with(
            fantasy_league.id, fantasy_league.current_week
        )


def create_fantasy_team(
        fantasy_league_id: FantasyLeagueID,
        user_id: UserID,
        week: int,
        set_top_player_id: bool = True,
        set_jungle_player_id: bool = True,
        set_mid_player_id: bool = True,
        set_adc_player_id: bool = True,
        set_support_player_id: bool = True) -> FantasyTeam:
    return FantasyTeam(
        fantasy_league_id=fantasy_league_id,
        user_id=user_id,
        week=week,
        top_player_id=ProPlayerID(f"topId{user_id}") if set_top_player_id else None,
        jungle_player_id=ProPlayerID(f"jungleId{user_id}") if set_jungle_player_id else None,
        mid_player_id=ProPlayerID(f"midId{user_id}") if set_mid_player_id else None,
        adc_player_id=ProPlayerID(f"adcId{user_id}") if set_adc_player_id else None,
        support_player_id=ProPlayerID(f"supportId{user_id}") if set_support_player_id else None,
    )
