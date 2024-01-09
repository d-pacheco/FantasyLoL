from typing import List
from sqlalchemy import select
from sqlalchemy.orm import aliased
from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import (
    League,
    Tournament,
    Match,
    Game,
    PlayerGameMetadata,
    PlayerGameStats,
    ProfessionalTeam,
    ProfessionalPlayer,
    Schedule
)


# --------------------------------------------------
# --------------- League Operations ----------------
# --------------------------------------------------
def save_league(league: League):
    with DatabaseConnection() as db:
        db.merge(league)
        db.commit()


def get_leagues(filters: list = None) -> List[Match]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(League).filter(*filters)
        else:
            query = db.query(League)
        return query.all()


def get_league_by_id(league_id: int) -> League:
    with DatabaseConnection() as db:
        return db.query(League).filter(League.id == league_id).first()


# --------------------------------------------------
# ------------- Tournament Operations --------------
# --------------------------------------------------
def save_tournament(tournament: Tournament):
    with DatabaseConnection() as db:
        db.merge(tournament)
        db.commit()


def get_tournaments(filters: list) -> List[Tournament]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(Tournament).filter(*filters)
        else:
            query = db.query(Tournament)
        return query.all()


def get_tournament_by_id(tournament_id: int) -> Tournament:
    with DatabaseConnection() as db:
        return db.query(Tournament).filter(Tournament.id == tournament_id).first()


# --------------------------------------------------
# --------------- Match Operations -----------------
# --------------------------------------------------
def save_match(match: Match):
    with DatabaseConnection() as db:
        db.merge(match)
        db.commit()


def get_matches(filters: list = None) -> List[Match]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(Match).filter(*filters)
        else:
            query = db.query(Match)
        return query.all()


def get_match_by_id(match_id: int) -> Match:
    with DatabaseConnection() as db:
        return db.query(Match).filter(Match.id == match_id).first()


def get_matches_without_games() -> List[Match]:
    game_alias = aliased(Game)

    # Query to get match IDs without any associated games
    with DatabaseConnection() as db:
        subquery = (
            select([game_alias.match_id])
            .where(game_alias.match_id.isnot(None))
            .distinct()
            .alias()
        )

        # Query to get match IDs without associated games
        matches_without_games = (
            db.query(Match.id)
            .outerjoin(subquery, Match.id == subquery.c.match_id)
            .filter(subquery.c.match_id.is_(None))
            .all()
        )
    return matches_without_games


# --------------------------------------------------
# ---------------- Game Operations -----------------
# --------------------------------------------------
def save_game(game: Game):
    with DatabaseConnection() as db:
        db.merge(game)
        db.commit()


def bulk_save_games(games: List[Game]):
    with DatabaseConnection() as db:
        db.bulk_save_objects(games)
        db.commit()


def get_games(filters: list = None) -> List[Game]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(Game).filter(*filters)
        else:
            query = db.query(Game)
        return query.all()


def get_game_by_id(game_id: int) -> Game:
    with DatabaseConnection() as db:
        return db.query(Game).filter(Game.id == game_id).first()


# --------------------------------------------------
# ---------------- Team Operations ----------------
# --------------------------------------------------
def save_team(team: ProfessionalTeam):
    with DatabaseConnection() as db:
        db.merge(team)
        db.commit()


def get_teams(filters: list = None) -> List[ProfessionalTeam]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(ProfessionalTeam).filter(*filters)
        else:
            query = db.query(ProfessionalTeam)
        return query.all()


def get_team_by_id(team_id: int) -> ProfessionalTeam:
    with DatabaseConnection() as db:
        return db.query(ProfessionalTeam).filter(ProfessionalTeam.id == team_id).first()


# --------------------------------------------------
# --------------- Player Operations --------------
# --------------------------------------------------
def save_player(player: ProfessionalPlayer):
    with DatabaseConnection() as db:
        db.merge(player)
        db.commit()


def get_players(filters: list = None) -> List[ProfessionalPlayer]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(ProfessionalPlayer).filter(*filters)
        else:
            query = db.query(ProfessionalPlayer)
        return query.all()


def get_player_by_id(player_id: int) -> ProfessionalPlayer:
    with DatabaseConnection() as db:
        return db.query(ProfessionalPlayer).filter(ProfessionalPlayer.id == player_id).first()


# --------------------------------------------------
# ----------- Player Metadata Operations -----------
# --------------------------------------------------
def save_player_metadata(player_metadata: PlayerGameMetadata):
    with DatabaseConnection() as db:
        db.merge(player_metadata)
        db.commit()


# --------------------------------------------------
# ------------- Player Stats Operations ------------
# --------------------------------------------------
def save_player_stats(player_stats: PlayerGameStats):
    with DatabaseConnection() as db:
        db.merge(player_stats)
        db.commit()


# --------------------------------------------------
# --------------- Schedule Operations --------------
# --------------------------------------------------
def get_schedule(schedule_name: str) -> Schedule:
    with DatabaseConnection() as db:
        return db.query(Schedule).filter(Schedule.schedule_name == schedule_name).first()


def update_schedule(schedule: Schedule):
    with DatabaseConnection() as db:
        db.merge(schedule)
        db.commit()
