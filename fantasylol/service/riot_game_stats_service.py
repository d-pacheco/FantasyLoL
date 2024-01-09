from datetime import datetime, timezone, timedelta
import logging

from fantasylol.db import crud
from fantasylol.db.models import PlayerGameMetadata
from fantasylol.db.models import PlayerGameStats
from fantasylol.util.riot_api_requester import RiotApiRequester

logger = logging.getLogger('fantasy-lol')


def round_current_time_to_10_seconds() -> str:
    current_time = datetime.now(timezone.utc)
    time_60_seconds_ago = current_time - timedelta(minutes=2)
    rounded_seconds = (time_60_seconds_ago.second // 10) * 10
    rounded_time = time_60_seconds_ago.replace(second=rounded_seconds, microsecond=0)
    formatted_time = rounded_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return formatted_time


def save_player_metadata_for_team(team_metadata: dict, game_id: int):
    participant_metadata = team_metadata.get("participantMetadata", [])
    for participant in participant_metadata:
        player_metadata_attr = {
            "game_id": game_id,
            "player_id": int(participant['esportsPlayerId']),
            "participant_id": participant['participantId'],
            "champion_id": participant['championId'],
            "role": participant['role']
        }
        player_metadata_model = PlayerGameMetadata(**player_metadata_attr)
        crud.save_player_metadata(player_metadata_model)


class RiotGameStatsService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_player_metadata_for_game(self, game_id: int):
        logger.info(f"Fetching player metadata for game with id: {game_id}")
        time_stamp = round_current_time_to_10_seconds()
        request_url = (
            "https://feed.lolesports.com"
            f"/livestats/v1/window/{game_id}?hl=en-GB&startingTime={time_stamp}"
        )
        try:
            res_json = self.riot_api_requester.make_request(request_url)
            game_metadata = res_json.get("gameMetadata", {})
            blue_team_metadata = game_metadata.get("blueTeamMetadata", {})
            red_team_metadata = game_metadata.get("redTeamMetadata", {})
            save_player_metadata_for_team(blue_team_metadata, game_id)
            save_player_metadata_for_team(red_team_metadata, game_id)
        except Exception as e:
            logger.error(f"{str(e)}")
            raise e

    def fetch_and_store_player_stats_for_game(self, game_id: int):
        logger.info(f"Fetching player stats for game with id: {game_id}")
        time_stamp = round_current_time_to_10_seconds()
        request_url = (
            "https://feed.lolesports.com"
            f"/livestats/v1/details/{game_id}?hl=en-GB&startingTime={time_stamp}"
        )
        try:
            res_json = self.riot_api_requester.make_request(request_url)
            frames = res_json.get("frames", [])
            if len(frames) < 1:
                logger.error(
                    f"No frames fetched for game id {game_id} with time stamp {time_stamp}"
                )
                return
            last_frame = frames[len(frames)-1]
            participants = last_frame.get("participants", [])
            for participant in participants:
                player_stats_attr = {
                    "game_id": game_id,
                    "participant_id": participant['participantId'],
                    "kills": participant['kills'],
                    "deaths": participant['deaths'],
                    "assists": participant['assists'],
                    "total_gold": participant['totalGoldEarned'],
                    "creep_score": participant['creepScore'],
                    "kill_participation": participant['killParticipation'],
                    "champion_damage_share": participant['championDamageShare'],
                    "wards_placed": participant['wardsPlaced'],
                    "wards_destroyed": participant['wardsDestroyed']
                }
                player_stats_model = PlayerGameStats(**player_stats_attr)
                crud.save_player_stats(player_stats_model)
        except Exception as e:
            logger.error(f"{str(e)}")
            raise e
