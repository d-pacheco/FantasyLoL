import logging

from src.common.schemas.riot_data_schemas import Game, GameState, RiotMatchID, ProTeamID
from src.db.database_service import DatabaseService
from src.riot_scraper.riot_api.riot_api_client import RiotApiClient
from src.riot_scraper.job_runner import JobRunner

logger = logging.getLogger('riot')


class RiotGameScraper:
    def __init__(
            self,
            database_service: DatabaseService,
            api_requester: RiotApiClient,
            job_runner: JobRunner,
    ):
        self.db = database_service
        self.riot_api_requester = api_requester
        self.job_runner = job_runner

    def fetch_games_from_match_ids_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.fetch_games_from_match_ids_job,
            job_name="fetch games from match ids job",
            max_retries=3
        )

    def fetch_games_from_match_ids_job(self, batch_size: int = 25):
        match_ids = self.db.get_match_ids_without_games()
        for i in range(0, len(match_ids), batch_size):
            batch = match_ids[i:i + batch_size]
            self.process_batch_match_ids(batch)

    def process_batch_match_ids(self, match_ids: list[RiotMatchID]):
        logger.info(f"Processes batch of match ids: {match_ids}")
        all_fetched_games: list[Game] = []
        for match_id in match_ids:
            get_event_details_response = self.riot_api_requester.get_event_details(match_id)
            if not get_event_details_response:
                self.db.update_match_has_games(match_id, False)
                logger.info(f"Match with ID {match_id} does not have any game data available")
                continue

            for game in get_event_details_response.data.event.match.games:
                teams = game.teams
                red_team_id = teams[0].id if teams[0].side == "red" else teams[1].id
                blue_team_id = teams[0].id if teams[0].side == "blue" else teams[1].id

                new_game = Game(
                    id=game.id,
                    state=GameState(game.state),
                    red_team=ProTeamID(red_team_id),
                    blue_team=ProTeamID(blue_team_id),
                    match_id=match_id
                )
                all_fetched_games.append(new_game)
        self.db.bulk_save_games(all_fetched_games)

    def update_game_states_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.update_game_states_job,
            job_name="update game states job",
            max_retries=3
        )

    def update_game_states_job(self):
        game_ids = self.db.get_games_to_check_state()

        batch_size = 10
        game_id_batches = [game_ids[i:i + batch_size] for i in range(0, len(game_ids), batch_size)]

        for batch in game_id_batches:
            get_games_response = self.riot_api_requester.get_games(batch)
            for game in get_games_response.data.games:
                self.db.update_game_state(game.id, game.state)
                if game.state == GameState.COMPLETED:
                    self.db.update_game_last_stats_fetch(game.id, True)
