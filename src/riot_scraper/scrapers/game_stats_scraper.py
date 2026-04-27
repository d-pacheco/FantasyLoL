import logging

from src.common.schemas.riot_data_schemas import (
    RiotGameID,
    PlayerGameMetadata,
    ProPlayerID,
    TeamGameStats,
    ProTeamID,
    PlayerGameStats,
)
from src.db.database_service import DatabaseService
from src.riot_scraper.riot_api.schemas.get_live_window import TeamMetaData, TeamWindowFrame
from src.riot_scraper.riot_api.riot_api_client import RiotApiClient
from src.riot_scraper.job_runner import JobRunner
from src.riot_scraper.timestamp_util import TimestampUtil

logger = logging.getLogger("scraper")


class RiotGameStatsScraper:
    def __init__(
        self,
        database_service: DatabaseService,
        riot_api_requester: RiotApiClient,
        job_runner: JobRunner,
    ):
        self.db = database_service
        self.riot_api_requester = riot_api_requester
        self.job_runner = job_runner

    def run_player_metadata_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.run_player_metadata_job, job_name="player metadata job", max_retries=3
        )

    def run_player_metadata_job(self) -> None:
        game_ids = self.db.get_game_ids_without_player_metadata()
        logger.info(f"Fetching player metadata for {len(game_ids)} games.")
        for game_id in game_ids:
            self.fetch_and_store_player_metadata_for_game(game_id)

    def fetch_and_store_player_metadata_for_game(self, game_id: RiotGameID) -> None:
        logger.info(f"Fetching player metadata for game with id: {game_id}")
        time_stamp = TimestampUtil.round_current_time_to_10_seconds()
        try:
            window_response = self.riot_api_requester.get_game_window(game_id, time_stamp)
            if not window_response:
                logger.info(f"Game id {game_id} has no player metadata available")
                self.db.update_has_game_data(game_id, False)
                return

            blue_team_player_metadata = parse_team_metadata(
                window_response.gameMetadata.blueTeamMetadata, game_id
            )
            red_team_player_metadata = parse_team_metadata(
                window_response.gameMetadata.redTeamMetadata, game_id
            )
            for player_metadata in blue_team_player_metadata + red_team_player_metadata:
                self.db.put_player_metadata(player_metadata)
        except Exception as e:
            logger.error(f"Error getting player metadata for game with id {game_id}: {str(e)}")
            raise e

    def run_player_stats_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.run_player_stats_job, job_name="player stats job", max_retries=3
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
        logger.info(f"Fetching player stats for game with id: {game_id}")
        time_stamp = TimestampUtil.round_current_time_to_10_seconds()
        try:
            fetched_player_stats = self.__fetch_player_stats(game_id, time_stamp)
            if len(fetched_player_stats) == 0:
                logger.info(f"Game id {game_id} has no player stats available")
                self.db.update_has_game_data(game_id, False)
            for player_stats in fetched_player_stats:
                self.db.put_player_stats(player_stats)

            fetched_team_stats = self.__fetch_team_stats(game_id, time_stamp)
            for team_stats in fetched_team_stats:
                self.db.put_team_stats(team_stats)

            if last_fetch:
                logger.info(f"Setting last fetch to false for game with id: {game_id}")
                self.db.update_game_last_stats_fetch(game_id, False)
        except Exception as e:
            logger.error(f"Error getting player stats for game with id {game_id}: {str(e)}")
            raise e

    def __fetch_player_stats(self, game_id: RiotGameID, time_stamp: str) -> list[PlayerGameStats]:
        details_response = self.riot_api_requester.get_game_details(game_id, time_stamp)
        if not details_response:
            return []
        if len(details_response.frames) == 0:
            logger.error(
                f"No detail frames fetched for game id {game_id} with time stamp {time_stamp}"
            )
            return []

        player_stats = []
        last_frame = details_response.frames[len(details_response.frames) - 1]
        for participant in last_frame.participants:
            new_player_stats = PlayerGameStats(
                game_id=game_id,
                participant_id=participant.participantId,
                kills=participant.kills,
                deaths=participant.deaths,
                assists=participant.assists,
                total_gold=participant.totalGoldEarned,
                creep_score=participant.creepScore,
                kill_participation=round(participant.killParticipation * 100),
                champion_damage_share=round(participant.championDamageShare * 100),
                wards_placed=participant.wardsPlaced,
                wards_destroyed=participant.wardsDestroyed,
            )
            player_stats.append(new_player_stats)

        return player_stats

    def __fetch_team_stats(self, game_id: RiotGameID, time_stamp: str) -> list[TeamGameStats]:
        window_response = self.riot_api_requester.get_game_window(game_id, time_stamp)
        if not window_response:
            return []
        if len(window_response.frames) == 0:
            logger.error(
                f"No window frames fetched for game id {game_id} with time stamp {time_stamp}"
            )
            return []

        last_frame = window_response.frames[len(window_response.frames) - 1]
        blue_team_stats = get_team_stats_from_frame(
            game_id,
            window_response.gameMetadata.blueTeamMetadata.esportsTeamId,
            last_frame.blueTeam,
        )
        red_team_stats = get_team_stats_from_frame(
            game_id,
            window_response.gameMetadata.blueTeamMetadata.esportsTeamId,
            last_frame.blueTeam,
        )

        return [blue_team_stats, red_team_stats]


def parse_team_metadata(
    team_metadata: TeamMetaData, game_id: RiotGameID
) -> list[PlayerGameMetadata]:
    player_metadata_for_team = []
    for participant in team_metadata.participantMetadata:
        player_id = (
            participant.esportsPlayerId
            if participant.esportsPlayerId
            else ProPlayerID(str(participant.participantId))
        )
        new_player_metadata = PlayerGameMetadata(
            game_id=game_id,
            participant_id=participant.participantId,
            champion_id=participant.championId,
            role=participant.role,
            player_id=player_id,  # Weird edge case where it doesn't exist for some games
        )
        player_metadata_for_team.append(new_player_metadata)
    return player_metadata_for_team


def get_team_stats_from_frame(
    game_id: RiotGameID, team_id: ProTeamID, team_frame: TeamWindowFrame
) -> TeamGameStats:
    return TeamGameStats(
        game_id=game_id,
        team_id=team_id,
        total_gold=team_frame.totalGold,
        inhibitors=team_frame.inhibitors,
        towers=team_frame.towers,
        barons=team_frame.barons,
        total_kills=team_frame.totalKills,
    )
