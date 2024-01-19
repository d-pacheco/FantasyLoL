from fantasylol.db.database import DatabaseConnection
from fantasylol.schemas import riot_data_schemas as schemas
from fantasylol.db import models


def save_league(league: schemas.League):
    db_league = models.LeagueModel(**league.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_league)
        db.commit()


def get_league_by_id(league_id: str) -> models.LeagueModel:
    with DatabaseConnection() as db:
        return db.query(models.LeagueModel)\
            .filter(models.LeagueModel.id == league_id).first()


def save_match(match: schemas.Match):
    db_match = models.MatchModel(**match.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_match)
        db.commit()


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


def save_team(team: schemas.ProfessionalTeam):
    db_team = models.ProfessionalTeamModel(**team.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_team)
        db.commit()


def get_team_by_id(team_id: str) -> models.ProfessionalTeamModel:
    with DatabaseConnection() as db:
        return db.query(models.ProfessionalTeamModel)\
            .filter(models.ProfessionalTeamModel.id == team_id).first()


def save_player(player: schemas.ProfessionalPlayer):
    db_player = models.ProfessionalPlayerModel(**player.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player)
        db.commit()


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
