import logging
from datetime import timedelta

from src.common.schemas.riot_data_schemas import RiotGameID, LiveGameState
from src.db.database_service import DatabaseService
from src.riot_scraper.riot_api.schemas.get_live_window import WindowFrame
from src.riot_scraper.riot_api.riot_api_client import RiotApiClient
from src.riot_scraper.job_runner import JobRunner
from src.riot_scraper.timestamp_util import TimestampUtil

logger = logging.getLogger("scraper")


class RiotGameDataScraper:
    def __init__(
        self,
        database_service: DatabaseService,
        riot_api_requester: RiotApiClient,
        job_runner: JobRunner,
    ):
        self.db = database_service
        self.riot_api_requester = riot_api_requester
        self.job_runner = job_runner

    def scrape_game(self, game_id: RiotGameID):
        logger.debug(f"Starting for game id {game_id}")
        start_time = self.__get_game_start_time(game_id)
        assert start_time is not None

        end_time = None
        game_finished = False
        paused_timestamp = None
        unpause_timestamp = None
        pauses = []

        current_time = TimestampUtil.round_to_10_seconds(start_time)
        while not game_finished:
            current_window = self.riot_api_requester.get_game_window(game_id, current_time)
            assert current_window is not None

            paused_frame = get_paused_frame(current_window.frames)
            if paused_frame and not paused_timestamp:
                paused_timestamp = paused_frame.rfc460Timestamp
            if not paused_frame and paused_timestamp:
                unpause_timestamp = current_window.frames[0].rfc460Timestamp
            if paused_timestamp and unpause_timestamp:
                pauses.append((paused_timestamp, unpause_timestamp))
                paused_timestamp = None
                unpause_timestamp = None

            game_finished = any(
                frame.gameState == LiveGameState.FINISHED for frame in current_window.frames
            )
            if game_finished:
                end_time = current_window.frames[-1].rfc460Timestamp
            current_time = TimestampUtil.add_10_seconds(current_time)

        assert end_time is not None
        total_game_time = get_game_duration(start_time, end_time, pauses)

        minutes = total_game_time // 60
        seconds = total_game_time % 60
        logger.debug(f"Game minutes {minutes}")
        logger.debug(f"Game seconds {seconds}")

    def __get_game_start_time(self, game_id: RiotGameID) -> str | None:
        initial_start_window = self.riot_api_requester.get_game_window(game_id)
        if not initial_start_window:
            raise Exception
        start_window_time = TimestampUtil.round_to_10_seconds(
            initial_start_window.frames[0].rfc460Timestamp
        )
        start_window = self.riot_api_requester.get_game_window(game_id, start_window_time)
        assert start_window is not None

        start_time = None
        for frame in start_window.frames:
            if frame.blueTeam.totalGold != 0 or frame.redTeam.totalGold != 0:
                start_time = frame.rfc460Timestamp
        return start_time


def get_game_duration(start_time: str, end_time: str, pauses: list[tuple[str, str]]) -> int:
    start_dt = TimestampUtil.parse_rfc3339(start_time)
    end_dt = TimestampUtil.parse_rfc3339(end_time)

    total_pause = timedelta()
    for pause_start, pause_end in pauses:
        pause_start_dt = TimestampUtil.parse_rfc3339(pause_start)
        pause_end_dt = TimestampUtil.parse_rfc3339(pause_end)
        total_pause += pause_end_dt - pause_start_dt

    effective_duration = end_dt - start_dt - total_pause
    total_seconds = int(effective_duration.total_seconds())

    return total_seconds


def get_paused_frame(frames: list[WindowFrame]) -> WindowFrame | None:
    for frame in frames:
        if frame.gameState == LiveGameState.PAUSED:
            return frame
    return None
