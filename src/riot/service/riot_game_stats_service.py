from datetime import datetime, timezone, timedelta
import logging
from typing import List

from src.common.schemas.search_parameters import PlayerGameStatsSearchParameters
from src.common.schemas.riot_data_schemas import PlayerGameData, RiotGameID

from src.db.database_service import DatabaseService
from src.db.views import PlayerGameView

from src.riot.util import RiotApiRequester
from src.riot.job_runner import JobRunner

logger = logging.getLogger('riot')


def round_current_time_to_10_seconds() -> str:
    current_time = datetime.now(timezone.utc)
    time_60_seconds_ago = current_time - timedelta(minutes=1)
    rounded_seconds = round(time_60_seconds_ago.second // 10) * 10
    rounded_time = time_60_seconds_ago.replace(second=rounded_seconds, microsecond=0)
    formatted_time = rounded_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return formatted_time


class RiotGameStatsService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
        self.riot_api_requester = RiotApiRequester()
        self.job_runner = JobRunner()

    def run_player_metadata_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.run_player_metadata_job,
            job_name="player metadata job",
            max_retries=3
        )

    def run_player_metadata_job(self):
        game_ids = self.db.get_game_ids_without_player_metadata()
        logger.info(f"Fetching player metadata for {len(game_ids)} games.")
        for game_id in game_ids:
            self.fetch_and_store_player_metadata_for_game(game_id)

    def fetch_and_store_player_metadata_for_game(self, game_id: RiotGameID):
        logger.debug(f"Fetching player metadata for game with id: {game_id}")
        time_stamp = round_current_time_to_10_seconds()
        try:
            fetched_player_metadata = self.riot_api_requester.get_player_metadata_for_game(
                game_id, time_stamp)
            if len(fetched_player_metadata) == 0:
                logger.debug(f"Game id {game_id} has no player metadata available")
                self.db.update_has_game_data(game_id, False)

            for player_metadata in fetched_player_metadata:
                self.db.put_player_metadata(player_metadata)
        except Exception as e:
            logger.error(f"Error getting player metadata for game with id {game_id}: {str(e)}")
            raise e

    def run_player_stats_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.run_player_stats_job,
            job_name="player stats job",
            max_retries=3
        )

    def run_player_stats_job(self):
        game_ids = self.db.get_game_ids_to_fetch_player_stats_for()
        logger.info(f"Fetching player stats for {len(game_ids)} games.")
        for game_id in game_ids:
            self.fetch_and_store_player_stats_for_game(game_id, False)

        last_fetch_games = self.db.get_games_with_last_stats_fetch(True)
        logger.info(f"Last fetch of player stats for {len(last_fetch_games)} games.")
        for game in last_fetch_games:
            self.fetch_and_store_player_stats_for_game(game.id, True)

    def fetch_and_store_player_stats_for_game(self, game_id: RiotGameID, last_fetch: bool):
        logger.debug(f"Fetching player stats for game with id: {game_id}")
        time_stamp = round_current_time_to_10_seconds()
        try:
            fetched_player_stats = self.riot_api_requester.get_player_stats_for_game(
                game_id, time_stamp)

            if len(fetched_player_stats) == 0:
                logger.debug(f"Game id {game_id} has no player stats available")
                self.db.update_has_game_data(game_id, False)

            for player_stats in fetched_player_stats:
                self.db.put_player_stats(player_stats)

            if last_fetch:
                logger.debug(f"Setting last fetch to false for game with id: {game_id}")
                self.db.update_game_last_stats_fetch(game_id, False)
        except Exception as e:
            logger.error(f"Error getting player stats for game with id {game_id}: {str(e)}")
            raise e

    def get_player_stats(self, search_parameters: PlayerGameStatsSearchParameters) \
            -> List[PlayerGameData]:
        filters = []
        if search_parameters.game_id is not None:
            filters.append(PlayerGameView.game_id == search_parameters.game_id)
        if search_parameters.player_id is not None:
            filters.append(PlayerGameView.player_id == search_parameters.player_id)
        player_game_stats = self.db.get_player_game_stats(filters)
        sorted_player_game_stats = sorted(player_game_stats,
                                          key=lambda x: (x.game_id, x.participant_id))
        return sorted_player_game_stats
