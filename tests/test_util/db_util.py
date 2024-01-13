from fantasylol.db.database import DatabaseConnection
from fantasylol.schemas import riot_data_schemas as schemas
from fantasylol.db import models


def save_league(league: schemas.LeagueSchema):
    db_league = models.League(**league.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_league)
        db.commit()


def save_match(match: schemas.MatchSchema):
    db_match = models.Match(**match.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_match)
        db.commit()


def save_game(game: schemas.GameSchema):
    db_game = models.Game(**game.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_game)
        db.commit()


def get_game(game_id: int) -> models.Game:
    with DatabaseConnection() as db:
        return db.query(models.Game).filter(models.Game.id == game_id).first()


def save_team(team: schemas.ProfessionalTeamSchema):
    db_team = models.ProfessionalTeam(**team.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_team)
        db.commit()


def save_player(player: schemas.ProfessionalPlayerSchema):
    db_player = models.ProfessionalPlayer(**player.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player)
        db.commit()


def save_player_metadata(player_metadata: schemas.PlayerGameMetadataSchema):
    db_player_metadata = models.PlayerGameMetadata(**player_metadata.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player_metadata)
        db.commit()


def save_player_stats(player_stats: schemas.PlayerGameStatsSchema):
    db_player_stats = models.PlayerGameStats(**player_stats.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player_stats)
        db.commit()