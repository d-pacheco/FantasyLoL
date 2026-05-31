import uuid
from copy import deepcopy

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures, riot_fixtures

from src.common.schemas.fantasy_schemas import (
    DraftState,  # noqa: F401
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
            pick_num_for_user = user_pick_count[user_idx]
            user_pick_count[user_idx] += 1

            if pick_num_for_user < 5:
                # Player pick
                role = all_roles[pick_num_for_user]
                player = self.make_player(role)
                self.draft_service.make_pick(league.id, user_ids[user_idx], player_id=player.id)
            else:
                # Team pick (6th pick for this user)
                team = ProfessionalTeam(
                    id=ProTeamID(f"filler-team-{user_idx}-{self._player_counter}"),
                    slug=f"filler-{user_idx}",
                    name="Filler Team",
                    code=f"F{user_idx}",
                    image="http://img.png",
                    status="active",
                    home_league_name=riot_fixtures.league_1_fixture.name,
                )
                self.db.put_team(team)
                self.draft_service.make_pick(league.id, user_ids[user_idx], team_id=team.id)

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

        # Act & Assert
        with self.assertRaises(ForbiddenException):
            self.draft_service.start_draft(fantasy_league.id, UserID(str(uuid.uuid4())))

    def test_start_draft_rejects_wrong_member_count(self):
        # Arrange
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

        # Act & Assert
        with self.assertRaises(FantasyLeagueStartDraftException):
            self.draft_service.start_draft(fantasy_league.id, user.id)

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
        with self.assertRaises(FantasyLeagueStartDraftException):
            self.draft_service.start_draft(fantasy_league.id, user.id)

    def test_start_draft_rejects_non_pre_draft_status(self):
        # Arrange
        active_league = deepcopy(fantasy_fixtures.fantasy_league_active_fixture)
        active_league.available_leagues = ["someRiotLeagueId"]
        self.db.create_fantasy_league(active_league)

        # Act & Assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            self.draft_service.start_draft(active_league.id, fantasy_fixtures.user_fixture.id)

    def test_start_draft_rejects_nonexistent_league(self):
        # Act & Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.draft_service.start_draft(FantasyLeagueID("nonexistent"), UserID("x"))

    # --------------------------------------------------
    # ------------------- make_pick --------------------
    # --------------------------------------------------
    def test_make_pick_valid_player(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        player = self.make_player(PlayerRole.TOP)

        # Act
        result = self.draft_service.make_pick(league.id, user_ids[0], player_id=player.id)

        # Assert
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
        # Arrange
        league, user_ids = self.setup_draft_league()
        self.advance_draft(league, user_ids, 4)
        player = self.make_player(PlayerRole.SUPPORT)

        # Act — round 2 starts with user 3 (snake reversal)
        result = self.draft_service.make_pick(league.id, user_ids[3], player_id=player.id)

        # Assert
        self.assertEqual(5, result.pick_number)
        self.assertEqual(2, result.round_number)
        self.assertEqual(user_ids[3], result.user_id)

    def test_make_pick_rejects_not_users_turn(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        player = self.make_player(PlayerRole.TOP)

        # Act & Assert — user 1 tries to pick but it's user 0's turn
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[1], player_id=player.id)

    def test_make_pick_rejects_player_already_drafted(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        player = self.make_player(PlayerRole.TOP)
        self.draft_service.make_pick(league.id, user_ids[0], player_id=player.id)

        # Act & Assert — user 1 tries to draft the same player
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[1], player_id=player.id)

    def test_make_pick_rejects_role_slot_filled(self):
        # Arrange — user 0 picks TOP, then we advance to user 0's next turn
        league, user_ids = self.setup_draft_league()
        top_player = self.make_player(PlayerRole.TOP)
        self.draft_service.make_pick(league.id, user_ids[0], player_id=top_player.id)
        self.advance_draft(league, user_ids, 6)
        another_top = self.make_player(PlayerRole.TOP)

        # Act & Assert — user 0 tries another TOP (slot already filled)
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[0], player_id=another_top.id)

    def test_make_pick_rejects_team_slot_filled(self):
        # Arrange — user 0 picks a team, then we advance to user 0's next turn
        league, user_ids = self.setup_draft_league()
        self.draft_service.make_pick(
            league.id, user_ids[0], team_id=riot_fixtures.team_1_fixture.id
        )
        self.advance_draft(league, user_ids, 6)
        self.db.put_team(riot_fixtures.team_2_fixture)

        # Act & Assert — user 0 tries another team (slot already filled)
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(
                league.id, user_ids[0], team_id=riot_fixtures.team_2_fixture.id
            )

    def test_make_pick_rejects_player_with_role_none(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        none_player = self.make_player(PlayerRole.NONE)

        # Act & Assert
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[0], player_id=none_player.id)

    def test_make_pick_rejects_player_not_from_available_leagues(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
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

        # Act & Assert
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[0], player_id=other_player.id)

    def test_make_pick_rejects_neither_player_nor_team(self):
        # Arrange
        league, user_ids = self.setup_draft_league()

        # Act & Assert
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[0])

    def test_make_pick_rejects_both_player_and_team(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        player = self.make_player(PlayerRole.TOP)

        # Act & Assert
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(
                league.id,
                user_ids[0],
                player_id=player.id,
                team_id=riot_fixtures.team_1_fixture.id,
            )

    def test_make_pick_valid_team(self):
        # Arrange
        league, user_ids = self.setup_draft_league()

        # Act
        result = self.draft_service.make_pick(
            league.id, user_ids[0], team_id=riot_fixtures.team_1_fixture.id
        )

        # Assert
        self.assertEqual(1, result.pick_number)
        self.assertEqual(riot_fixtures.team_1_fixture.id, result.team_id)
        self.assertIsNone(result.player_id)

        teams = self.db.get_all_fantasy_teams_for_user(league.id, user_ids[0])
        self.assertEqual(riot_fixtures.team_1_fixture.id, teams[0].team_id)

    # --------------------------------------------------
    # -------------- draft completion ------------------
    # --------------------------------------------------
    def test_draft_completes_after_final_pick(self):
        # Arrange — 4 users × 6 picks = 24 total picks
        league, user_ids = self.setup_draft_league()
        self.advance_draft(league, user_ids, 23)

        # Act — make the 24th (final) pick (user 0's 6th pick = team pick)
        final_team = ProfessionalTeam(
            id=ProTeamID("final-team"),
            slug="final",
            name="Final Team",
            code="FT",
            image="http://img.png",
            status="active",
            home_league_name=riot_fixtures.league_1_fixture.name,
        )
        self.db.put_team(final_team)
        self.draft_service.make_pick(league.id, user_ids[0], team_id=final_team.id)

        # Assert
        db_league = self.db.get_fantasy_league_by_id(league.id)
        self.assertEqual(FantasyLeagueStatus.ACTIVE, db_league.status)
        self.assertEqual(1, db_league.current_week)

    # --------------------------------------------------
    # --------------- get_draft_state ------------------
    # --------------------------------------------------
    def test_get_draft_state_mid_draft(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        player = self.make_player(PlayerRole.TOP)
        self.draft_service.make_pick(league.id, user_ids[0], player_id=player.id)

        # Act
        state = self.draft_service.get_draft_state(league.id, user_ids[0])

        # Assert
        self.assertEqual(league.id, state.fantasy_league_id)
        self.assertEqual(1, state.current_round)
        self.assertEqual(2, state.current_pick_number)
        self.assertEqual(24, state.total_picks)
        self.assertEqual(user_ids[1], state.current_turn_user_id)
        self.assertEqual(1, len(state.picks))
        self.assertFalse(state.is_complete)
        # User 0 should have TOP filled
        self.assertEqual(player.id, state.user_slots[user_ids[0]].top_player_id)
        # User 1 should have nothing
        self.assertIsNone(state.user_slots[user_ids[1]].top_player_id)

    def test_get_draft_state_after_completion(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        self.advance_draft(league, user_ids, 24)

        # Act
        state = self.draft_service.get_draft_state(league.id, user_ids[0])

        # Assert
        self.assertTrue(state.is_complete)
        self.assertIsNone(state.current_turn_user_id)
        self.assertEqual(24, len(state.picks))
        self.assertEqual(24, state.total_picks)

    # --------------------------------------------------
    # ------------- get_available_players --------------
    # --------------------------------------------------
    def test_get_available_players_excludes_drafted_and_role_none(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        valid_player = self.make_player(PlayerRole.TOP)
        drafted_player = self.make_player(PlayerRole.JUNGLE)
        none_player = self.make_player(PlayerRole.NONE)
        self.draft_service.make_pick(league.id, user_ids[0], player_id=drafted_player.id)

        # Act
        available = self.draft_service.get_available_players(league.id, user_ids[0])

        # Assert
        available_ids = [p.id for p in available]
        self.assertIn(valid_player.id, available_ids)
        self.assertNotIn(drafted_player.id, available_ids)
        self.assertNotIn(none_player.id, available_ids)

    def test_get_available_players_only_from_available_leagues(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        valid_player = self.make_player(PlayerRole.TOP)

        # Player from a different league
        other_league = riot_fixtures.league_2_fixture
        self.db.put_league(other_league)
        other_team = ProfessionalTeam(
            id=ProTeamID("other-league-team"),
            slug="other",
            name="Other",
            code="OT",
            image="http://img.png",
            status="active",
            home_league_name=other_league.name,
        )
        self.db.put_team(other_team)
        other_player = self.make_player(PlayerRole.MID, team_id=other_team.id)

        # Act
        available = self.draft_service.get_available_players(league.id, user_ids[0])

        # Assert
        available_ids = [p.id for p in available]
        self.assertIn(valid_player.id, available_ids)
        self.assertNotIn(other_player.id, available_ids)

    # --------------------------------------------------
    # ------------- get_available_teams ----------------
    # --------------------------------------------------
    def test_get_available_teams_excludes_drafted(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        self.db.put_team(riot_fixtures.team_2_fixture)
        self.draft_service.make_pick(
            league.id, user_ids[0], team_id=riot_fixtures.team_1_fixture.id
        )

        # Act
        available = self.draft_service.get_available_teams(league.id, user_ids[1])

        # Assert
        available_ids = [t.id for t in available]
        self.assertNotIn(riot_fixtures.team_1_fixture.id, available_ids)
        self.assertIn(riot_fixtures.team_2_fixture.id, available_ids)

    def test_get_available_teams_only_from_available_leagues(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        other_league = riot_fixtures.league_2_fixture
        self.db.put_league(other_league)
        other_team = ProfessionalTeam(
            id=ProTeamID("other-league-team-2"),
            slug="other",
            name="Other",
            code="OT",
            image="http://img.png",
            status="active",
            home_league_name=other_league.name,
        )
        self.db.put_team(other_team)

        # Act
        available = self.draft_service.get_available_teams(league.id, user_ids[0])

        # Assert
        available_ids = [t.id for t in available]
        self.assertIn(riot_fixtures.team_1_fixture.id, available_ids)
        self.assertNotIn(other_team.id, available_ids)

    def test_get_available_players_returns_empty_when_all_drafted(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        player = self.make_player(PlayerRole.TOP)
        self.draft_service.make_pick(league.id, user_ids[0], player_id=player.id)

        # Act — the only available player was just drafted
        available = self.draft_service.get_available_players(league.id, user_ids[1])

        # Assert
        self.assertEqual([], available)

    def test_get_available_teams_returns_empty_when_all_drafted(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        # team_1 is the only team in the available league
        self.draft_service.make_pick(
            league.id, user_ids[0], team_id=riot_fixtures.team_1_fixture.id
        )

        # Act
        available = self.draft_service.get_available_teams(league.id, user_ids[1])

        # Assert
        self.assertEqual([], available)

    # --------------------------------------------------
    # ------------------ auto_pick ---------------------
    # --------------------------------------------------
    def test_auto_pick_fills_first_empty_slot(self):
        # Arrange
        league, user_ids = self.setup_draft_league()
        self.make_player(PlayerRole.TOP)  # available for auto_pick

        # Act
        result = self.draft_service.auto_pick(league.id, user_ids[0])

        # Assert — should pick a TOP player (first empty slot)
        self.assertEqual(user_ids[0], result.user_id)
        self.assertIsNotNone(result.player_id)
        teams = self.db.get_all_fantasy_teams_for_user(league.id, user_ids[0])
        self.assertIsNotNone(teams[0].top_player_id)

    def test_auto_pick_skips_filled_slots(self):
        # Arrange — fill TOP for user 0, then advance back to user 0
        league, user_ids = self.setup_draft_league()
        self.make_player(PlayerRole.JUNGLE)  # available for auto_pick
        top_player = self.make_player(PlayerRole.TOP)
        self.draft_service.make_pick(league.id, user_ids[0], player_id=top_player.id)
        self.advance_draft(league, user_ids, 6)

        # Act — user 0's turn again, TOP is filled so should pick JUNGLE
        self.draft_service.auto_pick(league.id, user_ids[0])

        # Assert
        teams = self.db.get_all_fantasy_teams_for_user(league.id, user_ids[0])
        self.assertIsNotNone(teams[0].jungle_player_id)

    def test_auto_pick_picks_team_when_all_player_slots_filled(self):
        # Arrange — fill all 5 player slots for user 0
        league, user_ids = self.setup_draft_league()
        self.db.put_team(riot_fixtures.team_2_fixture)

        # User 0's turns in a 4-user snake: picks 1, 8, 9, 16, 17, 24
        # Fill 5 player slots across user 0's first 5 turns
        roles_to_fill = [
            PlayerRole.TOP,
            PlayerRole.JUNGLE,
            PlayerRole.MID,
            PlayerRole.BOTTOM,
            PlayerRole.SUPPORT,
        ]

        # Pick 1: user 0
        p = self.make_player(roles_to_fill[0])
        self.draft_service.make_pick(league.id, user_ids[0], player_id=p.id)
        # Advance picks 2-7 (6 picks)
        self.advance_draft(league, user_ids, 6)
        # Pick 8: user 0 (round 2 snake: pos 4,3,2,1 → pick 8 = pos 1 = user 0)
        p = self.make_player(roles_to_fill[1])
        self.draft_service.make_pick(league.id, user_ids[0], player_id=p.id)
        # Pick 9: user 0 (round 3: pos 1 = user 0)
        p = self.make_player(roles_to_fill[2])
        self.draft_service.make_pick(league.id, user_ids[0], player_id=p.id)
        # Advance picks 10-15 (6 picks)
        self.advance_draft(league, user_ids, 6)
        # Pick 16: user 0 (round 4 snake: pos 4,3,2,1 → pick 16 = pos 1 = user 0)
        p = self.make_player(roles_to_fill[3])
        self.draft_service.make_pick(league.id, user_ids[0], player_id=p.id)
        # Pick 17: user 0 (round 5: pos 1 = user 0)
        p = self.make_player(roles_to_fill[4])
        self.draft_service.make_pick(league.id, user_ids[0], player_id=p.id)
        # Advance picks 18-23 (6 picks)
        self.advance_draft(league, user_ids, 6)

        # Now pick 24: user 0's turn, all player slots filled
        # Act
        result = self.draft_service.auto_pick(league.id, user_ids[0])

        # Assert
        self.assertIsNotNone(result.team_id)
        teams = self.db.get_all_fantasy_teams_for_user(league.id, user_ids[0])
        self.assertIsNotNone(teams[0].team_id)
