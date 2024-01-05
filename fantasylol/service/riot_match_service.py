import logging
from typing import List
from datetime import datetime
from fantasylol.db.database import DatabaseConnection
from fantasylol.db import crud
from fantasylol.db.models import Match
from fantasylol.db.models import Tournament
from fantasylol.db.models import Schedule
from fantasylol.exceptions.match_not_found_exception import MatchNotFoundException
from fantasylol.schemas.search_parameters import MatchSearchParameters
from fantasylol.util.riot_api_requester import RiotApiRequester


class RiotMatchService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_entire_schedule(self):
        # To only be used on a new deployment to populate the database with the entire schedule
        # After which fetch new schedule should only be used

        # Check if a riot schedule already exists:
        riot_schedule = crud.get_schedule("riot_schedule")
        if riot_schedule is None:
            # Save the starting schedule into the database
            schedule_res_json = self.get_schedule()
            schedule = schedule_res_json["data"].get("schedule", {})
            pages = schedule['pages']
            self.save_schedule(schedule)
            riot_schedule_attr = {
                'schedule_name': "riot_schedule",
                'older_token_key': None,
                'current_token_key': pages['newer']
            }
            riot_schedule_model = Schedule(**riot_schedule_attr)

            # Used as a save point if we encounter an error during back prop
            entire_schedule_attr = {
                'schedule_name': "entire_schedule",
                'older_token_key': pages['older'],
                'current_token_key': None
            }
            entire_schedule_model = Schedule(**entire_schedule_attr)
            crud.update_schedule(riot_schedule_model)
            crud.update_schedule(entire_schedule_model)

        self.backprop_older_schedules()
        self.fetch_new_schedule()

    def backprop_older_schedules(self):
        entire_schedule = crud.get_schedule("entire_schedule")
        older_page_token = entire_schedule.older_token_key

        no_more_schedules = False
        while not no_more_schedules:
            if older_page_token is None:
                no_more_schedules = True
                continue
            older_schedule_res_json = self.get_schedule(older_page_token)
            older_schedule = older_schedule_res_json["data"].get("schedule", {})
            self.save_schedule(older_schedule)
            older_page_token = older_schedule['pages']['older']

            entire_schedule_attr = {
                'schedule_name': "entire_schedule",
                'older_token_key': older_page_token,
                'current_token_key': None
            }
            entire_schedule_model = Schedule(**entire_schedule_attr)
            crud.update_schedule(entire_schedule_model)

    def fetch_new_schedule(self) -> bool:
        riot_schedule = crud.get_schedule("riot_schedule")
        newer_page_token = riot_schedule.current_token_key

        schedule_updated = False
        no_new_schedule = False
        while not no_new_schedule:
            newer_schedule_res_json = self.get_schedule(newer_page_token)
            newer_schedule = newer_schedule_res_json["data"].get("schedule", {})
            pages = newer_schedule['pages']
            newer_page_token = pages['newer']
            if newer_page_token is None:
                no_new_schedule = True
                continue

            self.save_schedule(newer_schedule)
            schedule_updated = True
            riot_schedule_attr = {
                'schedule_name': "riot_schedule",
                'older_token_key': pages['older'],
                'current_token_key': newer_page_token
            }
            riot_schedule_model = Schedule(**riot_schedule_attr)
            crud.update_schedule(riot_schedule_model)
        return schedule_updated

    def get_schedule(self, page_token: str = None):
        if page_token is None:
            schedule_url = "https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-GB"
        else:
            schedule_url = (
                "https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-GB"
                f"&pageToken={page_token}"
            )
        return self.riot_api_requester.make_request(schedule_url)

    def save_schedule(self, schedule: dict):
        fetched_matches = []
        events = schedule.get("events", [])
        for event in events:
            match = event['match']
            event_details_url = (
                f"https://esports-api.lolesports.com/persisted/gw/getEventDetails"
                f"?hl=en-GB&id={match['id']}"
            )
            event_res_json = self.riot_api_requester.make_request(event_details_url)
            new_match_attrs = {
                "id": int(match['id']),
                "start_time": event['startTime'],
                "block_name": event['blockName'],
                "league_name": event['league']['name'],
                "strategy_type": match['strategy']['type'],
                "strategy_count": match['strategy']['count'],
                "tournament_id": event_res_json['data']['event']['tournament']['id'],
                "team_1_name": match['teams'][0]['name'],
                "team_2_name": match['teams'][1]['name']
            }
            new_match = Match(**new_match_attrs)
            fetched_matches.append(new_match)
        for new_match in fetched_matches:
            crud.save_match(new_match)

    def fetch_and_store_matchs_from_tournament(
            self, tournament_id: int) -> List[Match]:
        logging.info(f"Fetching matches for tournament with id {tournament_id}")
        request_url = (
            "https://esports-api.lolesports.com/persisted/gw"
            f"/getCompletedEvents?hl=en-GB&tournamentId={tournament_id}"
        )
        try:
            res_json = self.riot_api_requester.make_request(request_url)
            fetched_matches = []
            events = res_json["data"]["schedule"].get("events", [])
            for event in events:
                match = event['match']
                new_match_attrs = {
                    "id": int(match['id']),
                    "start_time": event['startTime'],
                    "block_name": event['blockName'],
                    "league_name": event['league']['name'],
                    "strategy_type": match['strategy']['type'],
                    "strategy_count": match['strategy']['count'],
                    "tournament_id": int(tournament_id),
                    "team_1_name": match['teams'][0]['name'],
                    "team_2_name": match['teams'][1]['name']
                }
                new_match = Match(**new_match_attrs)
                fetched_matches.append(new_match)

            logging.info(f"Saving fetched matches to db. Match count: {len(fetched_matches)}")
            for new_match in fetched_matches:
                crud.save_match(new_match)
            return fetched_matches
        except Exception as e:
            logging.error(f"{str(e)}")
            raise e

    def get_all_matches(self) -> List[Match]:
        logging.info("Fetching matches for all saved tournaments")
        try:
            fetched_matches = []
            with DatabaseConnection() as db:
                stored_tournaments: List[Tournament] = db.query(Tournament).all()
            min_start_date = datetime(2020, 1, 1)
            for tournament in stored_tournaments:
                if min_start_date < datetime.strptime(tournament.start_date, "%Y-%m-%d"):
                    matches = self.fetch_and_store_matchs_from_tournament(tournament.id)
                else:
                    continue
                for match in matches:
                    fetched_matches.append(match)
            return fetched_matches
        except Exception as e:
            raise e

    @staticmethod
    def get_matches(search_parameters: MatchSearchParameters) -> List[Match]:
        filters = []
        if search_parameters.league_name is not None:
            filters.append(Match.league_name == search_parameters.league_name)
        if search_parameters.tournament_id is not None:
            filters.append(Match.tournament_id == search_parameters.tournament_id)
        matches = crud.get_matches(filters)
        return matches

    @staticmethod
    def get_match_by_id(match_id: int) -> Match:
        match = crud.get_match_by_id(match_id)
        if match is None:
            raise MatchNotFoundException()
        return match
