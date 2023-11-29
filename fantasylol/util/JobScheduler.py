from apscheduler.schedulers.background import BackgroundScheduler

from fantasylol.service.RiotLeagueService import RiotLeagueService
from fantasylol.service.RiotTournamentService import RiotTournamentService
from fantasylol.util.config import Config

class JobScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.riot_league_service = RiotLeagueService()
        self.riot_tournament_service = RiotTournamentService()


    def schedule_all_jobs(self):
        print("Scheduling jobs")

        league_service_schedule_config = Config.LEAGUE_SERVICE_SCHEDULE
        self.scheduler.add_job(
            self.riot_league_service.fetch_and_store_leagues,
            trigger=league_service_schedule_config["trigger"],
            hour=league_service_schedule_config["hour"],
            minute=league_service_schedule_config["minute"]
        )

        tournament_service_schedule_config = Config.TOURNAMENT_SERVICE_SCHEDULE
        self.scheduler.add_job(
            self.riot_tournament_service.fetch_and_store_tournaments,
            trigger=tournament_service_schedule_config["trigger"],
            hour=tournament_service_schedule_config["hour"],
            minute=tournament_service_schedule_config["minute"]
        )

        self.scheduler.start()
