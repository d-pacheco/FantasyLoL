from typing import List
from sqlalchemy import text
from sqlalchemy import and_

from fantasylol.db.database import DatabaseConnection
from fantasylol.db import models
from fantasylol.db.views import PlayerGameView
from fantasylol.schemas import riot_data_schemas as riot_schemas
from fantasylol.schemas import fantasy_schemas as f_schemas


# --------------------------------------------------
# --------------- League Operations ----------------
# --------------------------------------------------
def save_league(league: riot_schemas.League):
    db_league = models.LeagueModel(**league.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_league)
        db.commit()


def get_leagues(filters: list = None) -> List[models.LeagueModel]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(models.LeagueModel).filter(*filters)
        else:
            query = db.query(models.LeagueModel)
        return query.all()


def get_league_by_id(league_id: str) -> models.LeagueModel:
    with DatabaseConnection() as db:
        return db.query(models.LeagueModel).filter(models.LeagueModel.id == league_id).first()


# --------------------------------------------------
# ------------- Tournament Operations --------------
# --------------------------------------------------
def save_tournament(tournament: riot_schemas.Tournament):
    db_tournament = models.TournamentModel(**tournament.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_tournament)
        db.commit()


def get_tournaments(filters: list) -> List[models.TournamentModel]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(models.TournamentModel).filter(*filters)
        else:
            query = db.query(models.TournamentModel)
        return query.all()


def get_tournament_by_id(tournament_id: str) -> models.TournamentModel:
    with DatabaseConnection() as db:
        return db.query(models.TournamentModel) \
            .filter(models.TournamentModel.id == tournament_id).first()


# --------------------------------------------------
# --------------- Match Operations -----------------
# --------------------------------------------------
def save_match(match: riot_schemas.Match):
    db_match = models.MatchModel(**match.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_match)
        db.commit()


def get_matches(filters: list = None) -> List[models.MatchModel]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(models.MatchModel).filter(*filters)
        else:
            query = db.query(models.MatchModel)
        return query.all()


def get_match_by_id(match_id: str) -> models.MatchModel:
    with DatabaseConnection() as db:
        return db.query(models.MatchModel) \
            .filter(models.MatchModel.id == match_id).first()


def get_match_ids_without_games() -> List[str]:
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
def save_game(game: riot_schemas.Game):
    db_game = models.GameModel(**game.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_game)
        db.commit()


def bulk_save_games(games: List[riot_schemas.Game]):
    db_games = []
    for game in games:
        db_games.append(models.GameModel(**game.model_dump()))
    with DatabaseConnection() as db:
        db.bulk_save_objects(db_games)
        db.commit()


def update_has_game_data(game_id: str, has_game_data: bool):
    with DatabaseConnection() as db:
        db_game: models.GameModel = db.query(models.GameModel) \
            .filter(models.GameModel.id == game_id).first()
        if db_game is not None:
            db_game.has_game_data = has_game_data
            db.merge(db_game)
            db.commit()


def update_game_state(game_id: str, state: str):
    with DatabaseConnection() as db:
        db_game: models.GameModel = db.query(models.GameModel) \
            .filter(models.GameModel.id == game_id).first()
        if db_game is not None:
            db_game.state = state
            db.merge(db_game)
            db.commit()


def get_games(filters: list = None) -> List[models.GameModel]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(models.GameModel).filter(*filters)
        else:
            query = db.query(models.GameModel)
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


def get_game_by_id(game_id: str) -> models.GameModel:
    with DatabaseConnection() as db:
        return db.query(models.GameModel) \
            .filter(models.GameModel.id == game_id).first()


# --------------------------------------------------
# ---------------- Team Operations ----------------
# --------------------------------------------------
def save_team(team: riot_schemas.ProfessionalTeam):
    db_team = models.ProfessionalTeamModel(**team.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_team)
        db.commit()


def get_teams(filters: list = None) -> List[models.ProfessionalTeamModel]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(models.ProfessionalTeamModel).filter(*filters)
        else:
            query = db.query(models.ProfessionalTeamModel)
        return query.all()


def get_team_by_id(team_id: str) -> models.ProfessionalTeamModel:
    with DatabaseConnection() as db:
        return db.query(models.ProfessionalTeamModel) \
            .filter(models.ProfessionalTeamModel.id == team_id).first()


# --------------------------------------------------
# --------------- Player Operations ----------------
# --------------------------------------------------
def save_player(player: riot_schemas.ProfessionalPlayer):
    db_player = models.ProfessionalPlayerModel(**player.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player)
        db.commit()


def get_players(filters: list = None) -> List[models.ProfessionalPlayerModel]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(models.ProfessionalPlayerModel).filter(*filters)
        else:
            query = db.query(models.ProfessionalPlayerModel)
        return query.all()


def get_player_by_id(player_id: str) -> models.ProfessionalPlayerModel:
    with DatabaseConnection() as db:
        return db.query(models.ProfessionalPlayerModel) \
            .filter(models.ProfessionalPlayerModel.id == player_id).first()


# --------------------------------------------------
# ----------- Player Metadata Operations -----------
# --------------------------------------------------
def save_player_metadata(player_metadata: riot_schemas.PlayerGameMetadata):
    db_player_metadata = models.PlayerGameMetadataModel(**player_metadata.model_dump())
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
def save_player_stats(player_stats: riot_schemas.PlayerGameStats):
    db_player_stats = models.PlayerGameStatsModel(**player_stats.model_dump())
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


def get_player_game_stats(filters: list = None) -> List[PlayerGameView]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(PlayerGameView).filter(*filters)
        else:
            query = db.query(PlayerGameView)
        return query.all()


# --------------------------------------------------
# --------------- Schedule Operations --------------
# --------------------------------------------------
def get_schedule(schedule_name: str) -> models.Schedule:
    with DatabaseConnection() as db:
        return db.query(models.Schedule) \
            .filter(models.Schedule.schedule_name == schedule_name).first()


def update_schedule(schedule: models.Schedule):
    with DatabaseConnection() as db:
        db.merge(schedule)
        db.commit()


# --------------------------------------------------
# ----------------- User Operations ----------------
# --------------------------------------------------
def create_user(user: f_schemas.User):
    db_user = models.UserModel(**user.model_dump())
    with DatabaseConnection() as db:
        db.add(db_user)
        db.commit()


def get_user_by_id(user_id: str) -> models.UserModel:
    with DatabaseConnection() as db:
        return db.query(models.UserModel) \
            .filter(models.UserModel.id == user_id).first()


def get_user_by_username(username: str) -> models.UserModel:
    with DatabaseConnection() as db:
        return db.query(models.UserModel) \
            .filter(models.UserModel.username == username).first()


def get_user_by_email(email: str) -> models.UserModel:
    with DatabaseConnection() as db:
        return db.query(models.UserModel) \
            .filter(models.UserModel.email == email).first()


# --------------------------------------------------
# ---------- Fantasy League Operations -------------
# --------------------------------------------------
def create_fantasy_league(fantasy_league: f_schemas.FantasyLeague):
    db_fantasy_league = models.FantasyLeagueModel(**fantasy_league.model_dump())
    with DatabaseConnection() as db:
        db.add(db_fantasy_league)
        db.commit()


def get_fantasy_league_by_id(fantasy_league_id: str) -> models.FantasyLeagueModel:
    with DatabaseConnection() as db:
        return db.query(models.FantasyLeagueModel) \
            .filter(models.FantasyLeagueModel.id == fantasy_league_id).first()


def update_fantasy_league_settings(
        fantasy_league_id: str,
        settings: f_schemas.FantasyLeagueSettings) -> models.FantasyLeagueModel:
    with DatabaseConnection() as db:
        league = db.query(models.FantasyLeagueModel).filter_by(id=fantasy_league_id).first()

        league.name = settings.name
        league.number_of_teams = settings.number_of_teams

        db.commit()
        db.refresh(league)
        return league


# --------------------------------------------------
# ------- Fantasy League Invite Operations ---------
# --------------------------------------------------
def create_fantasy_league_membership(fantasy_league_membership: f_schemas.FantasyLeagueMembership):
    db_fantasy_league_membership = models.FantasyLeagueMembershipModel(
        **fantasy_league_membership.model_dump()
    )
    with DatabaseConnection() as db:
        db.merge(db_fantasy_league_membership)
        db.commit()


def get_pending_and_accepted_members_for_league(league_id: str) \
        -> List[models.FantasyLeagueMembershipModel]:
    with DatabaseConnection() as db:
        return db.query(models.FantasyLeagueMembershipModel). \
            filter(and_(models.FantasyLeagueMembershipModel.league_id == league_id,
                        models.FantasyLeagueMembershipModel.status.in_(
                            [f_schemas.FantasyLeagueMembershipStatus.PENDING,
                             f_schemas.FantasyLeagueMembershipStatus.ACCEPTED]))
                   ).all()


def update_fantasy_league_membership_status(
        membership_model: models.FantasyLeagueMembershipModel,
        new_status: f_schemas.FantasyLeagueMembershipStatus):
    with DatabaseConnection() as db:
        membership_model.status = new_status
        db.merge(membership_model)
        db.commit()
