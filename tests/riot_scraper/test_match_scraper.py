from unittest.mock import MagicMock

from tests.test_base import TestBase
from src.common.schemas.riot_data_schemas import (
    RiotMatchID,
    MatchState,
    GameState,
    RiotGameID,
    RiotLeagueID,
    RiotTournamentID,
    ProTeamID,
)
from src.riot_scraper.riot_api.schemas.get_schedule import (
    GetScheduleResponse,
    ScheduleData,
    Schedule,
    Pages,
    ScheduleEvent,
    ScheduleLeague,
    ScheduleMatch as ApiScheduleMatch,
    MatchStrategy,
    MatchTeam,
    TeamRecord,
)
from src.riot_scraper.riot_api.schemas.get_event_details import (
    EventDetailsResponse,
    EventData,
    Event,
    EventTournament,
    EventLeague,
    EventMatch,
    MatchStrategy as DetailMatchStrategy,
    MatchTeam as DetailMatchTeam,
    MatchGame,
    GameTeam,
)
from src.riot_scraper.scrapers.match_scraper import RiotMatchScraper


def _make_schedule_response(events, older=None, newer=None):
    return GetScheduleResponse(
        data=ScheduleData(
            schedule=Schedule(
                pages=Pages(older=older, newer=newer),
                events=events,
            )
        )
    )


def _make_schedule_event(match_id, state=MatchState.UNSTARTED):
    return ScheduleEvent(
        startTime="2024-01-01T12:00:00Z",
        state=state,
        type="match",
        blockName="Week 1",
        league=ScheduleLeague(name="Test League", slug="test-league"),
        match=ApiScheduleMatch(
            id=RiotMatchID(match_id),
            teams=[
                MatchTeam(
                    name="Team A",
                    code="TA",
                    image="http://ta.png",
                    result=None,
                    record=TeamRecord(wins=1, losses=0),
                ),
                MatchTeam(
                    name="Team B",
                    code="TB",
                    image="http://tb.png",
                    result=None,
                    record=TeamRecord(wins=0, losses=1),
                ),
            ],
            strategy=MatchStrategy(type="bestOf", count=3),
        ),
    )


def _make_event_details_response(match_id):
    return EventDetailsResponse(
        data=EventData(
            event=Event(
                id=RiotMatchID(match_id),
                type="match",
                tournament=EventTournament(id=RiotTournamentID("tourn-1")),
                league=EventLeague(
                    id=RiotLeagueID("league-1"),
                    slug="test-league",
                    image="http://l.png",
                    name="Test League",
                ),
                match=EventMatch(
                    strategy=DetailMatchStrategy(count=3),
                    teams=[
                        DetailMatchTeam(
                            id=ProTeamID("team-a-id"),
                            name="Team A",
                            code="TA",
                            image="http://ta.png",
                            result=None,
                        ),
                        DetailMatchTeam(
                            id=ProTeamID("team-b-id"),
                            name="Team B",
                            code="TB",
                            image="http://tb.png",
                            result=None,
                        ),
                    ],
                    games=[
                        MatchGame(
                            number=1,
                            id=RiotGameID("game-1"),
                            state=GameState.COMPLETED,
                            teams=[
                                GameTeam(id=ProTeamID("team-a-id"), side="blue"),
                                GameTeam(id=ProTeamID("team-b-id"), side="red"),
                            ],
                        ),
                    ],
                ),
            )
        )
    )


class TestRiotMatchScraper(TestBase):
    def setUp(self):
        self.mock_api = MagicMock()
        self.scraper = RiotMatchScraper(
            database_service=self.db,
            riot_api_requester=self.mock_api,
        )

    # --- sync_schedule tests ---

    def test_sync_schedule_saves_matches_from_schedule(self):
        event = _make_schedule_event("match-sync-001")
        self.mock_api.get_schedule.return_value = _make_schedule_response([event])

        self.scraper.sync_schedule()

        result = self.db.get_match_by_id(RiotMatchID("match-sync-001"))
        self.assertIsNotNone(result)
        self.assertEqual("test-league", result.league_slug)

    def test_sync_schedule_stops_when_all_exist(self):
        event1 = _make_schedule_event("match-sync-002")

        # Pre-save the match so it already exists
        from src.common.schemas.riot_data_schemas import ScheduleMatch

        self.db.save_from_schedule(
            ScheduleMatch(
                id=RiotMatchID("match-sync-002"),
                start_time="2024-01-01T12:00:00Z",
                block_name="Week 1",
                league_slug="test-league",
                strategy_type="bestOf",
                strategy_count=3,
                state=MatchState.UNSTARTED,
                teams=[],
            )
        )

        # First page: all matches already exist → stop immediately
        self.mock_api.get_schedule.return_value = _make_schedule_response([event1], older="page-2")

        self.scraper.sync_schedule()

        # Should have called get_schedule only once (all_exist on first page)
        self.assertEqual(1, self.mock_api.get_schedule.call_count)

    def test_sync_schedule_makes_zero_get_event_details_calls(self):
        event = _make_schedule_event("match-sync-004")
        self.mock_api.get_schedule.return_value = _make_schedule_response([event])

        self.scraper.sync_schedule()

        self.mock_api.get_event_details.assert_not_called()

    # --- backfill_event_details tests ---

    def test_backfill_event_details_fetches_and_saves_details(self):
        # Set up league and tournament for FK resolution
        from src.common.schemas.riot_data_schemas import ScheduleMatch, ScheduleTeam
        from tests.test_util import riot_fixtures

        league = riot_fixtures.league_1_fixture.model_copy(deep=True)
        league.id = RiotLeagueID("league-1")
        league.slug = "test-league"
        self.db.put_league(league)

        from src.common.schemas.riot_data_schemas import Tournament

        tournament = Tournament(
            id=RiotTournamentID("tourn-1"),
            slug="test-tourn",
            start_date="2024-01-01",
            end_date="2024-12-31",
            league_id=league.id,
        )
        self.db.put_tournament(tournament)

        # Save a match via schedule (no games)
        self.db.save_from_schedule(
            ScheduleMatch(
                id=RiotMatchID("backfill-001"),
                start_time="2024-01-01T12:00:00Z",
                block_name="Week 1",
                league_slug="test-league",
                strategy_type="bestOf",
                strategy_count=3,
                state=MatchState.UNSTARTED,
                teams=[
                    ScheduleTeam(side=1, team_code="TA", team_name="Team A"),
                    ScheduleTeam(side=2, team_code="TB", team_name="Team B"),
                ],
            )
        )

        self.mock_api.get_event_details.return_value = _make_event_details_response("backfill-001")

        self.scraper.backfill_event_details()

        # Match should now have games
        ids_without_games = self.db.get_ids_without_games()
        self.assertNotIn(RiotMatchID("backfill-001"), ids_without_games)

    def test_backfill_event_details_skips_has_games_false(self):
        from src.common.schemas.riot_data_schemas import ScheduleMatch

        self.db.save_from_schedule(
            ScheduleMatch(
                id=RiotMatchID("backfill-002"),
                start_time="2024-01-01T12:00:00Z",
                block_name="Week 1",
                league_slug="test-league",
                strategy_type="bestOf",
                strategy_count=1,
                state=MatchState.UNSTARTED,
                teams=[],
            )
        )
        self.db.update_match_has_games(RiotMatchID("backfill-002"), False)

        self.scraper.backfill_event_details()

        self.mock_api.get_event_details.assert_not_called()

    # --- refresh_stale_events tests ---

    def test_refresh_stale_events_updates_match_state(self):
        from src.common.schemas.riot_data_schemas import ScheduleMatch, ScheduleTeam, Tournament
        from tests.test_util import riot_fixtures

        league = riot_fixtures.league_1_fixture.model_copy(deep=True)
        league.id = RiotLeagueID("league-1")
        league.slug = "test-league"
        self.db.put_league(league)
        tournament = Tournament(
            id=RiotTournamentID("tourn-1"),
            slug="test-tourn",
            start_date="2024-01-01",
            end_date="2024-12-31",
            league_id=league.id,
        )
        self.db.put_tournament(tournament)

        self.db.save_from_schedule(
            ScheduleMatch(
                id=RiotMatchID("stale-refresh-001"),
                start_time="2020-01-01T12:00:00Z",
                block_name="Week 1",
                league_slug="test-league",
                strategy_type="bestOf",
                strategy_count=1,
                state=MatchState.UNSTARTED,
                teams=[
                    ScheduleTeam(side=1, team_code="TA", team_name="Team A"),
                    ScheduleTeam(side=2, team_code="TB", team_name="Team B"),
                ],
            )
        )

        # Event details shows all games completed
        self.mock_api.get_event_details.return_value = _make_event_details_response(
            "stale-refresh-001"
        )

        self.scraper.refresh_stale_events()

        result = self.db.get_match_by_id(RiotMatchID("stale-refresh-001"))
        self.assertIsNotNone(result)
        # Match should have been updated with details
        self.mock_api.get_event_details.assert_called_once()

    def test_sync_schedule_then_backfill_then_refresh_runs_end_to_end(self):
        """Integration test: the three jobs run sequentially without error."""
        from src.common.schemas.riot_data_schemas import Tournament
        from tests.test_util import riot_fixtures

        # Set up league and tournament
        league = riot_fixtures.league_1_fixture.model_copy(deep=True)
        league.id = RiotLeagueID("league-1")
        league.slug = "test-league"
        self.db.put_league(league)
        tournament = Tournament(
            id=RiotTournamentID("tourn-1"),
            slug="test-tourn",
            start_date="2024-01-01",
            end_date="2024-12-31",
            league_id=league.id,
        )
        self.db.put_tournament(tournament)

        # sync_schedule saves a match
        event = _make_schedule_event("e2e-001")
        self.mock_api.get_schedule.return_value = _make_schedule_response([event])
        self.scraper.sync_schedule()

        # backfill_event_details fills in details
        self.mock_api.get_event_details.return_value = _make_event_details_response("e2e-001")
        self.scraper.backfill_event_details()

        # refresh_stale_events is a no-op (match is in the future)
        self.scraper.refresh_stale_events()

        result = self.db.get_match_by_id(RiotMatchID("e2e-001"))
        self.assertIsNotNone(result)
        ids_without_games = self.db.get_ids_without_games()
        self.assertNotIn(RiotMatchID("e2e-001"), ids_without_games)
