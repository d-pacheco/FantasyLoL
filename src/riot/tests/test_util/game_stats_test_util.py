import random

from src.db.models import PlayerGameMetadataModel, PlayerGameStatsModel
from src.db.database import DatabaseConnection
from src.common.schemas.riot_data_schemas import PlayerRole


class GameStatsTestUtil:
    @staticmethod
    def create_player_metadata(game_id: str, participant_id: int):
        if participant_id % 5 == 1:
            role = PlayerRole.TOP
        elif participant_id % 5 == 2:
            role = PlayerRole.JUNGLE
        elif participant_id % 5 == 3:
            role = PlayerRole.MID
        elif participant_id % 5 == 4:
            role = PlayerRole.BOTTOM
        else:
            role = PlayerRole.SUPPORT

        player_metadata_attr = {
            "game_id": game_id,
            "player_id": random.randint(1, 9999999),
            "participant_id": participant_id,
            "champion_id": "championId",
            "role": role
        }
        player_metadata = PlayerGameMetadataModel(**player_metadata_attr)
        with DatabaseConnection() as db:
            db.add(player_metadata)
            db.commit()

    @staticmethod
    def create_player_stats(game_id: str, participant_id: int):
        player_stats_attr = {
            "game_id": game_id,
            "participant_id": participant_id,
            "kills": 1,
            "deaths": 1,
            "assists": 1,
            "total_gold": 10000,
            "creep_score": 100,
            "kill_participation": 0.5,
            "champion_damage_share": 0.2,
            "wards_placed": 10,
            "wards_destroyed": 10
        }
        player_stats = PlayerGameStatsModel(**player_stats_attr)
        with DatabaseConnection() as db:
            db.add(player_stats)
            db.commit()
