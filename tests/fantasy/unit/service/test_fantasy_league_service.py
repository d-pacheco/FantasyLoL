from unittest.mock import patch, MagicMock
import uuid
import copy

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueID,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus,
    FantasyLeagueMemberResponse,
    FantasyLeagueSettings,
    FantasyLeagueStatus,
    UserID,
)
from src.fantasy.exceptions import (
    FantasyLeagueNotFoundException,
    ForbiddenException,
    FantasyLeagueInviteException,
)
from src.fantasy.service import FantasyLeagueService

FANTASY_LEAGUE_SERV_PATH = "src.fantasy.service.fantasy_league_service.FantasyLeagueService"


class TestFantasyLeagueService(TestBase):
    def setUp(self):
        self.mock_db_service = MagicMock()
        self.fantasy_league_service = FantasyLeagueService(self.mock_db_service)

    def tearDown(self):
        self.mock_db_service.reset_mock()

    @patch(f"{FANTASY_LEAGUE_SERV_PATH}.generate_new_valid_id")
    def test_create_fantasy_league(self, mock_generate_new_valid_id: MagicMock):
        # Arrange
        fantasy_league_id = FantasyLeagueID(str(uuid.uuid4()))
        owner_id = UserID(str(uuid.uuid4()))
        fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture
        expected_fantasy_league = FantasyLeague(
            id=fantasy_league_id,
            owner_id=owner_id,
            status=FantasyLeagueStatus.PRE_DRAFT,
            name=fantasy_league_settings.name,
        )
        self.mock_db_service.get_fantasy_league_by_id.return_value = expected_fantasy_league
        mock_generate_new_valid_id.return_value = fantasy_league_id

        # Act
        fantasy_league = self.fantasy_league_service.create_fantasy_league(
            owner_id, fantasy_league_settings
        )

        # Assert
        self.assertEqual(expected_fantasy_league, fantasy_league)
        mock_generate_new_valid_id.assert_called_once()
        self.mock_db_service.create_fantasy_league.assert_called_once_with(expected_fantasy_league)

    @patch("uuid.uuid4", side_effect=["id1", "id2"])
    def test_generate_new_valid_id(self, mock_uuid4: MagicMock):
        # Arrange
        mock_get_fantasy_league_by_id = MagicMock(side_effect=[MagicMock(), None])
        self.mock_db_service.get_fantasy_league_by_id = mock_get_fantasy_league_by_id

        # Act
        generated_id = self.fantasy_league_service.generate_new_valid_id()

        # Assert
        self.assertEqual(generated_id, "id2")
        mock_uuid4.assert_called()
        self.assertEqual(mock_uuid4.call_count, 2)
        mock_get_fantasy_league_by_id.assert_any_call("id1")
        mock_get_fantasy_league_by_id.assert_any_call("id2")
        mock_get_fantasy_league_by_id.assert_called_with("id2")

    def test_get_fantasy_league_settings_successful(self):
        # Arrange
        expected_fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        member = fantasy_fixtures.user_2_fixture  # non-owner accepted member
        accepted_membership = FantasyLeagueMembership(
            league_id=fantasy_league.id,
            user_id=member.id,
            status=FantasyLeagueMembershipStatus.ACCEPTED,
        )
        self.mock_db_service.get_fantasy_league_by_id.return_value = fantasy_league
        self.mock_db_service.get_user_membership_for_fantasy_league.return_value = (
            accepted_membership
        )

        # Act
        fantasy_league_settings = self.fantasy_league_service.get_fantasy_league_settings(
            member.id, fantasy_league.id
        )

        # Assert
        self.assertEqual(expected_fantasy_league_settings, fantasy_league_settings)

    def test_get_fantasy_league_settings_no_league_found_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = None

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.get_fantasy_league_settings(
                fantasy_league.owner_id, fantasy_league.id
            )

    def test_get_fantasy_league_settings_non_member_raises_forbidden(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        non_member_id = UserID(str(uuid.uuid4()))
        self.mock_db_service.get_fantasy_league_by_id.return_value = fantasy_league
        self.mock_db_service.get_user_membership_for_fantasy_league.return_value = None

        # Act and Assert
        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.get_fantasy_league_settings(
                non_member_id, fantasy_league.id
            )

    def test_update_fantasy_league_settings_successful(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        owner_id = fantasy_league.owner_id
        league_id = fantasy_league.id

        expected_updated_league_settings = FantasyLeagueSettings(
            name="Update fantasy league", number_of_teams=10
        )
        expected_updated_league = copy.deepcopy(fantasy_league)
        expected_updated_league.name = expected_updated_league_settings.name
        expected_updated_league.number_of_teams = expected_updated_league_settings.number_of_teams

        self.mock_db_service.get_fantasy_league_by_id.return_value = fantasy_league
        self.mock_db_service.update_fantasy_league_settings.return_value = expected_updated_league

        # Act
        updated_settings = self.fantasy_league_service.update_fantasy_league_settings(
            owner_id, league_id, expected_updated_league_settings
        )

        # Assert
        self.assertEqual(expected_updated_league_settings, updated_settings)
        self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(league_id)
        self.mock_db_service.update_fantasy_league_settings.assert_called_once_with(
            league_id, expected_updated_league_settings
        )

    def test_update_fantasy_league_settings_league_not_found_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        owner_id = fantasy_league.owner_id
        league_id = fantasy_league.id

        updated_league_settings = FantasyLeagueSettings(
            name="Update fantasy league", number_of_teams=10
        )
        self.mock_db_service.get_fantasy_league_by_id.return_value = None

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.update_fantasy_league_settings(
                owner_id, league_id, updated_league_settings
            )
        self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(league_id)
        self.mock_db_service.update_fantasy_league_settings.assert_not_called()

    def test_update_fantasy_league_settings_forbidden_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        owner_id = UserID(str(uuid.uuid4()))
        league_id = fantasy_league.id

        updated_league_settings = FantasyLeagueSettings(
            name="Update fantasy league", number_of_teams=10
        )

        self.mock_db_service.get_fantasy_league_by_id.return_value = fantasy_league

        # Act and Assert
        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.update_fantasy_league_settings(
                owner_id, league_id, updated_league_settings
            )
        self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(league_id)
        self.mock_db_service.update_fantasy_league_settings.assert_not_called()

    # --- get_scoring_settings ---

    def test_get_scoring_settings_accepted_member_successful(self):
        # Arrange
        league = fantasy_fixtures.fantasy_league_fixture
        member = fantasy_fixtures.user_2_fixture
        expected_scoring = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = league
        self.mock_db_service.get_user_membership_for_fantasy_league.return_value = (
            FantasyLeagueMembership(
                league_id=league.id,
                user_id=member.id,
                status=FantasyLeagueMembershipStatus.ACCEPTED,
            )
        )
        self.mock_db_service.get_fantasy_league_scoring_settings_by_id.return_value = (
            expected_scoring
        )

        result = self.fantasy_league_service.get_scoring_settings(member.id, league.id)

        self.assertEqual(expected_scoring, result)

    def test_get_scoring_settings_non_member_raises_forbidden(self):
        # Arrange
        league = fantasy_fixtures.fantasy_league_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = league
        self.mock_db_service.get_user_membership_for_fantasy_league.return_value = None

        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.get_scoring_settings(UserID(str(uuid.uuid4())), league.id)

    # --- get_fantasy_league_by_id ---

    def test_get_fantasy_league_by_id_accepted_member_successful(self):
        # Arrange
        league = fantasy_fixtures.fantasy_league_fixture
        member = fantasy_fixtures.user_2_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = league
        self.mock_db_service.get_user_membership_for_fantasy_league.return_value = (
            FantasyLeagueMembership(
                league_id=league.id,
                user_id=member.id,
                status=FantasyLeagueMembershipStatus.ACCEPTED,
            )
        )

        result = self.fantasy_league_service.get_fantasy_league_by_id(member.id, league.id)

        self.assertEqual(league, result)

    def test_get_fantasy_league_by_id_league_not_found_raises_exception(self):
        self.mock_db_service.get_fantasy_league_by_id.return_value = None

        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_service.get_fantasy_league_by_id(
                UserID(str(uuid.uuid4())), FantasyLeagueID(str(uuid.uuid4()))
            )

    def test_get_fantasy_league_by_id_non_member_raises_forbidden(self):
        league = fantasy_fixtures.fantasy_league_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = league
        self.mock_db_service.get_user_membership_for_fantasy_league.return_value = None

        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.get_fantasy_league_by_id(
                UserID(str(uuid.uuid4())), league.id
            )

    # --- get_league_members ---

    def test_get_league_members_returns_members_with_usernames(self):
        # Arrange
        league = fantasy_fixtures.fantasy_league_fixture
        user1 = fantasy_fixtures.user_fixture
        user2 = fantasy_fixtures.user_2_fixture
        memberships = [
            FantasyLeagueMembership(
                league_id=league.id,
                user_id=user1.id,
                status=FantasyLeagueMembershipStatus.ACCEPTED,
            ),
            FantasyLeagueMembership(
                league_id=league.id,
                user_id=user2.id,
                status=FantasyLeagueMembershipStatus.PENDING,
            ),
        ]
        self.mock_db_service.get_fantasy_league_by_id.return_value = league
        self.mock_db_service.get_user_membership_for_fantasy_league.return_value = memberships[0]
        self.mock_db_service.get_pending_and_accepted_members_for_league.return_value = memberships
        self.mock_db_service.get_user_by_id.side_effect = [user1, user2]

        result = self.fantasy_league_service.get_league_members(user1.id, league.id)

        self.assertEqual(2, len(result))
        self.assertEqual(
            FantasyLeagueMemberResponse(
                user_id=user1.id,
                username=user1.username,
                status=FantasyLeagueMembershipStatus.ACCEPTED,
            ),
            result[0],
        )
        self.assertEqual(
            FantasyLeagueMemberResponse(
                user_id=user2.id,
                username=user2.username,
                status=FantasyLeagueMembershipStatus.PENDING,
            ),
            result[1],
        )

    def test_get_league_members_non_member_raises_forbidden(self):
        league = fantasy_fixtures.fantasy_league_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = league
        self.mock_db_service.get_user_membership_for_fantasy_league.return_value = None

        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.get_league_members(UserID(str(uuid.uuid4())), league.id)

    # --- get_fantasy_league_draft_order ---

    def test_get_fantasy_league_draft_order_accepted_member_successful(self):
        # Arrange
        league = fantasy_fixtures.fantasy_league_fixture
        member = fantasy_fixtures.user_2_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = league
        self.mock_db_service.get_user_membership_for_fantasy_league.return_value = (
            FantasyLeagueMembership(
                league_id=league.id,
                user_id=member.id,
                status=FantasyLeagueMembershipStatus.ACCEPTED,
            )
        )
        self.mock_db_service.get_fantasy_league_draft_order.return_value = []

        result = self.fantasy_league_service.get_fantasy_league_draft_order(member.id, league.id)

        self.assertEqual([], result)

    def test_get_fantasy_league_draft_order_non_member_raises_forbidden(self):
        league = fantasy_fixtures.fantasy_league_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = league
        self.mock_db_service.get_user_membership_for_fantasy_league.return_value = None

        with self.assertRaises(ForbiddenException):
            self.fantasy_league_service.get_fantasy_league_draft_order(
                UserID(str(uuid.uuid4())), league.id
            )

    # --- send_fantasy_league_invite ---

    def _setup_invite(self, membership_status=None):
        """Helper: sets up league, owner, and target user for invite tests."""
        league = fantasy_fixtures.fantasy_league_fixture
        owner = fantasy_fixtures.user_fixture
        target = fantasy_fixtures.user_2_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = league
        self.mock_db_service.get_pending_and_accepted_members_for_league.return_value = []
        self.mock_db_service.get_user_by_username.return_value = target
        if membership_status is None:
            self.mock_db_service.get_user_membership_for_fantasy_league.return_value = None
        else:
            self.mock_db_service.get_user_membership_for_fantasy_league.return_value = (
                FantasyLeagueMembership(
                    league_id=league.id, user_id=target.id, status=membership_status
                )
            )
        return league, owner, target

    def test_send_invite_no_existing_membership_creates_pending(self):
        league, owner, target = self._setup_invite(membership_status=None)

        self.fantasy_league_service.send_fantasy_league_invite(owner.id, league.id, target.username)

        self.mock_db_service.create_fantasy_league_membership.assert_called_once()

    def test_send_invite_declined_member_updates_to_pending(self):
        league, owner, target = self._setup_invite(FantasyLeagueMembershipStatus.DECLINED)

        self.fantasy_league_service.send_fantasy_league_invite(owner.id, league.id, target.username)

        self.mock_db_service.update_fantasy_league_membership_status.assert_called_once()
        self.mock_db_service.create_fantasy_league_membership.assert_not_called()

    def test_send_invite_revoked_member_updates_to_pending(self):
        league, owner, target = self._setup_invite(FantasyLeagueMembershipStatus.REVOKED)

        self.fantasy_league_service.send_fantasy_league_invite(owner.id, league.id, target.username)

        self.mock_db_service.update_fantasy_league_membership_status.assert_called_once()
        self.mock_db_service.create_fantasy_league_membership.assert_not_called()

    def test_send_invite_pending_member_raises_invite_exception(self):
        league, owner, target = self._setup_invite(FantasyLeagueMembershipStatus.PENDING)

        with self.assertRaises(FantasyLeagueInviteException):
            self.fantasy_league_service.send_fantasy_league_invite(
                owner.id, league.id, target.username
            )

    def test_send_invite_accepted_member_raises_invite_exception(self):
        league, owner, target = self._setup_invite(FantasyLeagueMembershipStatus.ACCEPTED)

        with self.assertRaises(FantasyLeagueInviteException):
            self.fantasy_league_service.send_fantasy_league_invite(
                owner.id, league.id, target.username
            )
