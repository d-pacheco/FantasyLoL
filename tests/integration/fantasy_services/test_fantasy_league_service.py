import uuid

from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures
from tests.test_util import db_util

from common.schemas.fantasy_schemas import FantasyLeagueMembershipStatus
from common.schemas.fantasy_schemas import FantasyLeagueMembership
from common.schemas.fantasy_schemas import FantasyLeagueScoringSettings
from fantasy.service.fantasy_league_service import FantasyLeagueService
from fantasy.exceptions.fantasy_league_invite_exception import FantasyLeagueInviteException
from fantasy.exceptions.forbidden_exception import ForbiddenException
from fantasy.exceptions.fantasy_league_not_found_exception import FantasyLeagueNotFoundException
from fantasy.exceptions.user_not_found_exception import UserNotFoundException


class FantasyLeagueServiceIntegrationTest(FantasyLolTestBase):
    def test_default_fantasy_league_settings_created_on_fantasy_league_creation(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture
        user = fantasy_fixtures.user_fixture
        db_util.create_user(user)

        # Act
        new_fantasy_league = fantasy_league_service.create_fantasy_league(
            user.id, fantasy_league_settings
        )
        expected_default_settings = FantasyLeagueScoringSettings(
            fantasy_league_id=new_fantasy_league.id
        )

        # Assert
        scoring_settings_from_db = db_util.get_fantasy_league_scoring_settings_by_id(
            new_fantasy_league.id
        )
        self.assertIsNotNone(scoring_settings_from_db)
        self.assertEqual(
            FantasyLeagueScoringSettings.model_validate(expected_default_settings),
            FantasyLeagueScoringSettings.model_validate(scoring_settings_from_db)
        )

    def test_get_fantasy_league_scoring_settings_successful(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        expected_scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        db_util.create_user(user)
        db_util.create_fantasy_league(fantasy_league)
        db_util.create_fantasy_league_scoring_settings(expected_scoring_settings)

        # Act
        returned_scoring_settings = fantasy_league_service.get_scoring_settings(
            user.id, fantasy_league.id
        )

        # Assert
        self.assertEqual(expected_scoring_settings, returned_scoring_settings)

    def test_get_fantasy_league_scoring_settings_non_existing_league(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        db_util.create_user(user)
        db_util.create_fantasy_league(fantasy_league)
        db_util.create_fantasy_league_scoring_settings(scoring_settings)

        # Act and Act
        with self.assertRaises(ForbiddenException):
            fantasy_league_service.get_scoring_settings("badUserId", fantasy_league.id)

    def test_get_fantasy_league_scoring_settings_not_owner_of_league(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        user = fantasy_fixtures.user_fixture
        db_util.create_user(user)

        # Act and Act
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_league_service.get_scoring_settings(user.id, "badLeagueId")

    def test_send_fantasy_league_invite_successful(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        user_2 = fantasy_fixtures.user_2_fixture
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_user(user)
        db_util.create_user(user_2)
        db_util.create_fantasy_league(fantasy_league)

        # Act
        fantasy_league_service.send_fantasy_league_invite(
            user.id, fantasy_league.id, user_2.username
        )

        # Assert
        pending_and_active_members = db_util.get_pending_and_accepted_members_for_league(
            fantasy_league.id
        )
        self.assertEqual(1, len(pending_and_active_members))
        self.assertEqual(user_2.id, pending_and_active_members[0].user_id)

    def test_send_fantasy_league_invite_not_as_owner(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        user_2 = fantasy_fixtures.user_2_fixture
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_user(user)
        db_util.create_user(user_2)
        db_util.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(ForbiddenException):
            fantasy_league_service.send_fantasy_league_invite(
                "badOwnerId", fantasy_league.id, user_2.username
            )

    def test_send_fantasy_league_invite_for_non_existing_league(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        user_2 = fantasy_fixtures.user_2_fixture
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_user(user)
        db_util.create_user(user_2)
        db_util.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_league_service.send_fantasy_league_invite(
                user.id, "badLeagueId", user_2.username
            )

    def test_send_fantasy_league_invite_to_non_existing_user(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_user(user)
        db_util.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(UserNotFoundException):
            fantasy_league_service.send_fantasy_league_invite(
                user.id, fantasy_league.id, "badUserName"
            )

    def test_send_fantasy_league_invite_exceeds_max_number_of_players(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        user_2 = fantasy_fixtures.user_2_fixture
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_user(user)
        db_util.create_user(user_2)
        db_util.create_fantasy_league(fantasy_league)
        for _ in range(fantasy_league.number_of_teams):
            new_user_id = str(uuid.uuid4())
            create_fantasy_league_membership_for_league(
                fantasy_league.id, new_user_id, FantasyLeagueMembershipStatus.PENDING
            )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            fantasy_league_service.send_fantasy_league_invite(
                user.id, fantasy_league.id, user_2.username
            )

    def test_join_fantasy_league_successful(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        user_2 = fantasy_fixtures.user_2_fixture
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.PENDING
        )

        # Act
        fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

        # Assert
        pending_and_active_members = db_util.get_pending_and_accepted_members_for_league(
            fantasy_league.id
        )
        self.assertEqual(1, len(pending_and_active_members))
        membership_from_db = pending_and_active_members[0]
        self.assertEqual(user_2.id, membership_from_db.user_id)
        self.assertEqual(FantasyLeagueMembershipStatus.ACCEPTED, membership_from_db.status)

    def test_join_fantasy_league_no_membership_for_league(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        user_2 = fantasy_fixtures.user_2_fixture

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

    def test_join_fantasy_league_revoked_membership(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        db_util.create_fantasy_league(fantasy_league)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.REVOKED
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

    def test_join_fantasy_league_declined_membership(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        db_util.create_fantasy_league(fantasy_league)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.DECLINED
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

    def test_join_fantasy_league_already_accepted_status(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        db_util.create_fantasy_league(fantasy_league)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act
        fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

        # Assert
        pending_and_active_members = db_util.get_pending_and_accepted_members_for_league(
            fantasy_league.id
        )
        self.assertEqual(1, len(pending_and_active_members))
        membership_from_db = pending_and_active_members[0]
        self.assertEqual(user_2.id, membership_from_db.user_id)
        self.assertEqual(FantasyLeagueMembershipStatus.ACCEPTED, membership_from_db.status)

    def test_join_non_existing_fantasy_league(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_2 = fantasy_fixtures.user_2_fixture

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

    def test_join_full_fantasy_league(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        user_2 = fantasy_fixtures.user_2_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        for _ in range(fantasy_league.number_of_teams):
            new_user_id = str(uuid.uuid4())
            create_fantasy_league_membership_for_league(
                fantasy_league.id, new_user_id, FantasyLeagueMembershipStatus.ACCEPTED
            )
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.PENDING
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException) as context:
            fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)
        self.assertIn("Fantasy league is full", str(context.exception))

    def test_leave_fantasy_league_successful(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        user_2 = fantasy_fixtures.user_2_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act
        fantasy_league_service.leave_fantasy_league(user_2.id, fantasy_league.id)

        # Assert
        pending_and_active_members = db_util.get_all_league_memberships(fantasy_league.id)
        self.assertEqual(1, len(pending_and_active_members))
        membership_from_db = pending_and_active_members[0]
        self.assertEqual(user_2.id, membership_from_db.user_id)
        self.assertEqual(FantasyLeagueMembershipStatus.DECLINED, membership_from_db.status)

    def test_leave_fantasy_league_when_owner_exception(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user.id, FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            fantasy_league_service.leave_fantasy_league(user.id, fantasy_league.id)

    def test_leave_fantasy_league_with_no_membership_exception(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        user_2 = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            fantasy_league_service.leave_fantasy_league(user_2.id, fantasy_league.id)

    def test_leave_fantasy_league_with_no_accepted_membership_exception(self):
        # Arrange
        fantasy_league_service = FantasyLeagueService()
        user_2 = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.PENDING
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            fantasy_league_service.leave_fantasy_league(user_2.id, fantasy_league.id)


def create_fantasy_league_membership_for_league(
        league_id: str, user_id: str, status: FantasyLeagueMembershipStatus):
    fantasy_league_membership = FantasyLeagueMembership(
        league_id=league_id,
        user_id=user_id,
        status=status
    )
    db_util.create_fantasy_league_membership(fantasy_league_membership)
