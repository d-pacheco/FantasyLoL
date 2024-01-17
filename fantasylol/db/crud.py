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
    ProfessionalTeamModel,
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


def get_league_by_id(league_id: str) -> League:
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


def get_tournament_by_id(tournament_id: str) -> Tournament:
    with DatabaseConnection() as db:
        return db.query(Tournament).filter(Tournament.id == tournament_id).first()


# --------------------------------------------------
# --------------- Match Operations -----------------
# --------------------------------------------------
def save_match(match: schemas.MatchSchema):
    db_match = Match(**match.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_match)
        db.commit()


def get_matches(filters: list = None) -> List[Match]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(Match).filter(*filters)
        else:
            query = db.query(Match)
        return query.all()


def get_match_by_id(match_id: str) -> Match:
    with DatabaseConnection() as db:
        return db.query(Match).filter(Match.id == match_id).first()


def get_matches_ids_without_games() -> List[str]:
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
    db_game = Game(**game.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_game)
        db.commit()


def bulk_save_games(games: List[schemas.GameSchema]):
    db_games = []
    for game in games:
        db_games.append(Game(**game.model_dump()))
    with DatabaseConnection() as db:
        db.bulk_save_objects(db_games)
        db.commit()


def update_has_game_data(game_id: str, has_game_data: bool):
    with DatabaseConnection() as db:
        db_game: Game = db.query(Game).filter(Game.id == game_id).first()
        if db_game is not None:
            db_game.has_game_data = has_game_data
            db.merge(db_game)
            db.commit()


def update_game_state(game_id: str, state: str):
    with DatabaseConnection() as db:
        db_game: Game = db.query(Game).filter(Game.id == game_id).first()
        if db_game is not None:
            db_game.state = state
            db.merge(db_game)
            db.commit()


def get_games(filters: list = None) -> List[Game]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(Game).filter(*filters)
        else:
            query = db.query(Game)
        return query.all()


def get_games_to_check_state() -> List[str]:
    sql_query = """
        SELECT games.id
        FROM games
        JOIN matches ON games.match_id = matches.id
        WHERE matches.start_time < strftime('%Y-%m-%dT%H:%M:%SZ', 'now', 'utc')
        AND games.state != 'COMPLETED' AND games.state != 'UNNEEDED'
    """
    with DatabaseConnection() as db:
        result = db.execute(text(sql_query))
        rows = result.fetchall()
    game_ids = []
    for row in rows:
        game_ids.append(row[0])
    return game_ids


def get_game_by_id(game_id: str) -> Game:
    with DatabaseConnection() as db:
        return db.query(Game).filter(Game.id == game_id).first()


# --------------------------------------------------
# ---------------- Team Operations ----------------
# --------------------------------------------------
def save_team(team: schemas.ProfessionalTeam):
    db_team = ProfessionalTeamModel(**team.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_team)
        db.commit()


def get_teams(filters: list = None) -> List[ProfessionalTeamModel]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(ProfessionalTeamModel).filter(*filters)
        else:
            query = db.query(ProfessionalTeamModel)
        return query.all()


def get_team_by_id(team_id: str) -> ProfessionalTeamModel:
    with DatabaseConnection() as db:
        return db.query(ProfessionalTeamModel).filter(ProfessionalTeamModel.id == team_id).first()


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


def get_player_by_id(player_id: str) -> ProfessionalPlayer:
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
            AND (games.has_game_data = True)
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
        WHERE ((games.state = 'COMPLETED'
                AND (SELECT COUNT(*) FROM player_game_stats WHERE game_id = games.id) < 10)
                OR games.state = 'INPROGRESS')
            AND (games.has_game_data = True)
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
