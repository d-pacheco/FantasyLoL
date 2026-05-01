from tests.test_base import TestBase
from tests.test_util import riot_fixtures

from src.common.schemas.riot_data_schemas import (
    Match, RiotMatchID, MatchState, ScheduleMatch, ScheduleTeam,
    MatchDetails, DetailTeam, DetailGame, RiotLeagueID, RiotTournamentID,
    RiotGameID, GameState,
)
from src.db.models import EventTeamsModel, MatchModel
from src.db.views import MatchView


class TestCrudRiotMatch(TestBase):
    def setUp(self):
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)

    def test_put_match_no_existing_match(self):
        # Arrange
        match = riot_fixtures.match_fixture

        # Act and Assert
        match_before_put = self.db.get_match_by_id(match.id)
        self.assertIsNone(match_before_put)
        self.db.put_match(match)
        match_after_put = self.db.get_match_by_id(match.id)
        self.assertEqual(match, match_after_put)

    def test_put_match_existing_match(self):
        # Arrange
        match = riot_fixtures.match_fixture
        self.db.put_match(match)
        updated_match = match.model_copy(deep=True)
        updated_match.strategy_count = match.strategy_count + 2

        # Act and Assert
        match_before_put = self.db.get_match_by_id(match.id)
        self.assertEqual(match, match_before_put)
        self.assertEqual(match.id, updated_match.id)
        self.db.put_match(updated_match)
        match_after_put = self.db.get_match_by_id(match.id)
        self.assertEqual(updated_match, match_after_put)

    def test_get_matches_no_filters(self):
        # Arrange
        expected_match = riot_fixtures.match_fixture
        self.db.put_match(expected_match)

        # Act
        matches_from_db = self.db.get_matches()

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        match_from_db = matches_from_db[0]
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_empty_filters(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        self.db.put_match(expected_match)

        # Act
        matches_from_db = self.db.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        match_from_db = matches_from_db[0]
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_league_slug_filter_existing_match(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        filters.append(MatchView.league_slug == expected_match.league_slug)
        self.db.put_match(expected_match)

        # Act
        matches_from_db = self.db.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        match_from_db = matches_from_db[0]
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_league_slug_filter_no_existing_match(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        filters.append(MatchView.league_slug == "badFilter")
        self.db.put_match(expected_match)

        # Act
        matches_from_db = self.db.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(0, len(matches_from_db))

    def test_get_matches_tournament_id_filter_existing_match(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        filters.append(MatchView.tournament_id == expected_match.tournament_id)
        self.db.put_match(expected_match)

        # Act
        matches_from_db = self.db.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        match_from_db = matches_from_db[0]
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_tournament_id_filter_no_existing_match(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        filters.append(MatchView.tournament_id == "badFilter")
        self.db.put_match(expected_match)

        # Act
        matches_from_db = self.db.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(0, len(matches_from_db))

    def test_get_match_by_id_existing_match(self):
        # Arrange
        expected_match = riot_fixtures.match_fixture
        self.db.put_match(expected_match)

        # Act
        match_from_db = self.db.get_match_by_id(expected_match.id)

        # Assert
        self.assertIsNotNone(match_from_db)
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_match_by_id_no_existing_match(self):
        # Arrange
        expected_match = riot_fixtures.match_fixture

        # Act
        match_from_db = self.db.get_match_by_id(expected_match.id)

        # Assert
        self.assertIsNone(match_from_db)

    def test_get_match_ids_without_games_matches_with_no_games(self):
        # Arrange
        match_with_has_games = riot_fixtures.match_fixture.model_copy(deep=True)
        match_with_has_games.has_games = True
        self.db.put_match(match_with_has_games)

        match_without_has_games = match_with_has_games.model_copy(deep=True)
        match_without_has_games.id = RiotMatchID("123")
        match_without_has_games.has_games = False
        self.db.put_match(match_without_has_games)

        self.db.put_match(riot_fixtures.future_match_fixture)
        game_for_future_match = riot_fixtures.game_1_fixture_unstarted_future_match
        self.db.put_game(game_for_future_match)

        # Act
        match_ids_without_games = self.db.get_match_ids_without_games()

        # Assert
        self.assertNotEqual(game_for_future_match.match_id, match_with_has_games.id)
        self.assertNotEqual(game_for_future_match.match_id, match_without_has_games.id)
        self.assertIsInstance(match_ids_without_games, list)
        self.assertEqual(1, len(match_ids_without_games))
        self.assertEqual(match_with_has_games.id, match_ids_without_games[0])

    def test_get_match_ids_without_games_matches_with_games(self):
        # Arrange
        match_with_has_games = riot_fixtures.match_fixture.model_copy(deep=True)
        match_with_has_games.has_games = True
        self.db.put_match(match_with_has_games)

        match_without_has_games = match_with_has_games.model_copy(deep=True)
        match_without_has_games.id = RiotMatchID("123")
        match_without_has_games.has_games = False
        self.db.put_match(match_without_has_games)

        match_1_game = riot_fixtures.game_1_fixture_completed.model_copy(deep=True)
        match_1_game.match_id = match_with_has_games.id
        self.db.put_game(match_1_game)

        match_2_game = riot_fixtures.game_2_fixture_inprogress.model_copy(deep=True)
        match_2_game.match_id = match_without_has_games.id
        self.db.put_game(match_2_game)

        # Act
        match_ids_without_games = self.db.get_match_ids_without_games()

        # Assert
        self.assertEqual(match_1_game.match_id, match_with_has_games.id)
        self.assertEqual(match_2_game.match_id, match_without_has_games.id)
        self.assertIsInstance(match_ids_without_games, list)
        self.assertEqual(0, len(match_ids_without_games))

    def test_put_match_without_league_or_tournament(self):
        # A match saved without league_id or tournament_id should still be retrievable
        match = riot_fixtures.match_fixture.model_copy(deep=True)
        match.league_slug = "unknown-league"
        match.tournament_id = None
        match.team_1_name = None
        match.team_2_name = None
        match.team_1_wins = None
        match.team_2_wins = None
        match.winning_team = None

        match_before = self.db.get_match_by_id(match.id)
        self.assertIsNone(match_before)
        self.db.put_match(match)
        match_after = self.db.get_match_by_id(match.id)
        self.assertIsNotNone(match_after)
        self.assertEqual(match.id, match_after.id)
        self.assertEqual("unknown-league", match_after.league_slug)
        self.assertIsNone(match_after.tournament_id)

    def test_match_view_with_event_teams_without_team_id(self):
        # event_teams rows keyed by (match_id, team_code) with team_id=None
        # should still appear in the match view
        match = riot_fixtures.match_fixture.model_copy(deep=True)
        match.tournament_id = None
        match.league_slug = "unknown-league"

        with self.db_provider.get_db() as session:
            db_match = MatchModel(
                id=match.id,
                start_time=match.start_time,
                block_name=match.block_name,
                league_slug=match.league_slug,
                strategy_type=match.strategy_type,
                strategy_count=match.strategy_count,
                state=match.state,
            )
            session.merge(db_match)
            session.flush()

            et1 = EventTeamsModel(
                match_id=match.id,
                team_code="T1",
                team_id=None,
                side=1,
                team_name="Team One",
                team_image="http://t1.png",
                game_wins=2,
                outcome="win",
            )
            et2 = EventTeamsModel(
                match_id=match.id,
                team_code="T2",
                team_id=None,
                side=2,
                team_name="Team Two",
                team_image="http://t2.png",
                game_wins=1,
                outcome="loss",
            )
            session.merge(et1)
            session.merge(et2)
            session.commit()

        result = self.db.get_match_by_id(match.id)
        self.assertIsNotNone(result)
        self.assertEqual("Team One", result.team_1_name)
        self.assertEqual("Team Two", result.team_2_name)
        self.assertEqual(2, result.team_1_wins)
        self.assertEqual(1, result.team_2_wins)
        self.assertEqual("Team One", result.winning_team)

    def test_update_match_has_games(self):
        # Arrange
        match = riot_fixtures.match_fixture.model_copy(deep=True)
        match.has_games = True
        self.db.put_match(match)

        new_has_games = not match.has_games
        updated_match = match.model_copy(deep=True)
        updated_match.has_games = new_has_games

        # Act and Assert
        self.assertEqual(match.id, updated_match.id)
        self.assertNotEqual(match.has_games, new_has_games)
        match_before_update = self.db.get_match_by_id(match.id)
        self.assertEqual(match, match_before_update)
        self.db.update_match_has_games(match.id, new_has_games)
        match_after_update = self.db.get_match_by_id(match.id)
        self.assertEqual(updated_match, match_after_update)

        with self.assertRaises(AssertionError):
            self.db.update_match_has_games(RiotMatchID("123"), new_has_games)


    # --- save_from_schedule tests ---

    def test_save_from_schedule_creates_retrievable_match(self):
        schedule_match = ScheduleMatch(
            id=RiotMatchID("sched-001"),
            start_time="2024-01-01T12:00:00Z",
            block_name="Week 1",
            league_slug="test-league",
            strategy_type="bestOf",
            strategy_count=3,
            state=MatchState.UNSTARTED,
            teams=[
                ScheduleTeam(side=1, team_code="T1", team_name="Team One", team_image="http://t1.png"),
                ScheduleTeam(side=2, team_code="T2", team_name="Team Two", team_image="http://t2.png"),
            ],
        )

        self.db.save_from_schedule(schedule_match)
        result = self.db.get_match_by_id(RiotMatchID("sched-001"))

        self.assertIsNotNone(result)
        self.assertEqual("sched-001", result.id)
        self.assertEqual("test-league", result.league_slug)
        self.assertEqual("Team One", result.team_1_name)
        self.assertEqual("Team Two", result.team_2_name)
        self.assertIsNone(result.tournament_id)

    def test_save_from_schedule_upserts_on_second_call(self):
        schedule_match = ScheduleMatch(
            id=RiotMatchID("sched-002"),
            start_time="2024-01-01T12:00:00Z",
            block_name="Week 1",
            league_slug="test-league",
            strategy_type="bestOf",
            strategy_count=3,
            state=MatchState.UNSTARTED,
            teams=[
                ScheduleTeam(side=1, team_code="T1", team_name="Team One"),
                ScheduleTeam(side=2, team_code="T2", team_name="Team Two"),
            ],
        )
        self.db.save_from_schedule(schedule_match)

        updated = schedule_match.model_copy(deep=True)
        updated.state = MatchState.INPROGRESS
        updated.teams[0].game_wins = 1
        self.db.save_from_schedule(updated)

        result = self.db.get_match_by_id(RiotMatchID("sched-002"))
        self.assertEqual(MatchState.INPROGRESS, result.state)
        self.assertEqual(1, result.team_1_wins)

    def test_save_from_schedule_works_without_teams_in_professional_teams(self):
        # No teams in professional_teams table — should still save
        schedule_match = ScheduleMatch(
            id=RiotMatchID("sched-003"),
            start_time="2024-01-01T12:00:00Z",
            block_name="Week 1",
            league_slug="test-league",
            strategy_type="bestOf",
            strategy_count=1,
            state=MatchState.UNSTARTED,
            teams=[
                ScheduleTeam(side=1, team_code="NEW1", team_name="New Team 1"),
                ScheduleTeam(side=2, team_code="NEW2", team_name="New Team 2"),
            ],
        )
        self.db.save_from_schedule(schedule_match)
        result = self.db.get_match_by_id(RiotMatchID("sched-003"))
        self.assertIsNotNone(result)
        self.assertEqual("New Team 1", result.team_1_name)
        self.assertEqual("New Team 2", result.team_2_name)

    # --- all_exist tests ---

    def test_all_exist_returns_true_when_all_present(self):
        self.db.put_match(riot_fixtures.match_fixture)
        result = self.db.all_exist([riot_fixtures.match_fixture.id])
        self.assertTrue(result)

    def test_all_exist_returns_false_when_any_missing(self):
        self.db.put_match(riot_fixtures.match_fixture)
        result = self.db.all_exist([riot_fixtures.match_fixture.id, RiotMatchID("missing-id")])
        self.assertFalse(result)

    def test_all_exist_returns_true_for_empty_list(self):
        result = self.db.all_exist([])
        self.assertTrue(result)

    # --- save_from_details tests ---

    def test_save_from_details_backfills_ids_and_creates_games(self):
        # First save via schedule (no IDs)
        schedule_match = ScheduleMatch(
            id=RiotMatchID("detail-001"),
            start_time="2024-01-01T12:00:00Z",
            block_name="Week 1",
            league_slug="test-league",
            strategy_type="bestOf",
            strategy_count=3,
            state=MatchState.COMPLETED,
            teams=[
                ScheduleTeam(side=1, team_code="T1", team_name="Team One", game_wins=2, outcome="win"),
                ScheduleTeam(side=2, team_code="T2", team_name="Team Two", game_wins=1, outcome="loss"),
            ],
        )
        self.db.save_from_schedule(schedule_match)

        # Create league and tournament for FK resolution
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_tournament(riot_fixtures.tournament_fixture)

        # Now backfill details
        details = MatchDetails(
            match_id=RiotMatchID("detail-001"),
            league_id=riot_fixtures.league_1_fixture.id,
            tournament_id=riot_fixtures.tournament_fixture.id,
            teams=[
                DetailTeam(team_id=riot_fixtures.team_1_fixture.id, team_code="T1"),
                DetailTeam(team_id=riot_fixtures.team_2_fixture.id, team_code="T2"),
            ],
            games=[
                DetailGame(id=RiotGameID("game-1"), state=GameState.COMPLETED, number=1),
                DetailGame(id=RiotGameID("game-2"), state=GameState.COMPLETED, number=2),
                DetailGame(id=RiotGameID("game-3"), state=GameState.COMPLETED, number=3),
            ],
        )
        self.db.save_from_details(details)

        result = self.db.get_match_by_id(RiotMatchID("detail-001"))
        self.assertIsNotNone(result)
        self.assertEqual(riot_fixtures.tournament_fixture.id, result.tournament_id)

        # Verify games were created
        ids_without_games = self.db.get_ids_without_games()
        self.assertNotIn(RiotMatchID("detail-001"), ids_without_games)

    def test_save_from_details_is_idempotent(self):
        schedule_match = ScheduleMatch(
            id=RiotMatchID("detail-002"),
            start_time="2024-01-01T12:00:00Z",
            block_name="Week 1",
            league_slug="test-league",
            strategy_type="bestOf",
            strategy_count=1,
            state=MatchState.COMPLETED,
            teams=[
                ScheduleTeam(side=1, team_code="T1", team_name="Team One", game_wins=1, outcome="win"),
                ScheduleTeam(side=2, team_code="T2", team_name="Team Two", game_wins=0, outcome="loss"),
            ],
        )
        self.db.save_from_schedule(schedule_match)
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_tournament(riot_fixtures.tournament_fixture)

        details = MatchDetails(
            match_id=RiotMatchID("detail-002"),
            league_id=riot_fixtures.league_1_fixture.id,
            tournament_id=riot_fixtures.tournament_fixture.id,
            teams=[],
            games=[
                DetailGame(id=RiotGameID("game-idem-1"), state=GameState.COMPLETED, number=1),
            ],
        )
        self.db.save_from_details(details)
        self.db.save_from_details(details)  # second call should not fail

        result = self.db.get_match_by_id(RiotMatchID("detail-002"))
        self.assertIsNotNone(result)

    # --- get_ids_without_games tests ---

    def test_get_ids_without_games_returns_matches_needing_backfill(self):
        schedule_match = ScheduleMatch(
            id=RiotMatchID("no-games-001"),
            start_time="2024-01-01T12:00:00Z",
            block_name="Week 1",
            league_slug="test-league",
            strategy_type="bestOf",
            strategy_count=1,
            state=MatchState.UNSTARTED,
            teams=[],
        )
        self.db.save_from_schedule(schedule_match)

        ids = self.db.get_ids_without_games()
        self.assertIn(RiotMatchID("no-games-001"), ids)

    def test_get_ids_without_games_excludes_has_games_false(self):
        schedule_match = ScheduleMatch(
            id=RiotMatchID("no-games-002"),
            start_time="2024-01-01T12:00:00Z",
            block_name="Week 1",
            league_slug="test-league",
            strategy_type="bestOf",
            strategy_count=1,
            state=MatchState.UNSTARTED,
            teams=[],
        )
        self.db.save_from_schedule(schedule_match)
        self.db.update_match_has_games(RiotMatchID("no-games-002"), False)

        ids = self.db.get_ids_without_games()
        self.assertNotIn(RiotMatchID("no-games-002"), ids)

    # --- get_stale_match_ids tests ---

    def test_get_stale_match_ids_returns_past_unstarted(self):
        schedule_match = ScheduleMatch(
            id=RiotMatchID("stale-001"),
            start_time="2020-01-01T12:00:00Z",
            block_name="Week 1",
            league_slug="test-league",
            strategy_type="bestOf",
            strategy_count=1,
            state=MatchState.UNSTARTED,
            teams=[],
        )
        self.db.save_from_schedule(schedule_match)

        ids = self.db.get_stale_match_ids()
        self.assertIn(RiotMatchID("stale-001"), ids)

    def test_get_stale_match_ids_returns_past_inprogress(self):
        schedule_match = ScheduleMatch(
            id=RiotMatchID("stale-002"),
            start_time="2020-01-01T12:00:00Z",
            block_name="Week 1",
            league_slug="test-league",
            strategy_type="bestOf",
            strategy_count=1,
            state=MatchState.INPROGRESS,
            teams=[],
        )
        self.db.save_from_schedule(schedule_match)

        ids = self.db.get_stale_match_ids()
        self.assertIn(RiotMatchID("stale-002"), ids)

    def test_get_stale_match_ids_excludes_completed(self):
        schedule_match = ScheduleMatch(
            id=RiotMatchID("stale-003"),
            start_time="2020-01-01T12:00:00Z",
            block_name="Week 1",
            league_slug="test-league",
            strategy_type="bestOf",
            strategy_count=1,
            state=MatchState.COMPLETED,
            teams=[],
        )
        self.db.save_from_schedule(schedule_match)

        ids = self.db.get_stale_match_ids()
        self.assertNotIn(RiotMatchID("stale-003"), ids)

    def test_get_stale_match_ids_excludes_future_unstarted(self):
        schedule_match = ScheduleMatch(
            id=RiotMatchID("stale-004"),
            start_time="2099-01-01T12:00:00Z",
            block_name="Week 1",
            league_slug="test-league",
            strategy_type="bestOf",
            strategy_count=1,
            state=MatchState.UNSTARTED,
            teams=[],
        )
        self.db.save_from_schedule(schedule_match)

        ids = self.db.get_stale_match_ids()
        self.assertNotIn(RiotMatchID("stale-004"), ids)