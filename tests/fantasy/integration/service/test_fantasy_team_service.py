import uuid
from copy import deepcopy

from tests.test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures, riot_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus,
    FantasyLeagueStatus,
    FantasyLeagueDraftOrder,
    UserID
)
from src.common.schemas.riot_data_schemas import (
    PlayerRole,
    ProfessionalPlayer,
    ProPlayerID,
    ProTeamID
)
from src.db import crud
from src.fantasy.exceptions import (
    FantasyDraftException,
    FantasyLeagueNotFoundException,
    FantasyLeagueInvalidRequiredStateException,
    FantasyMembershipException
)
from src.fantasy.service import FantasyTeamService
from src.riot.exceptions import ProfessionalPlayerNotFoundException

pro_player_fixture = ProfessionalPlayer(
    id=ProPlayerID(str(uuid.uuid4())),
    team_id=ProTeamID(str(uuid.uuid4())),
    summoner_name="summonerName1",
    image="imageUrl",
    role=PlayerRole.JUNGLE
)

pro_player_2_fixture = ProfessionalPlayer(
    id=ProPlayerID(str(uuid.uuid4())),
    team_id=ProTeamID(str(uuid.uuid4())),
    summoner_name="summonerName2",
    image="imageUrl2",
    role=PlayerRole.JUNGLE
)

fantasy_team_service = FantasyTeamService()


class FantasyTeamServiceIntegrationTest(FantasyLolTestBase):
    # -------------------------------------
    # ---- Get All Fantasy Team Weeks  ----
    # -------------------------------------
    def test_get_all_fantasy_team_weeks_successful(self):
        # Arrange
        crud.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.create_user(fantasy_fixtures.user_2_fixture)
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
        crud.put_fantasy_team(user_1_fantasy_team_week_1)

        user_1_fantasy_team_week_2 = deepcopy(fantasy_fixtures.fantasy_team_week_2)
        user_1_fantasy_team_week_2.jungle_player_id = pro_player_2_fixture.id
        crud.put_fantasy_team(user_1_fantasy_team_week_2)

        user_2_fantasy_team_week_1 = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team_week_1.user_id = fantasy_fixtures.user_2_fixture.id
        crud.put_fantasy_team(user_2_fantasy_team_week_1)
        crud.put_player(pro_player_fixture)
        crud.put_player(pro_player_2_fixture)

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
            self.assertEqual(expected_fantasy_team_weeks[i], returned_fantasy_team_weeks[i])

    def test_get_all_fantasy_team_weeks_league_not_found_exception(self):
        # Arrange
        crud.create_user(fantasy_fixtures.user_fixture)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_team_service.get_all_fantasy_team_weeks(
                FantasyLeagueID("badFantasyLeagueId"), fantasy_fixtures.user_fixture.id
            )

    def test_get_all_fantasy_team_weeks_not_valid_required_fantasy_league_state(self):
        # Arrange
        crud.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)

        # Act and Assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            fantasy_team_service.get_all_fantasy_team_weeks(
                fantasy_fixtures.fantasy_league_fixture.id,
                fantasy_fixtures.user_fixture.id
            )

    def test_get_all_fantasy_team_weeks_user_not_an_active_member(self):
        # Arrange
        crud.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        crud.create_user(fantasy_fixtures.user_fixture)
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
        crud.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        crud.create_user(fantasy_fixtures.user_fixture)

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            fantasy_team_service.get_all_fantasy_team_weeks(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id
            )

    # --------------------------------------
    # ----------- Pickup Player  -----------
    # --------------------------------------

    def test_pickup_player_has_initial_fantasy_team_for_draft_league_successful(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_draft_fixture)
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        fantasy_league.current_draft_position = 1
        crud.create_fantasy_league(fantasy_league)
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        crud.create_user(user_1)
        crud.create_user(user_2)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_1.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_fantasy_league_draft_position(fantasy_league.id, user_1.id, 1)
        create_fantasy_league_draft_position(fantasy_league.id, user_2.id, 2)

        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.fantasy_league_id = fantasy_league.id
        user_1_fantasy_team.week = fantasy_league.current_week
        crud.put_fantasy_team(user_1_fantasy_team)

        user_2_fantasy_team = deepcopy(user_1_fantasy_team)
        user_2_fantasy_team.user_id = user_2.id
        crud.put_fantasy_team(user_2_fantasy_team)

        expected_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        expected_fantasy_team.fantasy_league_id = fantasy_league.id
        expected_fantasy_team.week = fantasy_league.current_week
        expected_fantasy_team.top_player_id = riot_fixtures.player_1_fixture.id

        # Act
        returned_fantasy_team = fantasy_team_service.pickup_player(
            fantasy_league.id, user_1.id, riot_fixtures.player_1_fixture.id
        )

        # Assert
        self.assertEqual(expected_fantasy_team, returned_fantasy_team)
        user_1_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_league.id, user_1.id
        )
        self.assertEqual(1, len(user_1_fantasy_teams_from_db))
        self.assertEqual(expected_fantasy_team, user_1_fantasy_teams_from_db[0])
        # Check that user 2's fantasy team didn't update
        user_2_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_league.id, user_2.id
        )
        self.assertEqual(1, len(user_2_fantasy_teams_from_db))
        self.assertEqual(user_2_fantasy_team, user_2_fantasy_teams_from_db[0])
        db_fantasy_league = crud.get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(
            fantasy_league.current_draft_position + 1, db_fantasy_league.current_draft_position
        )
        self.assertEqual(FantasyLeagueStatus.DRAFT, db_fantasy_league.status)

    def test_pickup_player_has_no_initial_fantasy_team_for_draft_league_successful(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_draft_fixture)
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        crud.create_fantasy_league(fantasy_league)
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        crud.create_user(user_1)
        crud.create_user(user_2)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_1.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_fantasy_league_draft_position(fantasy_league.id, user_1.id, 1)
        create_fantasy_league_draft_position(fantasy_league.id, user_2.id, 2)

        user_2_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team.fantasy_league_id = fantasy_league.id
        user_2_fantasy_team.user_id = fantasy_fixtures.user_2_fixture.id
        crud.put_fantasy_team(user_2_fantasy_team)

        expected_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        expected_fantasy_team.fantasy_league_id = fantasy_league.id
        expected_fantasy_team.week = fantasy_league.current_week
        expected_fantasy_team.top_player_id = riot_fixtures.player_1_fixture.id

        # Act
        returned_fantasy_team = fantasy_team_service.pickup_player(
            fantasy_league.id, user_1.id, riot_fixtures.player_1_fixture.id
        )

        # Assert
        self.assertEqual(expected_fantasy_team, returned_fantasy_team)
        user_1_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_league.id, user_1.id
        )
        self.assertEqual(1, len(user_1_fantasy_teams_from_db))
        self.assertEqual(expected_fantasy_team, user_1_fantasy_teams_from_db[0])
        # Check that user 2's fantasy team didn't update
        user_2_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_league.id, user_2.id
        )
        self.assertEqual(1, len(user_2_fantasy_teams_from_db))
        self.assertEqual(user_2_fantasy_team, user_2_fantasy_teams_from_db[0])
        db_fantasy_league = crud.get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(
            fantasy_league.current_draft_position + 1, db_fantasy_league.current_draft_position
        )
        self.assertEqual(FantasyLeagueStatus.DRAFT, db_fantasy_league.status)

    def test_pickup_player_for_draft_league_moves_to_active_status_all_teams_fully_drafted(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_draft_fixture)
        fantasy_league.number_of_teams = 4
        fantasy_league.current_week = 0
        fantasy_league.current_draft_position = fantasy_league.number_of_teams
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        crud.create_fantasy_league(fantasy_league)

        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        user_3 = fantasy_fixtures.user_3_fixture
        user_4 = fantasy_fixtures.user_4_fixture
        users = [user_1, user_2, user_3, user_4]
        draft_position = 1
        for user in users:
            crud.create_user(user)
            create_fantasy_league_membership_for_league(
                fantasy_league.id, user.id, FantasyLeagueMembershipStatus.ACCEPTED
            )
            create_fantasy_league_draft_position(fantasy_league.id, user.id, draft_position)
            draft_position += 1

            user_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_full)
            user_fantasy_team.fantasy_league_id = fantasy_league.id
            user_fantasy_team.user_id = user.id
            user_fantasy_team.week = fantasy_league.current_week

            if user.id == user_4.id:  # Set the user 4 to have an empty spot for the draft call
                user_fantasy_team.top_player_id = None
            crud.put_fantasy_team(user_fantasy_team)

        # Act
        returned_fantasy_team = fantasy_team_service.pickup_player(
            fantasy_league.id, user_4.id, riot_fixtures.player_1_fixture.id
        )

        # Assert
        self.assertEqual(riot_fixtures.player_1_fixture.id, returned_fantasy_team.top_player_id)
        db_fantasy_league = crud.get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(1, db_fantasy_league.current_draft_position)
        self.assertEqual(FantasyLeagueStatus.ACTIVE, db_fantasy_league.status)

    def test_pickup_player_for_active_league_successful(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        crud.create_fantasy_league(fantasy_league)
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        crud.create_user(user_1)
        crud.create_user(user_2)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_1.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )

        user_1_fantasy_team = fantasy_fixtures.fantasy_team_week_1
        crud.put_fantasy_team(user_1_fantasy_team)

        user_2_fantasy_team = deepcopy(user_1_fantasy_team)
        user_2_fantasy_team.user_id = user_2.id
        crud.put_fantasy_team(user_2_fantasy_team)

        expected_fantasy_team = deepcopy(user_1_fantasy_team)
        expected_fantasy_team.top_player_id = riot_fixtures.player_1_fixture.id

        # Act
        returned_fantasy_team = fantasy_team_service.pickup_player(
            fantasy_league.id, user_1.id, riot_fixtures.player_1_fixture.id
        )

        # Assert
        self.assertEqual(expected_fantasy_team, returned_fantasy_team)
        user_1_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_league.id, user_1.id
        )
        self.assertEqual(1, len(user_1_fantasy_teams_from_db))
        self.assertEqual(expected_fantasy_team, user_1_fantasy_teams_from_db[0])
        # Check that user 2's fantasy team didn't update
        user_2_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_league.id, user_2.id
        )
        self.assertEqual(1, len(user_2_fantasy_teams_from_db))
        self.assertEqual(user_2_fantasy_team, user_2_fantasy_teams_from_db[0])
        db_fantasy_league = crud.get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(FantasyLeagueStatus.ACTIVE, db_fantasy_league.status)

    def test_pickup_player_not_users_current_draft_position_exception(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_draft_fixture)
        fantasy_league.current_draft_position = 2
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        crud.create_fantasy_league(fantasy_league)

        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        crud.create_user(user_1)
        crud.create_user(user_2)

        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_1.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )

        create_fantasy_league_draft_position(fantasy_league.id, user_1.id, 1)
        create_fantasy_league_draft_position(fantasy_league.id, user_2.id, 2)

        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.fantasy_league_id = fantasy_league.id
        user_1_fantasy_team.week = fantasy_league.current_week
        crud.put_fantasy_team(user_1_fantasy_team)

        user_2_fantasy_team = deepcopy(user_1_fantasy_team)
        user_2_fantasy_team.user_id = user_2.id
        crud.put_fantasy_team(user_2_fantasy_team)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.pickup_player(
                fantasy_league.id, user_1.id, riot_fixtures.player_1_fixture.id
            )
        self.assertIn("Invalid user draft position", str(context.exception))
        self.assertIn(f"user with ID {user_1.id}", str(context.exception))
        self.assertIn(f"fantasy league with ID {fantasy_league.id}", str(context.exception))
        db_user_fantasy_teams = crud.get_all_fantasy_teams_for_user(fantasy_league.id, user_1.id)
        self.assertEqual(1, len(db_user_fantasy_teams))
        self.assertEqual(user_1_fantasy_team, db_user_fantasy_teams[0])

    def test_pickup_player_no_available_leagues_for_fantasy_league_exception(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        fantasy_league.available_leagues = []
        crud.create_fantasy_league(fantasy_league)
        crud.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        crud.put_fantasy_team(fantasy_fixtures.fantasy_team_week_1)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.pickup_player(
                fantasy_league.id,
                fantasy_fixtures.user_fixture.id,
                riot_fixtures.player_1_fixture.id
            )
        self.assertIn("Player not in available league", str(context.exception))

    def test_pickup_player_not_in_available_leagues_for_fantasy_league_exception(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        fantasy_league.available_leagues = [riot_fixtures.league_2_fixture.id]
        crud.create_fantasy_league(fantasy_league)
        crud.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        crud.put_fantasy_team(fantasy_fixtures.fantasy_team_week_1)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.pickup_player(
                fantasy_league.id,
                fantasy_fixtures.user_fixture.id,
                riot_fixtures.player_1_fixture.id
            )
        self.assertIn("Player not in available league", str(context.exception))

    def test_pickup_player_no_slot_available_to_pickup_player_for_role(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        crud.create_fantasy_league(fantasy_league)
        crud.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.top_player_id = "somePlayerId"
        crud.put_fantasy_team(user_1_fantasy_team)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.pickup_player(
                fantasy_league.id,
                fantasy_fixtures.user_fixture.id,
                riot_fixtures.player_1_fixture.id
            )
        self.assertIn("Slot not available for role", str(context.exception))

    def test_pickup_player_already_drafted_exception(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        crud.create_fantasy_league(fantasy_league)
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.create_user(fantasy_fixtures.user_2_fixture)
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
        crud.put_fantasy_team(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team.user_id = fantasy_fixtures.user_2_fixture.id
        user_2_fantasy_team.top_player_id = riot_fixtures.player_1_fixture.id
        crud.put_fantasy_team(user_2_fantasy_team)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.pickup_player(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                riot_fixtures.player_1_fixture.id
            )
        self.assertIn("Player already drafted", str(context.exception))

    def test_pickup_player_fantasy_league_not_found_exception(self):
        # Arrange
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.put_player(pro_player_fixture)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_team_service.pickup_player(
                FantasyLeagueID("badFantasyLeagueId"),
                fantasy_fixtures.user_fixture.id,
                pro_player_fixture.id
            )

    def test_pickup_player_fantasy_league_not_draft_or_active_state(self):
        # Arrange
        bad_states = [
            FantasyLeagueStatus.PRE_DRAFT,
            FantasyLeagueStatus.COMPLETED,
            FantasyLeagueStatus.DELETED
        ]
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.put_player(pro_player_fixture)

        # Act and Assert
        for bad_state in bad_states:
            bad_fantasy_league = fantasy_fixtures.fantasy_league_fixture.model_copy(deep=True)
            bad_fantasy_league.id = FantasyLeagueID(str(uuid.uuid4()))
            bad_fantasy_league.status = bad_state
            crud.create_fantasy_league(bad_fantasy_league)
            with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
                fantasy_team_service.pickup_player(
                    bad_fantasy_league.id,
                    fantasy_fixtures.user_fixture.id,
                    pro_player_fixture.id
                )

    def test_pickup_player_user_not_an_active_member_exception(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        crud.create_fantasy_league(fantasy_league)
        crud.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.PENDING
        )

        # Act and Assert
        with self.assertRaises(FantasyMembershipException):
            fantasy_team_service.pickup_player(
                fantasy_league.id,
                fantasy_fixtures.user_fixture.id,
                riot_fixtures.player_1_fixture.id
            )

    def test_pickup_player_professional_player_not_found_exception(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        crud.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        crud.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and Assert
        with self.assertRaises(ProfessionalPlayerNotFoundException):
            fantasy_team_service.pickup_player(
                fantasy_fixtures.fantasy_league_active_fixture.id,
                fantasy_fixtures.user_fixture.id,
                ProPlayerID("badProPlayerId")
            )

    # -------------------------------------
    # ----------- Drop Player  ------------
    # -------------------------------------

    def test_drop_player_successful(self):
        # Arrange
        crud.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.create_user(fantasy_fixtures.user_2_fixture)
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
        crud.put_fantasy_team(user_1_fantasy_team)

        user_2_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team.user_id = fantasy_fixtures.user_2_fixture.id
        user_2_fantasy_team.jungle_player_id = "someOtherPlayerId"
        crud.put_fantasy_team(user_2_fantasy_team)
        crud.put_player(pro_player_fixture)

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
        self.assertEqual(expected_fantasy_team, user_1_fantasy_teams_from_db[0])
        # Check that user 2's fantasy team didn't update
        user_2_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_fixtures.fantasy_league_active_fixture.id, fantasy_fixtures.user_2_fixture.id
        )
        self.assertEqual(1, len(user_2_fantasy_teams_from_db))
        self.assertEqual(user_2_fantasy_team, user_2_fantasy_teams_from_db[0])

    def test_drop_player_user_does_not_have_player_drafted_exception(self):
        # Arrange
        crud.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        crud.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.jungle_player_id = "someOtherPlayerId"
        crud.put_fantasy_team(user_1_fantasy_team)
        crud.put_player(pro_player_fixture)

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
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.put_player(pro_player_fixture)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_team_service.drop_player(
                FantasyLeagueID("badFantasyLeagueId"),
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
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.put_player(pro_player_fixture)

        # Act and Assert
        for bad_state in bad_states:
            bad_fantasy_league = fantasy_fixtures.fantasy_league_fixture.model_copy(deep=True)
            bad_fantasy_league.id = FantasyLeagueID(str(uuid.uuid4()))
            bad_fantasy_league.status = bad_state
            crud.create_fantasy_league(bad_fantasy_league)
            with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
                fantasy_team_service.drop_player(
                    bad_fantasy_league.id,
                    fantasy_fixtures.user_fixture.id,
                    pro_player_fixture.id
                )

    def test_drop_player_user_not_an_active_member_exception(self):
        # Arrange
        crud.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.put_player(pro_player_fixture)
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
        crud.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        crud.create_user(fantasy_fixtures.user_fixture)
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
                ProPlayerID("badProPlayerId")
            )

    # -------------------------------------
    # ------------ Swap Player  -----------
    # -------------------------------------

    def test_swap_players_successful(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        crud.create_fantasy_league(fantasy_league)
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.create_user(fantasy_fixtures.user_2_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_2_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        jungle_player_1 = riot_fixtures.player_2_fixture
        jungle_player_2 = riot_fixtures.player_7_fixture
        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.jungle_player_id = jungle_player_1.id
        crud.put_fantasy_team(user_1_fantasy_team)

        user_2_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team.user_id = fantasy_fixtures.user_2_fixture.id
        user_2_fantasy_team.jungle_player_id = "someOtherJunglePlayerId"
        crud.put_fantasy_team(user_2_fantasy_team)

        expected_fantasy_team = deepcopy(user_1_fantasy_team)
        expected_fantasy_team.jungle_player_id = jungle_player_2.id

        # Act
        returned_fantasy_team = fantasy_team_service.swap_players(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            jungle_player_1.id,
            jungle_player_2.id
        )

        # Assert
        self.assertEqual(expected_fantasy_team, returned_fantasy_team)
        user_1_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_league.id, fantasy_fixtures.user_fixture.id
        )
        self.assertEqual(1, len(user_1_fantasy_teams_from_db))
        self.assertEqual(expected_fantasy_team, user_1_fantasy_teams_from_db[0])
        # Check that user 2's fantasy team didn't update
        user_2_fantasy_teams_from_db = crud.get_all_fantasy_teams_for_user(
            fantasy_league.id, fantasy_fixtures.user_2_fixture.id
        )
        self.assertEqual(1, len(user_2_fantasy_teams_from_db))
        self.assertEqual(user_2_fantasy_team, user_2_fantasy_teams_from_db[0])
        self.assertEqual(jungle_player_1.role, jungle_player_2.role)

    def test_swap_players_mismatched_player_roles_exception(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        crud.create_fantasy_league(fantasy_league)
        crud.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        player_1 = riot_fixtures.player_1_fixture
        player_2 = riot_fixtures.player_2_fixture
        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.jungle_player_id = player_2.id
        crud.put_fantasy_team(user_1_fantasy_team)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.swap_players(
                fantasy_league.id,
                fantasy_fixtures.user_fixture.id,
                player_2.id,
                player_1.id
            )
        self.assertIn("Mismatching roles", str(context.exception))
        self.assertNotEqual(player_1.role, player_2.role)

    def test_swap_players_user_does_not_have_player_drafted_exception(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        crud.create_fantasy_league(fantasy_league)
        crud.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        jungle_player_1 = riot_fixtures.player_2_fixture
        jungle_player_2 = riot_fixtures.player_7_fixture
        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.jungle_player_id = "someOtherPlayerId"
        crud.put_fantasy_team(user_1_fantasy_team)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.swap_players(
                fantasy_league.id,
                fantasy_fixtures.user_fixture.id,
                jungle_player_1.id,
                jungle_player_2.id
            )
        self.assertIn("Player not drafted", str(context.exception))
        self.assertEqual(jungle_player_1.role, jungle_player_2.role)

    def test_swap_players_already_drafted_exception(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        fantasy_league.available_leagues = [riot_fixtures.league_1_fixture.id]
        crud.create_fantasy_league(fantasy_league)
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        crud.create_user(user_1)
        crud.create_user(user_2)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_1.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.jungle_player_id = riot_fixtures.player_2_fixture.id
        crud.put_fantasy_team(user_1_fantasy_team)

        user_2_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_2_fantasy_team.user_id = user_2.id
        user_2_fantasy_team.jungle_player_id = riot_fixtures.player_7_fixture.id
        crud.put_fantasy_team(user_2_fantasy_team)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.swap_players(
                fantasy_league.id,
                user_1.id,
                riot_fixtures.player_2_fixture.id,
                riot_fixtures.player_7_fixture.id
            )
        self.assertIn("Player already drafted", str(context.exception))
        db_user_1_fantasy_teams = crud.get_all_fantasy_teams_for_user(
            fantasy_league.id, user_1.id
        )
        self.assertIsInstance(db_user_1_fantasy_teams, list)
        self.assertEqual(1, len(db_user_1_fantasy_teams))
        self.assertEqual(user_1_fantasy_team, db_user_1_fantasy_teams[0])
        db_user_2_fantasy_teams = crud.get_all_fantasy_teams_for_user(
            fantasy_league.id, user_2.id
        )
        self.assertIsInstance(db_user_2_fantasy_teams, list)
        self.assertEqual(1, len(db_user_2_fantasy_teams))
        self.assertEqual(user_2_fantasy_team, db_user_2_fantasy_teams[0])

    def test_swap_players_player_to_pickup_not_in_available_leagues_exception(self):
        # Arrange
        setup_league_team_player_date()
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        fantasy_league.available_leagues = ["12345"]
        crud.create_fantasy_league(fantasy_league)
        crud.create_user(fantasy_fixtures.user_fixture)
        create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        user_1_fantasy_team = deepcopy(fantasy_fixtures.fantasy_team_week_1)
        user_1_fantasy_team.jungle_player_id = riot_fixtures.player_2_fixture.id
        crud.put_fantasy_team(user_1_fantasy_team)

        # Act and Assert
        with self.assertRaises(FantasyDraftException) as context:
            fantasy_team_service.swap_players(
                fantasy_league.id,
                fantasy_fixtures.user_fixture.id,
                riot_fixtures.player_2_fixture.id,
                riot_fixtures.player_7_fixture.id
            )
        self.assertIn("Player not in available league", str(context.exception))

    def test_swap_players_fantasy_league_not_found_exception(self):
        # Arrange
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.put_player(pro_player_fixture)
        crud.put_player(pro_player_2_fixture)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_team_service.swap_players(
                FantasyLeagueID("badFantasyLeagueId"),
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
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.put_player(pro_player_fixture)
        crud.put_player(pro_player_2_fixture)

        # Act and Assert
        for bad_state in bad_states:
            bad_fantasy_league = fantasy_fixtures.fantasy_league_fixture.model_copy(deep=True)
            bad_fantasy_league.id = FantasyLeagueID(str(uuid.uuid4()))
            bad_fantasy_league.status = bad_state
            crud.create_fantasy_league(bad_fantasy_league)
            with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
                fantasy_team_service.swap_players(
                    bad_fantasy_league.id,
                    fantasy_fixtures.user_fixture.id,
                    pro_player_fixture.id,
                    pro_player_2_fixture.id
                )

    def test_swap_players_user_not_an_active_member_exception(self):
        # Arrange
        crud.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.put_player(pro_player_fixture)
        crud.put_player(pro_player_2_fixture)
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
        crud.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.put_player(pro_player_2_fixture)
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
                ProPlayerID("badProPlayerId"),
                pro_player_2_fixture.id
            )

    def test_swap_players_professional_player_to_pickup_not_found_exception(self):
        # Arrange
        crud.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        crud.create_user(fantasy_fixtures.user_fixture)
        crud.put_player(pro_player_fixture)
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
                ProPlayerID("badProPlayerId")
            )


def create_fantasy_league_membership_for_league(
        league_id: FantasyLeagueID, user_id: UserID, status: FantasyLeagueMembershipStatus):
    fantasy_league_membership = FantasyLeagueMembership(
        league_id=league_id,
        user_id=user_id,
        status=status
    )
    crud.create_fantasy_league_membership(fantasy_league_membership)


def create_fantasy_league_draft_position(
        fantasy_league_id: FantasyLeagueID, user_id: UserID, position: int):
    fantasy_league_draft_order = FantasyLeagueDraftOrder(
        fantasy_league_id=fantasy_league_id,
        user_id=user_id,
        position=position
    )
    crud.create_fantasy_league_draft_order(fantasy_league_draft_order)


def setup_league_team_player_date():
    crud.put_league(riot_fixtures.league_1_fixture)
    crud.put_league(riot_fixtures.league_2_fixture)
    crud.put_team(riot_fixtures.team_1_fixture)
    crud.put_team(riot_fixtures.team_2_fixture)
    crud.put_player(riot_fixtures.player_1_fixture)
    crud.put_player(riot_fixtures.player_2_fixture)
    crud.put_player(riot_fixtures.player_7_fixture)
