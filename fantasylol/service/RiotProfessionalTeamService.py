from db.database import DatabaseConnection
from db.models import ProfessionalTeam
from exceptions.RiotApiStatusException import RiotApiStatusCodeAssertException
from util.RiotApiRequester import RiotApiRequester

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
                returned_teams.append(new_professional_team)
        
            for new_professional_team in returned_teams:
                with DatabaseConnection() as db:
                    db.merge(new_professional_team)
                    db.commit()
        except RiotApiStatusCodeAssertException as e:
            print(f"Error: {str(e)}")
            raise e
        except Exception as e:
            print(f"Error: {str(e)}")

