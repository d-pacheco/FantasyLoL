from sqlalchemy import text
from sqlalchemy import and_
from typing import Optional

from ..common.schemas.fantasy_schemas import *
from ..common.schemas.riot_data_schemas import *

from .database import DatabaseConnection
from .models import *
from .views import PlayerGameView


# --------------------------------------------------
# --------------- League Operations ----------------
# --------------------------------------------------
def save_league(league: League):
    db_league = LeagueModel(**league.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_league)
        db.commit()


def get_leagues(filters: list = None) -> List[League]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(LeagueModel).filter(*filters)
        else:
            query = db.query(LeagueModel)
        league_models = query.all()
        leagues = [League.model_validate(league_model) for league_model in league_models]

        return leagues


def get_league_by_id(league_id: str) -> Optional[League]:
    with DatabaseConnection() as db:
        db_league = db.query(LeagueModel).filter(LeagueModel.id == league_id).first()
        if db_league is None:
            return None
        else:
            return League.model_validate(db_league)


def update_league_fantasy_available_status(league_id: str, new_status: bool) -> Optional[League]:
    with DatabaseConnection() as db:
        db_league: Optional[LeagueModel] = db.query(LeagueModel)\
            .filter(LeagueModel.id == league_id).first()
        if db_league is None:
            return None
        db_league.fantasy_available = new_status
        db.merge(db_league)
        db.commit()
        db.refresh(db_league)

        league = League.model_validate(db_league)
        return league


def get_league_ids_for_player(player_id: str) -> List[str]:
    sql_query = f"""
        SELECT DISTINCT l.id
        FROM professional_players p
        JOIN professional_teams t ON p.team_id = t.id
        JOIN leagues l ON t.home_league = l.name
        WHERE p.id = '{player_id}'
        """
    with DatabaseConnection() as db:
        result = db.execute(text(sql_query))
        rows = result.fetchall()
    league_ids = [row[0] for row in rows]
    return league_ids


# --------------------------------------------------
# ------------- Tournament Operations --------------
# --------------------------------------------------
def save_tournament(tournament: Tournament):
    db_tournament = TournamentModel(**tournament.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_tournament)
        db.commit()


def get_tournaments(filters: list) -> List[Tournament]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(TournamentModel).filter(*filters)
        else:
            query = db.query(TournamentModel)
        tournament_models = query.all()
        tournaments = [
            Tournament.model_validate(tournament_model)
            for tournament_model in tournament_models
        ]
        return tournaments


def get_tournament_by_id(tournament_id: str) -> Optional[Tournament]:
    with DatabaseConnection() as db:
        tournament_model = db.query(TournamentModel)\
            .filter(TournamentModel.id == tournament_id).first()
        if tournament_model is None:
            return None
        else:
            return Tournament.model_validate(tournament_model)


# --------------------------------------------------
# --------------- Match Operations -----------------
# --------------------------------------------------
def save_match(match: Match):
    db_match = MatchModel(**match.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_match)
        db.commit()


def get_matches(filters: list = None) -> List[MatchModel]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(MatchModel).filter(*filters)
        else:
            query = db.query(MatchModel)
        return query.all()


def get_match_by_id(match_id: str) -> MatchModel:
    with DatabaseConnection() as db:
        return db.query(MatchModel) \
            .filter(MatchModel.id == match_id).first()


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
def save_game(game: Game):
    db_game = GameModel(**game.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_game)
        db.commit()


def bulk_save_games(games: List[Game]):
    db_games = []
    for game in games:
        db_games.append(GameModel(**game.model_dump()))
    with DatabaseConnection() as db:
        db.bulk_save_objects(db_games)
        db.commit()


def update_has_game_data(game_id: str, has_game_data: bool):
    with DatabaseConnection() as db:
        db_game: GameModel = db.query(GameModel) \
            .filter(GameModel.id == game_id).first()
        if db_game is not None:
            db_game.has_game_data = has_game_data
            db.merge(db_game)
            db.commit()


def update_game_state(game_id: str, state: str):
    with DatabaseConnection() as db:
        db_game: GameModel = db.query(GameModel) \
            .filter(GameModel.id == game_id).first()
        if db_game is not None:
            db_game.state = state
            db.merge(db_game)
            db.commit()


def get_games(filters: list = None) -> List[GameModel]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(GameModel).filter(*filters)
        else:
            query = db.query(GameModel)
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


def get_game_by_id(game_id: str) -> GameModel:
    with DatabaseConnection() as db:
        return db.query(GameModel) \
            .filter(GameModel.id == game_id).first()


# --------------------------------------------------
# ---------------- Team Operations ----------------
# --------------------------------------------------
def save_team(team: ProfessionalTeam):
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
        return db.query(ProfessionalTeamModel) \
            .filter(ProfessionalTeamModel.id == team_id).first()


# --------------------------------------------------
# --------------- Player Operations ----------------
# --------------------------------------------------
def save_player(player: ProfessionalPlayer):
    db_player = ProfessionalPlayerModel(**player.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player)
        db.commit()


def get_players(filters: list = None) -> List[ProfessionalPlayerModel]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(ProfessionalPlayerModel).filter(*filters)
        else:
            query = db.query(ProfessionalPlayerModel)
        return query.all()


def get_player_by_id(player_id: str) -> ProfessionalPlayerModel:
    with DatabaseConnection() as db:
        return db.query(ProfessionalPlayerModel) \
            .filter(ProfessionalPlayerModel.id == player_id).first()


# --------------------------------------------------
# ----------- Player Metadata Operations -----------
# --------------------------------------------------
def save_player_metadata(player_metadata: PlayerGameMetadata):
    db_player_metadata = PlayerGameMetadataModel(**player_metadata.model_dump())
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
def save_player_stats(player_stats: PlayerGameStats):
    db_player_stats = PlayerGameStatsModel(**player_stats.model_dump())
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
def get_schedule(schedule_name: str) -> Schedule:
    with DatabaseConnection() as db:
        return db.query(Schedule) \
            .filter(Schedule.schedule_name == schedule_name).first()


def update_schedule(schedule: Schedule):
    with DatabaseConnection() as db:
        db.merge(schedule)
        db.commit()


# --------------------------------------------------
# ----------------- User Operations ----------------
# --------------------------------------------------
def create_user(user: User):
    db_user = UserModel(**user.model_dump())
    with DatabaseConnection() as db:
        db.add(db_user)
        db.commit()


def get_user_by_id(user_id: str) -> UserModel:
    with DatabaseConnection() as db:
        return db.query(UserModel) \
            .filter(UserModel.id == user_id).first()


def get_user_by_username(username: str) -> UserModel:
    with DatabaseConnection() as db:
        return db.query(UserModel) \
            .filter(UserModel.username == username).first()


def get_user_by_email(email: str) -> UserModel:
    with DatabaseConnection() as db:
        return db.query(UserModel) \
            .filter(UserModel.email == email).first()


# --------------------------------------------------
# ---------- Fantasy League Operations -------------
# --------------------------------------------------
def create_fantasy_league(fantasy_league: FantasyLeague):
    db_fantasy_league = FantasyLeagueModel(**fantasy_league.model_dump())
    with DatabaseConnection() as db:
        db.add(db_fantasy_league)
        db.commit()


def get_fantasy_league_by_id(fantasy_league_id: str) -> FantasyLeagueModel:
    with DatabaseConnection() as db:
        return db.query(FantasyLeagueModel) \
            .filter(FantasyLeagueModel.id == fantasy_league_id).first()


def create_fantasy_league_scoring_settings(
        scoring_settings: FantasyLeagueScoringSettings):
    db_scoring_settings = FantasyLeagueScoringSettingModel(**scoring_settings.model_dump())
    with DatabaseConnection() as db:
        db.add(db_scoring_settings)
        db.commit()


def get_fantasy_league_scoring_settings_by_id(league_id: str) \
        -> FantasyLeagueScoringSettings:
    with DatabaseConnection() as db:
        return db.query(FantasyLeagueScoringSettingModel) \
            .filter(FantasyLeagueScoringSettingModel.fantasy_league_id == league_id) \
            .first()


def update_fantasy_league_scoring_settings(
        scoring_settings: FantasyLeagueScoringSettings):
    db_scoring_settings = FantasyLeagueScoringSettingModel(**scoring_settings.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_scoring_settings)
        db.commit()


def update_fantasy_league_settings(
        fantasy_league_id: str,
        settings: FantasyLeagueSettings) -> FantasyLeagueModel:
    with DatabaseConnection() as db:
        fantasy_league = db.query(FantasyLeagueModel).filter_by(id=fantasy_league_id).first()

        fantasy_league.name = settings.name
        fantasy_league.number_of_teams = settings.number_of_teams
        fantasy_league.available_leagues = settings.available_leagues

        db.commit()
        db.refresh(fantasy_league)
        return fantasy_league


def update_fantasy_league_status(
        fantasy_league_id: str,
        new_status: FantasyLeagueStatus) -> FantasyLeagueModel:
    with DatabaseConnection() as db:
        fantasy_league = db.query(FantasyLeagueModel).filter_by(id=fantasy_league_id).first()

        fantasy_league.status = new_status
        db.commit()
        db.refresh(fantasy_league)
        return fantasy_league


def update_fantasy_league_current_draft_position(
        fantasy_league_id: str, new_current_draft_position: int) -> FantasyLeagueModel:
    with DatabaseConnection() as db:
        fantasy_league = db.query(FantasyLeagueModel).filter_by(id=fantasy_league_id).first()

        fantasy_league.current_draft_position = new_current_draft_position
        db.commit()
        db.refresh(fantasy_league)
        return fantasy_league


# --------------------------------------------------
# ------- Fantasy League Invite Operations ---------
# --------------------------------------------------
def create_fantasy_league_membership(fantasy_league_membership: FantasyLeagueMembership):
    db_fantasy_league_membership = FantasyLeagueMembershipModel(
        **fantasy_league_membership.model_dump()
    )
    with DatabaseConnection() as db:
        db.merge(db_fantasy_league_membership)
        db.commit()


def get_pending_and_accepted_members_for_league(league_id: str) \
        -> List[FantasyLeagueMembershipModel]:
    with DatabaseConnection() as db:
        return db.query(FantasyLeagueMembershipModel). \
            filter(and_(FantasyLeagueMembershipModel.league_id == league_id,
                        FantasyLeagueMembershipModel.status.in_(
                            [FantasyLeagueMembershipStatus.PENDING,
                             FantasyLeagueMembershipStatus.ACCEPTED]))
                   ).all()


def update_fantasy_league_membership_status(
        membership_model: FantasyLeagueMembershipModel,
        new_status: FantasyLeagueMembershipStatus):
    with DatabaseConnection() as db:
        membership_model.status = new_status
        db.merge(membership_model)
        db.commit()


def get_user_membership_for_fantasy_league(
        user_id: str, fantasy_league_id: str) -> FantasyLeagueMembershipModel:
    with DatabaseConnection() as db:
        return db.query(FantasyLeagueMembershipModel) \
            .filter(FantasyLeagueMembershipModel.league_id == fantasy_league_id,
                    FantasyLeagueMembershipModel.user_id == user_id).first()


def get_users_fantasy_leagues_with_membership_status(
        user_id: str,
        membership_status: FantasyLeagueMembershipStatus) \
            -> List[FantasyLeagueModel]:
    with DatabaseConnection() as db:
        return db.query(FantasyLeagueModel) \
            .join(FantasyLeagueMembershipModel,
                  FantasyLeagueModel.id == FantasyLeagueMembershipModel.league_id) \
            .filter(and_(
                FantasyLeagueMembershipModel.user_id == user_id,
                FantasyLeagueMembershipModel.status == membership_status
            )).all()


def update_fantasy_leagues_current_draft_position(
        fantasy_league_id: str, new_draft_position: int) -> FantasyLeagueModel:
    with DatabaseConnection() as db:
        fantasy_league_db: FantasyLeagueModel = db.query(FantasyLeagueModel)\
            .filter(FantasyLeagueModel.id == fantasy_league_id).first()
        if fantasy_league_db is not None:
            fantasy_league_db.current_draft_position = new_draft_position
            db.merge(fantasy_league_db)
            db.commit(fantasy_league_db)
            db.refresh(fantasy_league_db)
            return fantasy_league_db


# --------------------------------------------------
# ----- Fantasy League Draft Order Operations ------
# --------------------------------------------------
def create_fantasy_league_draft_order(draft_order: FantasyLeagueDraftOrder):
    db_draft_order = FantasyLeagueDraftOrderModel(**draft_order.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_draft_order)
        db.commit()


def get_fantasy_league_draft_order(league_id: str) -> List[FantasyLeagueDraftOrderModel]:
    with DatabaseConnection() as db:
        return db.query(FantasyLeagueDraftOrderModel) \
            .filter(FantasyLeagueDraftOrderModel.fantasy_league_id == league_id) \
            .all()


def delete_fantasy_league_draft_order(draft_order_model: FantasyLeagueDraftOrderModel):
    with DatabaseConnection() as db:
        db.delete(draft_order_model)
        db.commit()


def update_fantasy_league_draft_order_position(
        draft_order_model: FantasyLeagueDraftOrderModel,
        new_position: int):
    with DatabaseConnection() as db:
        draft_order_model.position = new_position
        db.merge(draft_order_model)
        db.commit()


# --------------------------------------------------
# ------------ Fantasy Team Operations -------------
# --------------------------------------------------
def create_or_update_fantasy_team(fantasy_team: FantasyTeam):
    db_fantasy_team = FantasyTeamModel(**fantasy_team.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_fantasy_team)
        db.commit()


def get_all_fantasy_teams_for_user(fantasy_league_id: str, user_id: str) \
        -> List[FantasyTeamModel]:
    with DatabaseConnection() as db:
        return db.query(FantasyTeamModel) \
            .filter(FantasyTeamModel.fantasy_league_id == fantasy_league_id,
                    FantasyTeamModel.user_id == user_id).all()


# Need to add a test for this:
def get_all_fantasy_teams_for_current_week(fantasy_league_id: str, week: int) \
        -> List[FantasyTeamModel]:
    with DatabaseConnection() as db:
        return db.query(FantasyTeamModel) \
            .filter(FantasyTeamModel.fantasy_league_id == fantasy_league_id,
                    FantasyTeamModel.week == week).all()
