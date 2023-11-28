from typing import List
from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import ProfessionalTeam
from fantasylol.exceptions.professional_team_not_found_exception import ProfessionalTeamNotFoundException
from fantasylol.util.riot_api_requester import RiotApiRequester

class RiotProfessionalTeamService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_professional_teams(self) -> List[ProfessionalTeam]:
        print("Fetching and storing professional teams from riot's api")
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
                with DatabaseConnection() as db:
                    db.merge(new_professional_team)
                    db.commit()
            return fetched_teams
        except Exception as e:
            print(f"Error: {str(e)}")
            raise e

    def get_teams(self, query_params: dict = None) -> List[ProfessionalTeam]:
        with DatabaseConnection() as db:
            query = db.query(ProfessionalTeam)

            if query_params is None:
                return query.all()

            for param_key in query_params:
                param = query_params[param_key]
                if param is None:
                    continue
                column = getattr(ProfessionalTeam, param_key, None)
                if column is not None:
                    query = query.filter(column == param)
            professional_teams = query.all()
        return professional_teams
    
    def get_team_by_id(self, professional_team_id: int) -> ProfessionalTeam:
        with DatabaseConnection() as db:
            professional_team = db.query(ProfessionalTeam).filter(ProfessionalTeam.id == professional_team_id).first()
        if professional_team is None:
            raise ProfessionalTeamNotFoundException()
        return professional_team
