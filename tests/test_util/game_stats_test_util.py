import random

from fantasylol.db.models import PlayerGameMetadata, PlayerGameStats
from fantasylol.db.database import DatabaseConnection
from fantasylol.schemas.player_role import PlayerRole


class GameStatsTestUtil:
    @staticmethod
    def create_player_metadata(game_id: int, participant_id: int):
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
        player_metadata = PlayerGameMetadata(**player_metadata_attr)
        with DatabaseConnection() as db:
            db.add(player_metadata)
            db.commit()

    @staticmethod
    def create_player_stats(game_id: int, participant_id: int):
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
        player_stats = PlayerGameStats(**player_stats_attr)
        with DatabaseConnection() as db:
            db.add(player_stats)
            db.commit()
