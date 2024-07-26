from sqlalchemy import Column, Enum, Integer, String, PrimaryKeyConstraint, text
from sqlalchemy.ext.declarative import declarative_base

from ..common.schemas.riot_data_schemas import PlayerRole

Base = declarative_base()


class PlayerGameView(Base):  # type: ignore
    __tablename__ = "player_game_view"

    game_id = Column(String, primary_key=True)
    player_id = Column(String, primary_key=True)
    participant_id = Column(Integer)
    champion_id = Column(String)
    role = Column(Enum(PlayerRole), nullable=False)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    total_gold = Column(Integer)
    creep_score = Column(Integer)
    kill_participation = Column(Integer)
    champion_damage_share = Column(Integer)
    wards_placed = Column(Integer)
    wards_destroyed = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint('game_id', 'player_id'),
    )


player_game_view_query = text("""
    CREATE VIEW IF NOT EXISTS player_game_view AS
    SELECT
        m.game_id,
        m.player_id,
        m.participant_id,
        m.champion_id,
        m.role,
        s.kills,
        s.deaths,
        s.assists,
        s.total_gold,
        s.creep_score,
        s.kill_participation,
        s.champion_damage_share,
        s.wards_placed,
        s.wards_destroyed
    FROM
        player_game_metadata m
    JOIN
        player_game_stats s ON m.game_id = s.game_id AND m.participant_id = s.participant_id
""")
