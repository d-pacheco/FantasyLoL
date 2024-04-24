import uuid

from ...test_base import FantasyLolTestBase
from ...test_util import fantasy_fixtures
from ...test_util import db_util

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueMembershipStatus,
    FantasyLeagueMembership,
    FantasyLeagueScoringSettings,
    FantasyLeagueDraftOrder,
    FantasyLeagueDraftOrderResponse
)
from src.fantasy.service.fantasy_league_service import FantasyLeagueService
from src.fantasy.exceptions.fantasy_league_invite_exception import FantasyLeagueInviteException
from src.fantasy.exceptions.forbidden_exception import ForbiddenException
from src.fantasy.exceptions.fantasy_league_not_found_exception import FantasyLeagueNotFoundException
from src.fantasy.exceptions.user_not_found_exception import UserNotFoundException
from src.fantasy.exceptions.draft_order_exception import DraftOrderException


fantasy_league_service = FantasyLeagueService()


class FantasyLeagueServiceIntegrationTest(FantasyLolTestBase):
    def test_draft_order_entry_created_on_fantasy_league_creation(self):
        # Arrange
        fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture
        user = fantasy_fixtures.user_fixture
        db_util.create_user(user)

        # Act
        new_fantasy_league = fantasy_league_service.create_fantasy_league(
            user.id, fantasy_league_settings
        )
        expected_draft_order = FantasyLeagueDraftOrder(
            fantasy_league_id=new_fantasy_league.id, user_id=user.id, position=1
        )

        # Assert
        draft_order_from_db = db_util.get_fantasy_league_draft_order(new_fantasy_league.id)
        self.assertEqual(1, len(draft_order_from_db))
        self.assertEqual(
            FantasyLeagueDraftOrder.model_validate(expected_draft_order),
            FantasyLeagueDraftOrder.model_validate(draft_order_from_db[0])
        )

    def test_default_fantasy_league_settings_created_on_fantasy_league_creation(self):
        # Arrange
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

    def test_get_fantasy_league_scoring_settings_settings_not_owner_of_league(self):
        # Arrange
        scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        db_util.create_user(user)
        db_util.create_fantasy_league(fantasy_league)
        db_util.create_fantasy_league_scoring_settings(scoring_settings)

        # Act and Act
        with self.assertRaises(ForbiddenException):
            fantasy_league_service.get_scoring_settings("badUserId", fantasy_league.id)

    def test_get_fantasy_league_scoring_non_existing_league(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        db_util.create_user(user)

        # Act and Act
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_league_service.get_scoring_settings(user.id, "badLeagueId")

    def test_send_fantasy_league_invite_successful(self):
        # Arrange
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
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.PENDING
        )
        create_draft_order_for_fantasy_league(fantasy_league.id, user_1.id, 1)
        expected_user_1_draft_order = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
        )
        expected_user_2_draft_order = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
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

        draft_order_from_db = db_util.get_fantasy_league_draft_order(fantasy_league.id)
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
        db_util.create_fantasy_league(fantasy_league)
        user_2 = fantasy_fixtures.user_2_fixture

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

    def test_join_fantasy_league_revoked_membership(self):
        # Arrange
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
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_2 = fantasy_fixtures.user_2_fixture

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_league_service.join_fantasy_league(user_2.id, fantasy_league.id)

    def test_join_full_fantasy_league(self):
        # Arrange
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
        user_2 = fantasy_fixtures.user_2_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        create_draft_order_for_fantasy_league(fantasy_league.id, user_2.id, 2)

        # Act
        fantasy_league_service.leave_fantasy_league(user_2.id, fantasy_league.id)

        # Assert
        pending_and_active_members = db_util.get_all_league_memberships(fantasy_league.id)
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
        db_util.create_fantasy_league(fantasy_league)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.ACCEPTED
        )
        user_1_draft_order = create_draft_order_for_fantasy_league(fantasy_league.id, user_1.id, 1)
        create_draft_order_for_fantasy_league(fantasy_league.id, user_2.id, 2)
        user_3_draft_order = create_draft_order_for_fantasy_league(fantasy_league.id, user_3.id, 3)

        # Act
        fantasy_league_service.leave_fantasy_league(user_2.id, fantasy_league.id)

        # Assert
        draft_order_from_db = db_util.get_fantasy_league_draft_order(fantasy_league.id)
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
        db_util.create_fantasy_league(fantasy_league)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user.id, FantasyLeagueMembershipStatus.ACCEPTED
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            fantasy_league_service.leave_fantasy_league(user.id, fantasy_league.id)

    def test_leave_fantasy_league_with_no_membership_exception(self):
        # Arrange
        user_2 = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            fantasy_league_service.leave_fantasy_league(user_2.id, fantasy_league.id)

    def test_leave_fantasy_league_with_no_accepted_membership_exception(self):
        # Arrange
        user_2 = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        create_fantasy_league_membership_for_league(
            fantasy_league.id, user_2.id, FantasyLeagueMembershipStatus.PENDING
        )

        # Act and Assert
        with self.assertRaises(FantasyLeagueInviteException):
            fantasy_league_service.leave_fantasy_league(user_2.id, fantasy_league.id)

    def test_get_fantasy_league_draft_order_successful(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        db_util.create_user(user_1)
        user_1_draft_order = create_draft_order_for_fantasy_league(fantasy_league.id, user_1.id, 1)
        user_1_draft_order_response = FantasyLeagueDraftOrderResponse(
            user_id=user_1.id, username=user_1.username, position=user_1_draft_order.position
        )

        # Act
        current_draft_order = fantasy_league_service.get_fantasy_league_draft_order(
            user_1.id, fantasy_league.id
        )

        # Assert
        self.assertIsInstance(current_draft_order, list)
        self.assertEqual(1, len(current_draft_order))
        self.assertEqual(user_1_draft_order_response, current_draft_order[0])

    def test_get_fantasy_league_draft_order_non_existing_league(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        db_util.create_user(user_1)

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_league_service.get_fantasy_league_draft_order(user_1.id, "badLeagueId")

    def test_get_fantasy_league_draft_order_not_league_owner(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        user_1 = fantasy_fixtures.user_fixture
        db_util.create_user(user_1)

        # Act and Assert
        with self.assertRaises(ForbiddenException):
            fantasy_league_service.get_fantasy_league_draft_order("notOwner", fantasy_league.id)

    def test_update_fantasy_league_draft_order_successful(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        create_draft_order_for_fantasy_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            1
        )
        create_draft_order_for_fantasy_league(
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
        fantasy_league_service.update_fantasy_league_draft_order(
            fantasy_fixtures.user_fixture.id,
            fantasy_fixtures.fantasy_league_fixture.id,
            expected_updated_draft_order
        )

        # Assert
        db_draft_order = db_util.get_fantasy_league_draft_order(fantasy_league.id)
        self.assertEqual(2, len(db_draft_order))
        for expected_updated_position in expected_updated_draft_order:
            for db_position in db_draft_order:
                if expected_updated_position.user_id == db_position.user_id:
                    self.assertEqual(expected_updated_position.position, db_position.position)

    def test_update_fantasy_league_draft_order_missing_members(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        create_draft_order_for_fantasy_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            1
        )
        create_draft_order_for_fantasy_league(
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
            fantasy_league_service.update_fantasy_league_draft_order(
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                expected_updated_draft_order
            )

    def test_update_fantasy_league_draft_order_bad_user_id(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        create_draft_order_for_fantasy_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            1
        )
        create_draft_order_for_fantasy_league(
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
            fantasy_league_service.update_fantasy_league_draft_order(
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                expected_updated_draft_order
            )

    def test_update_fantasy_league_draft_order_bad_position_order(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        db_util.create_fantasy_league(fantasy_league)
        create_draft_order_for_fantasy_league(
            fantasy_league.id,
            fantasy_fixtures.user_fixture.id,
            1
        )
        create_draft_order_for_fantasy_league(
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
            fantasy_league_service.update_fantasy_league_draft_order(
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                expected_updated_draft_order
            )

    def test_update_fantasy_league_draft_order_no_existing_fantasy_league(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        db_util.create_user(user)
        expected_updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=fantasy_fixtures.user_fixture.id,
                username=fantasy_fixtures.user_fixture.username,
                position=1
            )
        ]

        # Act and Act
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_league_service.update_fantasy_league_draft_order(
                fantasy_fixtures.user_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                expected_updated_draft_order
            )

    def test_update_fantasy_league_draft_order_not_owner_of_league(self):
        # Arrange
        db_util.create_fantasy_league(fantasy_fixtures.fantasy_league_fixture)
        expected_updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=fantasy_fixtures.user_fixture.id,
                username=fantasy_fixtures.user_fixture.username,
                position=1
            )
        ]

        # Act and Act
        with self.assertRaises(ForbiddenException):
            fantasy_league_service.update_fantasy_league_draft_order(
                fantasy_fixtures.user_2_fixture.id,
                fantasy_fixtures.fantasy_league_fixture.id,
                expected_updated_draft_order
            )


def create_fantasy_league_membership_for_league(
        league_id: str, user_id: str, status: FantasyLeagueMembershipStatus):
    fantasy_league_membership = FantasyLeagueMembership(
        league_id=league_id,
        user_id=user_id,
        status=status
    )
    db_util.create_fantasy_league_membership(fantasy_league_membership)


def create_draft_order_for_fantasy_league(
        league_id: str, user_id: str, position: int):
    new_draft_position = FantasyLeagueDraftOrder(
        fantasy_league_id=league_id, user_id=user_id, position=position
    )
    db_util.create_fantasy_league_draft_order(new_draft_position)
    return new_draft_position
