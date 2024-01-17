import logging
from typing import List
from fantasylol.db import crud
from fantasylol.db.models import MatchModel
from fantasylol.db.models import Schedule
from fantasylol.exceptions.match_not_found_exception import MatchNotFoundException
from fantasylol.schemas.riot_data_schemas import Match
from fantasylol.schemas.search_parameters import MatchSearchParameters
from fantasylol.util.riot_api_requester import RiotApiRequester

logger = logging.getLogger('fantasy-lol')


class RiotMatchService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_entire_schedule(self) -> bool:
        # To only be used on a new deployment to populate the database with the entire schedule
        # After which fetch new schedule should only be used

        # Check if a riot schedule already exists:
        riot_schedule = crud.get_schedule("riot_schedule")
        if riot_schedule is None:
            # Save the starting schedule into the database
            fetched_matches = self.riot_api_requester.get_matches_from_schedule()
            for match in fetched_matches:
                crud.save_match(match)

            schedule_pages = self.riot_api_requester.get_pages_from_schedule()
            riot_schedule_attr = {
                'schedule_name': "riot_schedule",
                'older_token_key': None,
                'current_token_key': schedule_pages.newer
            }
            riot_schedule_model = Schedule(**riot_schedule_attr)

            # Used as a save point if we encounter an error during back prop
            entire_schedule_attr = {
                'schedule_name': "entire_schedule",
                'older_token_key': schedule_pages.older,
                'current_token_key': None
            }
            entire_schedule_model = Schedule(**entire_schedule_attr)
            crud.update_schedule(riot_schedule_model)
            crud.update_schedule(entire_schedule_model)

        self.backprop_older_schedules()
        return self.fetch_new_schedule()

    def backprop_older_schedules(self):
        entire_schedule = crud.get_schedule("entire_schedule")
        older_page_token = entire_schedule.older_token_key

        no_more_schedules = False
        while not no_more_schedules:
            if older_page_token is None:
                no_more_schedules = True
                continue
            fetched_matches = self.riot_api_requester.get_matches_from_schedule(older_page_token)
            for match in fetched_matches:
                crud.save_match(match)
            schedule_pages = self.riot_api_requester.get_pages_from_schedule(older_page_token)
            older_page_token = schedule_pages.older

            entire_schedule_attr = {
                'schedule_name': "entire_schedule",
                'older_token_key': older_page_token,
                'current_token_key': None
            }
            entire_schedule_model = Schedule(**entire_schedule_attr)
            crud.update_schedule(entire_schedule_model)

    def fetch_new_schedule(self) -> bool:
        riot_schedule = crud.get_schedule("riot_schedule")
        if riot_schedule is None:
            logging.warning("Riot schedule not found in db. Fetching entire schedule. "
                            "This should only occur on new deployments")
            return self.fetch_entire_schedule()
        newer_page_token = riot_schedule.current_token_key

        schedule_updated = False
        no_new_schedule = False
        while not no_new_schedule:
            schedule_pages = self.riot_api_requester.get_pages_from_schedule(newer_page_token)
            newer_page_token = schedule_pages.newer
            if newer_page_token is None:
                no_new_schedule = True
                continue

            fetched_matches = self.riot_api_requester.get_matches_from_schedule(newer_page_token)
            for match in fetched_matches:
                crud.save_match(match)

            schedule_updated = True
            riot_schedule_attr = {
                'schedule_name': "riot_schedule",
                'older_token_key': schedule_pages.older,
                'current_token_key': newer_page_token
            }
            riot_schedule_model = Schedule(**riot_schedule_attr)
            crud.update_schedule(riot_schedule_model)
        return schedule_updated

    @staticmethod
    def get_matches(search_parameters: MatchSearchParameters) -> List[Match]:
        filters = []
        if search_parameters.league_slug is not None:
            filters.append(MatchModel.league_slug == search_parameters.league_slug)
        if search_parameters.tournament_id is not None:
            filters.append(MatchModel.tournament_id == search_parameters.tournament_id)
        matches_orms = crud.get_matches(filters)
        matches = [Match.model_validate(match_orm) for match_orm in matches_orms]
        return matches

    @staticmethod
    def get_match_by_id(match_id: str) -> Match:
        match_orm = crud.get_match_by_id(match_id)
        if match_orm is None:
            raise MatchNotFoundException()
        match = Match.model_validate(match_orm)
        return match
