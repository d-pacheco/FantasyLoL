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
from src.common.schemas.riot_data_schemas import ProPlayerID, ProTeamID  # noqa: F401
from src.fantasy.exceptions import (
    FantasyDraftException,  # noqa: F401
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

    def create_draft_order(self, league_id, user_id, position):
        self.db.create_fantasy_league_draft_order(
            FantasyLeagueDraftOrder(fantasy_league_id=league_id, user_id=user_id, position=position)
        )

    def setup_draft_league(self, num_users=2):
        """Set up a league in DRAFT status with the given number of users.
        Returns (league, [user_ids]) where user_ids[0] is the owner and picks first.
        """
        league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        league.available_leagues = [riot_fixtures.league_1_fixture.id]
        league.number_of_teams = num_users
        self.db.create_fantasy_league(league)

        # Set up riot data
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)

        user_ids = []
        owner = fantasy_fixtures.user_fixture
        self.db.create_user(owner)
        user_ids.append(owner.id)
        self.create_membership(league.id, owner.id, FantasyLeagueMembershipStatus.ACCEPTED)
        self.create_draft_order(league.id, owner.id, 1)

        for i in range(num_users - 1):
            uid = UserID(str(uuid.uuid4()))
            user_ids.append(uid)
            self.create_membership(league.id, uid, FantasyLeagueMembershipStatus.ACCEPTED)
            self.create_draft_order(league.id, uid, i + 2)

        self.draft_service.start_draft(league.id, owner.id)
        return league, user_ids

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
        # Arrange
        league, user_ids = self.setup_draft_league(num_users=2)
        player = riot_fixtures.player_1_fixture  # role=TOP, team=team_1
        self.db.put_player(player)

        # Act
        result = self.draft_service.make_pick(league.id, user_ids[0], player_id=player.id)

        # Assert — returns correct DraftPick
        self.assertEqual(1, result.pick_number)
        self.assertEqual(1, result.round_number)
        self.assertEqual(user_ids[0], result.user_id)
        self.assertEqual(player.id, result.player_id)

        # Assert — draft_picks persisted
        picks = self.db.get_draft_picks_for_league(league.id)
        self.assertEqual(1, len(picks))

        # Assert — FantasyTeam updated
        teams = self.db.get_all_fantasy_teams_for_user(league.id, user_ids[0])
        self.assertEqual(player.id, teams[0].top_player_id)

        # Assert — draft position advanced to user 2
        db_league = self.db.get_fantasy_league_by_id(league.id)
        self.assertEqual(2, db_league.current_draft_position)

    def test_make_pick_snake_order_reverses_in_round_2(self):
        # Arrange — 2-user league, make picks for round 1, then verify round 2 reverses
        league, user_ids = self.setup_draft_league(num_users=2)
        player_1 = riot_fixtures.player_1_fixture  # TOP
        player_2 = riot_fixtures.player_2_fixture  # JUNGLE
        player_3 = riot_fixtures.player_3_fixture  # MID
        self.db.put_player(player_1)
        self.db.put_player(player_2)
        self.db.put_player(player_3)

        # Round 1: user_ids[0] (pos 1) then user_ids[1] (pos 2)
        self.draft_service.make_pick(league.id, user_ids[0], player_id=player_1.id)
        self.draft_service.make_pick(league.id, user_ids[1], player_id=player_2.id)

        # Round 2 (snake): user_ids[1] (pos 2) picks first
        result = self.draft_service.make_pick(league.id, user_ids[1], player_id=player_3.id)

        # Assert
        self.assertEqual(3, result.pick_number)
        self.assertEqual(2, result.round_number)
        self.assertEqual(user_ids[1], result.user_id)

    def test_make_pick_rejects_not_users_turn(self):
        # Arrange
        league, user_ids = self.setup_draft_league(num_users=2)
        player = riot_fixtures.player_1_fixture
        self.db.put_player(player)

        # Act & Assert — user_ids[1] tries to pick but it's user_ids[0]'s turn
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[1], player_id=player.id)

    def test_make_pick_rejects_player_already_drafted(self):
        # Arrange
        league, user_ids = self.setup_draft_league(num_users=2)
        player = riot_fixtures.player_1_fixture  # TOP
        self.db.put_player(player)

        # User 0 drafts the player
        self.draft_service.make_pick(league.id, user_ids[0], player_id=player.id)

        # Act & Assert — user 1 tries to draft the same player
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[1], player_id=player.id)

    def test_make_pick_rejects_role_slot_filled(self):
        # Arrange — 2-user league, user picks two TOP players
        league, user_ids = self.setup_draft_league(num_users=2)
        player_top_1 = riot_fixtures.player_1_fixture  # TOP
        self.db.put_player(player_top_1)

        # Need a second TOP player from team_2
        from src.common.schemas.riot_data_schemas import ProfessionalPlayer, PlayerRole

        self.db.put_team(riot_fixtures.team_2_fixture)
        player_top_2 = ProfessionalPlayer(
            id=ProPlayerID("second-top"),
            summoner_name="SecondTop",
            image="http://img.png",
            role=PlayerRole.TOP,
            team_id=riot_fixtures.team_2_fixture.id,
        )
        self.db.put_player(player_top_2)

        # User 0 picks first TOP
        self.draft_service.make_pick(league.id, user_ids[0], player_id=player_top_1.id)
        # User 1 picks (to advance turn back to user 0 in round 2 via snake)
        player_jg = riot_fixtures.player_2_fixture  # JUNGLE
        self.db.put_player(player_jg)
        self.draft_service.make_pick(league.id, user_ids[1], player_id=player_jg.id)
        # Round 2 snake: user 1 picks again
        player_mid = riot_fixtures.player_3_fixture  # MID
        self.db.put_player(player_mid)
        self.draft_service.make_pick(league.id, user_ids[1], player_id=player_mid.id)

        # Now it's user 0's turn again (round 2, position 1)
        # Act & Assert — user 0 tries to pick another TOP
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[0], player_id=player_top_2.id)

    def test_make_pick_rejects_team_slot_filled(self):
        # Arrange
        league, user_ids = self.setup_draft_league(num_users=2)
        self.db.put_team(riot_fixtures.team_2_fixture)

        # User 0 picks team_1
        self.draft_service.make_pick(
            league.id, user_ids[0], team_id=riot_fixtures.team_1_fixture.id
        )
        # User 1 picks to advance
        player = riot_fixtures.player_1_fixture
        self.db.put_player(player)
        self.draft_service.make_pick(league.id, user_ids[1], player_id=player.id)
        # Round 2 snake: user 1 picks again
        player_2 = riot_fixtures.player_2_fixture
        self.db.put_player(player_2)
        self.draft_service.make_pick(league.id, user_ids[1], player_id=player_2.id)

        # Now user 0's turn — tries to pick another team
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(
                league.id, user_ids[0], team_id=riot_fixtures.team_2_fixture.id
            )

    def test_make_pick_rejects_player_with_role_none(self):
        # Arrange
        league, user_ids = self.setup_draft_league(num_users=2)
        from src.common.schemas.riot_data_schemas import ProfessionalPlayer, PlayerRole

        none_player = ProfessionalPlayer(
            id=ProPlayerID("none-role-player"),
            summoner_name="NoneRole",
            image="http://img.png",
            role=PlayerRole.NONE,
            team_id=riot_fixtures.team_1_fixture.id,
        )
        self.db.put_player(none_player)

        # Act & Assert
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[0], player_id=none_player.id)

    def test_make_pick_rejects_player_not_from_available_leagues(self):
        # Arrange
        league, user_ids = self.setup_draft_league(num_users=2)
        # Create a player on a team in a different league
        from src.common.schemas.riot_data_schemas import (
            ProfessionalPlayer,
            ProfessionalTeam,
            PlayerRole,
        )

        other_league = riot_fixtures.league_2_fixture
        self.db.put_league(other_league)
        other_team = ProfessionalTeam(
            id=ProTeamID("other-team"),
            slug="other",
            name="Other Team",
            code="OT",
            image="http://img.png",
            status="active",
            home_league_name=other_league.name,
        )
        self.db.put_team(other_team)
        other_player = ProfessionalPlayer(
            id=ProPlayerID("other-player"),
            summoner_name="OtherPlayer",
            image="http://img.png",
            role=PlayerRole.TOP,
            team_id=other_team.id,
        )
        self.db.put_player(other_player)

        # Act & Assert
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[0], player_id=other_player.id)

    def test_make_pick_rejects_neither_player_nor_team(self):
        # Arrange
        league, user_ids = self.setup_draft_league(num_users=2)

        # Act & Assert
        with self.assertRaises(FantasyDraftException):
            self.draft_service.make_pick(league.id, user_ids[0])

    def test_make_pick_rejects_both_player_and_team(self):
        # Arrange
        league, user_ids = self.setup_draft_league(num_users=2)
        player = riot_fixtures.player_1_fixture
        self.db.put_player(player)

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
        league, user_ids = self.setup_draft_league(num_users=2)

        # Act
        result = self.draft_service.make_pick(
            league.id, user_ids[0], team_id=riot_fixtures.team_1_fixture.id
        )

        # Assert
        self.assertEqual(1, result.pick_number)
        self.assertEqual(riot_fixtures.team_1_fixture.id, result.team_id)
        self.assertIsNone(result.player_id)

        # Verify FantasyTeam updated
        teams = self.db.get_all_fantasy_teams_for_user(league.id, user_ids[0])
        self.assertEqual(riot_fixtures.team_1_fixture.id, teams[0].team_id)
