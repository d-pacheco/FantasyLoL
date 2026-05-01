from sqlalchemy import Boolean, Column, Enum, Integer, String, PrimaryKeyConstraint, text
from sqlalchemy.ext.declarative import declarative_base

from src.common.schemas.riot_data_schemas import GameState, MatchState, PlayerRole

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

    __table_args__ = (PrimaryKeyConstraint("game_id", "player_id"),)


create_player_game_view_query = text("""
    CREATE OR REPLACE VIEW player_game_view AS
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


class MatchView(Base):  # type: ignore
    __tablename__ = "match_view"

    id = Column(String, primary_key=True)
    start_time = Column(String)
    block_name = Column(String)
    league_slug = Column(String)
    strategy_type = Column(String)
    strategy_count = Column(Integer)
    tournament_id = Column(String)
    team_1_name = Column(String)
    team_2_name = Column(String)
    has_games = Column(Boolean)
    state = Column(Enum(MatchState), nullable=False)
    team_1_wins = Column(Integer, nullable=True)
    team_2_wins = Column(Integer, nullable=True)
    winning_team = Column(String, nullable=True)


create_match_view_query = text("""
    CREATE OR REPLACE VIEW match_view AS
    SELECT
        m.id,
        m.start_time,
        m.block_name,
        l.slug AS league_slug,
        m.strategy_type,
        m.strategy_count,
        m.tournament_id,
        t1.team_name AS team_1_name,
        t2.team_name AS team_2_name,
        m.has_games,
        m.state,
        t1.game_wins AS team_1_wins,
        t2.game_wins AS team_2_wins,
        CASE
            WHEN t1.outcome = 'win' THEN t1.team_name
            WHEN t2.outcome = 'win' THEN t2.team_name
            ELSE NULL
        END AS winning_team
    FROM matches m
    JOIN leagues l ON m.league_id = l.id
    LEFT JOIN event_teams t1 ON m.id = t1.match_id AND t1.side = 1
    LEFT JOIN event_teams t2 ON m.id = t2.match_id AND t2.side = 2
""")


class GameView(Base):  # type: ignore
    __tablename__ = "game_view"

    id = Column(String, primary_key=True)
    state = Column(Enum(GameState), nullable=False)
    number = Column(Integer)
    red_team = Column(String)
    blue_team = Column(String)
    match_id = Column(String)
    has_game_data = Column(Boolean)
    last_stats_fetch = Column(Boolean)


create_game_view_query = text("""
    CREATE OR REPLACE VIEW game_view AS
    SELECT
        g.id,
        g.state,
        g.number,
        red.team_id AS red_team,
        blue.team_id AS blue_team,
        g.match_id,
        COALESCE(g.details_status != 'unavailable', TRUE) AS has_game_data,
        COALESCE(g.details_status = 'needs_final_fetch', FALSE) AS last_stats_fetch
    FROM games g
    LEFT JOIN game_teams red ON g.id = red.game_id AND red.side = 'red'
    LEFT JOIN game_teams blue ON g.id = blue.game_id AND blue.side = 'blue'
""")
