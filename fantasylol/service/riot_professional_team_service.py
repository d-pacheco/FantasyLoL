import logging
from typing import List
from fantasylol.db import crud
from fantasylol.db.models import ProfessionalTeam
from fantasylol.exceptions.professional_team_not_found_exception import \
    ProfessionalTeamNotFoundException
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.schemas.search_parameters import TeamSearchParameters


class RiotProfessionalTeamService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_professional_teams(self) -> List[ProfessionalTeam]:
        logging.info("Fetching and storing professional teams from riot's api")
        request_url = "https://esports-api.lolesports.com/persisted/gw/getTeams?hl=en-GB"
        try:
            res_json = self.riot_api_requester.make_request(request_url)
            fetched_teams = []

            for team in res_json['data']['teams']:
                # Validate the team data
                for key in team.keys():
                    if team[key] is None:
                        team[key] = 'None'
                if team['homeLeague'] != 'None':
                    team['homeLeague'] = team['homeLeague']['name']

                team_attrs = {
                    "id": int(team['id']),
                    "slug": team['slug'],
                    "name": team['name'],
                    "code": team['code'],
                    "image": team['image'],
                    "alternative_image": team['alternativeImage'],
                    "background_image": team['backgroundImage'],
                    "status": team['status'],
                    "home_league": team['homeLeague']
                }
                new_professional_team = ProfessionalTeam(**team_attrs)
                fetched_teams.append(new_professional_team)

            for new_professional_team in fetched_teams:
                crud.save_team(new_professional_team)
            return fetched_teams
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            raise e

    @staticmethod
    def get_teams(search_parameters: TeamSearchParameters) -> List[ProfessionalTeam]:
        filters = []
        if search_parameters.slug is not None:
            filters.append(ProfessionalTeam.slug == search_parameters.slug)
        if search_parameters.name is not None:
            filters.append(ProfessionalTeam.name == search_parameters.name)
        if search_parameters.code is not None:
            filters.append(ProfessionalTeam.code == search_parameters.code)
        if search_parameters.status is not None:
            filters.append(ProfessionalTeam.status == search_parameters.status)
        if search_parameters.league is not None:
            filters.append(ProfessionalTeam.home_league == search_parameters.league)

        professional_teams = crud.get_teams(filters)
        return professional_teams

    @staticmethod
    def get_team_by_id(professional_team_id: int) -> ProfessionalTeam:
        professional_team = crud.get_team_by_id(professional_team_id)
        if professional_team is None:
            raise ProfessionalTeamNotFoundException()
        return professional_team
