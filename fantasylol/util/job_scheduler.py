import logging
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from fantasylol.service.riot_league_service import RiotLeagueService
from fantasylol.service.riot_tournament_service import RiotTournamentService
from fantasylol.service.riot_professional_team_service import RiotProfessionalTeamService
from fantasylol.service.riot_match_service import RiotMatchService
from fantasylol.util.config import Config


class JobScheduler:
    def __init__(self):
        self.riot_league_service = RiotLeagueService()
        self.riot_tournament_service = RiotTournamentService()
        self.riot_team_service = RiotProfessionalTeamService()
        self.riot_match_service = RiotMatchService()

        job_store = SQLAlchemyJobStore(url=Config.DATABASE_URL)
        self.scheduler = BackgroundScheduler(jobstores={'default': job_store})
        self.scheduler.start()
        atexit.register(self.shutdown_jobs)

    def schedule_all_jobs(self):
        logging.info("Scheduling jobs")

        league_service_schedule_config = Config.LEAGUE_SERVICE_SCHEDULE
        self.scheduler.add_job(
            self.riot_league_service.fetch_and_store_leagues,
            trigger=league_service_schedule_config["trigger"],
            hour=league_service_schedule_config["hour"],
            minute=league_service_schedule_config["minute"],
            id='league_service_job',
            replace_existing=True
        )

        tournament_service_schedule_config = Config.TOURNAMENT_SERVICE_SCHEDULE
        self.scheduler.add_job(
            self.riot_tournament_service.fetch_and_store_tournaments,
            trigger=tournament_service_schedule_config["trigger"],
            hour=tournament_service_schedule_config["hour"],
            minute=tournament_service_schedule_config["minute"],
            id='tournament_service_job',
            replace_existing=True
        )

        team_service_schedule_config = Config.TEAM_SERVICE_SCHEDULE
        self.scheduler.add_job(
            self.riot_tournament_service.fetch_and_store_tournaments,
            trigger=team_service_schedule_config["trigger"],
            hour=team_service_schedule_config["hour"],
            minute=team_service_schedule_config["minute"],
            id='team_service_job',
            replace_existing=True
        )

    def shutdown_jobs(self):
        logging.info("Shutting down scheduled jobs")
        self.scheduler.shutdown()
