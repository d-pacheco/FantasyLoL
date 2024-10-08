from unittest.mock import MagicMock

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures, riot_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus,
    FantasyTeam,
    UserID
)
from src.common.schemas.riot_data_schemas import ProPlayerID

from src.fantasy.exceptions import FantasyMembershipException
from src.fantasy.service.fantasy_team_service import FantasyTeamService

from src.common.exceptions import ProfessionalPlayerNotFoundException


class TestFantasyTeamService(TestBase):
    def setUp(self):
        self.mock_db_service = MagicMock()
        self.fantasy_team_service = FantasyTeamService(self.mock_db_service)

    def tearDown(self):
        self.mock_db_service.reset_mock()

    def test_validate_user_membership_no_membership(self):
        # Arrange
        self.mock_db_service.get_user_membership_for_fantasy_league.return_value = None

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            self.fantasy_team_service.validate_user_membership(
                UserID("someUserId"), FantasyLeagueID("someId")
            )

    def test_validate_user_membership_no_active_membership(self):
        # Arrange
        fantasy_league_id = FantasyLeagueID("someFantasyLeagueId")
        user_id = UserID("someUserId")
        user_membership = FantasyLeagueMembership(
            league_id=fantasy_league_id,
            user_id=user_id,
            status=FantasyLeagueMembershipStatus.PENDING
        )
        self.mock_db_service.get_user_membership_for_fantasy_league.return_value = user_membership

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            self.fantasy_team_service.validate_user_membership(user_id, fantasy_league_id)

    def test_get_player_from_db_successful(self):
        # Arrange
        pro_player = riot_fixtures.player_2_fixture
        self.mock_db_service.get_player_by_id.return_value = pro_player

        # Act
        returned_pro_player = self.fantasy_team_service.get_player_from_db(pro_player.id)

        # Assert
        self.assertEqual(pro_player, returned_pro_player)

    def test_get_player_from_db_pro_player_not_found_exception(self):
        # Arrange
        pro_player = riot_fixtures.player_2_fixture
        self.mock_db_service.get_player_by_id.return_value = None

        # Act and assert
        with self.assertRaises(ProfessionalPlayerNotFoundException):
            self.fantasy_team_service.get_player_from_db(pro_player.id)

    def test_player_already_drafted_false(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_active_fixture.model_copy(deep=True)
        fantasy_league.current_week = 1
        pro_player = riot_fixtures.player_2_fixture
        user_1_fantasy_team = FantasyTeam(
            fantasy_league_id=fantasy_league.id,
            user_id=UserID("user1Id"),
            week=fantasy_league.current_week,
            top_player_id=ProPlayerID("some_top_id"),
            jungle_player_id=ProPlayerID("some_jungle_id"),
            mid_player_id=ProPlayerID("some_mid_id"),
            adc_player_id=ProPlayerID("some_adc_id"),
            support_player_id=ProPlayerID("some_support_id")
        )
        user_2_fantasy_team = FantasyTeam(
            fantasy_league_id=fantasy_league.id,
            user_id=UserID("user2Id"),
            week=fantasy_league.current_week,
            top_player_id=ProPlayerID("some_top2_id"),
            jungle_player_id=ProPlayerID("some_jungle2_id"),
            mid_player_id=ProPlayerID("some_mid2_id"),
            adc_player_id=ProPlayerID("some_adc2_id"),
            support_player_id=ProPlayerID("some_support2_id")
        )
        self.mock_db_service.get_all_fantasy_teams_for_week.return_value = [
            user_1_fantasy_team, user_2_fantasy_team
        ]

        # Act
        returned_bool = self.fantasy_team_service.player_already_drafted(pro_player, fantasy_league)

        # Assert
        self.assertFalse(returned_bool)

    def test_player_already_drafted_true(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_active_fixture.model_copy(deep=True)
        fantasy_league.current_week = 1
        pro_player = riot_fixtures.player_2_fixture
        user_1_fantasy_team = FantasyTeam(
            fantasy_league_id=fantasy_league.id,
            user_id=UserID("user1Id"),
            week=fantasy_league.current_week,
            top_player_id=ProPlayerID("some_top_id"),
            jungle_player_id=ProPlayerID("some_jungle_id"),
            mid_player_id=ProPlayerID("some_mid_id"),
            adc_player_id=ProPlayerID("some_adc_id"),
            support_player_id=ProPlayerID("some_support_id")
        )
        user_2_fantasy_team = FantasyTeam(
            fantasy_league_id=fantasy_league.id,
            user_id=UserID("user2Id"),
            week=fantasy_league.current_week,
            top_player_id=ProPlayerID("some_top2_id"),
            jungle_player_id=ProPlayerID(pro_player.id),
            mid_player_id=ProPlayerID("some_mid2_id"),
            adc_player_id=ProPlayerID("some_adc2_id"),
            support_player_id=ProPlayerID("some_support2_id")
        )
        self.mock_db_service.get_all_fantasy_teams_for_week.return_value = [
            user_1_fantasy_team, user_2_fantasy_team
        ]

        # Act
        returned_bool = self.fantasy_team_service.player_already_drafted(pro_player, fantasy_league)

        # Assert
        self.assertTrue(returned_bool)

    def test_validate_user_can_pickup_player_for_role_open_spot_available(self):
        # Arrange
        user_id = UserID("someUserId")
        fantasy_league = fantasy_fixtures.fantasy_league_active_fixture.model_copy(deep=True)
        fantasy_league.current_week = 2
        user_week_1_fantasy_team = FantasyTeam(
            fantasy_league_id=fantasy_league.id,
            user_id=user_id,
            week=1,
            top_player_id=ProPlayerID("some_top_id"),
            jungle_player_id=ProPlayerID("some_jungle_id"),
            mid_player_id=ProPlayerID("some_mid_id"),
            adc_player_id=ProPlayerID("some_adc_id"),
            support_player_id=ProPlayerID("some_support_id")
        )
        user_week_2_fantasy_team = FantasyTeam(
            fantasy_league_id=fantasy_league.id,
            user_id=user_id,
            week=fantasy_league.current_week,
            top_player_id=ProPlayerID("some_top2_id"),
            jungle_player_id=None,
            mid_player_id=ProPlayerID("some_mid2_id"),
            adc_player_id=ProPlayerID("some_adc2_id"),
            support_player_id=ProPlayerID("some_support2_id")
        )
        self.mock_db_service.get_all_fantasy_teams_for_user.return_value = [
            user_week_1_fantasy_team, user_week_2_fantasy_team
        ]

        # Act
        returned_fantasy_team = self.fantasy_team_service.get_users_most_recent_fantasy_team(
            fantasy_league, user_id
        )

        # Assert
        self.assertEqual(user_week_2_fantasy_team, returned_fantasy_team)

    def test_validate_user_can_pickup_player_no_fantasy_teams_yet_saved(self):
        # Arrange
        user_id = "someUserId"
        fantasy_league = fantasy_fixtures.fantasy_league_active_fixture.model_copy(deep=True)
        fantasy_league.current_week = 2
        self.mock_db_service.get_all_fantasy_teams_for_user.return_value = []
        expected_fantasy_team = FantasyTeam(
            fantasy_league_id=fantasy_league.id,
            user_id=UserID(user_id),
            week=fantasy_league.current_week
        )

        # Act
        returned_fantasy_team = self.fantasy_team_service.get_users_most_recent_fantasy_team(
            fantasy_league, UserID(user_id)
        )

        # Assert
        self.assertEqual(expected_fantasy_team, returned_fantasy_team)
