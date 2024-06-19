import logging
from typing import List

from ...common.schemas.search_parameters import GameSearchParameters
from ...common.schemas.riot_data_schemas import Game, RiotGameID, RiotMatchID

from ...db import crud
from ...db.models import GameModel

from ..util.riot_api_requester import RiotApiRequester
from ..util.job_runner import JobRunner
from ..exceptions.game_not_found_exception import GameNotFoundException

logger = logging.getLogger('fantasy-lol')


class RiotGameService:
    def __init__(
            self,
            api_requester: RiotApiRequester = RiotApiRequester(),
            job_runner: JobRunner = JobRunner()
    ):
        self.riot_api_requester = api_requester
        self.job_runner = job_runner

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

    def process_batch_match_ids(self, match_ids: List[RiotMatchID]):
        logger.debug(f"Processes batch of match ids: {match_ids}")
        all_fetched_games: List[Game] = []
        for match_id in match_ids:
            fetched_games = self.riot_api_requester.get_games_from_event_details(match_id)
            if len(fetched_games) == 0:
                crud.update_match_has_games(match_id, False)
                logger.info(f"Match with ID {match_id} does not have any game data available")
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
        games = crud.get_games(filters)
        return games

    @staticmethod
    def get_game_by_id(game_id: RiotGameID) -> Game:
        game = crud.get_game_by_id(game_id)
        if game is None:
            raise GameNotFoundException()
        return game
