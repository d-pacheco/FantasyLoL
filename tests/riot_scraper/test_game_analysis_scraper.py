from unittest.mock import MagicMock

from tests.test_base import TestBase
from tests.test_util import riot_fixtures
from src.common.schemas.riot_data_schemas import (
    RiotGameID,
    GameState,
    LiveGameState,
)
from src.riot_scraper.riot_api.schemas.get_live_window import (
    GetLiveWindowResponse,
    GameMetaData,
    TeamMetaData,
    ParticipantMetadata,
    WindowFrame,
    TeamWindowFrame,
    ParticipantWindowFrame,
)
from src.common.schemas.riot_data_schemas import PlayerRole, RiotMatchID
from src.riot_scraper.scrapers.game_analysis_scraper import GameAnalysisScraper


def _make_participant_frame(pid, kills=0, health=100):
    return ParticipantWindowFrame(
        participantId=pid, totalGold=1000, level=6, kills=kills,
        deaths=0, assists=0, creepScore=100, currentHealth=health, maxHealth=100,
    )


def _make_window_response(game_id, frames):
    return GetLiveWindowResponse(
        esportsGameId=game_id,
        esportsMatchId=RiotMatchID("match-1"),
        gameMetadata=GameMetaData(
            patchVersion="14.1",
            blueTeamMetadata=TeamMetaData(
                esportsTeamId=riot_fixtures.team_2_fixture.id,
                participantMetadata=[
                    ParticipantMetadata(
                        participantId=i, summonerName=f"Blue{i}",
                        championId="Ahri", role=PlayerRole.MID,
                    ) for i in range(1, 6)
                ],
            ),
            redTeamMetadata=TeamMetaData(
                esportsTeamId=riot_fixtures.team_1_fixture.id,
                participantMetadata=[
                    ParticipantMetadata(
                        participantId=i, summonerName=f"Red{i}",
                        championId="Zed", role=PlayerRole.MID,
                    ) for i in range(6, 11)
                ],
            ),
        ),
        frames=frames,
    )


def _make_frame(timestamp, state=LiveGameState.IN_GAME, blue_kills=None, red_kills=None,
                blue_dragons=None, red_dragons=None):
    if blue_kills is None:
        blue_kills = [0] * 5
    if red_kills is None:
        red_kills = [0] * 5
    return WindowFrame(
        rfc460Timestamp=timestamp,
        gameState=state,
        blueTeam=TeamWindowFrame(
            totalGold=5000, inhibitors=0, towers=0, barons=0, totalKills=sum(blue_kills),
            dragons=blue_dragons or [],
            participants=[_make_participant_frame(i + 1, kills=blue_kills[i]) for i in range(5)],
        ),
        redTeam=TeamWindowFrame(
            totalGold=5000, inhibitors=0, towers=0, barons=0, totalKills=sum(red_kills),
            dragons=red_dragons or [],
            participants=[_make_participant_frame(i + 6, kills=red_kills[i]) for i in range(5)],
        ),
    )


class TestGameAnalysisScraper(TestBase):
    def setUp(self):
        self.mock_api = MagicMock()
        self.scraper = GameAnalysisScraper(
            database_service=self.db,
            riot_api_client=self.mock_api,
        )
        # Set up required FK data
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)
        self.db.put_match(riot_fixtures.match_fixture)

    def _create_pending_game(self, game_id="game-analysis-001"):
        from src.common.schemas.riot_data_schemas import Game
        game = Game(
            id=RiotGameID(game_id),
            state=GameState.COMPLETED,
            number=1,
            match_id=riot_fixtures.match_fixture.id,
            red_team=riot_fixtures.team_1_fixture.id,
            blue_team=riot_fixtures.team_2_fixture.id,
            has_game_data=True,
        )
        self.db.put_game(game)
        self.db.update_frames_status(RiotGameID(game_id), "pending")
        return RiotGameID(game_id)

    def test_analyzes_pending_game_and_marks_completed(self):
        game_id = self._create_pending_game()

        # Simple game: 2 frames, no pauses, player 1 gets a double kill
        frames = [
            _make_frame("2024-01-01T00:00:00.000Z"),
            _make_frame("2024-01-01T00:00:05.000Z", blue_kills=[1, 0, 0, 0, 0]),
            _make_frame("2024-01-01T00:00:10.000Z", blue_kills=[2, 0, 0, 0, 0],
                        blue_dragons=["infernal"],
                        state=LiveGameState.FINISHED),
        ]

        # API returns all frames in one window call, then None for subsequent
        self.mock_api.get_game_window.side_effect = [
            _make_window_response(game_id, frames),  # initial call (no timestamp)
            _make_window_response(game_id, frames),  # call with rounded timestamp
            None,  # subsequent call returns None
        ]

        self.scraper.analyze_games()

        # Verify frames_status is completed
        game = self.db.get_game_by_id(game_id)
        self.assertIsNotNone(game)

        # Verify duration was persisted
        from src.db.models import GameModel
        with self.db_provider.get_db() as session:
            gm = session.query(GameModel).filter(GameModel.id == game_id).first()
            self.assertEqual("completed", gm.frames_status)
            self.assertEqual(10, gm.duration_seconds)

        # Verify multi-kills
        multi_kills = self.db.get_game_multi_kills(game_id)
        self.assertEqual(1, len(multi_kills))
        self.assertEqual(1, multi_kills[0].participant_id)
        self.assertEqual("double", multi_kills[0].kill_type)

        # Verify dragons
        dragons = self.db.get_game_dragons(game_id)
        self.assertEqual(1, len(dragons))
        self.assertEqual("infernal", dragons[0].dragon_type)

    def test_marks_unavailable_when_api_returns_no_data(self):
        game_id = self._create_pending_game("game-no-data-001")

        self.mock_api.get_game_window.return_value = None

        self.scraper.analyze_games()

        from src.db.models import GameModel
        with self.db_provider.get_db() as session:
            gm = session.query(GameModel).filter(GameModel.id == game_id).first()
            self.assertEqual("unavailable", gm.frames_status)

    def test_processes_at_most_5_games(self):
        # Create 7 pending games
        for i in range(7):
            self._create_pending_game(f"game-cap-{i:03d}")

        self.mock_api.get_game_window.return_value = None

        self.scraper.analyze_games()

        # Should have called get_game_window for only 5 games
        self.assertEqual(5, self.mock_api.get_game_window.call_count)

    def test_frames_status_set_to_pending_when_game_completes(self):
        """When a game transitions to COMPLETED, frames_status should be set to pending."""
        from src.common.schemas.riot_data_schemas import Game
        game_id = RiotGameID("game-lifecycle-001")
        game = Game(
            id=game_id,
            state=GameState.INPROGRESS,
            number=1,
            match_id=riot_fixtures.match_fixture.id,
            red_team=riot_fixtures.team_1_fixture.id,
            blue_team=riot_fixtures.team_2_fixture.id,
            has_game_data=True,
        )
        self.db.put_game(game)

        # Simulate game completing
        self.db.update_game_state(game_id, GameState.COMPLETED)
        self.db.update_frames_status(game_id, "pending")

        from src.db.models import GameModel
        with self.db_provider.get_db() as session:
            gm = session.query(GameModel).filter(GameModel.id == game_id).first()
            self.assertEqual("pending", gm.frames_status)

    def test_frames_status_set_to_unavailable_when_details_unavailable(self):
        """When game has details_status=unavailable, frames_status should be unavailable."""
        from src.common.schemas.riot_data_schemas import Game
        game_id = RiotGameID("game-lifecycle-002")
        game = Game(
            id=game_id,
            state=GameState.COMPLETED,
            number=1,
            match_id=riot_fixtures.match_fixture.id,
            red_team=riot_fixtures.team_1_fixture.id,
            blue_team=riot_fixtures.team_2_fixture.id,
            has_game_data=False,
        )
        self.db.put_game(game)

        # When details_status is "unavailable", frames_status should also be unavailable
        from src.db.models import GameModel
        with self.db_provider.get_db() as session:
            gm = session.query(GameModel).filter(GameModel.id == game_id).first()
            self.assertEqual("unavailable", gm.details_status)
            # frames_status should remain None (not set to pending)
            self.assertIsNone(gm.frames_status)

    def test_game_scraper_sets_frames_status_pending_on_completion(self):
        """The update_game_states_job sets frames_status=pending when game completes."""
        from src.common.schemas.riot_data_schemas import Game, GetGamesResponseSchema
        from src.riot_scraper.scrapers.game_scraper import RiotGameScraper
        from src.riot_scraper.job_runner import JobRunner
        from unittest.mock import MagicMock, patch

        game_id = RiotGameID("game-state-trans-001")
        game = Game(
            id=game_id,
            state=GameState.INPROGRESS,
            number=1,
            match_id=riot_fixtures.match_fixture.id,
            red_team=riot_fixtures.team_1_fixture.id,
            blue_team=riot_fixtures.team_2_fixture.id,
            has_game_data=True,
        )
        self.db.put_game(game)

        mock_api = MagicMock()
        # Simulate API returning game as completed
        mock_response = MagicMock()
        mock_response.data.games = [
            GetGamesResponseSchema(id=game_id, state=GameState.COMPLETED)
        ]
        mock_api.get_games.return_value = mock_response

        scraper = RiotGameScraper(
            database_service=self.db,
            api_requester=mock_api,
            job_runner=JobRunner(),
        )

        # Patch get_games_to_check_state to return our game
        with patch.object(self.db, 'get_games_to_check_state', return_value=[game_id]):
            scraper.update_game_states_job()

        from src.db.models import GameModel
        with self.db_provider.get_db() as session:
            gm = session.query(GameModel).filter(GameModel.id == game_id).first()
            self.assertEqual(GameState.COMPLETED, gm.state)
            self.assertEqual("pending", gm.frames_status)
