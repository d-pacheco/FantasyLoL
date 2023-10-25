from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from .database import Base

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

    def __eq__(self, other):
        if not isinstance(other, Tournament):
            return False
        return (
                self.id == other.id and
                self.slug == other.slug and
                self.start_date == other.start_date and
                self.end_date == other.end_date and
                self.league_id == other.league_id
            )

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

    def __eq__(self, other):
        if not isinstance(other, Game):
            return False
        return (
            self.id == other.id and
            self.start_time == other.start_time and
            self.block_name == other.block_name and
            self.strategy_type == other.strategy_type and
            self.strategy_count == other.strategy_count and
            self.state == other.state and
            self.number == other.number and
            self.tournament_id == other.tournament_id and
            self.team_1_id == other.team_1_id and
            self.team_2_id == other.team_2_id
        )

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

    def __eq__(self, other):
        if not isinstance(other, ProfessionalTeam):
            return False
        return (
            self.id == other.id and
            self.slug == other.slug and
            self.name == other.name and
            self.code == other.code and
            self.image == other.image and
            self.alternative_image == other.alternative_image and
            self.background_image == other.background_image and
            self.status == other.status and
            self.home_league == other.home_league
        )

class ProfessionalPlayer(Base):
    __tablename__ = "professional_players"

    id = Column(Integer, primary_key=True, index=True)
    esports_id = Column(Integer)
    summoner_name = Column(String)
    image = Column(String)
    role = Column(String)
    team_id = Column(Integer, ForeignKey("professional_teams.id"))

    def __eq__(self, other):
        if not isinstance(other, ProfessionalPlayer):
            return False
        return (
            self.id == other.id and
            self.esports_id == other.esports_id and
            self.summoner_name == other.summoner_name and
            self.image == other.image and
            self.role == other.role and
            self.team_id == other.team_id
        )

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

    def __eq__(self, other):
        if not isinstance(other, PlayerGameMetadata):
            return False
        return (
            self.id == other.id and
            self.game_id == other.game_id and
            self.player_id == other.player_id and
            self.participant_id == other.participant_id and
            self.champion_id == other.champion_id and
            self.kills == other.kills and
            self.deaths == other.deaths and
            self.assists == other.assists and
            self.creep_score == other.creep_score
        )
