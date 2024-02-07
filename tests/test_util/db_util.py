from sqlalchemy import and_
from typing import List

from fantasylol.db.database import DatabaseConnection
from fantasylol.schemas import riot_data_schemas as schemas
from fantasylol.schemas import fantasy_schemas
from fantasylol.db import models


def save_league(league: schemas.League):
    db_league = models.LeagueModel(**league.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_league)
        db.commit()


def get_league_by_id(league_id: str) -> models.LeagueModel:
    with DatabaseConnection() as db:
        return db.query(models.LeagueModel) \
            .filter(models.LeagueModel.id == league_id).first()


def save_match(match: schemas.Match):
    db_match = models.MatchModel(**match.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_match)
        db.commit()


def get_match_by_id(match_id: str) -> models.MatchModel:
    with DatabaseConnection() as db:
        return db.query(models.MatchModel).filter(models.MatchModel.id == match_id).first()


def save_game(game: schemas.Game):
    db_game = models.GameModel(**game.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_game)
        db.commit()


def get_game(game_id: int) -> models.GameModel:
    with DatabaseConnection() as db:
        return db.query(models.GameModel).filter(models.GameModel.id == game_id).first()


def save_tournament(tournament: schemas.Tournament):
    db_tournament = models.TournamentModel(**tournament.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_tournament)
        db.commit()


def get_tournament_by_id(tournament_id: str) -> models.TournamentModel:
    with DatabaseConnection() as db:
        return db.query(models.TournamentModel) \
            .filter(models.TournamentModel.id == tournament_id).first()


def save_team(team: schemas.ProfessionalTeam):
    db_team = models.ProfessionalTeamModel(**team.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_team)
        db.commit()


def get_team_by_id(team_id: str) -> models.ProfessionalTeamModel:
    with DatabaseConnection() as db:
        return db.query(models.ProfessionalTeamModel) \
            .filter(models.ProfessionalTeamModel.id == team_id).first()


def save_player(player: schemas.ProfessionalPlayer):
    db_player = models.ProfessionalPlayerModel(**player.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player)
        db.commit()


def get_player_by_id(player_id: str) -> models.ProfessionalPlayerModel:
    with DatabaseConnection() as db:
        return db.query(models.ProfessionalPlayerModel) \
            .filter(models.ProfessionalPlayerModel.id == player_id).first()


def save_player_metadata(player_metadata: schemas.PlayerGameMetadata):
    db_player_metadata = models.PlayerGameMetadataModel(**player_metadata.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player_metadata)
        db.commit()


def save_player_stats(player_stats: schemas.PlayerGameStats):
    db_player_stats = models.PlayerGameStatsModel(**player_stats.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player_stats)
        db.commit()


# --------------------------------------------------
# -------------- Fantasy Operations ----------------
# --------------------------------------------------
def get_user_by_username(username: str) -> models.UserModel:
    with DatabaseConnection() as db:
        return db.query(models.UserModel) \
            .filter(models.UserModel.username == username).first()


def create_user(user: fantasy_schemas.User):
    db_user = models.UserModel(**user.model_dump())
    with DatabaseConnection() as db:
        db.add(db_user)
        db.commit()


def create_fantasy_league(fantasy_league: fantasy_schemas.FantasyLeague):
    db_fantasy_league = models.FantasyLeagueModel(**fantasy_league.model_dump())
    with DatabaseConnection() as db:
        db.add(db_fantasy_league)
        db.commit()


def get_fantasy_league_by_id(fantasy_league_id: str) -> models.FantasyLeagueModel:
    with DatabaseConnection() as db:
        return db.query(models.FantasyLeagueModel) \
            .filter(models.FantasyLeagueModel.id == fantasy_league_id).first()


def get_pending_and_accepted_members_for_league(league_id: str) \
        -> List[models.FantasyLeagueMembershipModel]:
    with DatabaseConnection() as db:
        return db.query(models.FantasyLeagueMembershipModel). \
            filter(and_(models.FantasyLeagueMembershipModel.league_id == league_id,
                        models.FantasyLeagueMembershipModel.status.in_(
                            [fantasy_schemas.FantasyLeagueMembershipStatus.PENDING,
                             fantasy_schemas.FantasyLeagueMembershipStatus.ACCEPTED]))
                   ).all()


def create_fantasy_league_membership(
        fantasy_league_membership: fantasy_schemas.FantasyLeagueMembership):
    db_fantasy_league_membership = models.FantasyLeagueMembershipModel(
        **fantasy_league_membership.model_dump()
    )
    with DatabaseConnection() as db:
        db.merge(db_fantasy_league_membership)
        db.commit()
