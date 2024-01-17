from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from fantasylol.schemas.game_state import GameState
from fantasylol.schemas.player_role import PlayerRole


Base = declarative_base()


class LeagueModel(Base):
    __tablename__ = "leagues"

    id = Column(String, primary_key=True, index=True)
    slug = Column(String)
    name = Column(String)
    region = Column(String)
    image = Column(String)
    priority = Column(Integer)


class TournamentModel(Base):
    __tablename__ = "tournaments"

    id = Column(String, primary_key=True, index=True)
    slug = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    league_id = Column(String, ForeignKey("leagues.id"))


class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, index=True)
    start_time = Column(String)
    block_name = Column(String)
    league_slug = Column(String)
    strategy_type = Column(String)
    strategy_count = Column(Integer)
    tournament_id = Column(String)
    team_1_name = Column(String)
    team_2_name = Column(String)


class GameModel(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True, index=True)
    state = Column(Enum(GameState), nullable=False)
    number = Column(Integer)
    match_id = Column(String, ForeignKey("matches.id"))
    has_game_data = Column(Boolean, default=True)


class ProfessionalTeamModel(Base):
    __tablename__ = "professional_teams"

    id = Column(String, primary_key=True, index=True)
    slug = Column(String)
    name = Column(String)
    code = Column(String)
    image = Column(String)
    alternative_image = Column(String)
    background_image = Column(String)
    status = Column(String)
    home_league = Column(String)


class ProfessionalPlayerModel(Base):
    __tablename__ = "professional_players"

    id = Column(String, primary_key=True)
    team_id = Column(String, ForeignKey("professional_teams.id"), primary_key=True)
    summoner_name = Column(String)
    image = Column(String)
    role = Column(Enum(PlayerRole), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'team_id'),
    )


class PlayerGameMetadata(Base):
    __tablename__ = "player_game_metadata"

    game_id = Column(String, primary_key=True)
    player_id = Column(String, ForeignKey("professional_players.id"), primary_key=True)
    participant_id = Column(Integer)
    champion_id = Column(String)
    role = Column(Enum(PlayerRole), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('game_id', 'player_id'),
    )


class PlayerGameStats(Base):
    __tablename__ = "player_game_stats"

    game_id = Column(String, primary_key=True)
    participant_id = Column(String, primary_key=True)
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
        PrimaryKeyConstraint('game_id', 'participant_id'),
    )


class Schedule(Base):
    __tablename__ = "schedule"

    schedule_name = Column(String, primary_key=True)
    older_token_key = Column(String)
    current_token_key = Column(String)
