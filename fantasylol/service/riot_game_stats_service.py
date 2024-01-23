from datetime import datetime, timezone, timedelta
import logging
from typing import List

from fantasylol.db import crud
from fantasylol.db.views import PlayerGameView
from fantasylol.schemas.search_parameters import PlayerGameStatsSearchParameters
from fantasylol.schemas.riot_data_schemas import PlayerGameData
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.util.job_runner import JobRunner

logger = logging.getLogger('fantasy-lol')


def round_current_time_to_10_seconds() -> str:
    current_time = datetime.now(timezone.utc)
    time_60_seconds_ago = current_time - timedelta(minutes=1)
    rounded_seconds = round(time_60_seconds_ago.second // 10) * 10
    rounded_time = time_60_seconds_ago.replace(second=rounded_seconds, microsecond=0)
    formatted_time = rounded_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return formatted_time


class RiotGameStatsService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()
        self.job_runner = JobRunner()

    def run_player_metadata_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.run_player_metadata_job,
            job_name="player metadata job",
            max_retries=3
        )

    def run_player_metadata_job(self):
        game_ids = crud.get_game_ids_without_player_metadata()
        for game_id in game_ids:
            self.fetch_and_store_player_metadata_for_game(game_id)

    def fetch_and_store_player_metadata_for_game(self, game_id: str):
        logger.info(f"Fetching player metadata for game with id: {game_id}")
        time_stamp = round_current_time_to_10_seconds()
        try:
            fetched_player_metadata = self.riot_api_requester.get_player_metadata_for_game(
                game_id, time_stamp)
            if len(fetched_player_metadata) == 0:
                logger.info(f"Game id {game_id} has no player metadata available")
                crud.update_has_game_data(game_id, False)

            for player_metadata in fetched_player_metadata:
                crud.save_player_metadata(player_metadata)
        except Exception as e:
            logger.error(f"{str(e)}")
            raise e

    def run_player_stats_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.run_player_stats_job,
            job_name="player stats job",
            max_retries=3
        )

    def run_player_stats_job(self):
        game_ids = crud.get_game_ids_to_fetch_player_stats_for()
        for game_id in game_ids:
            self.fetch_and_store_player_stats_for_game(game_id)

    def fetch_and_store_player_stats_for_game(self, game_id: str):
        logger.info(f"Fetching player stats for game with id: {game_id}")
        time_stamp = round_current_time_to_10_seconds()
        try:
            fetched_player_stats = self.riot_api_requester.get_player_stats_for_game(
                game_id, time_stamp)

            if len(fetched_player_stats) == 0:
                logger.info(f"Game id {game_id} has no player stats available")
                crud.update_has_game_data(game_id, False)

            for player_stats in fetched_player_stats:
                crud.save_player_stats(player_stats)
        except Exception as e:
            logger.error(f"{str(e)}")
            raise e

    @staticmethod
    def get_player_stats(search_parameters: PlayerGameStatsSearchParameters) \
            -> List[PlayerGameData]:
        filters = []
        if search_parameters.game_id is not None:
            filters.append(PlayerGameView.game_id == search_parameters.game_id)
        if search_parameters.player_id is not None:
            filters.append(PlayerGameView.player_id == search_parameters.player_id)
        player_game_stats_orms = crud.get_player_game_stats(filters)
        player_game_stats = [PlayerGameData.model_validate(game_stats_orm)
                             for game_stats_orm in player_game_stats_orms]
        sorted_player_game_stats = sorted(player_game_stats,
                                          key=lambda x: (x.game_id, x.participant_id))
        return sorted_player_game_stats
