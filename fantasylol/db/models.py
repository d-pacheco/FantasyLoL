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

# Riot Data models:


class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String)
    name = Column(String)
    region = Column(String)
    image = Column(String)
    priority = Column(Integer)

    def __eq__(self, other):
        if not isinstance(other, League):
            return False
        return (
            self.id == other.id and
            self.slug == other.slug and
            self.name == other.name and
            self.region == other.region and
            self.image == other.image and
            self.priority == other.priority
        )

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "region": self.region,
            "image": self.image,
            "priority": self.priority
        }


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

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "league_id": self.league_id
        }


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(String)
    block_name = Column(String)
    league_name = Column(String)
    strategy_type = Column(String)
    strategy_count = Column(Integer)
    tournament_id = Column(Integer)
    team_1_name = Column(String)
    team_2_name = Column(String)

    def __eq__(self, other):
        if not isinstance(other, Match):
            return False
        return (
            self.id == other.id and
            self.start_time == other.start_time and
            self.block_name == other.block_name and
            self.league_name == other.league_name and
            self.strategy_type == other.strategy_type and
            self.strategy_count == other.strategy_count and
            self.tournament_id == other.tournament_id and
            self.team_1_name == other.team_1_name and
            self.team_2_name == other.team_2_name
        )

    def to_dict(self):
        return {
            "id": self.id,
            "start_time": self.start_time,
            "block_name": self.block_name,
            "league_name": self.league_name,
            "strategy_type": self.strategy_type,
            "strategy_count": self.strategy_count,
            "tournament_id": self.tournament_id,
            "team_1_name": self.team_1_name,
            "team_2_name": self.team_2_name
        }


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(Enum(GameState), nullable=False)
    number = Column(Integer)
    match_id = Column(Integer, ForeignKey("matches.id"))
    has_game_data = Column(Boolean, default=True)

    def __eq__(self, other):
        if not isinstance(other, Game):
            return False
        return (
            self.id == other.id and
            self.state == other.state and
            self.number == other.number and
            self.match_id == other.match_id
        )

    def to_dict(self):
        return {
            "id": self.id,
            "state": self.state,
            "number": self.number,
            "match_id": self.match_id,
        }


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

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "code": self.code,
            "image": self.image,
            "alternative_image": self.alternative_image,
            "background_image": self.background_image,
            "status": self.status,
            "home_league": self.home_league
        }


class ProfessionalPlayer(Base):
    __tablename__ = "professional_players"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("professional_teams.id"), primary_key=True)
    summoner_name = Column(String)
    image = Column(String)
    role = Column(Enum(PlayerRole), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'team_id'),
    )

    def __eq__(self, other):
        if not isinstance(other, ProfessionalPlayer):
            return False
        return (
            self.id == other.id and
            self.summoner_name == other.summoner_name and
            self.image == other.image and
            self.role == other.role and
            self.team_id == other.team_id
        )

    def to_dict(self):
        return {
            "id": self.id,
            "summoner_name": self.summoner_name,
            "image": self.image,
            "role": self.role,
            "team_id": self.team_id
        }


class PlayerGameMetadata(Base):
    __tablename__ = "player_game_metadata"

    game_id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("professional_players.id"), primary_key=True)
    participant_id = Column(Integer)
    champion_id = Column(String)
    role = Column(Enum(PlayerRole), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('game_id', 'player_id'),
    )

    def __eq__(self, other):
        if not isinstance(other, ProfessionalPlayer):
            return False
        return (
            self.game_id == other.game_id and
            self.player_id == other.player_id and
            self.participant_id == other.participant_id and
            self.champion_id == other.champion_id and
            self.role == other.role
        )

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "player_id": self.player_id,
            "participant_id": self.participant_id,
            "champion_id": self.champion_id,
            "role": self.role
        }


class PlayerGameStats(Base):
    __tablename__ = "player_game_stats"

    game_id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, primary_key=True)
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

    def __eq__(self, other):
        if not isinstance(other, ProfessionalPlayer):
            return False
        return (
            self.game_id == other.game_id and
            self.participant_id == other.participant_id and
            self.kills == other.kills and
            self.deaths == other.deaths and
            self.assists == other.assists and
            self.total_gold == other.total_gold and
            self.creep_score == other.creep_score and
            self.kill_participation == other.kill_participation and
            self.champion_damage_share == other.champion_damage_share and
            self.wards_placed == other.wards_placed and
            self.wards_destroyed == other.wards_destroyed
        )

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "participant_id": self.participant_id,
            "kills": self.kills,
            "deaths": self.deaths,
            "assists": self.assists,
            "total_gold": self.total_gold,
            "creep_score": self.creep_score,
            "kill_participation": self.kill_participation,
            "champion_damage_share": self.champion_damage_share,
            "wards_placed": self.wards_placed,
            "wards_destroyed": self.wards_destroyed,
        }


class Schedule(Base):
    __tablename__ = "schedule"

    schedule_name = Column(String, primary_key=True)
    older_token_key = Column(String)
    current_token_key = Column(String)
