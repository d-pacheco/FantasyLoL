from tests.test_base import TestBase
from tests.test_util import riot_fixtures

from src.common.schemas.riot_data_schemas import (
    RiotMatchID,
    MatchState,
    ScheduleMatch,
    ScheduleTeam,
)
from src.riot.service import RiotMatchService


class TestMatchSchedule(TestBase):
    def setUp(self):
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)
        # Mark league as fantasy available for schedule queries
        self.db.update_league_fantasy_available_status(riot_fixtures.league_1_fixture.id, True)
        self.match_service = RiotMatchService(self.db)

    def _create_match(self, match_id, state, start_time):
        self.db.save_from_schedule(
            ScheduleMatch(
                id=RiotMatchID(match_id),
                start_time=start_time,
                block_name="Week 1",
                league_slug=riot_fixtures.league_1_fixture.slug,
                strategy_type="bestOf",
                strategy_count=3,
                state=state,
                teams=[
                    ScheduleTeam(
                        side=1,
                        team_code=riot_fixtures.team_1_fixture.code,
                        team_name=riot_fixtures.team_1_fixture.name,
                        team_image=riot_fixtures.team_1_fixture.image,
                        game_wins=0,
                    ),
                    ScheduleTeam(
                        side=2,
                        team_code=riot_fixtures.team_2_fixture.code,
                        team_name=riot_fixtures.team_2_fixture.name,
                        team_image=riot_fixtures.team_2_fixture.image,
                        game_wins=0,
                    ),
                ],
            )
        )

    def test_match_response_includes_team_images(self):
        self._create_match("img-match-001", MatchState.UNSTARTED, "2099-01-01T12:00:00Z")

        match = self.db.get_match_by_id(RiotMatchID("img-match-001"))

        self.assertIsNotNone(match)
        self.assertEqual(riot_fixtures.team_1_fixture.image, match.team_1_image)
        self.assertEqual(riot_fixtures.team_2_fixture.image, match.team_2_image)

    def test_get_schedule_returns_live_upcoming_recent(self):
        # Live match
        self._create_match("live-001", MatchState.INPROGRESS, "2020-01-01T12:00:00Z")
        # Upcoming match
        self._create_match("upcoming-001", MatchState.UNSTARTED, "2099-01-01T12:00:00Z")
        # Recent match (completed, within 48h — use a time we know is recent)
        from datetime import datetime, timezone, timedelta

        recent_time = (datetime.now(timezone.utc) - timedelta(hours=6)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        self._create_match("recent-001", MatchState.COMPLETED, recent_time)
        # Old completed match (>48h ago — should NOT appear)
        self._create_match("old-001", MatchState.COMPLETED, "2020-01-01T12:00:00Z")

        schedule = self.match_service.get_schedule()

        live_ids = [m.id for m in schedule["live"]]
        upcoming_ids = [m.id for m in schedule["upcoming"]]
        recent_ids = [m.id for m in schedule["recent"]]

        self.assertIn(RiotMatchID("live-001"), live_ids)
        self.assertIn(RiotMatchID("upcoming-001"), upcoming_ids)
        self.assertIn(RiotMatchID("recent-001"), recent_ids)
        self.assertNotIn(RiotMatchID("old-001"), recent_ids)
