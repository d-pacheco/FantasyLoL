import uuid
from copy import deepcopy

from tests.test_base import FantasyLolTestBase
from tests.test_util import db_util, fantasy_fixtures

from src.common.schemas.fantasy_schemas import FantasyTeam
from src.common.schemas.fantasy_schemas import FantasyLeagueMembership
from src.common.schemas.fantasy_schemas import FantasyLeagueMembershipStatus
from src.common.schemas.fantasy_schemas import FantasyLeagueStatus
from src.common.schemas.fantasy_schemas import FantasyLeague
from src.common.schemas.riot_data_schemas import PlayerRole
from src.common.schemas.riot_data_schemas import ProfessionalPlayer

from src.db import crud

from src.fantasy.exceptions.fantasy_draft_exception import FantasyDraftException
from src.fantasy.exceptions.fantasy_league_not_found_exception import \
    FantasyLeagueNotFoundException
from src.fantasy.exceptions.fantasy_league_invalid_required_state_exception import \
    FantasyLeagueInvalidRequiredStateException
from src.fantasy.exceptions.fantasy_membership_exception import FantasyMembershipException
from src.fantasy.service.fantasy_team_service import FantasyTeamService

from src.riot.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException

pro_player_fixture = ProfessionalPlayer(
    id=str(uuid.uuid4()),
    team_id=str(uuid.uuid4()),
    summoner_name="summonerName1",
    image="imageUrl",
    role=PlayerRole.JUNGLE
)

pro_player_2_fixture = ProfessionalPlayer(
    id=str(uuid.uuid4()),
    team_id=str(uuid.uuid4()),
    summoner_name="summonerName2",
    image="imageUrl2",
    role=PlayerRole.JUNGLE
)

pro_player_3_fixture = ProfessionalPlayer(
    id=str(uuid.uuid4()),
    team_id=str(uuid.uuid4()),
    summoner_name="summonerName2",
    image="imageUrl2",
    role=PlayerRole.MID
)

fantasy_team_service = FantasyTeamService()


class FantasyTeamServiceIntegrationTest(FantasyLolTestBase):
    def test_get_all_fantasy_team_weeks_successful(self):
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
        user_1_fantasy_team_week_1 = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team_week_1.jungle_player_id = pro_player_fixture.id
        db_util.create_fantasy_team(user_1_fantasy_team_week_1)

        user_1_fantasy_team_week_2 = deepcopy(fantasy_fixtures.fantasy_team_week_2)
        user_1_fantasy_team_week_2.jungle_player_id = pro_player_2_fixture.id
        db_util.create_fantasy_team(user_1_fantasy_team_week_2)

        user_2_fantasy_team_week_1 = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team_week_1.user_id = fantasy_fixtures.user_2_fixture.id
        db_util.create_fantasy_team(user_2_fantasy_team_week_1)
        db_util.save_player(pro_player_fixture)
        db_util.save_player(pro_player_2_fixture)

        expected_fantasy_team_weeks = [user_1_fantasy_team_week_1, user_1_fantasy_team_week_2]

        # Act
        returned_fantasy_team_weeks = fantasy_team_service.get_all_fantasy_team_weeks(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id
        )

        # Assert
        self.assertIsInstance(returned_fantasy_team_weeks, list)
        self.assertEqual(len(expected_fantasy_team_weeks), len(returned_fantasy_team_weeks))
        for i in range(len(expected_fantasy_team_weeks)):
            self.assertEqual(
                expected_fantasy_team_weeks[i],
                FantasyTeam.model_validate(returned_fantasy_team_weeks[i])
            )

    def test_get_all_fantasy_team_weeks_league_not_found_exception(self):
        # Arrange
        db_util.create_user(fantasy_fixtures.user_fixture)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_team_service.get_all_fantasy_team_weeks(
                "badFantasyLeagueId", fantasy_fixtures.user_fixture.id
            )

    def test_get_all_fantasy_team_weeks_not_valid_required_fantasy_league_state(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)

        # Act and Assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            fantasy_team_service.get_all_fantasy_team_weeks(
                fantasy_fixtures.fantasy_league_fixture.id,
                fantasy_fixtures.user_fixture.id
            )

    def test_get_all_fantasy_team_weeks_user_not_an_active_member(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.PENDING
        )

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            fantasy_team_service.get_all_fantasy_team_weeks(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id
            )

    def test_get_all_fantasy_team_weeks_user_has_no_membership(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            fantasy_team_service.get_all_fantasy_team_weeks(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id
            )

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
        db_util.save_player(pro_player_fixture)

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
        db_util.save_player(pro_player_fixture)

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
        db_util.save_player(pro_player_fixture)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.draft_player(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id
            )
        self.assertIn("Slot not available for role", str(context.exception))

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
        db_util.save_player(pro_player_fixture)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.draft_player(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id
            )
        self.assertIn("Player already drafted", str(context.exception))

    def test_draft_player_fantasy_league_not_found_exception(self):
        # Arrange
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.save_player(pro_player_fixture)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_team_service.draft_player(
                "badFantasyLeagueId",
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id
            )

    def test_draft_player_fantasy_league_not_draft_or_active_state(self):
        # Arrange
        bad_states = [
            FantasyLeagueStatus.PRE_DRAFT,
            FantasyLeagueStatus.COMPLETED,
            FantasyLeagueStatus.DELETED
        ]
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.save_player(pro_player_fixture)

        # Act and Assert
        for bad_state in bad_states:
            bad_fantasy_league = FantasyLeague(
                id=str(uuid.uuid4()),
                owner_id=fantasy_fixtures.user_fixture.id,
                status=bad_state,
                current_week=1
            )
            db_util.create_fantasy_league(bad_fantasy_league)
            with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
                fantasy_team_service.draft_player(
                    bad_fantasy_league.id,
                    fantasy_fixtures.user_fixture.id,
                    pro_player_fixture.id
                )

    def test_draft_player_user_not_an_active_member_exception(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.save_player(pro_player_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.PENDING
        )

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            fantasy_team_service.draft_player(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id
            )

    def test_draft_player_professional_player_not_found_exception(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and Assert
        with self.assertRaises(ProfessionalPlayerNotFoundException):
            fantasy_team_service.draft_player(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                "badProPlayerId"
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
        db_util.save_player(pro_player_fixture)

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
        db_util.save_player(pro_player_fixture)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.drop_player(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id
            )
        self.assertIn("Player not drafted", str(context.exception))

    def test_drop_player_fantasy_league_not_found_exception(self):
        # Arrange
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.save_player(pro_player_fixture)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_team_service.drop_player(
                "badFantasyLeagueId",
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id
            )

    def test_drop_player_fantasy_league_not_active_state(self):
        # Arrange
        bad_states = [
            FantasyLeagueStatus.PRE_DRAFT,
            FantasyLeagueStatus.DRAFT,
            FantasyLeagueStatus.COMPLETED,
            FantasyLeagueStatus.DELETED
        ]
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.save_player(pro_player_fixture)

        # Act and Assert
        for bad_state in bad_states:
            bad_fantasy_league = FantasyLeague(
                id=str(uuid.uuid4()),
                owner_id=fantasy_fixtures.user_fixture.id,
                status=bad_state,
                current_week=1
            )
            db_util.create_fantasy_league(bad_fantasy_league)
            with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
                fantasy_team_service.drop_player(
                    bad_fantasy_league.id,
                    fantasy_fixtures.user_fixture.id,
                    pro_player_fixture.id
                )

    def test_drop_player_user_not_an_active_member_exception(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.save_player(pro_player_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.PENDING
        )

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            fantasy_team_service.drop_player(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id
            )

    def test_drop_player_professional_player_not_found_exception(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and Assert
        with self.assertRaises(ProfessionalPlayerNotFoundException):
            fantasy_team_service.drop_player(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                "badProPlayerId"
            )

    def test_swap_players_successful(self):
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
        user_2_fantasy_team.jungle_player_id = "someOtherJunglePlayerId"
        db_util.create_fantasy_team(user_2_fantasy_team)

        db_util.save_player(pro_player_fixture)
        db_util.save_player(pro_player_2_fixture)

        expected_fantasy_team = deepcopy(user_1_fantasy_team)
        expected_fantasy_team.jungle_player_id = pro_player_2_fixture.id

        # Act
        returned_fantasy_team = fantasy_team_service.swap_players(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            pro_player_fixture.id,
            pro_player_2_fixture.id
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

    def test_swap_players_mismatched_player_roles_exception(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.jungle_player_id = pro_player_fixture.id
        db_util.create_fantasy_team(user_1_fantasy_team)
        db_util.save_player(pro_player_fixture)
        db_util.save_player(pro_player_3_fixture)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.swap_players(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id,
                pro_player_3_fixture.id
            )
        self.assertIn("Mismatching roles", str(context.exception))

    def test_swap_players_user_does_not_have_player_drafted_exception(self):
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
        db_util.save_player(pro_player_fixture)
        db_util.save_player(pro_player_2_fixture)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.swap_players(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id,
                pro_player_2_fixture.id
            )
        self.assertIn("Player not drafted", str(context.exception))

    def test_swap_players_already_drafted_exception(self):
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
        user_2_fantasy_team.jungle_player_id = pro_player_2_fixture.id
        db_util.create_fantasy_team(user_2_fantasy_team)

        db_util.save_player(pro_player_fixture)
        db_util.save_player(pro_player_2_fixture)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.swap_players(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id,
                pro_player_2_fixture.id
            )
        self.assertIn("Player already drafted", str(context.exception))

    def test_swap_players_fantasy_league_not_found_exception(self):
        # Arrange
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.save_player(pro_player_fixture)
        db_util.save_player(pro_player_2_fixture)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_team_service.swap_players(
                "badFantasyLeagueId",
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id,
                pro_player_2_fixture.id
            )

    def test_swap_players_fantasy_league_not_active_state(self):
        # Arrange
        bad_states = [
            FantasyLeagueStatus.PRE_DRAFT,
            FantasyLeagueStatus.DRAFT,
            FantasyLeagueStatus.COMPLETED,
            FantasyLeagueStatus.DELETED
        ]
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.save_player(pro_player_fixture)
        db_util.save_player(pro_player_2_fixture)

        # Act and Assert
        for bad_state in bad_states:
            bad_fantasy_league = FantasyLeague(
                id=str(uuid.uuid4()),
                owner_id=fantasy_fixtures.user_fixture.id,
                status=bad_state,
                current_week=1
            )
            db_util.create_fantasy_league(bad_fantasy_league)
            with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
                fantasy_team_service.swap_players(
                    bad_fantasy_league.id,
                    fantasy_fixtures.user_fixture.id,
                    pro_player_fixture.id,
                    pro_player_2_fixture.id
                )

    def test_swap_players_user_not_an_active_member_exception(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.save_player(pro_player_fixture)
        db_util.save_player(pro_player_2_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.PENDING
        )

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            fantasy_team_service.swap_players(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id,
                pro_player_2_fixture.id
            )

    def test_swap_players_professional_player_to_drop_not_found_exception(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.save_player(pro_player_2_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and Assert
        with self.assertRaises(ProfessionalPlayerNotFoundException):
            fantasy_team_service.swap_players(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                "badProPlayerId",
                pro_player_2_fixture.id
            )

    def test_swap_players_professional_player_to_pickup_not_found_exception(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        db_util.create_user(fantasy_fixtures.user_fixture)
        db_util.save_player(pro_player_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and Assert
        with self.assertRaises(ProfessionalPlayerNotFoundException):
            fantasy_team_service.swap_players(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id,
                "badProPlayerId"
            )


def create_fantasy_league_membership_for_league(
        league_id: str, user_id: str, status: FantasyLeagueMembershipStatus):
    fantasy_league_membership = FantasyLeagueMembership(
        league_id=league_id,
        user_id=user_id,
        status=status
    )
    db_util.create_fantasy_league_membership(fantasy_league_membership)
