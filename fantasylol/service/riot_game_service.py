import logging
from typing import List

from fantasylol.db import crud
from fantasylol.db.models import Game
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.exceptions.game_not_found_exception import GameNotFoundException
from fantasylol.exceptions.fantasy_lol_exception import FantasyLolException
from fantasylol.schemas.search_parameters import GameSearchParameters

logger = logging.getLogger('fantasy-lol')


class RiotGameService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_games_from_match_ids(self, batch_size: int = 25):
        max_retries = 3
        retry_count = 0
        error = None
        job_completed = False

        logger.info("Starting fetch games from match ids job")
        while retry_count <= max_retries and not job_completed:
            try:
                match_ids = crud.get_matches_ids_without_games()

                for i in range(0, len(match_ids), batch_size):
                    batch = match_ids[i:i + batch_size]
                    self.process_batch_match_ids(batch)

                job_completed = True
            except FantasyLolException as e:
                retry_count += 1
                error = e
                logger.warning(f"An error occurred during fetch games from match ids job."
                               f" Retry attempt: {retry_count}")
        if job_completed:
            logger.info("Fetch games from match ids job completed")
        else:
            logger.error(f"Fetch games from match ids job failed: {error}")

    def process_batch_match_ids(self, match_ids: List[int]):
        logger.info(f"Processes batch of match ids: {match_ids}")
        all_fetched_games = []
        for match_id in match_ids:
            fetched_games = self.riot_api_requester.get_games_from_event_details(match_id)
            all_fetched_games = all_fetched_games + fetched_games
        crud.bulk_save_games(all_fetched_games)

    @staticmethod
    def get_games(search_parameters: GameSearchParameters) -> List[Game]:
        filters = []
        if search_parameters.state is not None:
            filters.append(Game.state == search_parameters.state)
        if search_parameters.match_id is not None:
            filters.append(Game.match_id == search_parameters.match_id)

        games = crud.get_games(filters)
        return games

    @staticmethod
    def get_game_by_id(game_id: int) -> Game:
        game = crud.get_game_by_id(game_id)
        if game is None:
            raise GameNotFoundException()
        return game
