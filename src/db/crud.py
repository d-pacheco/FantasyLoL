from sqlalchemy import text, and_
from typing import Optional, List

from ..common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueID,
    FantasyLeagueDraftOrder,
    FantasyLeagueScoringSettings,
    FantasyLeagueStatus,
    FantasyLeagueSettings,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus,
    FantasyTeam,
    User,
    UserID
)
from ..common.schemas.riot_data_schemas import (
    League,
    RiotLeagueID,
    ProfessionalPlayer,
    ProPlayerID,
    ProfessionalTeam,
    ProTeamID,
    Tournament,
    RiotTournamentID,
    Match,
    RiotMatchID,
    Game,
    RiotGameID,
    GameState,
    PlayerGameMetadata,
    PlayerGameData,
    PlayerGameStats,
    Schedule
)

from .database import DatabaseConnection
from .models import (
    # Riot Models
    LeagueModel,
    TournamentModel,
    MatchModel,
    GameModel,
    ProfessionalTeamModel,
    ProfessionalPlayerModel,
    PlayerGameMetadataModel,
    PlayerGameStatsModel,
    ScheduleModel,

    # Fantasy Models
    UserModel,
    FantasyLeagueDraftOrderModel,
    FantasyLeagueScoringSettingModel,
    FantasyLeagueModel,
    FantasyLeagueMembershipModel,
    FantasyTeamModel
)
from .views import PlayerGameView


# --------------------------------------------------
# --------------- League Operations ----------------
# --------------------------------------------------
def put_league(league: League) -> None:
    db_league = LeagueModel(**league.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_league)
        db.commit()


def get_leagues(filters: Optional[list] = None) -> List[League]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(LeagueModel).filter(*filters)
        else:
            query = db.query(LeagueModel)
        league_models = query.all()
        leagues = [League.model_validate(league_model) for league_model in league_models]

        return leagues


def get_league_by_id(league_id: RiotLeagueID) -> Optional[League]:
    with DatabaseConnection() as db:
        db_league = db.query(LeagueModel).filter(LeagueModel.id == league_id).first()
        if db_league is None:
            return None
        else:
            return League.model_validate(db_league)


def update_league_fantasy_available_status(
        league_id: RiotLeagueID, new_status: bool) -> Optional[League]:
    with DatabaseConnection() as db:
        db_league: Optional[LeagueModel] = db.query(LeagueModel) \
            .filter(LeagueModel.id == league_id).first()
        if db_league is None:
            return None
        db_league.fantasy_available = new_status
        db.merge(db_league)
        db.commit()
        db.refresh(db_league)

        league = League.model_validate(db_league)
        return league


def get_league_ids_for_player(player_id: ProPlayerID) -> List[RiotLeagueID]:
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
    league_ids = [RiotLeagueID(row[0]) for row in rows]
    return league_ids


# --------------------------------------------------
# ------------- Tournament Operations --------------
# --------------------------------------------------
def put_tournament(tournament: Tournament) -> None:
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
        tournament_models: List[TournamentModel] = query.all()
        tournaments = [
            Tournament.model_validate(tournament_model)
            for tournament_model in tournament_models
        ]
        return tournaments


def get_tournament_by_id(tournament_id: RiotTournamentID) -> Optional[Tournament]:
    with DatabaseConnection() as db:
        tournament_model: TournamentModel = db.query(TournamentModel) \
            .filter(TournamentModel.id == tournament_id).first()
        if tournament_model is None:
            return None
        else:
            return Tournament.model_validate(tournament_model)


# --------------------------------------------------
# --------------- Match Operations -----------------
# --------------------------------------------------
def put_match(match: Match) -> None:
    db_match = MatchModel(**match.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_match)
        db.commit()


def get_matches(filters: Optional[list] = None) -> List[Match]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(MatchModel).filter(*filters)
        else:
            query = db.query(MatchModel)
        match_models: List[MatchModel] = query.all()
        matches = [Match.model_validate(match_model) for match_model in match_models]

        return matches


def get_match_by_id(match_id: RiotMatchID) -> Optional[Match]:
    with DatabaseConnection() as db:
        match_model: MatchModel = db.query(MatchModel).filter(MatchModel.id == match_id).first()
        if match_model is None:
            return None
        else:
            return Match.model_validate(match_model)


def get_match_ids_without_games() -> List[RiotMatchID]:
    sql_query = """
        SELECT matches.id
        FROM matches
        LEFT JOIN games ON matches.id = games.match_id
        WHERE games.match_id IS NULL AND matches.has_games = True;
    """
    with DatabaseConnection() as db:
        result = db.execute(text(sql_query))
        rows = result.fetchall()
        match_ids = [RiotMatchID(row[0]) for row in rows]
        return match_ids


def update_match_has_games(match_id: RiotMatchID, new_has_games: bool) -> None:
    with DatabaseConnection() as db:
        db_match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
        assert (db_match is not None)
        db_match.has_games = new_has_games
        db.merge(db_match)
        db.commit()


# --------------------------------------------------
# ---------------- Game Operations -----------------
# --------------------------------------------------
def put_game(game: Game) -> None:
    db_game = GameModel(**game.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_game)
        db.commit()


def bulk_save_games(games: List[Game]) -> None:
    db_games = [GameModel(**game.model_dump()) for game in games]
    with DatabaseConnection() as db:
        db.bulk_save_objects(db_games)
        db.commit()


def update_has_game_data(game_id: RiotGameID, has_game_data: bool) -> None:
    with DatabaseConnection() as db:
        db_game: GameModel = db.query(GameModel).filter(GameModel.id == game_id).first()
        if db_game is not None:
            db_game.has_game_data = has_game_data
            db.merge(db_game)
            db.commit()


def update_game_state(game_id: RiotGameID, state: GameState) -> None:
    with DatabaseConnection() as db:
        db_game: GameModel = db.query(GameModel).filter(GameModel.id == game_id).first()
        if db_game is not None:
            db_game.state = state
            db.merge(db_game)
            db.commit()


def get_games(filters: Optional[list] = None) -> List[Game]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(GameModel).filter(*filters)
        else:
            query = db.query(GameModel)
        game_models: List[GameModel] = query.all()
        games = [Game.model_validate(game_model) for game_model in game_models]

        return games


def get_games_to_check_state() -> List[RiotGameID]:
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
        game_ids = [RiotGameID(row[0]) for row in rows]
        return game_ids


def get_game_by_id(game_id: RiotGameID) -> Optional[Game]:
    with DatabaseConnection() as db:
        game_model: GameModel = db.query(GameModel).filter(GameModel.id == game_id).first()
        if game_model is None:
            return None
        else:
            return Game.model_validate(game_model)


# --------------------------------------------------
# ---------------- Team Operations ----------------
# --------------------------------------------------
def put_team(team: ProfessionalTeam) -> None:
    db_team = ProfessionalTeamModel(**team.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_team)
        db.commit()


def get_teams(filters: Optional[list] = None) -> List[ProfessionalTeam]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(ProfessionalTeamModel).filter(*filters)
        else:
            query = db.query(ProfessionalTeamModel)
        team_models: List[ProfessionalTeamModel] = query.all()
        teams = [ProfessionalTeam.model_validate(team_model) for team_model in team_models]

        return teams


def get_team_by_id(team_id: ProTeamID) -> Optional[ProfessionalTeam]:
    with DatabaseConnection() as db:
        team_model: ProfessionalTeamModel = db.query(ProfessionalTeamModel) \
            .filter(ProfessionalTeamModel.id == team_id).first()
        if team_model is None:
            return None
        else:
            return ProfessionalTeam.model_validate(team_model)


# --------------------------------------------------
# --------------- Player Operations ----------------
# --------------------------------------------------
def put_player(player: ProfessionalPlayer) -> None:
    db_player = ProfessionalPlayerModel(**player.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player)
        db.commit()


def get_players(filters: Optional[list] = None) -> List[ProfessionalPlayer]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(ProfessionalPlayerModel).filter(*filters)
        else:
            query = db.query(ProfessionalPlayerModel)
        player_models: List[ProfessionalPlayer] = query.all()
        players = [ProfessionalPlayer.model_validate(player_model)
                   for player_model in player_models]
        return players


def get_player_by_id(player_id: ProPlayerID) -> Optional[ProfessionalPlayer]:
    with DatabaseConnection() as db:
        player_model: ProfessionalPlayerModel = db.query(ProfessionalPlayerModel) \
            .filter(ProfessionalPlayerModel.id == player_id).first()
        if player_model is None:
            return None
        else:
            return ProfessionalPlayer.model_validate(player_model)


# --------------------------------------------------
# ----------- Player Metadata Operations -----------
# --------------------------------------------------
def put_player_metadata(player_metadata: PlayerGameMetadata) -> None:
    db_player_metadata = PlayerGameMetadataModel(**player_metadata.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player_metadata)
        db.commit()


def get_player_metadata(
        player_id: ProPlayerID, game_id: RiotGameID) -> Optional[PlayerGameMetadata]:
    with DatabaseConnection() as db:
        player_metadata = db.query(PlayerGameMetadataModel) \
            .filter(PlayerGameMetadataModel.player_id == player_id,
                    PlayerGameMetadataModel.game_id == game_id).first()
        if player_metadata is None:
            return None
        else:
            return PlayerGameMetadata.model_validate(player_metadata)


def get_game_ids_without_player_metadata() -> List[RiotGameID]:
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
        game_ids = [RiotGameID(row[0]) for row in rows]
        return game_ids


# --------------------------------------------------
# ------------- Player Stats Operations ------------
# --------------------------------------------------
def put_player_stats(player_stats: PlayerGameStats) -> None:
    db_player_stats = PlayerGameStatsModel(**player_stats.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_player_stats)
        db.commit()


def get_player_stats(game_id: RiotGameID, participant_id: int) -> Optional[PlayerGameStats]:
    with DatabaseConnection() as db:
        player_game_stats = db.query(PlayerGameStatsModel) \
            .filter(PlayerGameStatsModel.game_id == game_id,
                    PlayerGameStatsModel.participant_id == participant_id).first()
        if player_game_stats is None:
            return None
        else:
            return PlayerGameStats.model_validate(player_game_stats)


def get_game_ids_to_fetch_player_stats_for() -> List[RiotGameID]:
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
        game_ids = [RiotGameID(row[0]) for row in rows]
        return game_ids


def get_player_game_stats(filters: Optional[list] = None) -> List[PlayerGameData]:
    with DatabaseConnection() as db:
        if filters:
            query = db.query(PlayerGameView).filter(*filters)
        else:
            query = db.query(PlayerGameView)

        player_game_stat_models: List[PlayerGameView] = query.all()
        player_game_data = [PlayerGameData.model_validate(player_game_stat_model)
                            for player_game_stat_model in player_game_stat_models]
        return player_game_data


# --------------------------------------------------
# --------------- Schedule Operations --------------
# --------------------------------------------------
def get_schedule(schedule_name: str) -> Optional[Schedule]:
    with DatabaseConnection() as db:
        schedule_model: ScheduleModel = db.query(ScheduleModel) \
            .filter(ScheduleModel.schedule_name == schedule_name).first()
        if schedule_model is None:
            return None
        else:
            return Schedule.model_validate(schedule_model)


def update_schedule(schedule: Schedule) -> None:
    db_schedule = ScheduleModel(**schedule.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_schedule)
        db.commit()


# --------------------------------------------------
# ----------------- User Operations ----------------
# --------------------------------------------------
def create_user(user: User) -> None:
    db_user = UserModel(**user.model_dump())
    with DatabaseConnection() as db:
        db.add(db_user)
        db.commit()


def get_user_by_id(user_id: UserID) -> Optional[User]:
    with DatabaseConnection() as db:
        user_model: UserModel = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user_model is None:
            return None
        else:
            return User.model_validate(user_model)


def get_user_by_username(username: str) -> Optional[User]:
    with DatabaseConnection() as db:
        user_model: UserModel = db.query(UserModel).filter(UserModel.username == username).first()
        if user_model is None:
            return None
        else:
            return User.model_validate(user_model)


def get_user_by_email(email: str) -> Optional[User]:
    with DatabaseConnection() as db:
        user_model: UserModel = db.query(UserModel).filter(UserModel.email == email).first()
        if user_model is None:
            return None
        else:
            return User.model_validate(user_model)


# --------------------------------------------------
# ---------- Fantasy League Operations -------------
# --------------------------------------------------
def create_fantasy_league(fantasy_league: FantasyLeague) -> None:
    db_fantasy_league = FantasyLeagueModel(**fantasy_league.model_dump())
    with DatabaseConnection() as db:
        db.add(db_fantasy_league)
        db.commit()


def get_fantasy_league_by_id(fantasy_league_id: FantasyLeagueID) -> Optional[FantasyLeague]:
    with DatabaseConnection() as db:
        fantasy_league_model: Optional[FantasyLeagueModel] = db.query(FantasyLeagueModel) \
            .filter(FantasyLeagueModel.id == fantasy_league_id).first()
        if fantasy_league_model is None:
            return None
        else:
            return FantasyLeague.model_validate(fantasy_league_model)


def put_fantasy_league_scoring_settings(
        scoring_settings: FantasyLeagueScoringSettings) -> None:
    db_scoring_settings = FantasyLeagueScoringSettingModel(**scoring_settings.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_scoring_settings)
        db.commit()


def get_fantasy_league_scoring_settings_by_id(fantasy_league_id: FantasyLeagueID) \
        -> Optional[FantasyLeagueScoringSettings]:
    with DatabaseConnection() as db:
        scoring_settings_model: Optional[FantasyLeagueScoringSettingModel] = db.query(
            FantasyLeagueScoringSettingModel) \
            .filter(FantasyLeagueScoringSettingModel.fantasy_league_id == fantasy_league_id) \
            .first()
        if scoring_settings_model is None:
            return None
        else:
            return FantasyLeagueScoringSettings.model_validate(scoring_settings_model)


def update_fantasy_league_settings(
        fantasy_league_id: FantasyLeagueID,
        settings: FantasyLeagueSettings) -> FantasyLeague:
    with DatabaseConnection() as db:
        fantasy_league_model: Optional[FantasyLeagueModel] = db.query(FantasyLeagueModel) \
            .filter_by(id=fantasy_league_id).first()
        assert (fantasy_league_model is not None)

        fantasy_league_model.name = settings.name
        fantasy_league_model.number_of_teams = settings.number_of_teams
        fantasy_league_model.available_leagues = settings.available_leagues

        db.commit()
        db.refresh(fantasy_league_model)
        return FantasyLeague.model_validate(fantasy_league_model)


def update_fantasy_league_status(
        fantasy_league_id: FantasyLeagueID,
        new_status: FantasyLeagueStatus) -> FantasyLeague:
    with DatabaseConnection() as db:
        fantasy_league_model: Optional[FantasyLeagueModel] = db.query(FantasyLeagueModel) \
            .filter_by(id=fantasy_league_id).first()
        assert (fantasy_league_model is not None)

        fantasy_league_model.status = new_status
        db.commit()
        db.refresh(fantasy_league_model)
        return FantasyLeague.model_validate(fantasy_league_model)


def update_fantasy_league_current_draft_position(
        fantasy_league_id: FantasyLeagueID, new_current_draft_position: int) -> FantasyLeague:
    with DatabaseConnection() as db:
        fantasy_league_model: Optional[FantasyLeagueModel] = db.query(FantasyLeagueModel) \
            .filter_by(id=fantasy_league_id).first()
        assert (fantasy_league_model is not None)

        fantasy_league_model.current_draft_position = new_current_draft_position
        db.commit()
        db.refresh(fantasy_league_model)
        return FantasyLeague.model_validate(fantasy_league_model)


# --------------------------------------------------
# ------ Fantasy League Membership Operations ------
# --------------------------------------------------
def create_fantasy_league_membership(fantasy_league_membership: FantasyLeagueMembership) -> None:
    db_fantasy_league_membership = FantasyLeagueMembershipModel(
        **fantasy_league_membership.model_dump()
    )
    with DatabaseConnection() as db:
        db.add(db_fantasy_league_membership)
        db.commit()


def get_pending_and_accepted_members_for_league(
        fantasy_league_id: FantasyLeagueID) -> List[FantasyLeagueMembership]:
    with DatabaseConnection() as db:
        membership_models = db \
            .query(FantasyLeagueMembershipModel). \
            filter(and_(FantasyLeagueMembershipModel.league_id == fantasy_league_id,
                        FantasyLeagueMembershipModel.status.in_(
                            [FantasyLeagueMembershipStatus.PENDING,
                             FantasyLeagueMembershipStatus.ACCEPTED]))
                   ).all()
        memberships = [FantasyLeagueMembership.model_validate(membership_model)
                       for membership_model in membership_models]
        return memberships


def update_fantasy_league_membership_status(
        membership: FantasyLeagueMembership,
        new_status: FantasyLeagueMembershipStatus) -> None:
    membership.status = new_status
    db_membership = FantasyLeagueMembershipModel(**membership.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_membership)
        db.commit()


def get_user_membership_for_fantasy_league(
        user_id: UserID, fantasy_league_id: FantasyLeagueID) -> Optional[FantasyLeagueMembership]:
    with DatabaseConnection() as db:
        membership_model = db.query(FantasyLeagueMembershipModel) \
            .filter(FantasyLeagueMembershipModel.league_id == fantasy_league_id,
                    FantasyLeagueMembershipModel.user_id == user_id).first()
        if membership_model is None:
            return None
        else:
            return FantasyLeagueMembership.model_validate(membership_model)


def get_users_fantasy_leagues_with_membership_status(
        user_id: UserID,
        membership_status: FantasyLeagueMembershipStatus) \
        -> List[FantasyLeague]:
    with DatabaseConnection() as db:
        fantasy_league_models = db.query(FantasyLeagueModel) \
            .join(FantasyLeagueMembershipModel,
                  FantasyLeagueModel.id == FantasyLeagueMembershipModel.league_id) \
            .filter(and_(
                FantasyLeagueMembershipModel.user_id == user_id,
                FantasyLeagueMembershipModel.status == membership_status
            )).all()
        fantasy_leagues = [FantasyLeague.model_validate(fantasy_league_model)
                           for fantasy_league_model in fantasy_league_models]
        return fantasy_leagues


# --------------------------------------------------
# ----- Fantasy League Draft Order Operations ------
# --------------------------------------------------
def create_fantasy_league_draft_order(draft_order: FantasyLeagueDraftOrder) -> None:
    db_draft_order = FantasyLeagueDraftOrderModel(**draft_order.model_dump())
    with DatabaseConnection() as db:
        db.add(db_draft_order)
        db.commit()


def get_fantasy_league_draft_order(
        fantasy_league_id: FantasyLeagueID) -> List[FantasyLeagueDraftOrder]:
    with DatabaseConnection() as db:
        draft_order_models = db \
            .query(FantasyLeagueDraftOrderModel) \
            .filter(FantasyLeagueDraftOrderModel.fantasy_league_id == fantasy_league_id) \
            .all()
        draft_orders = [FantasyLeagueDraftOrder.model_validate(draft_order_model)
                        for draft_order_model in draft_order_models]
        return draft_orders


def delete_fantasy_league_draft_order(draft_order: FantasyLeagueDraftOrder) -> None:
    with DatabaseConnection() as db:
        db_draft_order = db.query(FantasyLeagueDraftOrderModel) \
            .filter(FantasyLeagueDraftOrderModel.fantasy_league_id == draft_order.fantasy_league_id,
                    FantasyLeagueDraftOrderModel.user_id == draft_order.user_id).first()
        assert (db_draft_order is not None)
        db.delete(db_draft_order)
        db.commit()


def update_fantasy_league_draft_order_position(
        draft_order: FantasyLeagueDraftOrder,
        new_position: int) -> None:
    draft_order.position = new_position
    db_draft_order = FantasyLeagueDraftOrderModel(**draft_order.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_draft_order)
        db.commit()


# --------------------------------------------------
# ------------ Fantasy Team Operations -------------
# --------------------------------------------------
def put_fantasy_team(fantasy_team: FantasyTeam) -> None:
    db_fantasy_team = FantasyTeamModel(**fantasy_team.model_dump())
    with DatabaseConnection() as db:
        db.merge(db_fantasy_team)
        db.commit()


def get_all_fantasy_teams_for_user(
        fantasy_league_id: FantasyLeagueID, user_id: UserID) -> List[FantasyTeam]:
    with DatabaseConnection() as db:
        fantasy_team_models = db.query(FantasyTeamModel) \
            .filter(FantasyTeamModel.fantasy_league_id == fantasy_league_id,
                    FantasyTeamModel.user_id == user_id).all()
        fantasy_teams = [FantasyTeam.model_validate(fantasy_team_model)
                         for fantasy_team_model in fantasy_team_models]
        return fantasy_teams


def get_all_fantasy_teams_for_week(
        fantasy_league_id: FantasyLeagueID, week: int) -> List[FantasyTeam]:
    with DatabaseConnection() as db:
        fantasy_team_models = db.query(FantasyTeamModel) \
            .filter(FantasyTeamModel.fantasy_league_id == fantasy_league_id,
                    FantasyTeamModel.week == week).all()
        fantasy_teams = [FantasyTeam.model_validate(fantasy_team_model)
                         for fantasy_team_model in fantasy_team_models]
        return fantasy_teams
