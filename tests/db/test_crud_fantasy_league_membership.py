from sqlalchemy.exc import IntegrityError

from tests.test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures

from src.db import crud

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus,
    UserID
)


class TestCrudFantasyLeagueMembership(FantasyLolTestBase):
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
        membership_before_create = crud.get_user_membership_for_fantasy_league(
            user.id, fantasy_league.id
        )
        self.assertIsNone(membership_before_create)
        crud.create_fantasy_league_membership(membership)
        membership_after_create = crud.get_user_membership_for_fantasy_league(
            user.id, fantasy_league.id
        )
        self.assertEqual(membership, membership_after_create)
        with self.assertRaises(IntegrityError) as context:
            crud.create_fantasy_league_membership(membership)
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
        crud.create_fantasy_league_membership(user_membership_accepted)
        crud.create_fantasy_league_membership(user_2_membership_pending)
        crud.create_fantasy_league_membership(user_3_membership_revoked)
        crud.create_fantasy_league_membership(user_4_membership_declined)

        # Act
        memberships = crud.get_pending_and_accepted_members_for_league(fantasy_league.id)

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
        crud.update_fantasy_league_membership_status(membership, new_status)
        updated_membership = crud.get_user_membership_for_fantasy_league(user.id, fantasy_league.id)
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
        crud.create_fantasy_league_membership(membership)

        # Act and Assert
        self.assertEqual(
            membership,
            crud.get_user_membership_for_fantasy_league(user.id, fantasy_league.id)
        )
        self.assertIsNone(
            crud.get_user_membership_for_fantasy_league(UserID("123"), fantasy_league.id)
        )
        self.assertIsNone(
            crud.get_user_membership_for_fantasy_league(user.id, FantasyLeagueID("123"))
        )

    def test_get_users_fantasy_leagues_with_membership_status(self):
        # Arrange
        fantasy_league_1 = fantasy_fixtures.fantasy_league_fixture
        fantasy_league_2 = fantasy_fixtures.fantasy_league_active_fixture
        crud.create_fantasy_league(fantasy_league_1)
        crud.create_fantasy_league(fantasy_league_2)
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
        crud.create_fantasy_league_membership(membership_1)
        crud.create_fantasy_league_membership(membership_2)

        # Act
        fantasy_leagues_pending = crud.get_users_fantasy_leagues_with_membership_status(
            user.id, FantasyLeagueMembershipStatus.PENDING
        )
        self.assertEqual(1, len(fantasy_leagues_pending))
        self.assertEqual(fantasy_league_1, fantasy_leagues_pending[0])
        fantasy_leagues_accepted = crud.get_users_fantasy_leagues_with_membership_status(
            user.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        self.assertEqual(1, len(fantasy_leagues_accepted))
        self.assertEqual(fantasy_league_2, fantasy_leagues_accepted[0])
        fantasy_leagues_declined = crud.get_users_fantasy_leagues_with_membership_status(
            user.id, FantasyLeagueMembershipStatus.DECLINED
        )
        self.assertEqual(0, len(fantasy_leagues_declined))
