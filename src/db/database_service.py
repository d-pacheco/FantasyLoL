from typing import Optional, List
from src.common.schemas.fantasy_schemas import (
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
    UserAccountStatus,
    UserID
)
from src.common.schemas.riot_data_schemas import (
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
    StoredSchedule
)
from src.db.database_connection_provider import DatabaseConnectionProvider
from src.db.fantasy_dao import (
    draft_order_dao,
    fantasy_league_dao,
    fantasy_team_dao,
    membership_dao,
    user_dao
)
from src.db.riot_dao import (
    game_dao,
    match_dao,
    player_dao,
    player_metadata_dao,
    player_stats_dao,
    riot_league_dao,
    schedule_dao,
    team_dao,
    tournament_dao
)


class DatabaseService:
    def __init__(self, connection_provider: DatabaseConnectionProvider):
        self.connection_provider = connection_provider

    # ------------------------ #
    # Riot Database Operations #
    # ------------------------ #
    def put_game(self, game: Game) -> None:
        with self.connection_provider.get_db() as db:
            game_dao.put_game(db, game)

    def bulk_save_games(self, games: List[Game]) -> None:
        with self.connection_provider.get_db() as db:
            game_dao.bulk_save_games(db, games)

    def update_has_game_data(self, game_id: RiotGameID, has_game_data: bool) -> None:
        with self.connection_provider.get_db() as db:
            game_dao.update_has_game_data(db, game_id, has_game_data)

    def update_game_state(self, game_id: RiotGameID, state: GameState) -> None:
        with self.connection_provider.get_db() as db:
            game_dao.update_game_state(db, game_id, state)

    def update_game_last_stats_fetch(self, game_id: RiotGameID, last_fetch: bool) -> None:
        with self.connection_provider.get_db() as db:
            game_dao.update_game_last_stats_fetch(db, game_id, last_fetch)

    def get_games_with_last_stats_fetch(self, last_stats_fetch: bool) -> List[Game]:
        with self.connection_provider.get_db() as db:
            return game_dao.get_games_with_last_stats_fetch(db, last_stats_fetch)

    def get_games(self, filters: Optional[list] = None) -> List[Game]:
        with self.connection_provider.get_db() as db:
            return game_dao.get_games(db, filters)

    def get_games_to_check_state(self) -> List[RiotGameID]:
        with self.connection_provider.get_db() as db:
            return game_dao.get_games_to_check_state(db)

    def get_game_by_id(self, game_id: RiotGameID) -> Optional[Game]:
        with self.connection_provider.get_db() as db:
            return game_dao.get_game_by_id(db, game_id)

    def put_match(self, match: Match) -> None:
        with self.connection_provider.get_db() as db:
            match_dao.put_match(db, match)

    def get_matches(self, filters: Optional[list] = None) -> List[Match]:
        with self.connection_provider.get_db() as db:
            return match_dao.get_matches(db, filters)

    def get_match_by_id(self, match_id: RiotMatchID) -> Optional[Match]:
        with self.connection_provider.get_db() as db:
            return match_dao.get_match_by_id(db, match_id)

    def get_match_ids_without_games(self) -> List[RiotMatchID]:
        with self.connection_provider.get_db() as db:
            return match_dao.get_match_ids_without_games(db)

    def update_match_has_games(self, match_id: RiotMatchID, new_has_games: bool) -> None:
        with self.connection_provider.get_db() as db:
            match_dao.update_match_has_games(db, match_id, new_has_games)

    def put_player(self, player: ProfessionalPlayer) -> None:
        with self.connection_provider.get_db() as db:
            player_dao.put_player(db, player)

    def get_players(self, filters: Optional[list] = None) -> List[ProfessionalPlayer]:
        with self.connection_provider.get_db() as db:
            return player_dao.get_players(db, filters)

    def get_player_by_id(self, player_id: ProPlayerID) -> Optional[ProfessionalPlayer]:
        with self.connection_provider.get_db() as db:
            return player_dao.get_player_by_id(db, player_id)

    def put_player_metadata(self, player_metadata: PlayerGameMetadata) -> None:
        with self.connection_provider.get_db() as db:
            player_metadata_dao.put_player_metadata(db, player_metadata)

    def get_player_metadata(
            self, player_id: ProPlayerID, game_id: RiotGameID
    ) -> Optional[PlayerGameMetadata]:
        with self.connection_provider.get_db() as db:
            return player_metadata_dao.get_player_metadata(db, player_id, game_id)

    def get_game_ids_without_player_metadata(self) -> List[RiotGameID]:
        with self.connection_provider.get_db() as db:
            return player_metadata_dao.get_game_ids_without_player_metadata(db)

    def put_player_stats(self, player_stats: PlayerGameStats) -> None:
        with self.connection_provider.get_db() as db:
            player_stats_dao.put_player_stats(db, player_stats)

    def get_player_stats(
            self, game_id: RiotGameID, participant_id: int
    ) -> Optional[PlayerGameStats]:
        with self.connection_provider.get_db() as db:
            return player_stats_dao.get_player_stats(db, game_id, participant_id)

    def get_game_ids_to_fetch_player_stats_for(self) -> List[RiotGameID]:
        with self.connection_provider.get_db() as db:
            return player_stats_dao.get_game_ids_to_fetch_player_stats_for(db)

    def get_player_game_stats(self, filters: Optional[list] = None) -> List[PlayerGameData]:
        with self.connection_provider.get_db() as db:
            return player_stats_dao.get_player_game_stats(db, filters)

    def put_league(self, league: League) -> None:
        with self.connection_provider.get_db() as db:
            riot_league_dao.put_league(db, league)

    def get_leagues(self, filters: Optional[list] = None) -> List[League]:
        with self.connection_provider.get_db() as db:
            return riot_league_dao.get_leagues(db, filters)

    def get_league_by_id(self, league_id: RiotLeagueID) -> Optional[League]:
        with self.connection_provider.get_db() as db:
            return riot_league_dao.get_league_by_id(db, league_id)

    def update_league_fantasy_available_status(
            self, league_id: RiotLeagueID, new_status: bool
    ) -> Optional[League]:
        with self.connection_provider.get_db() as db:
            return riot_league_dao.update_league_fantasy_available_status(db, league_id, new_status)

    def get_league_ids_for_player(self, player_id: ProPlayerID) -> List[RiotLeagueID]:
        with self.connection_provider.get_db() as db:
            return riot_league_dao.get_league_ids_for_player(db, player_id)

    def get_schedule(self, schedule_name: str) -> Optional[StoredSchedule]:
        with self.connection_provider.get_db() as db:
            return schedule_dao.get_schedule(db, schedule_name)

    def update_schedule(self, schedule: StoredSchedule) -> None:
        with self.connection_provider.get_db() as db:
            schedule_dao.update_schedule(db, schedule)

    def put_team(self, team: ProfessionalTeam) -> None:
        with self.connection_provider.get_db() as db:
            team_dao.put_team(db, team)

    def get_teams(self, filters: Optional[list] = None) -> List[ProfessionalTeam]:
        with self.connection_provider.get_db() as db:
            return team_dao.get_teams(db, filters)

    def get_team_by_id(self, team_id: ProTeamID) -> Optional[ProfessionalTeam]:
        with self.connection_provider.get_db() as db:
            return team_dao.get_team_by_id(db, team_id)

    def put_tournament(self, tournament: Tournament) -> None:
        with self.connection_provider.get_db() as db:
            tournament_dao.put_tournament(db, tournament)

    def get_tournaments(self, filters: list) -> List[Tournament]:
        with self.connection_provider.get_db() as db:
            return tournament_dao.get_tournaments(db, filters)

    def get_tournament_by_id(self, tournament_id: RiotTournamentID) -> Optional[Tournament]:
        with self.connection_provider.get_db() as db:
            return tournament_dao.get_tournament_by_id(db, tournament_id)

    # --------------------------- #
    # Fantasy Database Operations #
    # --------------------------- #
    def create_fantasy_league_draft_order(self, draft_order: FantasyLeagueDraftOrder) -> None:
        with self.connection_provider.get_db() as db:
            draft_order_dao.create_fantasy_league_draft_order(db, draft_order)

    def get_fantasy_league_draft_order(
            self, fantasy_league_id: FantasyLeagueID
    ) -> List[FantasyLeagueDraftOrder]:
        with self.connection_provider.get_db() as db:
            return draft_order_dao.get_fantasy_league_draft_order(db, fantasy_league_id)

    def delete_fantasy_league_draft_order(self, draft_order: FantasyLeagueDraftOrder) -> None:
        with self.connection_provider.get_db() as db:
            draft_order_dao.delete_fantasy_league_draft_order(db, draft_order)

    def update_fantasy_league_draft_order_position(
            self, draft_order: FantasyLeagueDraftOrder, new_position: int
    ) -> None:
        with self.connection_provider.get_db() as db:
            draft_order_dao.update_fantasy_league_draft_order_position(
                db, draft_order, new_position
            )

    def create_fantasy_league(self, fantasy_league: FantasyLeague) -> None:
        with self.connection_provider.get_db() as db:
            fantasy_league_dao.create_fantasy_league(db, fantasy_league)

    def get_fantasy_league_by_id(
            self, fantasy_league_id: FantasyLeagueID
    ) -> Optional[FantasyLeague]:
        with self.connection_provider.get_db() as db:
            return fantasy_league_dao.get_fantasy_league_by_id(db, fantasy_league_id)

    def put_fantasy_league_scoring_settings(
            self, scoring_settings: FantasyLeagueScoringSettings
    ) -> None:
        with self.connection_provider.get_db() as db:
            fantasy_league_dao.put_fantasy_league_scoring_settings(db, scoring_settings)

    def get_fantasy_league_scoring_settings_by_id(
            self, fantasy_league_id: FantasyLeagueID
    ) -> Optional[FantasyLeagueScoringSettings]:
        with self.connection_provider.get_db() as db:
            return fantasy_league_dao.get_fantasy_league_scoring_settings_by_id(
                db, fantasy_league_id
            )

    def update_fantasy_league_settings(
            self, fantasy_league_id: FantasyLeagueID, settings: FantasyLeagueSettings
    ) -> FantasyLeague:
        with self.connection_provider.get_db() as db:
            return fantasy_league_dao.update_fantasy_league_settings(
                db, fantasy_league_id, settings
            )

    def update_fantasy_league_status(
            self, fantasy_league_id: FantasyLeagueID, new_status: FantasyLeagueStatus
    ) -> FantasyLeague:
        with self.connection_provider.get_db() as db:
            return fantasy_league_dao.update_fantasy_league_status(
                db, fantasy_league_id, new_status
            )

    def update_fantasy_league_current_draft_position(
            self, fantasy_league_id: FantasyLeagueID, new_current_draft_position: int
    ) -> FantasyLeague:
        with self.connection_provider.get_db() as db:
            return fantasy_league_dao.update_fantasy_league_current_draft_position(
                db, fantasy_league_id, new_current_draft_position
            )

    def put_fantasy_team(self, fantasy_team: FantasyTeam) -> None:
        with self.connection_provider.get_db() as db:
            fantasy_team_dao.put_fantasy_team(db, fantasy_team)

    def get_all_fantasy_teams_for_user(
            self, fantasy_league_id: FantasyLeagueID, user_id: UserID
    ) -> List[FantasyTeam]:
        with self.connection_provider.get_db() as db:
            return fantasy_team_dao.get_all_fantasy_teams_for_user(db, fantasy_league_id, user_id)

    def get_all_fantasy_teams_for_week(
            self, fantasy_league_id: FantasyLeagueID, week: int
    ) -> List[FantasyTeam]:
        with self.connection_provider.get_db() as db:
            return fantasy_team_dao.get_all_fantasy_teams_for_week(db, fantasy_league_id, week)

    def create_fantasy_league_membership(
            self, fantasy_league_membership: FantasyLeagueMembership
    ) -> None:
        with self.connection_provider.get_db() as db:
            membership_dao.create_fantasy_league_membership(db, fantasy_league_membership)

    def get_pending_and_accepted_members_for_league(
            self, fantasy_league_id: FantasyLeagueID
    ) -> List[FantasyLeagueMembership]:
        with self.connection_provider.get_db() as db:
            return membership_dao.get_pending_and_accepted_members_for_league(db, fantasy_league_id)

    def update_fantasy_league_membership_status(
            self, membership: FantasyLeagueMembership, new_status: FantasyLeagueMembershipStatus
    ) -> None:
        with self.connection_provider.get_db() as db:
            membership_dao.update_fantasy_league_membership_status(db, membership, new_status)

    def get_user_membership_for_fantasy_league(
            self, user_id: UserID, fantasy_league_id: FantasyLeagueID
    ) -> Optional[FantasyLeagueMembership]:
        with self.connection_provider.get_db() as db:
            return membership_dao.get_user_membership_for_fantasy_league(db, user_id,
                                                                         fantasy_league_id)

    def get_users_fantasy_leagues_with_membership_status(
            self, user_id: UserID, membership_status: FantasyLeagueMembershipStatus
    ) -> List[FantasyLeague]:
        with self.connection_provider.get_db() as db:
            return membership_dao.get_users_fantasy_leagues_with_membership_status(
                db, user_id, membership_status
            )

    def create_user(self, user: User) -> None:
        with self.connection_provider.get_db() as db:
            user_dao.create_user(db, user)

    def get_user_by_id(self, user_id: UserID) -> Optional[User]:
        with self.connection_provider.get_db() as db:
            return user_dao.get_user_by_id(db, user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        with self.connection_provider.get_db() as db:
            return user_dao.get_user_by_username(db, username)

    def get_user_by_email(self, email: str) -> Optional[User]:
        with self.connection_provider.get_db() as db:
            return user_dao.get_user_by_email(db, email)

    def update_user_account_status(
            self, user_id: UserID, account_status: UserAccountStatus
    ) -> None:
        with self.connection_provider.get_db() as db:
            user_dao.update_user_account_status(db, user_id, account_status)

    def update_user_verified(self, user_id: UserID, verified: bool) -> None:
        with self.connection_provider.get_db() as db:
            return user_dao.update_user_verified(db, user_id, verified)

    def get_user_by_verification_token(self, verification_token: str) -> Optional[User]:
        with self.connection_provider.get_db() as db:
            return user_dao.get_user_by_verification_token(db, verification_token)

    def update_user_verification_token(
            self,
            user_id: UserID,
            verification_token: Optional[str]
    ) -> None:
        with self.connection_provider.get_db() as db:
            user_dao.update_user_verification_token(db, user_id, verification_token)
