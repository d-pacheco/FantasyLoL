from unittest.mock import patch, MagicMock

from tests.test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures, riot_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus,
    FantasyTeam,
    UserID
)
from src.fantasy.exceptions.fantasy_membership_exception import FantasyMembershipException
from src.fantasy.service.fantasy_team_service import (
    validate_user_membership,
    get_player_from_db,
    player_already_drafted,
    get_users_most_recent_fantasy_team
)
from src.common.schemas.riot_data_schemas import ProPlayerID
from src.riot.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException

BASE_CRUD_PATH = 'src.db.crud'


class TestFantasyTeamService(FantasyLolTestBase):
    @patch(f'{BASE_CRUD_PATH}.get_user_membership_for_fantasy_league')
    def test_validate_user_membership_no_membership(self, mock_get_user_membership: MagicMock):
        # Arrange
        mock_get_user_membership.return_value = None

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            validate_user_membership(UserID("someUserId"), FantasyLeagueID("someId"))

    @patch(f'{BASE_CRUD_PATH}.get_user_membership_for_fantasy_league')
    def test_validate_user_membership_no_active_membership(
            self, mock_get_user_membership: MagicMock):
        # Arrange
        fantasy_league_id = FantasyLeagueID("someFantasyLeagueId")
        user_id = UserID("someUserId")
        user_membership = FantasyLeagueMembership(
            league_id=fantasy_league_id,
            user_id=user_id,
            status=FantasyLeagueMembershipStatus.PENDING
        )
        mock_get_user_membership.return_value = user_membership

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            validate_user_membership(user_id, fantasy_league_id)

    @patch(f'{BASE_CRUD_PATH}.get_player_by_id')
    def test_get_player_from_db_successful(self, mock_get_player_by_id: MagicMock):
        # Arrange
        pro_player = riot_fixtures.player_2_fixture
        mock_get_player_by_id.return_value = pro_player

        # Act
        returned_pro_player = get_player_from_db(pro_player.id)

        # Assert
        self.assertEqual(pro_player, returned_pro_player)

    @patch(f'{BASE_CRUD_PATH}.get_player_by_id')
    def test_get_player_from_db_pro_player_not_found_exception(self, mock_get_player_by_id):
        # Arrange
        pro_player = riot_fixtures.player_2_fixture
        mock_get_player_by_id.return_value = None

        # Act and assert
        with self.assertRaises(ProfessionalPlayerNotFoundException):
            get_player_from_db(pro_player.id)

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_week')
    def test_player_already_drafted_false(
            self, mock_get_all_fantasy_teams_for_current_week: MagicMock):
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
        mock_get_all_fantasy_teams_for_current_week.return_value = [
            user_1_fantasy_team, user_2_fantasy_team
        ]

        # Act
        returned_bool = player_already_drafted(pro_player, fantasy_league)

        # Assert
        self.assertFalse(returned_bool)

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_week')
    def test_player_already_drafted_true(
            self, mock_get_all_fantasy_teams_for_current_week: MagicMock):
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
        mock_get_all_fantasy_teams_for_current_week.return_value = [
            user_1_fantasy_team, user_2_fantasy_team
        ]

        # Act
        returned_bool = player_already_drafted(pro_player, fantasy_league)

        # Assert
        self.assertTrue(returned_bool)

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_user')
    def test_validate_user_can_pickup_player_for_role_open_spot_available(
            self, mock_get_all_fantasy_teams_for_user: MagicMock):
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
        mock_get_all_fantasy_teams_for_user.return_value = [
            user_week_1_fantasy_team, user_week_2_fantasy_team
        ]

        # Act
        returned_fantasy_team = get_users_most_recent_fantasy_team(fantasy_league, user_id)

        # Assert
        self.assertEqual(user_week_2_fantasy_team, returned_fantasy_team)

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_user')
    def test_validate_user_can_pickup_player_no_fantasy_teams_yet_saved(
            self, mock_get_all_fantasy_teams_for_user: MagicMock):
        # Arrange
        user_id = "someUserId"
        fantasy_league = fantasy_fixtures.fantasy_league_active_fixture.model_copy(deep=True)
        fantasy_league.current_week = 2
        mock_get_all_fantasy_teams_for_user.return_value = []
        expected_fantasy_team = FantasyTeam(
            fantasy_league_id=fantasy_league.id,
            user_id=UserID(user_id),
            week=fantasy_league.current_week
        )

        # Act
        returned_fantasy_team = get_users_most_recent_fantasy_team(fantasy_league, UserID(user_id))

        # Assert
        self.assertEqual(expected_fantasy_team, returned_fantasy_team)
