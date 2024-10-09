import uuid
from copy import deepcopy

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures, riot_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueID,
    FantasyLeagueStatus,
    FantasyLeagueMembershipStatus,
    FantasyLeagueMembership,
    FantasyLeagueSettings,
    FantasyLeagueScoringSettings,
    FantasyLeagueDraftOrder,
    FantasyLeagueDraftOrderResponse,
    UsersFantasyLeagues,
    UserAccountStatus,
    UserID
)
from src.common.exceptions import LeagueNotFoundException
from src.fantasy.exceptions import (
    DraftOrderException,
    FantasyLeagueInviteException,
    FantasyLeagueNotFoundException,
    FantasyLeagueSettingsException,
    FantasyLeagueStartDraftException,
    FantasyUnavailableException,
    FantasyLeagueInvalidRequiredStateException,
    ForbiddenException,
    UserNotFoundException
)
from src.fantasy.service import FantasyLeagueService


class FantasyLeagueServiceIntegrationTest(TestBase):
    def setUp(self):
        super().setUp()
        self.fantasy_league_service = FantasyLeagueService(self.db)

    # --------------------------------------------------
    # ------------- Create Fantasy League  -------------
    # --------------------------------------------------
    def test_draft_order_entry_created_on_fantasy_league_creation(self):
        # Arrange
        fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)

        # Act
        new_fantasy_league = self.fantasy_league_service.create_fantasy_league(
            user.id, fantasy_league_settings
        )
        expected_draft_order = FantasyLeagueDraftOrder(
            fantasy_league_id=new_fantasy_league.id, user_id=user.id, position=1
        )

        # Assert
        draft_order_from_db = self.db.get_fantasy_league_draft_order(new_fantasy_league.id)
        self.assertEqual(1, len(draft_order_from_db))
        self.assertEqual(
            FantasyLeagueDraftOrder.model_validate(expected_draft_order),
            FantasyLeagueDraftOrder.model_validate(draft_order_from_db[0])
        )

    def test_default_fantasy_league_scoring_settings_created_on_fantasy_league_creation(self):
        # Arrange
        fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)

        # Act
        new_fantasy_league = self.fantasy_league_service.create_fantasy_league(
            user.id, fantasy_league_settings
        )
        expected_default_settings = FantasyLeagueScoringSettings(
            fantasy_league_id=new_fantasy_league.id
        )

        # Assert
        scoring_settings_from_db = self.db.get_fantasy_league_scoring_settings_by_id(
            new_fantasy_league.id
        )
        self.assertIsNotNone(scoring_settings_from_db)
        self.assertEqual(
            FantasyLeagueScoringSettings.model_validate(expected_default_settings),
            FantasyLeagueScoringSettings.model_validate(scoring_settings_from_db)
        )

    def test_fantasy_league_membership_created_on_fantasy_league_creation(self):
        # Arrange
        fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)

        # Act
        new_fantasy_league = self.fantasy_league_service.create_fantasy_league(
            user.id, fantasy_league_settings
        )

        # Assert
        fantasy_league_memberships = self.test_db.get_all_league_memberships(new_fantasy_league.id)
        self.assertEqual(1, len(fantasy_league_memberships))
        self.assertEqual(user.id, fantasy_league_memberships[0].user_id)
        self.assertEqual(
            FantasyLeagueMembershipStatus.ACCEPTED,
            fantasy_league_memberships[0].status
        )

    def test_create_fantasy_league_with_available_leagues_successful(self):
        # Arrange
        fantasy_league_settings = deepcopy(fantasy_fixtures.fantasy_league_settings_fixture)
        fantasy_league_settings.available_leagues = [riot_fixtures.league_2_fixture.id]
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_league(riot_fixtures.league_2_fixture)

        # Act
        returned_fantasy_league = self.fantasy_league_service.create_fantasy_league(
            user.id, fantasy_league_settings
        )

        # Assert
        self.assertEqual(1, len(returned_fantasy_league.available_leagues))
        self.assertEqual(
            riot_fixtures.league_2_fixture.id, returned_fantasy_league.available_leagues[0]
        )
        self.assertFalse(riot_fixtures.league_1_fixture.fantasy_available)
        self.assertTrue(riot_fixtures.league_2_fixture.fantasy_available)

    def test_create_fantasy_league_with_available_leagues_riot_league_not_found_exception(self):
        # Arrange
        fantasy_league_settings = deepcopy(fantasy_fixtures.fantasy_league_settings_fixture)
        fantasy_league_settings.available_leagues = ["badRiotLeagueId"]
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_league(riot_fixtures.league_2_fixture)

        # Act and Assert
        with self.assertRaises(LeagueNotFoundException):
            self.fantasy_league_service.create_fantasy_league(user.id, fantasy_league_settings)
        self.assertFalse(riot_fixtures.league_1_fixture.fantasy_available)
        self.assertTrue(riot_fixtures.league_2_fixture.fantasy_available)

    def test_create_fantasy_league_with_available_leagues_riot_league_unavailable_exception(self):
        # Arrange
        fantasy_league_settings = deepcopy(fantasy_fixtures.fantasy_league_settings_fixture)
        fantasy_league_settings.available_leagues = [riot_fixtures.league_1_fixture.id]
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_league(riot_fixtures.league_2_fixture)

        # Act and Assert
        with self.assertRaises(FantasyUnavailableException):
            self.fantasy_league_service.create_fantasy_league(user.id, fantasy_league_settings)
        self.assertFalse(riot_fixtures.league_1_fixture.fantasy_available)
        self.assertTrue(riot_fixtures.league_2_fixture.fantasy_available)

    # --------------------------------------------------
    # ----------- Get Fantasy League Settings ----------
    # --------------------------------------------------

    def test_get_fantasy_league_settings_successful(self):
        # Arrange
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        self.db.create_user(fantasy_fixtures.user_fixture)
        expected_fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture

        # Act
        returned_fantasy_league_settings = self.fantasy_league_service.get_fantasy_league_settings(
            fantasy_fixtures.user_fixture.id, fantasy_fixtures.fantasy_league_fixture.id
        )

        # Assert
        self.assertEqual(
            expected_fantasy_league_settings,
            FantasyLeagueSettings.model_validate(returned_fantasy_league_settings)
        )

    def test_get_fantasy_league_settings_non_existing_fantasy_league_exception(self):
        # Arrange
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        self.db.create_user(fantasy_fixtures.user_fixture)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.get_fantasy_league_settings(
                fantasy_fixtures.user_fixture.id, FantasyLeagueID("badFantasyLeagueId")
            )

    def test_get_fantasy_league_settings_non_owner_of_fantasy_league_exception(self):
        # Arrange
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        self.db.create_user(fantasy_fixtures.user_fixture)
        self.db.create_user(fantasy_fixtures.user_2_fixture)

        # Act
        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.get_fantasy_league_settings(
                fantasy_fixtures.user_2_fixture.id, fantasy_fixtures.fantasy_league_fixture.id
            )

    # --------------------------------------------------
    # --------- Update Fantasy League Settings ---------
    # --------------------------------------------------

    def test_update_fantasy_league_settings_successful(self):
        # Arrange
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        self.db.create_user(fantasy_fixtures.user_fixture)
        updated_fantasy_league_settings = deepcopy(fantasy_fixtures.fantasy_league_settings_fixture)
        updated_fantasy_league_settings.name = "updatedFantasyLeague"

        # Act
        returned_settings = self.fantasy_league_service.update_fantasy_league_settings(
            fantasy_fixtures.user_fixture.id,
            fantasy_fixtures.fantasy_league_fixture.id,
            updated_fantasy_league_settings
        )

        # Assert
        self.assertEqual(
            updated_fantasy_league_settings,
            FantasyLeagueSettings.model_validate(returned_settings)
        )

    def test_update_fantasy_league_settings_available_leagues_successful(self):
        # Arrange
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_league(riot_fixtures.league_2_fixture)
        self.db.create_user(fantasy_fixtures.user_fixture)
        updated_fantasy_league_settings = deepcopy(fantasy_fixtures.fantasy_league_settings_fixture)
        updated_fantasy_league_settings.available_leagues = [riot_fixtures.league_2_fixture.id]

        # Act
        returned_settings = self.fantasy_league_service.update_fantasy_league_settings(
            fantasy_fixtures.user_fixture.id,
            fantasy_fixtures.fantasy_league_fixture.id,
            updated_fantasy_league_settings
        )

        # Assert
        self.assertEqual(updated_fantasy_league_settings, returned_settings)

    def test_update_fantasy_league_settings_available_leagues_riot_league_not_found_exception(self):
        # Arrange
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_league(riot_fixtures.league_2_fixture)
        self.db.create_user(fantasy_fixtures.user_fixture)
        updated_fantasy_league_settings = deepcopy(fantasy_fixtures.fantasy_league_settings_fixture)
        updated_fantasy_league_settings.available_leagues = ["badRiotLeagueId"]

        # Act and Assert
        with self.assertRaises(LeagueNotFoundException):
            self.fantasy_league_service.update_fantasy_league_settings(
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                updated_fantasy_league_settings
            )

    def test_update_fantasy_league_settings_available_fantasy_unavailable_exception(self):
        # Arrange
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_league(riot_fixtures.league_2_fixture)
        self.db.create_user(fantasy_fixtures.user_fixture)
        updated_fantasy_league_settings = deepcopy(fantasy_fixtures.fantasy_league_settings_fixture)
        updated_fantasy_league_settings.available_leagues = [riot_fixtures.league_1_fixture.id]

        # Act and Assert
        with self.assertRaises(FantasyUnavailableException):
            self.fantasy_league_service.update_fantasy_league_settings(
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                updated_fantasy_league_settings
            )

    def test_update_fantasy_league_settings_non_existing_fantasy_league_exception(self):
        # Arrange
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        self.db.create_user(fantasy_fixtures.user_fixture)
        updated_fantasy_league_settings = deepcopy(fantasy_fixtures.fantasy_league_settings_fixture)
        updated_fantasy_league_settings.name = "updatedFantasyLeague"

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.update_fantasy_league_settings(
                fantasy_fixtures.user_fixture.id,
                FantasyLeagueID("badFantasyLeagueId"),
                updated_fantasy_league_settings
            )

    def test_update_fantasy_league_settings_non_owner_of_fantasy_league_exception(self):
        # Arrange
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        self.db.create_user(fantasy_fixtures.user_fixture)
        self.db.create_user(fantasy_fixtures.user_2_fixture)
        updated_fantasy_league_settings = deepcopy(fantasy_fixtures.fantasy_league_settings_fixture)
        updated_fantasy_league_settings.name = "updatedFantasyLeague"

        # Act and Assert
        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.update_fantasy_league_settings(
                fantasy_fixtures.user_2_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                updated_fantasy_league_settings
            )

    def test_update_fantasy_league_settings_status_not_pre_draft_exception(self):
        # Arrange
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        self.db.create_user(fantasy_fixtures.user_fixture)
        updated_fantasy_league_settings = deepcopy(fantasy_fixtures.fantasy_league_settings_fixture)
        updated_fantasy_league_settings.name = "updatedFantasyLeague"

        # Act and Assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            self.fantasy_league_service.update_fantasy_league_settings(
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.fantasy_league_active_fixture.id,
                updated_fantasy_league_settings
            )

    def test_update_fantasy_league_settings_num_teams_less_than_active_member_count(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        for _ in range(fantasy_league.number_of_teams):
            new_user_id = str(uuid.uuid4())
            self.create_fantasy_league_membership_for_league(
                fantasy_league.id, UserID(new_user_id), FantasyLeagueMembershipStatus.ACCEPTED
            )
        updated_fantasy_league_settings = deepcopy(fantasy_fixtures.fantasy_league_settings_fixture)
        updated_fantasy_league_settings.number_of_teams = 4

        # Act and Assert
        with self.assertRaises(FantasyLeagueSettingsException):
            self.fantasy_league_service.update_fantasy_league_settings(
                fantasy_fixtures.user_fixture.id,
                fantasy_league.id,
                updated_fantasy_league_settings
            )

    # --------------------------------------------------
    # ------ Get Fantasy League Scoring Settings -------
    # --------------------------------------------------

    def test_get_fantasy_league_scoring_settings_successful(self):
        # Arrange
        expected_scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)
        self.db.create_fantasy_league(fantasy_league)
        self.db.put_fantasy_league_scoring_settings(expected_scoring_settings)

        # Act
        returned_scoring_settings = self.fantasy_league_service.get_scoring_settings(
            user.id, fantasy_league.id
        )

        # Assert
        self.assertEqual(expected_scoring_settings, returned_scoring_settings)

    def test_get_fantasy_league_scoring_settings_settings_not_owner_of_league(self):
        # Arrange
        scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)
        self.db.create_fantasy_league(fantasy_league)
        self.db.put_fantasy_league_scoring_settings(scoring_settings)

        # Act and Act
        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.get_scoring_settings(UserID("badUserId"), fantasy_league.id)

    def test_get_fantasy_league_scoring_non_existing_league(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)

        # Act and Act
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.get_scoring_settings(
                user.id, FantasyLeagueID("badLeagueId"))

    # --------------------------------------------------
    # ----- Update Fantasy League Scoring Settings -----
    # --------------------------------------------------

    def test_update_scoring_settings_successful(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        self.db.create_user(user)
        self.db.create_fantasy_league(fantasy_league)
        self.db.put_fantasy_league_scoring_settings(scoring_settings)

        expected_updated_scoring_settings = deepcopy(scoring_settings)
        expected_updated_scoring_settings.assists += 1
        expected_updated_scoring_settings.wards_placed += 1

        # Act
        returned_scoring_settings = self.fantasy_league_service.update_scoring_settings(
            fantasy_league.id, user.id, expected_updated_scoring_settings
        )

        # Assert
        self.assertEqual(expected_updated_scoring_settings, returned_scoring_settings)
        db_scoring_settings = self.db.get_fantasy_league_scoring_settings_by_id(fantasy_league.id)
        self.assertEqual(
            expected_updated_scoring_settings,
            FantasyLeagueScoringSettings.model_validate(db_scoring_settings)
        )

    def test_update_scoring_settings_non_existing_fantasy_league_exception(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        self.db.create_user(user)
        self.db.create_fantasy_league(fantasy_league)
        self.db.put_fantasy_league_scoring_settings(scoring_settings)

        expected_updated_scoring_settings = deepcopy(scoring_settings)
        expected_updated_scoring_settings.assists += 1
        expected_updated_scoring_settings.wards_placed += 1

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.update_scoring_settings(
                FantasyLeagueID("badFantasyLeagueId"), user.id, expected_updated_scoring_settings
            )

    def test_update_scoring_settings_not_in_pre_draft_status_exception(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        active_fantasy_league = fantasy_fixtures.fantasy_league_active_fixture
        scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        self.db.create_user(user)
        self.db.create_fantasy_league(active_fantasy_league)
        self.db.put_fantasy_league_scoring_settings(scoring_settings)

        expected_updated_scoring_settings = deepcopy(scoring_settings)
        expected_updated_scoring_settings.assists += 1
        expected_updated_scoring_settings.wards_placed += 1

        # Act and Assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            self.fantasy_league_service.update_scoring_settings(
                active_fantasy_league.id, user.id, expected_updated_scoring_settings
            )

    def test_update_scoring_settings_not_owner_exception(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        self.db.create_user(user)
        self.db.create_fantasy_league(fantasy_league)
        self.db.put_fantasy_league_scoring_settings(scoring_settings)

        expected_updated_scoring_settings = deepcopy(scoring_settings)
        expected_updated_scoring_settings.assists += 1
        expected_updated_scoring_settings.wards_placed += 1

        # Act and Assert
        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.update_scoring_settings(
                fantasy_league.id, UserID("badUserId"), expected_updated_scoring_settings
            )

    def test_update_scoring_settings_fantasy_league_id_is_ignored_successful(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)
        fantasy_league_1 = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league_1)
        fantasy_league_1_scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        self.db.put_fantasy_league_scoring_settings(fantasy_league_1_scoring_settings)

        fantasy_league_2 = deepcopy(fantasy_league_1)
        fantasy_league_2.id = FantasyLeagueID(str(uuid.uuid4()))
        self.db.create_fantasy_league(fantasy_league_2)
        fantasy_league_2_scoring_settings = deepcopy(fantasy_league_1_scoring_settings)
        fantasy_league_2_scoring_settings.fantasy_league_id = fantasy_league_2.id
        self.db.put_fantasy_league_scoring_settings(fantasy_league_2_scoring_settings)

        expected_updated_scoring_settings = deepcopy(fantasy_league_1_scoring_settings)
        expected_updated_scoring_settings.assists += 1
        expected_updated_scoring_settings.wards_placed += 1

        # Put fantasy league 2's id into the scoring settings, but should be ignored in the
        # update and update only fantasy league 1's scoring settings instead
        updated_fantasy_league_1_scoring_settings = deepcopy(expected_updated_scoring_settings)
        updated_fantasy_league_1_scoring_settings.fantasy_league_id = fantasy_league_2.id

        # Act
        returned_scoring_settings = self.fantasy_league_service.update_scoring_settings(
            fantasy_league_1.id, user.id, updated_fantasy_league_1_scoring_settings
        )

        # Assert
        self.assertNotEqual(fantasy_league_1.id, fantasy_league_2.id)
        self.assertEqual(expected_updated_scoring_settings, returned_scoring_settings)
        league_2_scoring_settings_from_db = self.db.get_fantasy_league_scoring_settings_by_id(
            fantasy_league_2.id
        )
        self.assertEqual(
            fantasy_league_2_scoring_settings,
            FantasyLeagueScoringSettings.model_validate(league_2_scoring_settings_from_db)
        )

    # --------------------------------------------------
    # ---- Get Pending and Accepted Fantasy Leagues ----
    # --------------------------------------------------

    def test_get_users_pending_and_accepted_fantasy_leagues_successful(self):
        # Arrange
        self.db.create_user(fantasy_fixtures.user_fixture)
        self.db.create_user(fantasy_fixtures.user_2_fixture)
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)

        # Create user_1's memberships, all ACCEPTED as they are the owner
        self.create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        self.create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Create user_2's memberships
        self.create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_fixture.id,
            fantasy_fixtures.user_2_fixture.id,
            FantasyLeagueMembershipStatus.PENDING
        )
        self.create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_2_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act
        users_fantasy_leagues = self.fantasy_league_service. \
            get_users_pending_and_accepted_fantasy_leagues(fantasy_fixtures.user_2_fixture.id)

        # Assert
        self.assertIsInstance(users_fantasy_leagues, UsersFantasyLeagues)
        self.assertEqual(1, len(users_fantasy_leagues.pending))
        self.assertEqual(
            fantasy_fixtures.fantasy_league_fixture,
            FantasyLeague.model_validate(users_fantasy_leagues.pending[0])
        )
        self.assertEqual(1, len(users_fantasy_leagues.accepted))
        self.assertEqual(
            fantasy_fixtures.fantasy_league_active_fixture,
            FantasyLeague.model_validate(users_fantasy_leagues.accepted[0])
        )

    def test_get_users_pending_and_accepted_fantasy_leagues_no_pending_or_accepted(self):
        # Arrange
        self.db.create_user(fantasy_fixtures.user_fixture)
        self.db.create_user(fantasy_fixtures.user_2_fixture)
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)

        # Create user_1's memberships, all ACCEPTED as they are the owner
        self.create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        self.create_fantasy_league_membership_for_league(
            fantasy_fixtures.fantasy_league_active_fixture.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act
        users_fantasy_leagues = self.fantasy_league_service. \
            get_users_pending_and_accepted_fantasy_leagues(fantasy_fixtures.user_2_fixture.id)

        # Assert
        self.assertIsInstance(users_fantasy_leagues, UsersFantasyLeagues)
        self.assertEqual(0, len(users_fantasy_leagues.pending))
        self.assertEqual(0, len(users_fantasy_leagues.accepted))

    # --------------------------------------------------
    # ----------- Send Fantasy League Invite -----------
    # --------------------------------------------------

    def test_send_fantasy_league_invite_successful(self):
        # Arrange
        user_2 = fantasy_fixtures.user_2_fixture
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_user(user)
        self.db.create_user(user_2)
        self.db.create_fantasy_league(fantasy_league)

        # Act
        self.fantasy_league_service.send_fantasy_league_invite(
            user.id, fantasy_league.id, user_2.username
        )

        # Assert
        pending_and_active_members = self.db.get_pending_and_accepted_members_for_league(
            fantasy_league.id
        )
        self.assertEqual(1, len(pending_and_active_members))
        self.assertEqual(user_2.id, pending_and_active_members[0].user_id)

    def test_send_fantasy_league_invite_not_as_owner(self):
        # Arrange
        user_2 = fantasy_fixtures.user_2_fixture
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_user(user)
        self.db.create_user(user_2)
        self.db.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.send_fantasy_league_invite(
                UserID("badOwnerId"), fantasy_league.id, user_2.username
            )

    def test_send_fantasy_league_invite_for_non_existing_league(self):
        # Arrange
        user_2 = fantasy_fixtures.user_2_fixture
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_user(user)
        self.db.create_user(user_2)
        self.db.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.send_fantasy_league_invite(
                user.id, FantasyLeagueID("badLeagueId"), user_2.username
            )

    def test_send_fantasy_league_invite_outside_of_pre_draft_status_exception(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        active_fantasy_league = fantasy_fixtures.fantasy_league_active_fixture
        self.db.create_user(user_1)
        self.db.create_user(user_2)
        self.db.create_fantasy_league(active_fantasy_league)

        # Act and Assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            self.fantasy_league_service.send_fantasy_league_invite(
                user_1.id, active_fantasy_league.id, user_2.username
            )

    def test_send_fantasy_league_invite_to_non_existing_user(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_user(user)
        self.db.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(UserNotFoundException):
            self.fantasy_league_service.send_fantasy_league_invite(
                user.id, fantasy_league.id, "badUserName"
            )

    def test_send_fantasy_league_invite_to_deleted_user(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        deleted_user = fantasy_fixtures.user_2_fixture
        deleted_user.account_status = UserAccountStatus.DELETED
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_user(user)
        self.db.create_user(deleted_user)
        self.db.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(UserNotFoundException):
            self.fantasy_league_service.send_fantasy_league_invite(
                user.id, fantasy_league.id, deleted_user.username
            )

    def test_send_fantasy_league_invite_exceeds_max_number_of_players(self):
        # Arrange
        user_2 = fantasy_fixtures.user_2_fixture
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_user(user)
        self.db.create_user(user_2)
        self.db.create_fantasy_league(fantasy_league)
        for _ in range(fantasy_league.number_of_teams):
            new_user_id = UserID(str(uuid.uuid4()))
            self.create_fantasy_league_membership_for_league(
                fantasy_league.id, new_user_id, FantasyLeagueMembershipStatus.PENDING
            )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            self.fantasy_league_service.send_fantasy_league_invite(
                user.id, fantasy_league.id, user_2.username
            )

    # --------------------------------------------------
    # -------------- Join Fantasy League ---------------
    # --------------------------------------------------

    def test_join_fantasy_league_successful(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.PENDING
        )
        self.create_draft_order_for_fantasy_league(fantasy_league.id, user_1.id, 1)
        expected_user_1_draft_order = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
        )
        expected_user_2_draft_order = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
        )

        # Act
        self.fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

        # Assert
        pending_and_active_members = self.db.get_pending_and_accepted_members_for_league(
            fantasy_league.id
        )
        self.assertEqual(1, len(pending_and_active_members))
        membership_from_db = pending_and_active_members[0]
        self.assertEqual(user_2.id, membership_from_db.user_id)
        self.assertEqual(FantasyLeagueMembershipStatus.ACCEPTED, membership_from_db.status)

        draft_order_from_db = self.db.get_fantasy_league_draft_order(fantasy_league.id)
        draft_order_from_db.sort(key=lambda x: x.position)
        self.assertEqual(2, len(draft_order_from_db))
        self.assertEqual(
            FantasyLeagueDraftOrder.model_validate(expected_user_1_draft_order),
            FantasyLeagueDraftOrder.model_validate(draft_order_from_db[0])
        )
        self.assertEqual(
            FantasyLeagueDraftOrder.model_validate(expected_user_2_draft_order),
            FantasyLeagueDraftOrder.model_validate(draft_order_from_db[1])
        )

    def test_join_fantasy_league_no_membership_for_league(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        user_2 = fantasy_fixtures.user_2_fixture

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            self.fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

    def test_join_fantasy_league_revoked_membership(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.REVOKED
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            self.fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

    def test_join_fantasy_league_declined_membership(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.DECLINED
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            self.fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

    def test_join_fantasy_league_already_accepted_status(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act
        self.fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

        # Assert
        pending_and_active_members = self.db.get_pending_and_accepted_members_for_league(
            fantasy_league.id
        )
        self.assertEqual(1, len(pending_and_active_members))
        membership_from_db = pending_and_active_members[0]
        self.assertEqual(user_2.id, membership_from_db.user_id)
        self.assertEqual(FantasyLeagueMembershipStatus.ACCEPTED, membership_from_db.status)

    def test_join_non_existing_fantasy_league(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_2 = fantasy_fixtures.user_2_fixture

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

    def test_join_full_fantasy_league(self):
        # Arrange
        user_2 = fantasy_fixtures.user_2_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        for _ in range(fantasy_league.number_of_teams):
            new_user_id = UserID(str(uuid.uuid4()))
            self.create_fantasy_league_membership_for_league(
                fantasy_league.id, new_user_id, FantasyLeagueMembershipStatus.ACCEPTED
            )
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.PENDING
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException) as context:
            self.fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)
        self.assertIn("Fantasy league is full", str(context.exception))

    def test_join_fantasy_league_not_in_pre_draft_state(self):
        # Arrange
        user_2 = fantasy_fixtures.user_2_fixture
        active_fantasy_league = fantasy_fixtures.fantasy_league_active_fixture
        self.db.create_fantasy_league(active_fantasy_league)
        self.create_fantasy_league_membership_for_league(
            active_fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.PENDING
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            self.fantasy_league_service.join_fantasy_league(user_2.id, active_fantasy_league.id)

    # --------------------------------------------------
    # -------------- Leave Fantasy League --------------
    # --------------------------------------------------

    def test_leave_fantasy_league_successful(self):
        # Arrange
        user_2 = fantasy_fixtures.user_2_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        self.create_draft_order_for_fantasy_league(fantasy_league.id, user_2.id, 2)

        # Act
        self.fantasy_league_service.leave_fantasy_league(user_2.id, fantasy_league.id)

        # Assert
        pending_and_active_members = self.test_db.get_all_league_memberships(fantasy_league.id)
        self.assertEqual(1, len(pending_and_active_members))
        membership_from_db = pending_and_active_members[0]
        self.assertEqual(user_2.id, membership_from_db.user_id)
        self.assertEqual(FantasyLeagueMembershipStatus.DECLINED, membership_from_db.status)

    def test_draft_order_is_updated_when_user_leaves_league(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        user_3 = fantasy_fixtures.user_3_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        user_1_draft_order = self.create_draft_order_for_fantasy_league(
            fantasy_league.id, user_1.id, 1)
        self.create_draft_order_for_fantasy_league(fantasy_league.id, user_2.id, 2)
        user_3_draft_order = self.create_draft_order_for_fantasy_league(
            fantasy_league.id, user_3.id, 3)

        # Act
        self.fantasy_league_service.leave_fantasy_league(user_2.id, fantasy_league.id)

        # Assert
        draft_order_from_db = self.db.get_fantasy_league_draft_order(fantasy_league.id)
        draft_order_from_db.sort(key=lambda x: x.position)
        self.assertEqual(2, len(draft_order_from_db))
        self.assertEqual(
            FantasyLeagueDraftOrder.model_validate(user_1_draft_order),
            FantasyLeagueDraftOrder.model_validate(draft_order_from_db[0])
        )
        expected_updated_user_3_draft_order = user_3_draft_order
        expected_updated_user_3_draft_order.position = 2
        self.assertEqual(
            FantasyLeagueDraftOrder.model_validate(expected_updated_user_3_draft_order),
            FantasyLeagueDraftOrder.model_validate(draft_order_from_db[1])
        )

    def test_leave_fantasy_league_when_owner_exception(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id, user.id, FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            self.fantasy_league_service.leave_fantasy_league(user.id, fantasy_league.id)

    def test_leave_fantasy_league_with_no_membership_exception(self):
        # Arrange
        user_2 = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            self.fantasy_league_service.leave_fantasy_league(user_2.id, fantasy_league.id)

    def test_leave_fantasy_league_with_no_accepted_membership_exception(self):
        # Arrange
        user_2 = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.PENDING
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            self.fantasy_league_service.leave_fantasy_league(user_2.id, fantasy_league.id)

    def test_leave_fantasy_league_outside_of_pre_draft_state_exception(self):
        # Arrange
        user_2 = fantasy_fixtures.user_2_fixture
        active_fantasy_league = fantasy_fixtures.fantasy_league_active_fixture
        self.db.create_fantasy_league(active_fantasy_league)
        self.create_fantasy_league_membership_for_league(
            active_fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            self.fantasy_league_service.leave_fantasy_league(user_2.id, active_fantasy_league.id)

    # --------------------------------------------------
    # ----------- Revoke From Fantasy League -----------
    # --------------------------------------------------

    def test_revoke_from_fantasy_league_successful(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)

        users = [
            fantasy_fixtures.user_fixture,
            fantasy_fixtures.user_2_fixture,
            fantasy_fixtures.user_3_fixture
        ]
        draft_order_position = 1
        for user in users:
            self.db.create_user(user)
            self.create_draft_order_for_fantasy_league(
                fantasy_league.id, user.id, draft_order_position)
            self.create_fantasy_league_membership_for_league(
                fantasy_league.id, user.id, FantasyLeagueMembershipStatus.ACCEPTED
            )
            draft_order_position += 1

        # Act
        self.fantasy_league_service.revoke_from_fantasy_league(
            fantasy_league.id, users[0].id, users[1].id
        )

        # Assert
        memberships_from_db = self.test_db.get_all_league_memberships(fantasy_league.id)
        self.assertEqual(len(users), len(memberships_from_db))
        for membership in memberships_from_db:
            if membership.user_id == users[1].id:
                self.assertEqual(membership.status, FantasyLeagueMembershipStatus.REVOKED)
            else:
                self.assertEqual(membership.status, FantasyLeagueMembershipStatus.ACCEPTED)

        draft_order_from_db = self.db.get_fantasy_league_draft_order(fantasy_league.id)
        self.assertEqual(len(users) - 1, len(draft_order_from_db))
        draft_order_from_db.sort(key=lambda x: x.position)
        self.assertEqual(users[0].id, draft_order_from_db[0].user_id)
        self.assertEqual(1, draft_order_from_db[0].position)
        self.assertEqual(users[2].id, draft_order_from_db[1].user_id)
        self.assertEqual(2, draft_order_from_db[1].position)

    def test_revoke_from_fantasy_league_non_existing_fantasy_league_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)

        users = [
            fantasy_fixtures.user_fixture,
            fantasy_fixtures.user_2_fixture,
            fantasy_fixtures.user_3_fixture
        ]
        draft_order_position = 1
        for user in users:
            self.db.create_user(user)
            self.create_draft_order_for_fantasy_league(
                fantasy_league.id, user.id, draft_order_position)
            self.create_fantasy_league_membership_for_league(
                fantasy_league.id, user.id, FantasyLeagueMembershipStatus.ACCEPTED
            )
            draft_order_position += 1

        # Act and assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.revoke_from_fantasy_league(
                FantasyLeagueID("badFantasyLeagueId"), users[0].id, users[1].id
            )

    def test_revoke_from_fantasy_league_not_in_pre_draft_status_exception(self):
        # Arrange
        active_fantasy_league = fantasy_fixtures.fantasy_league_active_fixture
        self.db.create_fantasy_league(active_fantasy_league)
        self.db.create_user(fantasy_fixtures.user_fixture)
        self.db.create_user(fantasy_fixtures.user_2_fixture)
        self.db.create_user(fantasy_fixtures.user_3_fixture)

        # Act and assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            self.fantasy_league_service.revoke_from_fantasy_league(
                active_fantasy_league.id,
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.user_2_fixture.id
            )

    def test_revoke_from_fantasy_league_not_owner_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(fantasy_fixtures.user_fixture)
        self.db.create_user(fantasy_fixtures.user_2_fixture)
        self.db.create_user(fantasy_fixtures.user_3_fixture)

        # Act and assert
        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.revoke_from_fantasy_league(
                fantasy_league.id, UserID("badUserId"), fantasy_fixtures.user_2_fixture.id
            )

    def test_revoke_from_fantasy_league_own_id_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(user)
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException) as context:
            self.fantasy_league_service.revoke_from_fantasy_league(
                fantasy_league.id, user.id, user.id)
        self.assertIn("Invalid revoke request", str(context.exception))

    def test_revoke_from_fantasy_league_no_membership_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(fantasy_fixtures.user_fixture)
        self.db.create_user(fantasy_fixtures.user_2_fixture)
        self.db.create_user(fantasy_fixtures.user_3_fixture)
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_3_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and assert
        with self.assertRaises(FantasyLeagueInviteException) as context:
            self.fantasy_league_service.revoke_from_fantasy_league(
                fantasy_league.id,
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.user_2_fixture.id
            )
        self.assertIn("No accepted membership", str(context.exception))

    def test_revoke_from_fantasy_league_no_accepted_membership_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(fantasy_fixtures.user_fixture)
        self.db.create_user(fantasy_fixtures.user_2_fixture)
        self.db.create_user(fantasy_fixtures.user_3_fixture)
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_2_fixture.id,
            FantasyLeagueMembershipStatus.PENDING
        )
        self.create_fantasy_league_membership_for_league(
            fantasy_league.id,
            fantasy_fixtures.user_3_fixture.id,
            FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and assert
        with self.assertRaises(FantasyLeagueInviteException) as context:
            self.fantasy_league_service.revoke_from_fantasy_league(
                fantasy_league.id,
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.user_2_fixture.id
            )
        self.assertIn("No accepted membership", str(context.exception))

    # --------------------------------------------------
    # --------- Get Fantasy League Draft Order ---------
    # --------------------------------------------------

    def test_get_fantasy_league_draft_order_successful(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(user_1)
        user_1_draft_order = self.create_draft_order_for_fantasy_league(
            fantasy_league.id, user_1.id, 1)
        user_1_draft_order_response = FantasyLeagueDraftOrderResponse(
            user_id=user_1.id, username=user_1.username, position=user_1_draft_order.position
        )

        # Act
        current_draft_order = self.fantasy_league_service.get_fantasy_league_draft_order(
            user_1.id, fantasy_league.id
        )

        # Assert
        self.assertIsInstance(current_draft_order, list)
        self.assertEqual(1, len(current_draft_order))
        self.assertEqual(user_1_draft_order_response, current_draft_order[0])

    def test_get_fantasy_league_draft_order_non_existing_league(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        self.db.create_user(user_1)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.get_fantasy_league_draft_order(
                user_1.id, FantasyLeagueID("badLeagueId")
            )

    def test_get_fantasy_league_draft_order_not_league_owner(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        user_1 = fantasy_fixtures.user_fixture
        self.db.create_user(user_1)

        # Act and Assert
        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.get_fantasy_league_draft_order(
                UserID("notOwner"), fantasy_league.id
            )

    # --------------------------------------------------
    # ------- Update Fantasy League Draft Order --------
    # --------------------------------------------------

    def test_update_fantasy_league_draft_order_successful(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.create_draft_order_for_fantasy_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            1
        )
        self.create_draft_order_for_fantasy_league(
            fantasy_league.id,
            fantasy_fixtures.user_2_fixture.id,
            2
        )
        expected_updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=fantasy_fixtures.user_fixture.id,
                username=fantasy_fixtures.user_fixture.username,
                position=2
            ),
            FantasyLeagueDraftOrderResponse(
                user_id=fantasy_fixtures.user_2_fixture.id,
                username=fantasy_fixtures.user_2_fixture.username,
                position=1
            )
        ]

        # Act
        self.fantasy_league_service.update_fantasy_league_draft_order(
            fantasy_fixtures.user_fixture.id,
            fantasy_fixtures.fantasy_league_fixture.id,
            expected_updated_draft_order
        )

        # Assert
        db_draft_order = self.db.get_fantasy_league_draft_order(fantasy_league.id)
        self.assertEqual(2, len(db_draft_order))
        for expected_updated_position in expected_updated_draft_order:
            for db_position in db_draft_order:
                if expected_updated_position.user_id == db_position.user_id:
                    self.assertEqual(expected_updated_position.position, db_position.position)

    def test_update_fantasy_league_draft_order_missing_members(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.create_draft_order_for_fantasy_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            1
        )
        self.create_draft_order_for_fantasy_league(
            fantasy_league.id,
            fantasy_fixtures.user_2_fixture.id,
            2
        )
        expected_updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=fantasy_fixtures.user_fixture.id,
                username=fantasy_fixtures.user_fixture.username,
                position=1
            )
        ]

        # Act and Assert
        with self.assertRaises(DraftOrderException):
            self.fantasy_league_service.update_fantasy_league_draft_order(
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                expected_updated_draft_order
            )

    def test_update_fantasy_league_draft_order_bad_user_id(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.create_draft_order_for_fantasy_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            1
        )
        self.create_draft_order_for_fantasy_league(
            fantasy_league.id,
            fantasy_fixtures.user_2_fixture.id,
            2
        )
        expected_updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=fantasy_fixtures.user_fixture.id,
                username=fantasy_fixtures.user_fixture.username,
                position=2
            ),
            FantasyLeagueDraftOrderResponse(
                user_id=fantasy_fixtures.user_3_fixture.id,
                username=fantasy_fixtures.user_3_fixture.username,
                position=1
            )
        ]

        # Act and Assert
        with self.assertRaises(DraftOrderException):
            self.fantasy_league_service.update_fantasy_league_draft_order(
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                expected_updated_draft_order
            )

    def test_update_fantasy_league_draft_order_bad_position_order(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        self.create_draft_order_for_fantasy_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            1
        )
        self.create_draft_order_for_fantasy_league(
            fantasy_league.id,
            fantasy_fixtures.user_2_fixture.id,
            2
        )
        expected_updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=fantasy_fixtures.user_fixture.id,
                username=fantasy_fixtures.user_fixture.username,
                position=3
            ),
            FantasyLeagueDraftOrderResponse(
                user_id=fantasy_fixtures.user_2_fixture.id,
                username=fantasy_fixtures.user_2_fixture.username,
                position=1
            )
        ]

        # Act and Assert
        with self.assertRaises(DraftOrderException):
            self.fantasy_league_service.update_fantasy_league_draft_order(
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                expected_updated_draft_order
            )

    def test_update_fantasy_league_draft_order_no_existing_fantasy_league(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        self.db.create_user(user)
        expected_updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=fantasy_fixtures.user_fixture.id,
                username=fantasy_fixtures.user_fixture.username,
                position=1
            )
        ]

        # Act and Act
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.update_fantasy_league_draft_order(
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                expected_updated_draft_order
            )

    def test_update_fantasy_league_draft_order_not_owner_of_league(self):
        # Arrange
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        expected_updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=fantasy_fixtures.user_fixture.id,
                username=fantasy_fixtures.user_fixture.username,
                position=1
            )
        ]

        # Act and Act
        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.update_fantasy_league_draft_order(
                fantasy_fixtures.user_2_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                expected_updated_draft_order
            )

    def test_update_fantasy_league_draft_order_not_in_pre_draft_exception(self):
        # Arrange
        self.db.create_fantasy_league(fantasy_fixtures.fantasy_league_active_fixture)
        updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=fantasy_fixtures.user_fixture.id,
                username=fantasy_fixtures.user_fixture.username,
                position=1
            )
        ]

        # Act and Act
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            self.fantasy_league_service.update_fantasy_league_draft_order(
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.fantasy_league_active_fixture.id,
                updated_draft_order
            )

    # --------------------------------------------------
    # -------------- Start Fantasy Draft ---------------
    # --------------------------------------------------
    def test_start_fantasy_draft_successful(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(user)

        self.create_fantasy_league_membership_for_league(
            fantasy_league.id, user.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        for i in range(fantasy_league.number_of_teams - 1):  # -1 as we created one for user already
            self.create_fantasy_league_membership_for_league(
                fantasy_league.id, UserID(str(uuid.uuid4())), FantasyLeagueMembershipStatus.ACCEPTED
            )

        # Act and Assert
        try:
            self.fantasy_league_service.start_fantasy_draft(user.id, fantasy_league.id)
        except FantasyLeagueStartDraftException:
            self.fail("Start Fantasy Draft failed with an unexpected exception!")
        db_fantasy_league = self.db.get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(FantasyLeagueStatus.DRAFT, db_fantasy_league.status)
        self.assertEqual(1, db_fantasy_league.current_draft_position)

    def test_start_fantasy_draft_no_fantasy_league_found_exception(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.start_fantasy_draft(
                user.id, FantasyLeagueID("badFantasyLeagueId")
            )
        db_fantasy_league = self.db.get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(FantasyLeagueStatus.PRE_DRAFT, db_fantasy_league.status)
        self.assertEqual(None, db_fantasy_league.current_draft_position)

    def test_start_fantasy_draft_not_in_pre_draft_exception(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        active_fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        active_fantasy_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(active_fantasy_league)

        # Act and Assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            self.fantasy_league_service.start_fantasy_draft(user.id, active_fantasy_league.id)
        db_fantasy_league = self.db.get_fantasy_league_by_id(active_fantasy_league.id)
        self.assertEqual(FantasyLeagueStatus.ACTIVE, db_fantasy_league.status)
        self.assertEqual(None, db_fantasy_league.current_draft_position)

    def test_start_fantasy_draft_not_enough_members_exception(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(user)

        for i in range(fantasy_league.number_of_teams - 1):
            self.create_fantasy_league_membership_for_league(
                fantasy_league.id, UserID(str(uuid.uuid4())), FantasyLeagueMembershipStatus.ACCEPTED
            )

        # Act and Assert
        with self.assertRaises(FantasyLeagueStartDraftException) as context:
            self.fantasy_league_service.start_fantasy_draft(user.id, fantasy_league.id)
        self.assertIn("Invalid member count", str(context.exception))
        self.assertIn(
            f"Expected {fantasy_league.number_of_teams} but has "
            f"{fantasy_league.number_of_teams - 1}", str(context.exception))
        db_fantasy_league = self.db.get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(FantasyLeagueStatus.PRE_DRAFT, db_fantasy_league.status)
        self.assertEqual(None, db_fantasy_league.current_draft_position)

    def test_start_fantasy_draft_too_many__members_exception(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(user)

        for i in range(fantasy_league.number_of_teams + 1):
            self.create_fantasy_league_membership_for_league(
                fantasy_league.id, UserID(str(uuid.uuid4())), FantasyLeagueMembershipStatus.ACCEPTED
            )

        # Act and Assert
        with self.assertRaises(FantasyLeagueStartDraftException) as context:
            self.fantasy_league_service.start_fantasy_draft(user.id, fantasy_league.id)
        self.assertIn("Invalid member count", str(context.exception))
        self.assertIn(
            f"Expected {fantasy_league.number_of_teams} but has "
            f"{fantasy_league.number_of_teams + 1}", str(context.exception))
        db_fantasy_league = self.db.get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(FantasyLeagueStatus.PRE_DRAFT, db_fantasy_league.status)
        self.assertEqual(None, db_fantasy_league.current_draft_position)

    def test_start_fantasy_draft_no_available_leagues_set_exception(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = []
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(user)

        for i in range(fantasy_league.number_of_teams):
            self.create_fantasy_league_membership_for_league(
                fantasy_league.id, UserID(str(uuid.uuid4())), FantasyLeagueMembershipStatus.ACCEPTED
            )

        # Act and Assert
        with self.assertRaises(FantasyLeagueStartDraftException) as context:
            self.fantasy_league_service.start_fantasy_draft(user.id, fantasy_league.id)
        self.assertIn("Available leagues not set", str(context.exception))
        db_fantasy_league = self.db.get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(FantasyLeagueStatus.PRE_DRAFT, db_fantasy_league.status)
        self.assertEqual(None, db_fantasy_league.current_draft_position)

    def create_fantasy_league_membership_for_league(
            self,
            league_id: FantasyLeagueID,
            user_id: UserID,
            status: FantasyLeagueMembershipStatus
    ):
        fantasy_league_membership = FantasyLeagueMembership(
            league_id=league_id,
            user_id=user_id,
            status=status
        )
        self.db.create_fantasy_league_membership(fantasy_league_membership)

    def create_draft_order_for_fantasy_league(
            self,
            league_id: FantasyLeagueID,
            user_id: UserID,
            position: int
    ):
        new_draft_position = FantasyLeagueDraftOrder(
            fantasy_league_id=league_id, user_id=user_id, position=position
        )
        self.db.create_fantasy_league_draft_order(new_draft_position)
        return new_draft_position
