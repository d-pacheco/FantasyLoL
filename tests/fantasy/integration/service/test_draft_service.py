import uuid
from copy import deepcopy

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures, riot_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeagueStatus,
    FantasyLeagueMembershipStatus,
    FantasyLeagueMembership,
    FantasyLeagueDraftOrder,
    UserID,
)
from src.common.schemas.riot_data_schemas import (
    ProfessionalPlayer,
    ProfessionalTeam,
    PlayerRole,
    ProPlayerID,
    ProTeamID,
)
from src.fantasy.exceptions import (
    FantasyDraftException,
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
        self._player_counter = 0

    def create_membership(self, league_id, user_id, status):
        self.db.create_fantasy_league_membership(
            FantasyLeagueMembership(league_id=league_id, user_id=user_id, status=status)
        )

    def create_draft_order(self, league_id, user_id, position):
        self.db.create_fantasy_league_draft_order(
            FantasyLeagueDraftOrder(fantasy_league_id=league_id, user_id=user_id, position=position)
        )

    def make_player(self, role, team_id=None):
        """Create and persist a player with the given role. Returns the player."""
        self._player_counter += 1
        player = ProfessionalPlayer(
            id=ProPlayerID(f"test-player-{self._player_counter}"),
            summoner_name=f"Player{self._player_counter}",
            image="http://img.png",
            role=role,
            team_id=team_id or riot_fixtures.team_1_fixture.id,
        )
        self.db.put_player(player)
        return player

    def setup_draft_league(self):
        """Set up a 4-user league in DRAFT status.
        Returns (league, [user_ids]) where user_ids[0] is the owner at position 1.
        Snake order: R1 picks 1-4 → users 0,1,2,3 | R2 picks 5-8 → users 3,2,1,0
        """
        league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        league.available_leagues = [riot_fixtures.league_1_fixture.id]
        league.number_of_teams = 4
        self.db.create_fantasy_league(league)

        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)

        user_ids = []
        owner = fantasy_fixtures.user_fixture
        self.db.create_user(owner)
        user_ids.append(owner.id)
        self.create_membership(league.id, owner.id, FantasyLeagueMembershipStatus.ACCEPTED)
        self.create_draft_order(league.id, owner.id, 1)

        for i in range(3):
            uid = UserID(str(uuid.uuid4()))
            user_ids.append(uid)
            self.create_membership(league.id, uid, FantasyLeagueMembershipStatus.ACCEPTED)
            self.create_draft_order(league.id, uid, i + 2)

        self.draft_service.start_draft(league.id, owner.id)
        return league, user_ids

    def advance_draft(self, league, user_ids, num_picks):
        """Make num_picks filler picks following snake order from current state.
        Each user gets a different role each time to avoid slot conflicts.
        """
        snake = [0, 1, 2, 3, 3, 2, 1, 0]  # repeats every 8 picks for 4 users
        all_roles = [
            PlayerRole.TOP,
            PlayerRole.JUNGLE,
            PlayerRole.MID,
            PlayerRole.BOTTOM,
            PlayerRole.SUPPORT,
        ]
        user_pick_count: dict[int, int] = {0: 0, 1: 0, 2: 0, 3: 0}

        existing = self.db.get_draft_picks_for_league(league.id)
        start = len(existing)

        # Count existing picks per user to know which role index to start at
        for pick in existing:
            for i, uid in enumerate(user_ids):
                if pick.user_id == uid:
                    user_pick_count[i] += 1
                    break

        for i in range(num_picks):
            idx = (start + i) % len(snake)
            user_idx = snake[idx]
            role = all_roles[user_pick_count[user_idx] % len(all_roles)]
            user_pick_count[user_idx] += 1
            player = self.make_player(role)
            self.draft_service.make_pick(league.id, user_ids[user_idx], player_id=player.id)

    # --------------------------------------------------
    # ------------------- start_draft ------------------
    # --------------------------------------------------
    def test_start_draft_successful(self):
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

        self.draft_service.start_draft(fantasy_league.id, user.id)

        db_league = self.db.get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(FantasyLeagueStatus.DRAFT, db_league.status)
        self.assertEqual(1, db_league.current_draft_position)
        self.assertEqual(0, db_league.current_week)

    def test_start_draft_rejects_non_owner(self):
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(fantasy_league)

        with self.assertRaises(ForbiddenException):
            self.draft_service.start_draft(fantasy_league.id, UserID(str(uuid.uuid4())))

    def test_start_draft_rejects_wrong_member_count(self):
        user = fantasy_fixtures.user_fixture
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(fantasy_league)
        self.db.create_user(user)

        for _ in range(fantasy_league.number_of_teams - 1):
            self.create_membership(
                fantasy_league.id,
                UserID(str(uuid.uuid4())),
                FantasyLeagueMembershipStatus.ACCEPTED,
            )

        with self.assertRaises(FantasyLeagueStartDraftException):
            self.draft_service.start_draft(fantasy_league.id, user.id)

    def test_start_draft_rejects_empty_available_leagues(self):
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

        with self.assertRaises(FantasyLeagueStartDraftException):
            self.draft_service.start_draft(fantasy_league.id, user.id)

    def test_start_draft_rejects_non_pre_draft_status(self):
        active_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        active_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(active_league)

        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            self.draft_service.start_draft(active_league.id, fantasy_fixtures.user_fixture.id)

    def test_start_draft_rejects_nonexistent_league(self):
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.draft_service.start_draft(FantasyLeagueID("nonexistent"), UserID("x"))

    # --------------------------------------------------
    # ------------------- make_pick --------------------
    # --------------------------------------------------
    def test_make_pick_valid_player(self):
        league, user_ids = self.setup_draft_league()
        player = self.make_player(PlayerRole.TOP)

        result = self.draft_service.make_pick(league.id, user_ids[0], player_id=player.id)

        self.assertEqual(1, result.pick_number)
        self.assertEqual(1, result.round_number)
        self.assertEqual(user_ids[0], result.user_id)
        self.assertEqual(player.id, result.player_id)

        picks = self.db.get_draft_picks_for_league(league.id)
        self.assertEqual(1, len(picks))

        teams = self.db.get_all_fantasy_teams_for_user(league.id, user_ids[0])
        self.assertEqual(player.id, teams[0].top_player_id)

        db_league = self.db.get_fantasy_league_by_id(league.id)
        self.assertEqual(2, db_league.current_draft_position)

    def test_make_pick_snake_order_reverses_in_round_2(self):
        league, user_ids = self.setup_draft_league()
        # Fill round 1 (4 picks), then verify round 2 starts with user 3
        self.advance_draft(league, user_ids, 4)

        player = self.make_player(PlayerRole.SUPPORT)
        result = self.draft_service.make_pick(league.id, user_ids[3], player_id=player.id)

        self.assertEqual(5, result.pick_number)
        self.assertEqual(2, result.round_number)
        self.assertEqual(user_ids[3], result.user_id)

    def test_make_pick_rejects_not_users_turn(self):
        league, user_ids = self.setup_draft_league()
        player = self.make_player(PlayerRole.TOP)

        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[1], player_id=player.id)

    def test_make_pick_rejects_player_already_drafted(self):
        league, user_ids = self.setup_draft_league()
        player = self.make_player(PlayerRole.TOP)

        self.draft_service.make_pick(league.id, user_ids[0], player_id=player.id)

        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[1], player_id=player.id)

    def test_make_pick_rejects_role_slot_filled(self):
        league, user_ids = self.setup_draft_league()
        # User 0 picks TOP in pick 1
        top_player = self.make_player(PlayerRole.TOP)
        self.draft_service.make_pick(league.id, user_ids[0], player_id=top_player.id)
        # Advance picks 2-7 so it's user 0's turn again (pick 8)
        self.advance_draft(league, user_ids, 6)

        # User 0 tries another TOP
        another_top = self.make_player(PlayerRole.TOP)
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[0], player_id=another_top.id)

    def test_make_pick_rejects_team_slot_filled(self):
        league, user_ids = self.setup_draft_league()
        # User 0 picks a team in pick 1
        self.draft_service.make_pick(
            league.id, user_ids[0], team_id=riot_fixtures.team_1_fixture.id
        )
        # Advance picks 2-7 so it's user 0's turn again
        self.advance_draft(league, user_ids, 6)

        # User 0 tries another team
        self.db.put_team(riot_fixtures.team_2_fixture)
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(
                league.id, user_ids[0], team_id=riot_fixtures.team_2_fixture.id
            )

    def test_make_pick_rejects_player_with_role_none(self):
        league, user_ids = self.setup_draft_league()
        none_player = self.make_player(PlayerRole.NONE)

        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[0], player_id=none_player.id)

    def test_make_pick_rejects_player_not_from_available_leagues(self):
        league, user_ids = self.setup_draft_league()
        # Player on a team in a different league
        other_league = riot_fixtures.league_2_fixture
        self.db.put_league(other_league)
        other_team = ProfessionalTeam(
            id=ProTeamID("other-team"),
            slug="other",
            name="Other",
            code="OT",
            image="http://img.png",
            status="active",
            home_league_name=other_league.name,
        )
        self.db.put_team(other_team)
        other_player = self.make_player(PlayerRole.TOP, team_id=other_team.id)

        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[0], player_id=other_player.id)

    def test_make_pick_rejects_neither_player_nor_team(self):
        league, user_ids = self.setup_draft_league()

        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[0])

    def test_make_pick_rejects_both_player_and_team(self):
        league, user_ids = self.setup_draft_league()
        player = self.make_player(PlayerRole.TOP)

        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(
                league.id,
                user_ids[0],
                player_id=player.id,
                team_id=riot_fixtures.team_1_fixture.id,
            )

    def test_make_pick_valid_team(self):
        league, user_ids = self.setup_draft_league()

        result = self.draft_service.make_pick(
            league.id, user_ids[0], team_id=riot_fixtures.team_1_fixture.id
        )

        self.assertEqual(1, result.pick_number)
        self.assertEqual(riot_fixtures.team_1_fixture.id, result.team_id)
        self.assertIsNone(result.player_id)

        teams = self.db.get_all_fantasy_teams_for_user(league.id, user_ids[0])
        self.assertEqual(riot_fixtures.team_1_fixture.id, teams[0].team_id)
