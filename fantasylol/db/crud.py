from typing import List
from sqlalchemy import text
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
from fantasylol.schemas import riot_data_schemas as schemas


# --------------------------------------------------
# --------------- League Operations ----------------
# --------------------------------------------------
def save_league(league: schemas.LeagueSchema):
    db_league = League(**league.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_league)
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
def save_tournament(tournament: schemas.TournamentSchema):
    db_tournament = Tournament(**tournament.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_tournament)
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


def get_matches_ids_without_games() -> List[int]:
    sql_query = """
        SELECT matches.id
        FROM matches
        LEFT JOIN games ON matches.id = games.match_id
        WHERE games.match_id IS NULL;
    """
    with DatabaseConnection() as db:
        result = db.execute(text(sql_query))
        rows = result.fetchall()
    match_ids = []
    for row in rows:
        match_ids.append(row[0])
    return match_ids


# --------------------------------------------------
# ---------------- Game Operations -----------------
# --------------------------------------------------
def save_game(game: Game):
    with DatabaseConnection() as db:
        db.merge(game)
        db.commit()


def bulk_save_games(games: List[schemas.GameSchema]):
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
def save_team(team: schemas.ProfessionalTeamSchema):
    db_team = ProfessionalTeam(**team.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_team)
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
def save_player(player: schemas.ProfessionalPlayerSchema):
    db_player = ProfessionalPlayer(**player.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player)
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
def save_player_metadata(player_metadata: schemas.PlayerGameMetadataSchema):
    db_player_metadata = PlayerGameMetadata(**player_metadata.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player_metadata)
        db.commit()


def get_game_ids_without_player_metadata():
    sql_query = """
        SELECT games.id as game_id
        FROM games
        LEFT JOIN player_game_metadata ON games.id = player_game_metadata.game_id
        WHERE games.state in ('COMPLETED', 'INPROGRESS')
        GROUP BY games.id
        HAVING COUNT(player_game_metadata.game_id) <> 10
        OR COUNT(player_game_metadata.game_id) IS NULL;
    """
    with DatabaseConnection() as db:
        result = db.execute(text(sql_query))
        rows = result.fetchall()
    game_ids = []
    for row in rows:
        game_ids.append(row[0])
    return game_ids


# --------------------------------------------------
# ------------- Player Stats Operations ------------
# --------------------------------------------------
def save_player_stats(player_stats: schemas.PlayerGameStatsSchema):
    db_player_stats = PlayerGameStats(**player_stats.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player_stats)
        db.commit()


def get_game_ids_to_fetch_player_stats_for():
    sql_query = """
        SELECT games.id as game_id
        FROM games
        LEFT JOIN player_game_stats ON games.id = player_game_stats.game_id
        WHERE (games.state = 'COMPLETED'
                AND (SELECT COUNT(*) FROM player_game_stats WHERE game_id = games.id) < 10)
           OR games.state = 'INPROGRESS'
        GROUP BY games.id
    """
    with DatabaseConnection() as db:
        result = db.execute(text(sql_query))
        rows = result.fetchall()
    game_ids = []
    for row in rows:
        game_ids.append(row[0])
    return game_ids


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
