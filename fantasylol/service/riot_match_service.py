from typing import List
from datetime import datetime
from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import Match
from fantasylol.db.models import Tournament
from fantasylol.db.models import Schedule
from fantasylol.exceptions.match_not_found_exception import MatchNotFoundException
from fantasylol.util.riot_api_requester import RiotApiRequester


class RiotMatchService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_entire_schedule(self):
        # To only be used on a new deployment to populate the database with the entire schedule
        # After which fetch new schedule should only be used

        # Check if a riot schedule already exists:
        with DatabaseConnection() as db:
            riot_schedule = db.query(Schedule)\
                .filter(Schedule.schedule_name == "riot_schedule").first()

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
            with DatabaseConnection() as db:
                db.merge(riot_schedule_model)
                db.merge(entire_schedule_model)
                db.commit()

        self.backprop_older_schedules()
        self.fetch_new_schedule()

    def backprop_older_schedules(self):
        with DatabaseConnection() as db:
            entire_schedule = db.query(Schedule) \
                .filter(Schedule.schedule_name == "entire_schedule").first()
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
            with DatabaseConnection() as db:
                db.merge(entire_schedule_model)
                db.commit()

    def fetch_new_schedule(self) -> bool:
        with DatabaseConnection() as db:
            riot_schedule = db.query(Schedule)\
                .filter(Schedule.schedule_name == "riot_schedule").first()
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
            with DatabaseConnection() as db:
                db.merge(riot_schedule_model)
                db.commit()
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
        with DatabaseConnection() as db:
            for new_match in fetched_matches:
                db.merge(new_match)
                db.commit()

    def fetch_and_store_matchs_from_tournament(
            self, tournament_id: int) -> List[Match]:
        print(f"Fetching matches for tournament with id {tournament_id}")
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

            print("Saving fetched matches to db")
            for new_match in fetched_matches:
                with DatabaseConnection() as db:
                    db.merge(new_match)
                    db.commit()
            return fetched_matches
        except Exception as e:
            print(f"Error: {str(e)}")
            raise e

    def get_all_matches(self) -> List[Match]:
        print("Fetching matches for all saved tournaments")
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

    def get_matches(self, query_params: dict = None) -> List[Match]:
        with DatabaseConnection() as db:
            query = db.query(Match)

            if query_params is None:
                return query.all()

            for param_key in query_params:
                param = query_params[param_key]
                if param is None:
                    continue
                column = getattr(Match, param_key, None)
                if column is not None:
                    query = query.filter(column == param)
            matches = query.all()
        return matches

    def get_match_by_id(self, match_id: int) -> Match:
        with DatabaseConnection() as db:
            match = db.query(Match).filter(Match.id == match_id).first()
        if match is None:
            raise MatchNotFoundException()
        return match
