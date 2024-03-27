import logging
from typing import List

from src.db import crud
from src.db.models import GameModel
from src.riot.util.riot_api_requester import RiotApiRequester
from src.riot.util.job_runner import JobRunner
from src.riot.exceptions.game_not_found_exception import GameNotFoundException
from src.common.schemas.search_parameters import GameSearchParameters
from src.common.schemas.riot_data_schemas import Game

logger = logging.getLogger('fantasy-lol')


class RiotGameService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()
        self.job_runner = JobRunner()

    def fetch_games_from_match_ids_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.fetch_games_from_match_ids_job,
            job_name="fetch games from match ids job",
            max_retries=3
        )

    def fetch_games_from_match_ids_job(self, batch_size: int = 25):
        match_ids = crud.get_match_ids_without_games()
        for i in range(0, len(match_ids), batch_size):
            batch = match_ids[i:i + batch_size]
            self.process_batch_match_ids(batch)

    def process_batch_match_ids(self, match_ids: List[str]):
        logger.debug(f"Processes batch of match ids: {match_ids}")
        all_fetched_games = []
        for match_id in match_ids:
            fetched_games = self.riot_api_requester.get_games_from_event_details(match_id)
            all_fetched_games = all_fetched_games + fetched_games
        crud.bulk_save_games(all_fetched_games)

    def update_game_states_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.update_game_states_job,
            job_name="update game states job",
            max_retries=3
        )

    def update_game_states_job(self):
        game_ids = crud.get_games_to_check_state()
        games = self.riot_api_requester.get_games(game_ids)
        for game in games:
            crud.update_game_state(game.id, game.state)

    @staticmethod
    def get_games(search_parameters: GameSearchParameters) -> List[Game]:
        filters = []
        if search_parameters.state is not None:
            filters.append(GameModel.state == search_parameters.state)
        if search_parameters.match_id is not None:
            filters.append(GameModel.match_id == search_parameters.match_id)
        game_orms = crud.get_games(filters)
        games = [Game.model_validate(game_orm) for game_orm in game_orms]
        return games

    @staticmethod
    def get_game_by_id(game_id: str) -> Game:
        game_orm = crud.get_game_by_id(game_id)
        if game_orm is None:
            raise GameNotFoundException()
        game = Game.model_validate(game_orm)
        return game
