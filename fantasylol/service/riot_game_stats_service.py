from datetime import datetime, timezone, timedelta
import logging
import time

from fantasylol.db import crud
from fantasylol.exceptions.fantasy_lol_exception import FantasyLolException
from fantasylol.util.riot_api_requester import RiotApiRequester

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

    def run_player_metadata_job(self):
        max_retries = 3
        retry_count = 0
        error = None
        job_completed = False

        logger.info("Starting player metadata job")

        while retry_count <= max_retries and not job_completed:
            try:
                game_ids = crud.get_game_ids_without_player_metadata()
                for game_id in game_ids:
                    self.fetch_and_store_player_metadata_for_game(game_id)
                job_completed = True
            except FantasyLolException as e:
                retry_count += 1
                error = e
                logger.warning(f"An error occurred during player metadata job."
                               f" Retry attempt: {retry_count}")
                time.sleep(10)
        if job_completed:
            logger.info("Player metadata job completed")
        else:
            logger.error(f"Player metadata job failed with error: {error}")

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

    def run_player_stats_job(self):
        max_retries = 3
        retry_count = 0
        error = None
        job_completed = False

        logger.info("Starting player stats job")

        while retry_count <= max_retries and not job_completed:
            try:
                game_ids = crud.get_game_ids_to_fetch_player_stats_for()
                for game_id in game_ids:
                    self.fetch_and_store_player_stats_for_game(game_id)
                job_completed = True
            except FantasyLolException as e:
                retry_count += 1
                error = e
                logger.warning(f"An error occurred during player stats job."
                               f" Retry attempt: {retry_count}")
                time.sleep(10)
        if job_completed:
            logger.info("Player stats job completed")
        else:
            logger.error(f"Player stats job failed with error: {error}")

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
