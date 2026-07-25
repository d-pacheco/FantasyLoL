"""Integration test for LeaderboardService with real database."""

import uuid
from copy import deepcopy
from datetime import datetime, timedelta

import pytz

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures, riot_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueStatus,
    FantasyLeagueMembershipStatus,
    FantasyLeagueMembership,
    FantasyTeam,
    UserID,
)
from src.common.schemas.riot_data_schemas import (
    ProfessionalPlayer,
    ProfessionalTeam,
    PlayerRole,
    ProPlayerID,
    ProTeamID,
    RiotGameID,
    RiotMatchID,
    Tournament,
)
from src.fantasy.service.leaderboard_service import LeaderboardService


class LeaderboardServiceIntegrationTest(TestBase):
    def setUp(self):
        super().setUp()
        self.leaderboard_service = LeaderboardService(self.db)
        self.seed_tournament_prerequisites()

    def _setup_league_with_scores(self):
        """Set up a complete league in ACTIVE state with match data for scoring."""
        # Create Riot league and tournament
        riot_league = deepcopy(riot_fixtures.league_1_fixture)
        self.db.put_league(riot_league)

        now = datetime.now(pytz.utc)
        tournament = Tournament(
            id="tournament-1",
            slug="test-split-2026",
            start_date=(now - timedelta(days=30)).strftime("%Y-%m-%d"),
            end_date=(now + timedelta(days=30)).strftime("%Y-%m-%d"),
            league_id=riot_league.id,
        )
        self.db.put_tournament(tournament)

        # Create team
        team = ProfessionalTeam(
            id=ProTeamID("team-t1"),
            slug="t1",
            name="T1",
            code="T1",
            image="http://img.png",
            status="active",
            home_league_name=riot_league.name,
        )
        self.db.put_team(team)

        # Create player
        player = ProfessionalPlayer(
            id=ProPlayerID("player-faker"),
            summoner_name="Faker",
            image="http://img.png",
            role=PlayerRole.MID,
            team_id=team.id,
        )
        self.db.put_player(player)

        # Create fantasy league in ACTIVE state
        fantasy_league = deepcopy(fantasy_fixtures.fantasy_league_fixture)
        fantasy_league.status = FantasyLeagueStatus.ACTIVE
        fantasy_league.available_leagues = [riot_league.id]
        fantasy_league.tournament_id = tournament.id
        fantasy_league.start_week = 1
        fantasy_league.current_week = 1
        fantasy_league.number_of_teams = 4
        self.db.create_fantasy_league(fantasy_league)

        # Create scoring settings with defaults
        from src.common.schemas.fantasy_schemas import FantasyLeagueScoringSettings

        scoring = FantasyLeagueScoringSettings(fantasy_league_id=fantasy_league.id)
        self.db.put_fantasy_league_scoring_settings(scoring)

        # Create owner user
        owner = fantasy_fixtures.user_fixture
        self.db.create_user(owner)
        self.db.create_fantasy_league_membership(
            FantasyLeagueMembership(
                league_id=fantasy_league.id,
                user_id=owner.id,
                status=FantasyLeagueMembershipStatus.ACCEPTED,
            )
        )

        # Create second user
        user2_id = UserID(str(uuid.uuid4()))
        self.db.create_fantasy_league_membership(
            FantasyLeagueMembership(
                league_id=fantasy_league.id,
                user_id=user2_id,
                status=FantasyLeagueMembershipStatus.ACCEPTED,
            )
        )

        # Create roster for owner (mid = Faker)
        roster = FantasyTeam(
            fantasy_league_id=fantasy_league.id,
            user_id=owner.id,
            week=1,
            mid_player_id=player.id,
            team_id=team.id,
        )
        self.db.put_fantasy_team(roster)

        # Create a match for Week 1
        match_id = RiotMatchID("match-wk1-1")
        match_start = (now - timedelta(days=5)).isoformat()
        from src.db.models import MatchModel

        with self.db_provider.get_db() as db:
            db.merge(
                MatchModel(
                    id=match_id,
                    start_time=match_start,
                    block_name="Week 1",
                    league_slug=riot_league.slug,
                    strategy_type="bestOf",
                    strategy_count=3,
                    tournament_id=tournament.id,
                    state="completed",
                    has_games=True,
                )
            )
            db.commit()

        # Create a game for the match
        game_id = RiotGameID("game-wk1-1-g1")
        from src.db.models import GameModel

        with self.db_provider.get_db() as db:
            db.merge(
                GameModel(
                    id=game_id,
                    state="completed",
                    number=1,
                    match_id=match_id,
                    duration_seconds=1800,  # 30 minutes
                )
            )
            db.commit()

        # Create player game metadata + stats (Faker: 8 kills, 2 deaths, 5 assists)
        from src.db.models import PlayerGameMetadataModel, PlayerGameStatsModel

        with self.db_provider.get_db() as db:
            db.merge(
                PlayerGameMetadataModel(
                    game_id=game_id,
                    player_id=player.id,
                    participant_id=1,
                    champion_id="Azir",
                    role="mid",
                )
            )
            db.merge(
                PlayerGameStatsModel(
                    game_id=game_id,
                    participant_id=1,
                    kills=8,
                    deaths=2,
                    assists=5,
                    total_gold=15000,
                    creep_score=200,
                    kill_participation=70,
                    champion_damage_share=30,
                    wards_placed=10,
                    wards_destroyed=5,
                )
            )
            db.commit()

        # Create team game stats
        from src.db.models import TeamGameStatsModel

        with self.db_provider.get_db() as db:
            db.merge(
                TeamGameStatsModel(
                    game_id=game_id,
                    team_id=team.id,
                    total_gold=60000,
                    inhibitors=2,
                    towers=8,
                    barons=1,
                    total_kills=20,
                )
            )
            db.commit()

        # Create match view data (need event_teams for the view)
        from src.db.models import EventTeamsModel

        with self.db_provider.get_db() as db:
            db.merge(
                EventTeamsModel(
                    match_id=match_id,
                    side=1,
                    team_code="T1",
                    team_name="T1",
                    team_image="http://img.png",
                    game_wins=2,
                    outcome="win",
                )
            )
            db.merge(
                EventTeamsModel(
                    match_id=match_id,
                    side=2,
                    team_code="GEN",
                    team_name="GEN",
                    team_image="http://img.png",
                    game_wins=0,
                    outcome="loss",
                )
            )
            db.commit()

        return fantasy_league, owner, user2_id, player, team

    def test_leaderboard_returns_ranked_members(self):
        """Leaderboard should return members ranked by total points."""
        fantasy_league, owner, user2_id, player, team = self._setup_league_with_scores()

        result = self.leaderboard_service.get_leaderboard(fantasy_league.id, owner.id)

        assert result["fantasy_league_id"] == fantasy_league.id
        assert result["start_week"] == 1
        assert len(result["members"]) == 2

        # Owner should have points (has a roster with Faker)
        owner_entry = next(m for m in result["members"] if m["user_id"] == owner.id)
        assert owner_entry["total_points"] > 0

        # User2 has no roster, should have 0 points
        user2_entry = next(m for m in result["members"] if m["user_id"] == user2_id)
        assert user2_entry["total_points"] == 0.0

        # Owner should be ranked higher
        assert owner_entry["position"] < user2_entry["position"]

    def test_week_scores_returns_per_member_breakdown(self):
        """Week scores should return roster detail with per-category breakdown."""
        fantasy_league, owner, user2_id, player, team = self._setup_league_with_scores()

        result = self.leaderboard_service.get_week_scores(fantasy_league.id, owner.id, 1)

        assert result["fantasy_league_id"] == fantasy_league.id
        assert result["week"] == 1
        assert len(result["members"]) == 2

        # Find owner's entry
        owner_entry = next(m for m in result["members"] if m["user_id"] == owner.id)
        assert owner_entry["total_points"] > 0

        # Check roster has mid slot with Faker
        assert "mid" in owner_entry["roster"]
        mid_slot = owner_entry["roster"]["mid"]
        assert mid_slot["player_id"] == player.id
        assert mid_slot["summoner_name"] == "Faker"
        assert mid_slot["points"] > 0
        assert "kills" in mid_slot["breakdown"]

        # Check team slot
        assert "team" in owner_entry["roster"]
        team_slot = owner_entry["roster"]["team"]
        assert team_slot["team_id"] == team.id
        assert team_slot["team_name"] == "T1"

    def test_leaderboard_ignores_matches_from_other_tournaments_with_overlapping_dates(self):
        """Scoring must be scoped to the league's tournament_id, not just any tournament
        whose date range covers today. A decoy tournament in the same Riot league with
        overlapping dates and its own Week 1 match must not contribute points."""
        fantasy_league, owner, user2_id, player, team = self._setup_league_with_scores()

        # Create a second tournament for the same riot league with an overlapping date range
        now = datetime.now(pytz.utc)
        decoy_tournament = Tournament(
            id="decoy-tournament",
            slug="decoy-split-2026",
            start_date=(now - timedelta(days=30)).strftime("%Y-%m-%d"),
            end_date=(now + timedelta(days=30)).strftime("%Y-%m-%d"),
            league_id=riot_fixtures.league_1_fixture.id,
        )
        self.db.put_tournament(decoy_tournament)

        # Decoy match in Week 1 of the decoy tournament, involving the same player's team,
        # with a huge kill count that would inflate the score if it leaked in
        from src.db.models import (
            MatchModel,
            GameModel,
            PlayerGameMetadataModel,
            PlayerGameStatsModel,
        )

        decoy_match_id = RiotMatchID("decoy-match-wk1")
        decoy_game_id = RiotGameID("decoy-game-wk1-g1")
        with self.db_provider.get_db() as db:
            db.merge(
                MatchModel(
                    id=decoy_match_id,
                    start_time=(now - timedelta(days=5)).isoformat(),
                    block_name="Week 1",
                    league_slug=riot_fixtures.league_1_fixture.slug,
                    strategy_type="bestOf",
                    strategy_count=3,
                    tournament_id=decoy_tournament.id,
                    state="completed",
                    has_games=True,
                )
            )
            db.commit()

        with self.db_provider.get_db() as db:
            db.merge(
                GameModel(
                    id=decoy_game_id,
                    state="completed",
                    number=1,
                    match_id=decoy_match_id,
                    duration_seconds=1800,
                )
            )
            db.commit()

        with self.db_provider.get_db() as db:
            db.merge(
                PlayerGameMetadataModel(
                    game_id=decoy_game_id,
                    player_id=player.id,
                    participant_id=1,
                    champion_id="Azir",
                    role="mid",
                )
            )
            db.merge(
                PlayerGameStatsModel(
                    game_id=decoy_game_id,
                    participant_id=1,
                    kills=999,
                    deaths=0,
                    assists=999,
                    total_gold=99999,
                    creep_score=999,
                    kill_participation=100,
                    champion_damage_share=100,
                    wards_placed=99,
                    wards_destroyed=99,
                )
            )
            db.commit()

        result = self.leaderboard_service.get_leaderboard(fantasy_league.id, owner.id)

        owner_entry = next(m for m in result["members"] if m["user_id"] == owner.id)
        week_result = self.leaderboard_service.get_week_scores(fantasy_league.id, owner.id, 1)
        owner_week_entry = next(m for m in week_result["members"] if m["user_id"] == owner.id)
        mid_slot = owner_week_entry["roster"]["mid"]

        # The decoy match's 999 kills must not be included — only the real tournament's
        # match (8 kills) should count.
        assert mid_slot["breakdown"]["kills"]["value"] == 8
        assert owner_entry["total_points"] == owner_week_entry["total_points"]
