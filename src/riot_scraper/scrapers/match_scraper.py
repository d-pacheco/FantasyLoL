import logging
from datetime import datetime, timezone

from src.common.schemas.riot_data_schemas import StoredSchedule, Match, MatchState
from src.db.database_service import DatabaseService
from src.riot_scraper.riot_api.schemas.get_schedule import Schedule
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

    def fetch_new_schedule_retry_job(self) -> None:
        self.job_runner.run_retry_job(
            job_function=self.fetch_new_schedule_job,
            job_name="fetch schedule from riot job",
            max_retries=3,
        )

    def fetch_matches_with_missing_data(self) -> None:
        missing_data_matches = self.db.get_missing_data_matches()
        earliest_match = get_earliest_past_match(missing_data_matches)
        if not earliest_match:
            return
        logger.info("Past matches found with missing data. Fetching previous schedules for data.")

        earliest_start = datetime.fromisoformat(earliest_match.start_time.replace("Z", "+00:00"))
        riot_schedule = self.db.get_schedule("riot_schedule")
        assert riot_schedule is not None
        current_page_token = riot_schedule.older_token_key

        while True:
            get_schedule_response = self.riot_api_requester.get_schedule(current_page_token)
            schedule = get_schedule_response.data.schedule
            matches = self.__get_matches_from_schedule(schedule)
            for match in matches:
                self.db.put_match(match)

            all_matches_before_earliest_tbd = all(
                datetime.fromisoformat(match.start_time.replace("Z", "+00:00")) < earliest_start
                for match in matches
            )
            if all_matches_before_earliest_tbd:
                break
            current_page_token = schedule.pages.older

    def fetch_new_schedule_job(self) -> None:
        riot_schedule = self.db.get_schedule("riot_schedule")
        if riot_schedule is None:
            logger.warning("No stored riot schedule found.")
            self.fetch_entire_schedule()
            return
        self.fetch_matches_with_missing_data()
        current_page_token = riot_schedule.newer_token_key

        no_new_schedule = False
        while not no_new_schedule:
            get_schedule_response = self.riot_api_requester.get_schedule(current_page_token)
            schedule = get_schedule_response.data.schedule
            matches = self.__get_matches_from_schedule(schedule)

            if len(matches) == 0:
                logger.info(f"No matches found for page token {current_page_token}")
            else:
                logger.info(f"{len(matches)} matches found for page token {current_page_token}")

            for match in matches:
                self.db.put_match(match)

            if schedule.pages.newer is None:
                logger.info(
                    f"No new page token available for current page token {current_page_token}"
                )
                no_new_schedule = True
                continue

            last_fetched_page_token = current_page_token
            current_page_token = schedule.pages.newer

            riot_schedule.older_token_key = last_fetched_page_token
            riot_schedule.newer_token_key = current_page_token
            self.db.update_schedule(riot_schedule)

    def fetch_entire_schedule(self) -> None:
        # To only be used on a new deployment to populate the database with the entire schedule
        # After which fetch new schedule should only be used

        # Save the starting schedule into the database
        logger.warning("Fetching entire schedule. " "This should only occur on new deployments")
        get_schedule_response = self.riot_api_requester.get_schedule()
        schedule = get_schedule_response.data.schedule
        matches = self.__get_matches_from_schedule(schedule)

        for match in matches:
            self.db.put_match(match)

        newer_page = schedule.pages.newer
        riot_curr_token: str | None = newer_page if newer_page is not None else schedule.pages.older
        if schedule.pages.newer is not None:
            riot_curr_token = schedule.pages.newer
        else:
            riot_curr_token = schedule.pages.older

        riot_schedule = StoredSchedule(
            schedule_name="riot_schedule", older_token_key=None, newer_token_key=riot_curr_token
        )

        # Used as a save point if we encounter an error during back prop
        entire_schedule = StoredSchedule(
            schedule_name="entire_schedule",
            older_token_key=schedule.pages.older,
            newer_token_key=None,
        )
        self.db.update_schedule(riot_schedule)
        self.db.update_schedule(entire_schedule)

        self.backprop_older_schedules()
        self.fetch_new_schedule_job()

    def backprop_older_schedules(self) -> None:
        logger.info("Back propagating older schedule")
        entire_schedule = self.db.get_schedule("entire_schedule")
        assert entire_schedule is not None
        current_page_token = entire_schedule.older_token_key

        no_more_schedules = False
        while not no_more_schedules:
            if current_page_token is None:
                logger.info("No more schedule to back propagate.")
                no_more_schedules = True
                continue

            get_schedule_response = self.riot_api_requester.get_schedule(current_page_token)
            schedule = get_schedule_response.data.schedule
            matches = self.__get_matches_from_schedule(schedule)

            logger.info(f"{len(matches)} matches found for page token {current_page_token}")
            for match in matches:
                self.db.put_match(match)

            current_page_token = schedule.pages.older

            entire_schedule.older_token_key = current_page_token
            entire_schedule.newer_token_key = None
            self.db.update_schedule(entire_schedule)

    def __get_matches_from_schedule(self, schedule: Schedule) -> list[Match]:
        matches_from_schedule = []

        for event in schedule.events:
            if event.type != "match":
                continue
            match = event.match
            team_1_wins = None
            team_2_wins = None
            winning_team = None

            if event.state in [MatchState.COMPLETED, MatchState.INPROGRESS]:
                if match.teams[0].result:
                    team_1_wins = match.teams[0].result.gameWins
                if match.teams[1].result:
                    team_2_wins = match.teams[1].result.gameWins
            if event.state == MatchState.COMPLETED:
                assert match.teams[0].result is not None
                if match.teams[0].result.outcome == "win":
                    winning_team = match.teams[0].name
                else:
                    winning_team = match.teams[1].name

            get_event_details_response = self.riot_api_requester.get_event_details(match.id)
            assert get_event_details_response is not None

            event_detail = get_event_details_response.data.event

            new_match = Match(
                id=match.id,
                start_time=event.startTime,
                block_name=event.blockName,
                league_slug=event.league.slug,
                strategy_type=match.strategy.type,
                strategy_count=match.strategy.count,
                tournament_id=event_detail.tournament.id,
                team_1_name=match.teams[0].name,
                team_2_name=match.teams[1].name,
                state=event.state,
                team_1_wins=team_1_wins,
                team_2_wins=team_2_wins,
                winning_team=winning_team,
            )
            matches_from_schedule.append(new_match)

        return matches_from_schedule


def get_earliest_past_match(tbd_matches: list[Match]) -> Match | None:
    now_utc = datetime.now(timezone.utc)
    past_tbd_matches = [
        match
        for match in tbd_matches
        if datetime.fromisoformat(match.start_time.replace("Z", "+00:00")) < now_utc
    ]

    if not past_tbd_matches:
        return None

    return min(
        past_tbd_matches, key=lambda m: datetime.fromisoformat(m.start_time.replace("Z", "+00:00"))
    )
