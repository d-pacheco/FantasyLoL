from db.database import DatabaseConnection
from util.RiotApiRequester import RiotApiRequester
from db.models import ProfessionalTeam

class RiotProfessionalTeamService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_professional_teams(self):
        print("Fetching and storing professional teams from riot's api")
        request_url = "https://esports-api.lolesports.com/persisted/gw/getTeams?hl=en-GB"
        try:
            res_json = self.riot_api_requester.make_request(request_url)
            returned_teams = []

            for team in res_json['data']['teams']:
                # Validate the team data
                for key in team.keys():
                    if team[key] is None:
                        team[key] = 'None'
                if team['homeLeague'] != 'None':
                    team['homeLeague'] = team['homeLeague']['name']

                new_professional_team = ProfessionalTeam()
                new_professional_team.id = int(team['id']),
                new_professional_team.slug = team['slug'],
                new_professional_team.name = team['name'],
                new_professional_team.code = team['code'],
                new_professional_team.image = team['image'],
                new_professional_team.alternative_image = team['alternativeImage'],
                new_professional_team.background_image = team['backgroundImage'],
                new_professional_team.status = team['status'],
                new_professional_team.home_league = team['homeLeague']
                returned_teams.append(new_professional_team)
        
            for new_professional_team in returned_teams:
                with DatabaseConnection() as db:
                    db.merge(new_professional_team)
                    db.commit()
        except Exception as e:
            random = 3
