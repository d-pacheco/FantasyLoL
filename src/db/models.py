from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    PrimaryKeyConstraint,
    String
)
from sqlalchemy.ext.declarative import declarative_base
import uuid

from src.common.schemas.riot_data_schemas import GameState, PlayerRole
from src.common.schemas.fantasy_schemas import (
    FantasyLeagueStatus,
    FantasyLeagueMembershipStatus,
    UserAccountStatus
)


Base = declarative_base()


# --------------------------------------------------
# ---------------- Riot Data Models ----------------
# --------------------------------------------------
class LeagueModel(Base):  # type: ignore
    __tablename__ = "leagues"

    id = Column(String, primary_key=True, index=True)
    slug = Column(String)
    name = Column(String)
    region = Column(String)
    image = Column(String)
    priority = Column(Integer)
    fantasy_available = Column(Boolean)


class TournamentModel(Base):  # type: ignore
    __tablename__ = "tournaments"

    id = Column(String, primary_key=True, index=True)
    slug = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    league_id = Column(String, ForeignKey("leagues.id"))


class MatchModel(Base):  # type: ignore
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
    has_games = Column(Boolean, default=True)


class GameModel(Base):  # type: ignore
    __tablename__ = "games"

    id = Column(String, primary_key=True, index=True)
    state = Column(Enum(GameState), nullable=False)
    number = Column(Integer)
    match_id = Column(String, ForeignKey("matches.id"))
    has_game_data = Column(Boolean, default=True)
    last_stats_fetch = Column(Boolean, default=False)


class ProfessionalTeamModel(Base):  # type: ignore
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


class ProfessionalPlayerModel(Base):  # type: ignore
    __tablename__ = "professional_players"

    id = Column(String, primary_key=True)
    team_id = Column(String, ForeignKey("professional_teams.id"), primary_key=True)
    summoner_name = Column(String)
    image = Column(String)
    role = Column(Enum(PlayerRole), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'team_id'),
    )


class PlayerGameMetadataModel(Base):  # type: ignore
    __tablename__ = "player_game_metadata"

    game_id = Column(String, primary_key=True)
    player_id = Column(String, ForeignKey("professional_players.id"), primary_key=True)
    participant_id = Column(Integer)
    champion_id = Column(String)
    role = Column(Enum(PlayerRole), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('game_id', 'player_id'),
    )


class PlayerGameStatsModel(Base):  # type: ignore
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


class ScheduleModel(Base):  # type: ignore
    __tablename__ = "schedule"

    schedule_name = Column(String, primary_key=True)
    older_token_key = Column(String)
    current_token_key = Column(String)


# --------------------------------------------------
# ----------------- Fantasy Models -----------------
# --------------------------------------------------
class UserModel(Base):  # type: ignore
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()),
                unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    permissions = Column(String)
    account_status = Column(Enum(UserAccountStatus), nullable=False)
    verified = Column(Boolean, default=False)
    verification_token = Column(String)

    def set_permissions(self, permissions_list):
        self.permissions = ','.join(permissions_list)

    def get_permissions(self):
        return self.permissions.split(',') if self.permissions else []


class FantasyLeagueModel(Base):  # type: ignore
    __tablename__ = "fantasy_leagues"

    id = Column(String, primary_key=True, unique=True, nullable=False)
    owner_id = Column(String, nullable=False)
    status = Column(Enum(FantasyLeagueStatus), nullable=False)
    name = Column(String)
    number_of_teams = Column(Integer)
    current_week = Column(Integer, nullable=True)
    current_draft_position = Column(Integer, nullable=True)
    available_leagues = Column(JSON)


class FantasyLeagueMembershipModel(Base):  # type: ignore
    __tablename__ = "fantasy_league_memberships"

    league_id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, primary_key=True, nullable=False)
    status = Column(Enum(FantasyLeagueMembershipStatus), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('league_id', 'user_id'),
    )


class FantasyLeagueScoringSettingModel(Base):  # type: ignore
    __tablename__ = "fantasy_league_scoring_settings"

    fantasy_league_id = Column(String, primary_key=True, nullable=False)
    kills = Column(Integer, nullable=False)
    deaths = Column(Integer, nullable=False)
    assists = Column(Integer, nullable=False)
    creep_score = Column(Float, nullable=False)
    wards_placed = Column(Float, nullable=False)
    wards_destroyed = Column(Float, nullable=False)
    kill_participation = Column(Integer, nullable=False)
    damage_percentage = Column(Integer, nullable=False)


class FantasyLeagueDraftOrderModel(Base):  # type: ignore
    __tablename__ = "fantasy_league_draft_order"

    fantasy_league_id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, primary_key=True, nullable=False)
    position = Column(Integer, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('fantasy_league_id', 'user_id'),
    )


class FantasyTeamModel(Base):  # type: ignore
    __tablename__ = "fantasy_teams"

    fantasy_league_id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, primary_key=True, nullable=False)
    week = Column(Integer, primary_key=True, nullable=False)
    top_player_id = Column(String, nullable=True)
    jungle_player_id = Column(String, nullable=True)
    mid_player_id = Column(String, nullable=True)
    adc_player_id = Column(String, nullable=True)
    support_player_id = Column(String, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('fantasy_league_id', 'user_id', 'week'),
    )
