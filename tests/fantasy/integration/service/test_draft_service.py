import uuid
from copy import deepcopy

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeagueStatus,
    FantasyLeagueMembershipStatus,
    FantasyLeagueMembership,
    UserID,
)
from src.fantasy.exceptions import (
    FantasyLeagueNotFoundException,
    FantasyLeagueStartDraftException,
    FantasyLeagueInvalidRequiredStateException,
    ForbiddenException,
)
from src.fantasy.service import DraftService


class DraftServiceIntegrationTest(TestBase):
    def setUp(self):
        super().setUp()
        self.draft_service = DraftService(self.db)

    def create_membership(self, league_id, user_id, status):
        self.db.create_fantasy_league_membership(
            FantasyLeagueMembership(league_id=league_id, user_id=user_id, status=status)
        )

    # --------------------------------------------------
    # ------------------- start_draft ------------------
    # --------------------------------------------------
    def test_start_draft_successful(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(user)

        self.create_membership(fantasy_league.id, user.id, FantasyLeagueMembershipStatus.ACCEPTED)
        for _ in range(fantasy_league.number_of_teams - 1):
            self.create_membership(
                fantasy_league.id,
                UserID(str(uuid.uuid4())),
                FantasyLeagueMembershipStatus.ACCEPTED,
            )

        # Act
        self.draft_service.start_draft(fantasy_league.id, user.id)

        # Assert
        db_league = self.db.get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(FantasyLeagueStatus.DRAFT, db_league.status)
        self.assertEqual(1, db_league.current_draft_position)
        self.assertEqual(0, db_league.current_week)

    def test_start_draft_rejects_non_owner(self):
        # Arrange
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(fantasy_league)

        non_owner_id = UserID(str(uuid.uuid4()))

        # Act & Assert
        with self.assertRaises(ForbiddenException):
            self.draft_service.start_draft(fantasy_league.id, non_owner_id)

    def test_start_draft_rejects_wrong_member_count(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(user)

        # Only add half the required members
        for _ in range(fantasy_league.number_of_teams - 1):
            self.create_membership(
                fantasy_league.id,
                UserID(str(uuid.uuid4())),
                FantasyLeagueMembershipStatus.ACCEPTED,
            )

        # Act & Assert
        with self.assertRaises(FantasyLeagueStartDraftException) as ctx:
            self.draft_service.start_draft(fantasy_league.id, user.id)
        self.assertIn("Invalid member count", str(ctx.exception))

    def test_start_draft_rejects_empty_available_leagues(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = []
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(user)

        for _ in range(fantasy_league.number_of_teams):
            self.create_membership(
                fantasy_league.id,
                UserID(str(uuid.uuid4())),
                FantasyLeagueMembershipStatus.ACCEPTED,
            )

        # Act & Assert
        with self.assertRaises(FantasyLeagueStartDraftException) as ctx:
            self.draft_service.start_draft(fantasy_league.id, user.id)
        self.assertIn("Available leagues not set", str(ctx.exception))

    def test_start_draft_rejects_non_pre_draft_status(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        active_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        active_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(active_league)

        # Act & Assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            self.draft_service.start_draft(active_league.id, user.id)

    def test_start_draft_rejects_nonexistent_league(self):
        # Act & Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.draft_service.start_draft(FantasyLeagueID("nonexistent"), UserID("some-user"))
