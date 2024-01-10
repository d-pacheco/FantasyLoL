import logging
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from fantasylol.exceptions.JobConfigException import JobConfigException
from fantasylol.service.riot_league_service import RiotLeagueService
from fantasylol.service.riot_tournament_service import RiotTournamentService
from fantasylol.service.riot_professional_team_service import RiotProfessionalTeamService
from fantasylol.service.riot_professional_player_service import RiotProfessionalPlayerService
from fantasylol.service.riot_match_service import RiotMatchService
from fantasylol.service.riot_game_service import RiotGameService
from fantasylol.service.riot_game_stats_service import RiotGameStatsService
from fantasylol.util.config import Config

logger = logging.getLogger('fantasy-lol')


class JobScheduler:
    def __init__(self):
        self.riot_league_service = RiotLeagueService()
        self.riot_tournament_service = RiotTournamentService()
        self.riot_team_service = RiotProfessionalTeamService()
        self.riot_player_service = RiotProfessionalPlayerService()
        self.riot_match_service = RiotMatchService()
        self.riot_game_service = RiotGameService()
        self.riot_game_stats_service = RiotGameStatsService()

        job_store = SQLAlchemyJobStore(url=Config.DATABASE_URL)
        self.scheduler = BackgroundScheduler(jobstores={'default': job_store})
        self.scheduler.start()
        atexit.register(self.shutdown_jobs)

    def schedule_all_jobs(self):
        logger.info("Scheduling jobs")

        self.schedule_job(
            job_function=self.riot_league_service.fetch_and_store_leagues,
            job_config=Config.LEAGUE_SERVICE_SCHEDULE,
            job_id='league_service_job',
        )
        self.schedule_job(
            job_function=self.riot_tournament_service.fetch_and_store_tournaments,
            job_config=Config.TOURNAMENT_SERVICE_SCHEDULE,
            job_id='tournament_service_job'
        )
        self.schedule_job(
            job_function=self.riot_team_service.fetch_and_store_professional_teams,
            job_config=Config.TEAM_SERVICE_SCHEDULE,
            job_id='team_service_job'
        )
        self.schedule_job(
            job_function=self.riot_player_service.fetch_and_store_professional_players,
            job_config=Config.PLAYER_SERVICE_SCHEDULE,
            job_id='player_service_job'
        )
        self.schedule_job(
            job_function=self.riot_match_service.fetch_new_schedule,
            job_config=Config.MATCH_SERVICE_SCHEDULE,
            job_id='match_service_job'
        )
        self.schedule_job(
            job_function=self.riot_game_service.fetch_and_store_games_from_match_ids,
            job_config=Config.GAME_SERVICE_SCHEDULE,
            job_id='games_from_match_ids_job'
        )
        self.schedule_job(
            job_function=self.riot_game_stats_service.run_player_metadata_job,
            job_config=Config.GAME_STATS_SERVICE_SCHEDULE,
            job_id='player_metadata_job'
        )
        self.schedule_job(
            job_function=self.riot_game_stats_service.run_player_stats_job,
            job_config=Config.GAME_STATS_SERVICE_SCHEDULE,
            job_id='player_stats_job'
        )

    def schedule_job(self, job_function, job_config: dict, job_id: str, replace: bool = True):
        trigger = job_config.get('trigger', None)

        if trigger == 'cron':
            job_trigger = CronTrigger(
                day=job_config.get('day', None),
                week=job_config.get('week', None),
                hour=job_config.get('hour', None),
                minute=job_config.get('minute', None),
                second=job_config.get('second', None),
            )
        elif trigger == 'interval':
            job_trigger = IntervalTrigger(
                weeks=job_config.get('weeks', 0),
                days=job_config.get('days', 0),
                hours=job_config.get('hours', 0),
                minutes=job_config.get('minutes', 0),
                seconds=job_config.get('seconds', 0)
            )
        else:
            raise JobConfigException(
                f"Invalid trigger ({trigger}) when scheduling job with id: {job_id}"
            )

        self.scheduler.add_job(
            job_function,
            trigger=job_trigger,
            id=job_id,
            replace_existing=replace
        )

    def shutdown_jobs(self):
        logger.info("Shutting down scheduled jobs")
        self.scheduler.shutdown()
