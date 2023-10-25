from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from db.database import Base

# Riot Data models:

class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String)
    name = Column(String)
    region = Column(String)
    image = Column(String)
    priority = Column(Integer)

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    league_id = Column(Integer, ForeignKey("leagues.id"))

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(String)
    block_name = Column(String)
    strategy_type = Column(String)
    strategy_count = Column(Integer)
    state = Column(String)
    number = Column(Integer)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    team_1_id = Column(Integer)
    team_2_id = Column(Integer)

class ProfessionalTeam(Base):
    __tablename__ = "professional_teams"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String)
    name = Column(String)
    code = Column(String)
    image = Column(String)
    alternative_image = Column(String)
    background_image = Column(String)
    status = Column(String)
    home_league = Column(String)

class ProfessionalPlayer(Base):
    __tablename__ = "professional_players"

    id = Column(Integer, primary_key=True, index=True)
    esports_id = Column(Integer)
    summoner_name = Column(String)
    image = Column(String)
    role = Column(String)
    team_id = Column(Integer, ForeignKey("professional_teams.id"))

class PlayerGameMetadata(Base):
    __tablename__ = "player_game_metadata"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer, ForeignKey("professional_players.id"))
    participant_id = Column(Integer)
    champion_id = Column(String)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    creep_score = Column(Integer)
