from apscheduler.schedulers.background import BackgroundScheduler

from fantasylol.service.RiotLeagueService import RiotLeagueService
from fantasylol.service.RiotTournamentService import RiotTournamentService

class JobScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.riot_league_service = RiotLeagueService()
        self.riot_tournament_service = RiotTournamentService()


    def schedule_all_jobs(self):
        print("Scheduling jobs")

        self.scheduler.add_job(
            self.riot_league_service.fetch_and_store_leagues,
            trigger="cron",
            hour = "10",
            minute = "00"
        )

        self.scheduler.add_job(
            self.riot_tournament_service.fetch_and_store_tournaments,
            trigger="cron",
            hour = "10",
            minute = "05"
        )

        self.scheduler.start()
