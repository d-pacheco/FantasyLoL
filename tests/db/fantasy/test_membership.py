from sqlalchemy.exc import IntegrityError

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus,
    UserID
)


class TestCrudFantasyLeagueMembership(TestBase):
    def test_create_fantasy_league_membership(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        membership = FantasyLeagueMembership(
            league_id=fantasy_league.id,
            user_id=user.id,
            status=FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and Assert
        membership_before_create = self.db.get_user_membership_for_fantasy_league(
            user.id, fantasy_league.id
        )
        self.assertIsNone(membership_before_create)
        self.db.create_fantasy_league_membership(membership)
        membership_after_create = self.db.get_user_membership_for_fantasy_league(
            user.id, fantasy_league.id
        )
        self.assertEqual(membership, membership_after_create)
        with self.assertRaises(IntegrityError) as context:
            self.db.create_fantasy_league_membership(membership)
        self.assertIn(
            'UNIQUE constraint failed: fantasy_league_memberships.league_id, '
            'fantasy_league_memberships.user_id',
            str(context.exception)
        )

    def test_get_pending_and_accepted_members_for_league(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        user_3 = fantasy_fixtures.user_3_fixture
        user_4 = fantasy_fixtures.user_4_fixture
        user_membership_accepted = FantasyLeagueMembership(
            league_id=fantasy_league.id,
            user_id=user.id,
            status=FantasyLeagueMembershipStatus.ACCEPTED
        )
        user_2_membership_pending = FantasyLeagueMembership(
            league_id=fantasy_league.id,
            user_id=user_2.id,
            status=FantasyLeagueMembershipStatus.PENDING
        )
        user_3_membership_revoked = FantasyLeagueMembership(
            league_id=fantasy_league.id,
            user_id=user_3.id,
            status=FantasyLeagueMembershipStatus.REVOKED
        )
        user_4_membership_declined = FantasyLeagueMembership(
            league_id=fantasy_league.id,
            user_id=user_4.id,
            status=FantasyLeagueMembershipStatus.DECLINED
        )
        self.db.create_fantasy_league_membership(user_membership_accepted)
        self.db.create_fantasy_league_membership(user_2_membership_pending)
        self.db.create_fantasy_league_membership(user_3_membership_revoked)
        self.db.create_fantasy_league_membership(user_4_membership_declined)

        # Act
        memberships = self.db.get_pending_and_accepted_members_for_league(fantasy_league.id)

        # Assert
        self.assertEqual(2, len(memberships))
        for membership in memberships:
            if membership.user_id == user_membership_accepted.user_id:
                self.assertEqual(membership, user_membership_accepted)
            elif membership.user_id == user_2_membership_pending.user_id:
                self.assertEqual(membership, user_2_membership_pending)
            else:
                self.fail("Membership returned with an unexpected user ID")

    def test_update_fantasy_league_membership_status(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        membership = FantasyLeagueMembership(
            league_id=fantasy_league.id,
            user_id=user.id,
            status=FantasyLeagueMembershipStatus.PENDING
        )
        new_status = FantasyLeagueMembershipStatus.ACCEPTED
        expected_updated_membership = membership.model_copy(deep=True)
        expected_updated_membership.status = new_status

        # Act and Assert
        self.assertNotEqual(membership.status, new_status)
        self.db.update_fantasy_league_membership_status(membership, new_status)
        updated_membership = self.db.get_user_membership_for_fantasy_league(
            user.id, fantasy_league.id
        )
        self.assertEqual(expected_updated_membership, updated_membership)

    def test_get_user_membership_for_fantasy_league(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        membership = FantasyLeagueMembership(
            league_id=fantasy_league.id,
            user_id=user.id,
            status=FantasyLeagueMembershipStatus.PENDING
        )
        self.db.create_fantasy_league_membership(membership)

        # Act and Assert
        self.assertEqual(
            membership,
            self.db.get_user_membership_for_fantasy_league(user.id, fantasy_league.id)
        )
        self.assertIsNone(
            self.db.get_user_membership_for_fantasy_league(UserID("123"), fantasy_league.id)
        )
        self.assertIsNone(
            self.db.get_user_membership_for_fantasy_league(user.id, FantasyLeagueID("123"))
        )

    def test_get_users_fantasy_leagues_with_membership_status(self):
        # Arrange
        fantasy_league_1 = fantasy_fixtures.fantasy_league_fixture
        fantasy_league_2 = fantasy_fixtures.fantasy_league_active_fixture
        self.db.create_fantasy_league(fantasy_league_1)
        self.db.create_fantasy_league(fantasy_league_2)
        user = fantasy_fixtures.user_fixture
        membership_1 = FantasyLeagueMembership(
            league_id=fantasy_league_1.id,
            user_id=user.id,
            status=FantasyLeagueMembershipStatus.PENDING
        )
        membership_2 = FantasyLeagueMembership(
            league_id=fantasy_league_2.id,
            user_id=user.id,
            status=FantasyLeagueMembershipStatus.ACCEPTED
        )
        self.db.create_fantasy_league_membership(membership_1)
        self.db.create_fantasy_league_membership(membership_2)

        # Act
        fantasy_leagues_pending = self.db.get_users_fantasy_leagues_with_membership_status(
            user.id, FantasyLeagueMembershipStatus.PENDING
        )
        self.assertEqual(1, len(fantasy_leagues_pending))
        self.assertEqual(fantasy_league_1, fantasy_leagues_pending[0])
        fantasy_leagues_accepted = self.db.get_users_fantasy_leagues_with_membership_status(
            user.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        self.assertEqual(1, len(fantasy_leagues_accepted))
        self.assertEqual(fantasy_league_2, fantasy_leagues_accepted[0])
        fantasy_leagues_declined = self.db.get_users_fantasy_leagues_with_membership_status(
            user.id, FantasyLeagueMembershipStatus.DECLINED
        )
        self.assertEqual(0, len(fantasy_leagues_declined))
