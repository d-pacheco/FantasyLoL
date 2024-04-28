from unittest.mock import patch
import uuid

from ...test_base import FantasyLolTestBase
from ...test_util import fantasy_fixtures

from src.db.models import (
    FantasyTeamModel,
    FantasyLeagueModel,
    FantasyLeagueMembershipModel,
    ProfessionalPlayerModel
)
from src.fantasy.exceptions.fantasy_league_not_found_exception import \
    FantasyLeagueNotFoundException
from src.fantasy.exceptions.fantasy_membership_exception import FantasyMembershipException
from src.fantasy.exceptions.fantasy_draft_exception import FantasyDraftException
from src.fantasy.service.fantasy_team_service import (
    validate_league,
    validate_user_membership,
    get_player_from_db,
    player_already_drafted,
    validate_user_can_draft_player_for_role
)
from src.common.schemas.fantasy_schemas import (
    FantasyLeagueStatus,
    FantasyLeagueMembershipStatus,
    FantasyTeam
)
from src.common.schemas.riot_data_schemas import PlayerRole
from src.riot.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException

BASE_CRUD_PATH = 'src.db.crud'

pro_player_model_fixture = ProfessionalPlayerModel(
    id=str(uuid.uuid4()),
    team_id=str(uuid.uuid4()),
    summoner_name="summonerName1",
    image="imageUrl",
    role=PlayerRole.JUNGLE
)


class TestFantasyTeamService(FantasyLolTestBase):

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_validate_league_successful(self, mock_get_fantasy_league_by_id):
        # Arrange
        expected_fantasy_league_model = create_fantasy_league_model(FantasyLeagueStatus.DRAFT, 1)
        mock_get_fantasy_league_by_id.return_value = expected_fantasy_league_model

        # Act
        returned_fantasy_league_model = validate_league(
            expected_fantasy_league_model.id, [FantasyLeagueStatus.DRAFT]
        )

        # Assert
        self.assertEqual(expected_fantasy_league_model, returned_fantasy_league_model)

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_validate_league_league_not_found_exception(self, mock_get_fantasy_league_by_id):
        # Arrange
        mock_get_fantasy_league_by_id.return_value = None

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            validate_league("someId", [FantasyLeagueStatus.DRAFT])

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_validate_league_not_in_required_state(self, mock_get_fantasy_league_by_id):
        # Arrange
        expected_fantasy_league_model = create_fantasy_league_model(
            FantasyLeagueStatus.PRE_DRAFT, 1
        )
        mock_get_fantasy_league_by_id.return_value = expected_fantasy_league_model

        # Act and Assert
        with self.assertRaises(FantasyDraftException):
            validate_league(expected_fantasy_league_model.id, [FantasyLeagueStatus.DRAFT])

    @patch(f'{BASE_CRUD_PATH}.get_user_membership_for_fantasy_league')
    def test_validate_user_membership_successful(self, mock_get_user_membership):
        # Arrange
        user_membership_model_active = FantasyLeagueMembershipModel(
            league_id="someId",
            user_id="someUserId",
            status=FantasyLeagueMembershipStatus.ACCEPTED
        )
        mock_get_user_membership.return_value = user_membership_model_active

        # Act and Assert
        try:
            validate_user_membership("someUserId", "someId")
        except FantasyMembershipException:
            self.fail()

    @patch(f'{BASE_CRUD_PATH}.get_user_membership_for_fantasy_league')
    def test_validate_user_membership_no_membership(self, mock_get_user_membership):
        # Arrange
        mock_get_user_membership.return_value = None

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            validate_user_membership("someUserId", "someId")

    @patch(f'{BASE_CRUD_PATH}.get_user_membership_for_fantasy_league')
    def test_validate_user_membership_no_active_membership(self, mock_get_user_membership):
        # Arrange
        user_membership_model_active = FantasyLeagueMembershipModel(
            league_id="someId",
            user_id="someUserId",
            status=FantasyLeagueMembershipStatus.PENDING
        )
        mock_get_user_membership.return_value = user_membership_model_active

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            validate_user_membership("someUserId", "someId")

    @patch(f'{BASE_CRUD_PATH}.get_player_by_id')
    def test_get_player_from_db_successful(self, mock_get_player_by_id):
        # Arrange
        mock_get_player_by_id.return_value = pro_player_model_fixture

        # Act
        returned_pro_player_model = get_player_from_db(pro_player_model_fixture.id)

        # Assert
        self.assertEqual(pro_player_model_fixture, returned_pro_player_model)

    @patch(f'{BASE_CRUD_PATH}.get_player_by_id')
    def test_get_player_from_db_pro_player_not_found_exception(self, mock_get_player_by_id):
        # Arrange
        mock_get_player_by_id.return_value = None

        # Act and assert
        with self.assertRaises(ProfessionalPlayerNotFoundException):
            get_player_from_db(pro_player_model_fixture.id)

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_current_week')
    def test_player_already_drafted_false(self, mock_get_all_fantasy_teams_for_current_week):
        # Arrange
        fantasy_league_model = create_fantasy_league_model(FantasyLeagueStatus.ACTIVE, 1)
        user_1_fantasy_team = FantasyTeamModel(
            fantasy_league_id=fantasy_league_model.id,
            user_id="user1Id",
            week=fantasy_league_model.current_week,
            top_player_id="some_top_id",
            jungle_player_id="some_jungle_id",
            mid_player_id="some_mid_id",
            adc_player_id="some_adc_id",
            support_player_id="some_support_id"
        )
        user_2_fantasy_team = FantasyTeamModel(
            fantasy_league_id=fantasy_league_model.id,
            user_id="user2Id",
            week=fantasy_league_model.current_week,
            top_player_id="some_top2_id",
            jungle_player_id="some_jungle2_id",
            mid_player_id="some_mid2_id",
            adc_player_id="some_adc2_id",
            support_player_id="some_support2_id"
        )
        mock_get_all_fantasy_teams_for_current_week.return_value = [
            user_1_fantasy_team, user_2_fantasy_team
        ]
        expected_bool = False

        # Act
        returned_bool = player_already_drafted(pro_player_model_fixture, fantasy_league_model)

        # Assert
        self.assertEqual(expected_bool, returned_bool)

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_current_week')
    def test_player_already_drafted_true(self, mock_get_all_fantasy_teams_for_current_week):
        # Arrange
        fantasy_league_model = create_fantasy_league_model(FantasyLeagueStatus.ACTIVE, 1)
        user_1_fantasy_team = FantasyTeamModel(
            fantasy_league_id=fantasy_league_model.id,
            user_id="user1Id",
            week=fantasy_league_model.current_week,
            top_player_id="some_top_id",
            jungle_player_id="some_jungle_id",
            mid_player_id="some_mid_id",
            adc_player_id="some_adc_id",
            support_player_id="some_support_id"
        )
        user_2_fantasy_team = FantasyTeamModel(
            fantasy_league_id=fantasy_league_model.id,
            user_id="user2Id",
            week=fantasy_league_model.current_week,
            top_player_id="some_top2_id",
            jungle_player_id=pro_player_model_fixture.id,
            mid_player_id="some_mid2_id",
            adc_player_id="some_adc2_id",
            support_player_id="some_support2_id"
        )
        mock_get_all_fantasy_teams_for_current_week.return_value = [
            user_1_fantasy_team, user_2_fantasy_team
        ]
        expected_bool = True

        # Act
        returned_bool = player_already_drafted(pro_player_model_fixture, fantasy_league_model)

        # Assert
        self.assertEqual(expected_bool, returned_bool)

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_user')
    def test_validate_user_can_draft_player_for_role_open_spot_available(
            self, mock_get_all_fantasy_teams_for_user):
        # Arrange
        user_id = "someUserId"
        fantasy_league_model = create_fantasy_league_model(FantasyLeagueStatus.ACTIVE, 2)
        user_week_1_fantasy_team = FantasyTeamModel(
            fantasy_league_id=fantasy_league_model.id,
            user_id=user_id,
            week=1,
            top_player_id="some_top_id",
            jungle_player_id="some_jungle_id",
            mid_player_id="some_mid_id",
            adc_player_id="some_adc_id",
            support_player_id="some_support_id"
        )
        user_week_2_fantasy_team = FantasyTeamModel(
            fantasy_league_id=fantasy_league_model.id,
            user_id=user_id,
            week=fantasy_league_model.current_week,
            top_player_id="some_top2_id",
            jungle_player_id=None,
            mid_player_id="some_mid2_id",
            adc_player_id="some_adc2_id",
            support_player_id="some_support2_id"
        )
        mock_get_all_fantasy_teams_for_user.return_value = [
            user_week_1_fantasy_team, user_week_2_fantasy_team
        ]
        expected_fantasy_team = FantasyTeam.model_validate(user_week_2_fantasy_team)

        # Act
        returned_fantasy_team = validate_user_can_draft_player_for_role(
            fantasy_league_model, user_id, pro_player_model_fixture
        )

        # Assert
        self.assertEqual(expected_fantasy_team, returned_fantasy_team)

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_user')
    def test_validate_user_can_draft_player_for_role_no_open_spot_available(
            self, mock_get_all_fantasy_teams_for_user):
        # Arrange
        user_id = "someUserId"
        fantasy_league_model = create_fantasy_league_model(FantasyLeagueStatus.ACTIVE, 2)
        user_week_1_fantasy_team = FantasyTeamModel(
            fantasy_league_id=fantasy_league_model.id,
            user_id=user_id,
            week=1,
            top_player_id="some_top_id",
            jungle_player_id="some_jungle_id",
            mid_player_id="some_mid_id",
            adc_player_id="some_adc_id",
            support_player_id="some_support_id"
        )
        user_week_2_fantasy_team = FantasyTeamModel(
            fantasy_league_id=fantasy_league_model.id,
            user_id=user_id,
            week=fantasy_league_model.current_week,
            top_player_id="some_top2_id",
            jungle_player_id="some_jungle2_id",
            mid_player_id="some_mid2_id",
            adc_player_id="some_adc2_id",
            support_player_id="some_support2_id"
        )
        mock_get_all_fantasy_teams_for_user.return_value = [
            user_week_1_fantasy_team, user_week_2_fantasy_team
        ]

        # Act and Assert
        with self.assertRaises(FantasyDraftException):
            validate_user_can_draft_player_for_role(
                fantasy_league_model, user_id, pro_player_model_fixture
            )

    @patch(f'{BASE_CRUD_PATH}.get_all_fantasy_teams_for_user')
    def test_validate_user_can_draft_player_no_fantasy_teams_yet_saved(
            self, mock_get_all_fantasy_teams_for_user):
        # Arrange
        user_id = "someUserId"
        fantasy_league_model = create_fantasy_league_model(FantasyLeagueStatus.ACTIVE, 2)
        mock_get_all_fantasy_teams_for_user.return_value = []
        expected_fantasy_team = FantasyTeam(
            fantasy_league_id=fantasy_league_model.id,
            user_id=user_id,
            week=fantasy_league_model.current_week
        )

        # Act
        returned_fantasy_team = validate_user_can_draft_player_for_role(
            fantasy_league_model, user_id, pro_player_model_fixture
        )

        # Assert
        self.assertEqual(expected_fantasy_team, returned_fantasy_team)


def create_fantasy_league_model(status: FantasyLeagueStatus, week: int):
    return FantasyLeagueModel(
        id=str(uuid.uuid4()),
        owner_id=fantasy_fixtures.user_fixture.id,
        status=status,
        name="Fantasy League Model Fixture",
        number_of_teams=6,
        current_week=week
    )
