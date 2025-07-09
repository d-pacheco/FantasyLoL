import logging

from src.common.schemas.riot_data_schemas import ProfessionalTeam, ProfessionalPlayer
from src.db.database_service import DatabaseService
from src.riot_scraper.riot_api.riot_api_client import RiotApiClient
from src.riot_scraper.job_runner import JobRunner

logger = logging.getLogger('scraper')


class RiotTeamScraper:
    def __init__(
            self,
            database_service: DatabaseService,
            riot_api_requester: RiotApiClient,
            job_runner: JobRunner
    ):
        self.db = database_service
        self.riot_api_requester = riot_api_requester
        self.job_runner = job_runner

    def fetch_professional_teams_from_riot_retry_job(self) -> None:
        self.job_runner.run_retry_job(
            job_function=self.fetch_professional_teams_from_riot_job,
            job_name="fetch teams from riot job",
            max_retries=3
        )

    def fetch_professional_teams_from_riot_job(self) -> None:
        get_teams_response = self.riot_api_requester.get_teams()

        for team in get_teams_response.data.teams:
            new_team = ProfessionalTeam(
                id=team.id,
                slug=team.slug,
                name=team.name,
                code=team.code,
                image=team.image,
                alternative_image=team.alternativeImage,
                background_image=team.backgroundImage,
                status=team.status,
                home_league=team.homeLeague.name if team.homeLeague else None
            )
            self.db.put_team(new_team)

            for player in team.players:
                new_player = ProfessionalPlayer(
                    id=player.id,
                    summoner_name=player.summonerName,
                    image=player.image,
                    role=player.role,
                    team_id=team.id
                )
                self.db.put_player(new_player)
