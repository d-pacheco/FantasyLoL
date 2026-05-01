import logging

from src.common.schemas.riot_data_schemas import (
    ScheduleMatch,
    ScheduleTeam,
    MatchDetails,
    DetailTeam,
    DetailGame,
    MatchState,
    GameState,
)
from src.db.database_service import DatabaseService
from src.riot_scraper.riot_api.riot_api_client import RiotApiClient
from src.riot_scraper.job_runner import JobRunner

logger = logging.getLogger("scraper")


class RiotMatchScraper:
    def __init__(
        self,
        database_service: DatabaseService,
        riot_api_requester: RiotApiClient,
        job_runner=JobRunner,
    ):
        self.db = database_service
        self.riot_api_requester = riot_api_requester
        self.job_runner = job_runner

    def sync_schedule(self) -> None:
        page_token = None
        while True:
            response = self.riot_api_requester.get_schedule(page_token)
            schedule = response.data.schedule
            match_ids = []

            for event in schedule.events:
                if event.type != "match" or event.match is None:
                    continue
                match_ids.append(event.match.id)

            # Check if all matches on this page already exist — early exit
            if match_ids and self.db.all_exist(match_ids):
                logger.info(f"All {len(match_ids)} matches on page already exist, stopping sync")
                break

            # Save matches from this page
            for event in schedule.events:
                if event.type != "match" or event.match is None:
                    continue
                match = event.match
                teams = []
                for i, team in enumerate(match.teams):
                    outcome = team.result.outcome if team.result else None
                    game_wins = team.result.gameWins if team.result else None
                    wins = team.record.wins if team.record else None
                    losses = team.record.losses if team.record else None
                    teams.append(
                        ScheduleTeam(
                            side=i + 1,
                            team_code=team.code,
                            team_name=team.name,
                            team_image=team.image,
                            game_wins=game_wins,
                            outcome=outcome,
                            wins=wins,
                            losses=losses,
                        )
                    )
                schedule_match = ScheduleMatch(
                    id=match.id,
                    start_time=event.startTime,
                    block_name=event.blockName or "",
                    league_slug=event.league.slug,
                    strategy_type=match.strategy.type,
                    strategy_count=match.strategy.count,
                    state=event.state,
                    teams=teams,
                )
                self.db.save_from_schedule(schedule_match)

            logger.info(f"Saved {len(match_ids)} matches from schedule page")

            if schedule.pages.older is None:
                logger.info("No older page token, stopping sync")
                break
            page_token = schedule.pages.older

    def backfill_event_details(self) -> None:
        match_ids = self.db.get_ids_without_games()
        for match_id in match_ids:
            response = self.riot_api_requester.get_event_details(match_id)
            if response is None:
                self.db.update_match_has_games(match_id, False)
                continue
            event = response.data.event
            teams = [DetailTeam(team_id=t.id, team_code=t.code) for t in event.match.teams]
            games = [DetailGame(id=g.id, state=g.state, number=g.number) for g in event.match.games]
            details = MatchDetails(
                match_id=match_id,
                league_id=event.league.id,
                tournament_id=event.tournament.id,
                teams=teams,
                games=games,
            )
            self.db.save_from_details(details)

    def refresh_stale_events(self) -> None:
        match_ids = self.db.get_stale_match_ids()
        for match_id in match_ids:
            response = self.riot_api_requester.get_event_details(match_id)
            if response is None:
                continue
            event = response.data.event
            teams = [DetailTeam(team_id=t.id, team_code=t.code) for t in event.match.teams]
            games = [DetailGame(id=g.id, state=g.state, number=g.number) for g in event.match.games]
            details = MatchDetails(
                match_id=match_id,
                league_id=event.league.id,
                tournament_id=event.tournament.id,
                teams=teams,
                games=games,
            )
            self.db.save_from_details(details)

            # Infer match state from game states
            if games and all(g.state == GameState.COMPLETED for g in games):
                self.db.update_match_state(match_id, MatchState.COMPLETED)
