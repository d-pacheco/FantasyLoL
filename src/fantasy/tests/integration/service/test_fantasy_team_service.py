import uuid
from copy import deepcopy

from ...test_base import FantasyLolTestBase
from ...test_util import db_util
from ...test_util import fantasy_fixtures

from src.common.schemas.fantasy_schemas import FantasyTeam
from src.common.schemas.fantasy_schemas import FantasyLeagueMembership
from src.common.schemas.fantasy_schemas import FantasyLeagueMembershipStatus
from src.common.schemas.riot_data_schemas import PlayerRole
from src.common.schemas.riot_data_schemas import ProfessionalPlayer

from src.db import crud

from src.fantasy.exceptions.fantasy_draft_exception import FantasyDraftException
from src.fantasy.service.fantasy_team_service import FantasyTeamService

pro_player_fixture = ProfessionalPlayer(
    id=str(uuid.uuid4()),
    team_id=str(uuid.uuid4()),
    summoner_name="summonerName1",
    image="imageUrl",
    role=PlayerRole.JUNGLE
)

fantasy_team_service = FantasyTeamService()


class FantasyTeamServiceIntegrationTest(FantasyLolTestBase):
    def test_draft_player_has_initial_fantasy_team_successful(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.create_user(fantasy_fixtures.user_2_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_2_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        db_util.create_fantasy_team(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team.user_id = fantasy_fixtures.user_2_fixture.id
        db_util.create_fantasy_team(user_2_fantasy_team)
        db_util.create_professional_player(pro_player_fixture)

        expected_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        expected_fantasy_team.jungle_player_id = pro_player_fixture.id

        # Act
        returned_fantasy_team = fantasy_team_service.draft_player(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            pro_player_fixture.id
        )

        # Assert
        self.assertEqual(expected_fantasy_team, returned_fantasy_team)
        user_1_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_fixtures.fantasy_league_active_fixture.id, fantasy_fixtures.user_fixture.id
        )
        self.assertEqual(1, len(user_1_fantasy_teams_from_db))
        self.assertEqual(
            expected_fantasy_team, FantasyTeam.model_validate(user_1_fantasy_teams_from_db[0])
        )
        # Check that user 2's fantasy team didn't update
        user_2_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_fixtures.fantasy_league_active_fixture.id, fantasy_fixtures.user_2_fixture.id
        )
        self.assertEqual(1, len(user_2_fantasy_teams_from_db))
        self.assertEqual(
            user_2_fantasy_team, FantasyTeam.model_validate(user_2_fantasy_teams_from_db[0])
        )

    def test_draft_player_has_no_initial_fantasy_team_successful(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.create_user(fantasy_fixtures.user_2_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_2_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )

        user_2_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team.user_id = fantasy_fixtures.user_2_fixture.id
        db_util.create_fantasy_team(user_2_fantasy_team)
        db_util.create_professional_player(pro_player_fixture)

        expected_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        expected_fantasy_team.jungle_player_id = pro_player_fixture.id

        # Act
        returned_fantasy_team = fantasy_team_service.draft_player(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            pro_player_fixture.id
        )

        # Assert
        self.assertEqual(expected_fantasy_team, returned_fantasy_team)
        user_1_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_fixtures.fantasy_league_active_fixture.id, fantasy_fixtures.user_fixture.id
        )
        self.assertEqual(1, len(user_1_fantasy_teams_from_db))
        self.assertEqual(
            expected_fantasy_team, FantasyTeam.model_validate(user_1_fantasy_teams_from_db[0])
        )
        # Check that user 2's fantasy team didn't update
        user_2_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_fixtures.fantasy_league_active_fixture.id, fantasy_fixtures.user_2_fixture.id
        )
        self.assertEqual(1, len(user_2_fantasy_teams_from_db))
        self.assertEqual(
            user_2_fantasy_team, FantasyTeam.model_validate(user_2_fantasy_teams_from_db[0])
        )

    def test_draft_player_no_slot_available_to_draft_player_for_role(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.jungle_player_id = "somePlayerId"
        db_util.create_fantasy_team(user_1_fantasy_team)
        db_util.create_professional_player(pro_player_fixture)

        # Act and Assert
        with self.assertRaises(FantasyDraftException):
            fantasy_team_service.draft_player(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id
            )

    def test_draft_player_already_drafted_exception(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.create_user(fantasy_fixtures.user_2_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_2_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        db_util.create_fantasy_team(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team.user_id = fantasy_fixtures.user_2_fixture.id
        user_2_fantasy_team.jungle_player_id = pro_player_fixture.id
        db_util.create_fantasy_team(user_2_fantasy_team)
        db_util.create_professional_player(pro_player_fixture)

        # Act and Assert
        with self.assertRaises(FantasyDraftException):
            fantasy_team_service.draft_player(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id
            )

    def test_drop_player_successful(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.create_user(fantasy_fixtures.user_2_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_2_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.jungle_player_id = pro_player_fixture.id
        db_util.create_fantasy_team(user_1_fantasy_team)

        user_2_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team.user_id = fantasy_fixtures.user_2_fixture.id
        user_2_fantasy_team.jungle_player_id = "someOtherPlayerId"
        db_util.create_fantasy_team(user_2_fantasy_team)
        db_util.create_professional_player(pro_player_fixture)

        expected_fantasy_team = deepcopy(user_1_fantasy_team)
        expected_fantasy_team.jungle_player_id = None

        # Act
        returned_fantasy_team = fantasy_team_service.drop_player(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            pro_player_fixture.id
        )

        # Assert
        self.assertEqual(expected_fantasy_team, returned_fantasy_team)
        user_1_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_fixtures.fantasy_league_active_fixture.id, fantasy_fixtures.user_fixture.id
        )
        self.assertEqual(1, len(user_1_fantasy_teams_from_db))
        self.assertEqual(
            expected_fantasy_team, FantasyTeam.model_validate(user_1_fantasy_teams_from_db[0])
        )
        # Check that user 2's fantasy team didn't update
        user_2_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_fixtures.fantasy_league_active_fixture.id, fantasy_fixtures.user_2_fixture.id
        )
        self.assertEqual(1, len(user_2_fantasy_teams_from_db))
        self.assertEqual(
            user_2_fantasy_team, FantasyTeam.model_validate(user_2_fantasy_teams_from_db[0])
        )

    def test_drop_player_user_does_not_have_player_drafted_exception(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.jungle_player_id = "someOtherPlayerId"
        db_util.create_fantasy_team(user_1_fantasy_team)
        db_util.create_professional_player(pro_player_fixture)

        # Act and Assert
        with self.assertRaises(FantasyDraftException):
            fantasy_team_service.drop_player(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id
            )


def create_fantasy_league_membership_for_league(
        league_id: str, user_id: str, status: FantasyLeagueMembershipStatus):
    fantasy_league_membership = FantasyLeagueMembership(
        league_id=league_id,
        user_id=user_id,
        status=status
    )
    db_util.create_fantasy_league_membership(fantasy_league_membership)
