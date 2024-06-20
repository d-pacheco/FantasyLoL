import logging
from typing import List

from ...common.schemas.riot_data_schemas import Match, Schedule, RiotMatchID
from ...common.schemas.search_parameters import MatchSearchParameters

from ...db import crud
from ...db.models import MatchModel

from ..exceptions.match_not_found_exception import MatchNotFoundException
from ..util.riot_api_requester import RiotApiRequester
from ..util.job_runner import JobRunner

logger = logging.getLogger('fantasy-lol')


class RiotMatchService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()
        self.job_runner = JobRunner()

    def fetch_new_schedule_retry_job(self):
        self.job_runner.run_retry_job(
            job_function=self.fetch_new_schedule_job,
            job_name="fetch schedule from riot job",
            max_retries=3
        )

    def fetch_new_schedule_job(self):
        riot_schedule = crud.get_schedule("riot_schedule")
        if riot_schedule is None:
            logging.warning("Riot schedule not found in db. Fetching entire schedule. "
                            "This should only occur on new deployments")
            return self.fetch_entire_schedule()
        current_page_token = riot_schedule.current_token_key
        last_fetched_page_token = None

        no_new_schedule = False
        while not no_new_schedule:
            schedule_pages = self.riot_api_requester.get_pages_from_schedule(current_page_token)
            if schedule_pages.current_token_key is None and last_fetched_page_token is None:
                no_new_schedule = True
                continue

            fetched_matches = self.riot_api_requester.get_matches_from_schedule(current_page_token)
            for match in fetched_matches:
                crud.put_match(match)

            if schedule_pages.current_token_key is None:
                no_new_schedule = True
                continue

            last_fetched_page_token = current_page_token
            current_page_token = schedule_pages.current_token_key

            riot_schedule.older_token_key = last_fetched_page_token
            riot_schedule.current_token_key = current_page_token
            crud.update_schedule(riot_schedule)

    def fetch_entire_schedule(self):
        # To only be used on a new deployment to populate the database with the entire schedule
        # After which fetch new schedule should only be used

        # Check if a riot schedule already exists:
        riot_schedule_from_db = crud.get_schedule("riot_schedule")
        if riot_schedule_from_db is None:
            # Save the starting schedule into the database
            fetched_matches = self.riot_api_requester.get_matches_from_schedule()
            for match in fetched_matches:
                crud.put_match(match)

            schedule_pages = self.riot_api_requester.get_pages_from_schedule()
            riot_schedule = Schedule(
                schedule_name="riot_schedule",
                older_token_key=None,
                current_token_key=schedule_pages.current_token_key
            )

            # Used as a save point if we encounter an error during back prop
            entire_schedule = Schedule(
                schedule_name="entire_schedule",
                older_token_key=schedule_pages.older_token_key,
                current_token_key=None
            )
            crud.update_schedule(riot_schedule)
            crud.update_schedule(entire_schedule)

        self.backprop_older_schedules()
        self.fetch_new_schedule_job()

    def backprop_older_schedules(self):
        entire_schedule = crud.get_schedule("entire_schedule")
        assert (entire_schedule is not None)
        older_page_token = entire_schedule.older_token_key

        no_more_schedules = False
        while not no_more_schedules:
            if older_page_token is None:
                no_more_schedules = True
                continue
            fetched_matches = self.riot_api_requester.get_matches_from_schedule(older_page_token)
            for match in fetched_matches:
                crud.put_match(match)
            schedule_pages = self.riot_api_requester.get_pages_from_schedule(older_page_token)
            assert (schedule_pages is not None)
            older_page_token = schedule_pages.older_token_key

            entire_schedule.older_token_key = older_page_token
            entire_schedule.current_token_key = None
            crud.update_schedule(entire_schedule)

    @staticmethod
    def get_matches(search_parameters: MatchSearchParameters) -> List[Match]:
        filters = []
        if search_parameters.league_slug is not None:
            filters.append(MatchModel.league_slug == search_parameters.league_slug)
        if search_parameters.tournament_id is not None:
            filters.append(MatchModel.tournament_id == search_parameters.tournament_id)
        matches = crud.get_matches(filters)
        return matches

    @staticmethod
    def get_match_by_id(match_id: RiotMatchID) -> Match:
        match = crud.get_match_by_id(match_id)
        if match is None:
            raise MatchNotFoundException()
        return match
