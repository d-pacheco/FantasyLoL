import logging

from src.common.schemas.riot_data_schemas import RiotGameID, GameDragons, ProTeamID
from src.db.database_service import DatabaseService
from src.riot_scraper.game_analysis import (
    detect_multi_kills,
    detect_dragon_order,
    compute_duration,
)
from src.riot_scraper.job_runner import JobRunner
from src.riot_scraper.riot_api.riot_api_client import RiotApiClient
from src.riot_scraper.riot_api.schemas.get_live_window import WindowFrame
from src.riot_scraper.timestamp_util import TimestampUtil

logger = logging.getLogger("scraper.game_analysis")


class GameAnalysisScraper:
    def __init__(self, database_service: DatabaseService, riot_api_client: RiotApiClient):
        self.db = database_service
        self.api = riot_api_client
        self.job_runner = JobRunner()

    def analyze_games_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.analyze_games,
            job_name="game analysis job",
            max_retries=3,
        )

    def analyze_games(self) -> None:
        game_ids = self.db.get_pending_analysis_game_ids(limit=5)
        for game_id in game_ids:
            self._analyze_game(game_id)

    def _analyze_game(self, game_id: RiotGameID) -> None:
        logger.info(f"Analyzing game {game_id}")
        frames = self._fetch_all_frames(game_id)
        if frames is None:
            logger.warning(f"No frame data for game {game_id}, marking unavailable")
            self.db.update_frames_status(game_id, "unavailable")
            return

        # Compute duration
        duration = compute_duration(frames)
        if duration > 0:
            self.db.update_game_duration(game_id, duration)

        # Detect multi-kills
        multi_kills = detect_multi_kills(frames)
        for mk in multi_kills:
            self.db.put_game_multi_kill(game_id, mk.participant_id, mk.kill_number, mk.kill_type)

        # Detect dragon order
        game = self.db.get_game_by_id(game_id)
        if game and game.blue_team and game.red_team:
            dragons = detect_dragon_order(frames, game.blue_team, game.red_team)
            for d in dragons:
                self.db.put_game_dragon(
                    GameDragons(
                        game_id=game_id,
                        dragon_number=d.dragon_number,
                        team_id=ProTeamID(d.team_id),
                        dragon_type=d.dragon_type,
                    )
                )

        self.db.update_frames_status(game_id, "completed")
        logger.info(f"Game {game_id} analysis complete")

    def _fetch_all_frames(self, game_id: RiotGameID) -> list[WindowFrame] | None:
        initial_window = self.api.get_game_window(game_id)
        if initial_window is None:
            return None

        all_frames: list[WindowFrame] = []
        seen_timestamps: set[str] = set()

        start_time = TimestampUtil.round_to_10_seconds(initial_window.frames[0].rfc460Timestamp)
        current_time = start_time
        finished = False

        while not finished:
            window = self.api.get_game_window(game_id, current_time)
            if window is None:
                break

            for frame in window.frames:
                if frame.rfc460Timestamp not in seen_timestamps:
                    seen_timestamps.add(frame.rfc460Timestamp)
                    all_frames.append(frame)
                from src.common.schemas.riot_data_schemas import LiveGameState

                if frame.gameState == LiveGameState.FINISHED:
                    finished = True

            current_time = TimestampUtil.add_10_seconds(current_time)

        return all_frames if all_frames else None
