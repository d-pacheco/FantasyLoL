import logging

from src.common.schemas.riot_data_schemas import Match, StoredSchedule, RiotMatchID
from src.common.schemas.search_parameters import MatchSearchParameters

from src.db.database_service import DatabaseService
from src.db.models import MatchModel

from src.riot.exceptions import MatchNotFoundException
from src.riot.util import RiotApiRequester
from src.riot.job_runner import JobRunner

logger = logging.getLogger('fantasy-lol')


class RiotMatchService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
        self.riot_api_requester = RiotApiRequester()
        self.job_runner = JobRunner()

    def fetch_new_schedule_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.fetch_new_schedule_job,
            job_name="fetch schedule from riot job",
            max_retries=3
        )

    def fetch_new_schedule_job(self):
        riot_schedule = self.db.get_schedule("riot_schedule")
        if riot_schedule is None:
            logger.warning("No stored riot schedule found.")
            self.fetch_entire_schedule()
        current_page_token = riot_schedule.newer_token_key
        last_fetched_page_token = None

        no_new_schedule = False
        while not no_new_schedule:
            schedule = self.riot_api_requester.get_schedule(current_page_token)

            if len(schedule.matches) == 0:
                logger.debug(f"No matches found for page token {current_page_token}")
            else:
                logger.debug(
                    f"{len(schedule.matches)} matches found for page token {current_page_token}"
                )

            for match in schedule.matches:
                self.db.put_match(match)

            if schedule.schedule_pages.newer_token is None:
                logger.info(
                    f"No new page token available for current page token {current_page_token}"
                )
                no_new_schedule = True
                continue

            last_fetched_page_token = current_page_token
            current_page_token = schedule.schedule_pages.newer_token

            riot_schedule.older_token_key = last_fetched_page_token
            riot_schedule.newer_token_key = current_page_token
            self.db.update_schedule(riot_schedule)

    def fetch_entire_schedule(self):
        # To only be used on a new deployment to populate the database with the entire schedule
        # After which fetch new schedule should only be used

        # Save the starting schedule into the database
        logger.warning("Fetching entire schedule. "
                       "This should only occur on new deployments")
        schedule = self.riot_api_requester.get_schedule()

        for match in schedule.matches:
            self.db.put_match(match)

        if schedule.schedule_pages.newer_token is not None:
            riot_curr_token = schedule.schedule_pages.newer_token
        else:
            riot_curr_token = schedule.schedule_pages.older_token

        riot_schedule = StoredSchedule(
            schedule_name="riot_schedule",
            older_token_key=None,
            newer_token_key=riot_curr_token
        )

        # Used as a save point if we encounter an error during back prop
        entire_schedule = StoredSchedule(
            schedule_name="entire_schedule",
            older_token_key=schedule.schedule_pages.older_token,
            newer_token_key=None
        )
        self.db.update_schedule(riot_schedule)
        self.db.update_schedule(entire_schedule)

        self.backprop_older_schedules()
        self.fetch_new_schedule_job()

    def backprop_older_schedules(self):
        logger.info("Back propagating older schedule")
        entire_schedule = self.db.get_schedule("entire_schedule")
        assert (entire_schedule is not None)
        current_page_token = entire_schedule.older_token_key

        no_more_schedules = False
        while not no_more_schedules:
            if current_page_token is None:
                logger.info("No more schedule to back propagate.")
                no_more_schedules = True
                continue

            schedule = self.riot_api_requester.get_schedule(current_page_token)

            logger.debug(
                f"{len(schedule.matches)} matches found for page token {current_page_token}"
            )
            for match in schedule.matches:
                self.db.put_match(match)

            current_page_token = schedule.schedule_pages.older_token

            entire_schedule.older_token_key = current_page_token
            entire_schedule.newer_token_key = None
            self.db.update_schedule(entire_schedule)

    def get_matches(self, search_parameters: MatchSearchParameters) -> list[Match]:
        filters = []
        if search_parameters.league_slug is not None:
            filters.append(MatchModel.league_slug == search_parameters.league_slug)
        if search_parameters.tournament_id is not None:
            filters.append(MatchModel.tournament_id == search_parameters.tournament_id)
        matches = self.db.get_matches(filters)
        return matches

    def get_match_by_id(self, match_id: RiotMatchID) -> Match:
        match = self.db.get_match_by_id(match_id)
        if match is None:
            raise MatchNotFoundException()
        return match
